# -*- coding: utf-8 -*-

"""
***************************************************************************
    maptoolselect.py
    ---------------------
    Date                 : October 2013
    Copyright            : (C) 2013-2018 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'October 2013'
__copyright__ = '(C) 2013-2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import sys

from qgis.PyQt.QtCore import pyqtSignal, Qt, QRect
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtGui import QColor

from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import (Qgis,
                       QgsGeometry,
                       QgsWkbTypes,
                       QgsRectangle,
                       QgsMessageLog,
                       QgsApplication,
                       QgsVectorLayer,
                       QgsCoordinateTransform,
                       QgsProject,
                       QgsVector,
                       QgsCsException,
                       QgsRenderContext,
                       QgsExpressionContextUtils,
                       QgsFeatureRequest,
                      )

FILL_COLOR = QColor(254, 178, 76, 63)
STROKE_COLOR = QColor(254, 58, 29, 100)


class MapToolSelect(QgsMapTool):
    ''' Based on the QGIS select tool
    '''
    featuresSelected = pyqtSignal()

    def __init__(self, canvas):
        super(MapToolSelect, self).__init__(canvas)

        self.canvas = canvas
        self.cursor = QgsApplication.getThemeCursor(QgsApplication.Select)

        self.rubberBand = None
        self.dragStart = None
        self.selectionActive = False

    def activate(self):
        super(MapToolSelect, self).activate()
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        super(MapToolSelect, self).deactivate()
        self.canvas.unsetCursor()

    def canvasPressEvent(self, event):
        if self.rubberBand is None:
            self.initRubberBand()

        self.dragStart = event.pos()

    def canvasMoveEvent(self, event):
        if event.buttons() != Qt.LeftButton:
            return

        r = QRect()
        if not self.selectionActive:
            self.selectionActive = True
            rect = QRect(event.pos(), event.pos())
        else:
            rect = QRect(event.pos(), self.dragStart)

        if self.rubberBand is not None:
            self.rubberBand.setToCanvasRectangle(rect)

    def canvasReleaseEvent(self, event):
        point = event.pos() - self.dragStart
        if not self.selectionActive or (point.manhattanLength() < QApplication.startDragDistance()):
            self.selectionActive = False
            self.selectFeatures(QgsGeometry.fromPointXY(self.toMapCoordinates(event.pos())), event.modifiers())

        if self.rubberBand is not None and self.selectionActive:
            self.selectFeatures(self.rubberBand.asGeometry(), event.modifiers())
            self.rubberBand.reset()

        self.selectionActive = False

        self.featuresSelected.emit()

    def initRubberBand(self):
        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rubberBand.setFillColor(FILL_COLOR)
        self.rubberBand.setStrokeColor(STROKE_COLOR)

    def selectFeatures(self, geometry, modifiers):
        if geometry.type() == QgsWkbTypes.PointGeometry:
            layer = self.canvas.currentLayer()
            # TODO: check layer validity
            rect = self.expandSelectRectangle(geometry.asPoint(), layer)
            self.selectSingleFeature(QgsGeometry.fromRect(rect), modifiers)
        else:
            self.selectMultipleFeatures(geometry, modifiers)

    def expandSelectRectangle(self, mapPoint, layer):
        boxSize = 0
        if layer is None or layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            # for lines and points make rectangle to simplify selection
            boxSize = 5
        else:
            boxSize = 1

        transform = self.canvas.getCoordinateTransform()
        point = transform.transform(mapPoint)
        ll = transform.toMapCoordinates(point.x() - boxSize, point.y() + boxSize)
        ur = transform.toMapCoordinates(point.x() + boxSize, point.y() - boxSize)
        return QgsRectangle(ll, ur)

    def selectSingleFeature(self, geometry, modifiers):
        layer = self.canvas.currentLayer()
        # TODO: check layer validity

        QApplication.setOverrideCursor(Qt.WaitCursor)
        selectedFeatures = self.getMatchingFeatures(geometry, False, True)
        if len(selectedFeatures) == 0:
            if not (modifiers & Qt.ShiftModifier or modifiers & Qt.ControlModifier):
                layer.removeSelection()

            QApplication.restoreOverrideCursor()
            return

        behavior = QgsVectorLayer.SetSelection
        if modifiers & Qt.ShiftModifier or modifiers & Qt.ControlModifier:
            # either shift or control modifier switches to "toggle" selection mode
            selectId = selectedFeatures[0]
            layerSelectedFeatures = layer.selectedFeatureIds()
            if selectId in layerSelectedFeatures:
                behavior = QgsVectorLayer.RemoveFromSelection
            else:
                behavior = QgsVectorLayer.AddToSelection

        layer.selectByIds(selectedFeatures, behavior)
        QApplication.restoreOverrideCursor()

    def selectMultipleFeatures(self, geometry, modifiers):
        behavior = QgsVectorLayer.SetSelection

        if modifiers & Qt.ShiftModifier and modifiers & Qt.ControlModifier:
            behavior = QgsVectorLayer.IntersectSelection
        elif modifiers & Qt.ShiftModifier:
            behavior = QgsVectorLayer.AddToSelection
        elif modifiers & Qt.ControlModifier:
            behavior = QgsVectorLayer.RemoveFromSelection

        contains = modifiers & Qt.AltModifier
        self.setSelectedFeatures(geometry, behavior, contains)

    def setSelectedFeatures(self, geometry, behavior=QgsVectorLayer.SetSelection, contains=True, singleSelect=False):
        layer = self.canvas.currentLayer()
        #TODO: check layer validity

        QApplication.setOverrideCursor(Qt.WaitCursor)

        selectedFeatures = self.getMatchingFeatures(geometry, contains, singleSelect)
        layer.selectByIds(selectedFeatures, behavior)

        QApplication.restoreOverrideCursor()

    def getMatchingFeatures(self, geometry, contains, singleSelect):
        newFeatures = []
        if geometry.type() != QgsWkbTypes.PolygonGeometry:
            return newFeatures

        layer = self.canvas.currentLayer()
        if layer is None:
            return newFeatures

        selectGeomTrans = QgsGeometry(geometry)
        try:
            ct = QgsCoordinateTransform(self.canvas.mapSettings().destinationCrs(), layer.crs(), QgsProject.instance())
            if not ct.isShortCircuited() and selectGeomTrans.type() == QgsWkbTypes.PolygonGeometry:
                poly = selectGeomTrans.asPolygon()
                if len(poly) == 1 and len(poly[0]) == 5:
                    ringIn = poly[0]
                    ringOut = []
                    ringOut.append(ringIn[0])
                    i = 1
                    for j in range(1, 5):
                        v = QgsVector((ringIn[j] - ringIn[j - 1]) / 10.0)
                        for k in range(9):
                            ringOut.append(ringOut[i - 1] + v)
                            i += 1
                        ringOut.append(ringIn[j])
                        i += 1
                    selectGeomTrans = QgsGeometry.fromPolygonXY([ringOut])

            selectGeomTrans.transform(ct)
        except QgsCsException as e:
            QgsMessageLog.logMessage("Selection extends beyond layer's coordinate system")
            return newFeatures

        context = QgsRenderContext.fromMapSettings(self.canvas.mapSettings())
        context.expressionContext().appendScope(QgsExpressionContextUtils.layerScope(layer))

        r = None
        if layer.renderer():
            r = layer.renderer().clone()
            r.startRender(context, layer.fields())

        request = QgsFeatureRequest()
        request.setFilterRect(selectGeomTrans.boundingBox())
        request.setFlags(QgsFeatureRequest.ExactIntersect)

        if r:
            request.setSubsetOfAttributes(r.usedAttributes(context), layer.fields())
        else:
            request.setSubsetOfAttributes([])

        closestFeatureId = 0
        foundSingleFeature = False
        closestFeatureDist = sys.float_info.max
        for f in layer.getFeatures(request):
            context.expressionContext().setFeature(f)
            if r and  not r.willRenderFeature(f, context):
                continue

            g = f.geometry()
            if contains:
                if not selectGeomTrans.contains(g):
                    continue

            else:
                if not selectGeomTrans.intersects(g):
                    continue

            if singleSelect:
                foundSingleFeature = True
                distance = g.distance(selectGeomTrans)
                if distance <= closestFeatureDist:
                    closestFeatureDist = distance
                    closestFeatureId = f.id()
            else:
                newFeatures.append(f.id())

        if singleSelect and foundSingleFeature:
            newFeatures.append(closestFeatureId)

        if r:
            r.stopRender(context)

        return newFeatures

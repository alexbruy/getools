# -*- coding: utf-8 -*-

"""
***************************************************************************
    selecttool.py
    ---------------------
    Date                 : October 2013
    Copyright            : (C) 2013 by Alexander Bruy
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
__copyright__ = '(C) 2013, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *


class SelectTool(QgsMapTool):
    featuresSelected = pyqtSignal()

    def __init__(self, iface, canvas):
        QgsMapTool.__init__(self, canvas)

        self.iface = iface
        self.canvas = canvas
        self.cursor = Qt.ArrowCursor

        self.dragging = False
        self.rubberBand = None
        self.selectRect = QRect()

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def canvasPressEvent(self, event):
        self.selectRect.setRect(0, 0, 0, 0)
        self.rubberBand = QgsRubberBand(self.canvas, QGis.Polygon)

    def canvasMoveEvent(self, event):
        if event.buttons() != Qt.LeftButton:
            return

        if not self.dragging:
            self.dragging = True
            self.selectRect.setTopLeft(event.pos())

        self.selectRect.setBottomRight(event.pos())
        self._setRubberBand()

    def canvasReleaseEvent(self, event):
        vlayer = self._getCurrentVectorLayer()
        if vlayer is None:
            if self.rubberBand:
                self.rubberBand.reset(QGis.Polygon)
                del self.rubberBand
                self.rubberBand = None
                self.dragging = False
            return

        # If the user simply clicked without dragging a rect we will
        # fabricate a small 1x1 pix rect and then continue as if they
        # had dragged a rect.
        if not self.dragging:
            self._expandSelectRectangle(vlayer, event.pos())
        else:
            # Set valid values for rectangle's width and height
            if self.selectRect.width() == 1:
                self.selectRect.setLeft(self.selectRect.left() + 1)
            if self.selectRect.height() == 1:
                self.selectRect.setBottom(self.selectRect.bottom() + 1)

        if self.rubberBand:
            self._setRubberBand()

            selectGeom = self.rubberBand.asGeometry()
            self._setSelectFeatures(selectGeom, event)
            del selectGeom

            self.rubberBand.reset(QGis.Polygon)
            del self.rubberBand
            self.rubberBand = None

        self.dragging = False
        self.featuresSelected.emit()

    def _setRubberBand(self):
        transform = self.canvas.getCoordinateTransform()

        ll = transform.toMapCoordinates(self.selectRect.left(),
                                        self.selectRect.bottom())
        ur = transform.toMapCoordinates(self.selectRect.right(),
                                        self.selectRect.top())

        if self.rubberBand:
            self.rubberBand.reset(QGis.Polygon)
            self.rubberBand.addPoint(ll, False)
            self.rubberBand.addPoint(QgsPoint(ur.x(), ll.y()), False)
            self.rubberBand.addPoint(ur, False)
            self.rubberBand.addPoint(QgsPoint(ll.x(), ur.y()), True)

    def _getCurrentVectorLayer(self):
        layer = self.canvas.currentLayer()
        if layer is None or layer.type() != QgsMapLayer.VectorLayer:
            self.iface.messageBar().pushMessage(
                self.tr('No active vector layer'),
                self.tr('To select features, choose a vector layer '
                        'in the legend'),
                QgsMessageBar.INFO,
                self.iface.messageTimeout())
        return layer

    def _expandSelectRectangle(self, layer, point):
        boxSize = 0

        if layer.geometryType() != QGis.Polygon:
            # If point or line use an artificial bounding box of 10x10 pixels
            # to aid the user to click on a feature accurately
            boxSize = 5
        else:
            # Otherwise just use the click point for polys
            boxSize = 1

        self.selectRect.setLeft(point.x() - boxSize)
        self.selectRect.setRight(point.x() + boxSize)
        self.selectRect.setTop(point.y() - boxSize)
        self.selectRect.setBottom(point.y() + boxSize)

    def _setSelectFeatures(self, selectGeometry, event):
        doContains = True if event.modifiers() & Qt.ShiftModifier else False
        doDifference = True if event.modifiers() & Qt.ControlModifier else False
        singleSelect = False

        if selectGeometry.type() != QGis.Polygon:
            return

        vlayer = self._getCurrentVectorLayer()
        if vlayer is None:
            return

        # toLayerCoordinates will throw an exception for any 'invalid' points
        # in the rubber band.
        # For example, if you project a world map onto a globe using EPSG:2163
        # and then click somewhere off the globe, an exception will be thrown.
        selectGeomTrans = QgsGeometry(selectGeometry)

        if self.canvas.mapRenderer().hasCrsTransformEnabled():
            try:
                ct = QgsCoordinateTransform(
                        self.canvas.mapRenderer().destinationCrs(),
                        vlayer.crs())
                selectGeomTrans.transform(ct)
            except QgsCsException as cse:
                # Catch exception for 'invalid' point and leave existing
                # selection unchanged
                self.iface.messageBar().pushMessage(
                    self.tr("CRS Exception"),
                    self.tr("Selection extends beyond layer's coordinate"
                            'system.'),
                    QgsMessageBar.WARNING,
                    self.iface.messageTimeout())
                return

        QApplication.setOverrideCursor(Qt.WaitCursor)

        print 'Selection layer:', vlayer.name()
        print 'Selection polygon:', selectGeomTrans.exportToWkt()
        print 'doContains:', 'T' if doContains else 'F'
        print 'doDifference:', 'T' if doDifference else 'F'

        request = QgsFeatureRequest().setFilterRect(
            selectGeomTrans.boundingBox()).setFlags(
                QgsFeatureRequest.ExactIntersect).setSubsetOfAttributes([])

        newSelectedFeatures = []
        closestFeatureId = 0
        foundSingleFeature = False
        closestFeatureDist = sys.float_info.max

        for f in vlayer.getFeatures(request):
            g = f.geometry()
            if doContains:
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
                newSelectedFeatures.append(f.id())

        if singleSelect and foundSingleFeature:
            newSelectedFeatures.append(closestFeatureId)

        print 'Number of new selected features:', len(newSelectedFeatures)

        if doDifference:
            layerSelectedFeatures = vlayer.selectedFeaturesIds()

            selectedFeatures = []
            deselectedFeatures = []
            for i in newSelectedFeatures:
                if i in layerSelectedFeatures:
                    deselectedFeatures.append(i)
                else:
                    selectedFeatures.append(i)

            vlayer.modifySelection(selectedFeatures, deselectedFeatures)
        else:
            vlayer.setSelectedFeatures(newSelectedFeatures)

        QApplication.restoreOverrideCursor()

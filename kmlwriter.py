# -*- coding: utf-8 -*-

"""
***************************************************************************
    kmlwriter.py
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

from PyQt4.QtCore import *
from qgis.core import *

from optionsdialog import OptionsDialog
import geutils as utils


class KMLWriter(QObject):
    def __init__(self):
        QObject.__init__(self)

        self.layer = None

        self.altMode = ''
        self.altitude = 0.0
        self.extrude = False
        self.tessellate = False

    def exportPoint(self, point):
        pass

    def exportLayer(self, layer, onlySelected=False):
        self.layer = layer
        layerType = self.layer.type()
        if layerType == QgsMapLayer.VectorLayer:
            if self.layer.hasGeometryType():
                self._exportVectorLayer(onlySelected)
            else:
                print 'Layer has no geometry'
        elif layerType == QgsMapLayer.RasterLayer:
            pass
        else:
            print 'Unsupported layer type', layerType

    def _exportVectorLayer(self, onlySelected):
        # Read geometry settings
        geometryType = self.layer.geometryType()
        if geometryType == QGis.Point:
            mode = self.settings.value(
                    'points/altitude_mode', 0, type=int)
            self.altMode = OptionsDialog.ALTITUDE_MODES[mode]
            self.altitude = self.settings.value(
                    'points/altitude', 0.0, type=float)
            self.extrude =  self.settings.value(
                    'points/extrude', False, type=bool)
        elif geometryType == QGis.Line:
            mode = self.settings.value(
                    'lines/altitude_mode', 0, type=int)
            self.altMode = OptionsDialog.ALTITUDE_MODES[mode]
            self.altitude = self.settings.value(
                    'lines/altitude', 0.0, type=float)
            self.extrude =  self.settings.value(
                    'lines/extrude', False, type=bool)
            self.tessellate =  self.settings.value(
                    'lines/tessellate', False, type=bool)
        elif geometryType == QGis.Polygon:
            mode = self.settings.value(
                    'polygons/altitude_mode', 0, type=int)
            self.altMode = OptionsDialog.ALTITUDE_MODES[mode]
            self.altitude = self.settings.value(
                    'polygons/altitude', 0.0, type=float)
            self.extrude =  self.settings.value(
                    'polygons/extrude', False, type=bool)
            self.tessellate =  self.settings.value(
                    'polygons/tessellate', False, type=bool)
        else:
            # TODO: emit signal and stop
            print 'Unsupported geometry type', geometryType

        fileName = utils.tempFileName()
        with open(fileName, 'w') as kmlFile:
            kmlFile.write(self._kmlHeader())
            s = utils.encodeStringForXml(layer.name())
            kmlFile.write('<name>%s</name>\n' % s)

            # TODO: write layer styles

            hasName = self.layer.fieldNameIndex('name') == -1
            hasDescription = self.layer.fieldNameIndex('descr') == -1

            if onlySelected:
                for f in self.layer.selectedFeatures():
                    kmlFile.write(self._featureToKml(f))
            else:
                for f in self.layer.getFeatures():
                    kmlFile.write(self._featureToKml(f))
            kmlFile.write(self._kmlFooter())

    def _exportRasterLayer(self):
        pass

    def _kmlHeader(self):
        return '<?xml version="1.0" encoding="UTF-8"?>\n' \
               '<kml xmlns="http://www.opengis.net/kml/2.2"\n' \
               'xmlns:gx="http://www.google.com/kml/ext/2.2">\n' \
               '<Document>'

    def _kmlFooter(self):
        return '</Document>\n</kml>'

    def _featureToKml(self, feature):
        geom = feature.geometry()
        kmlFile.write('<Placemark>\n')
        if hasName:
            s = utils.encodeStringFroXml(feature['name'])
            kmlFile.write('<name>%s</name>\n' % s)
        if hasDescription:
            s = utils.encodeStringFroXml(feature['descr'])
            kmlFile.write('<description>%s</description>\n' % s)
        # TODO: write feature style
        kmlFile.write(self._geometryToKml(geom))
        kmlFile.write('</Placemark>\n')

    def _geometryToKml(self, geometry):
        wkbType = geometry.wkbType()

        kmlGeom = ''

        if wkbType in [QGis.WKBPoint, QGis.WKBPoint25D]:
            point = geometry.asPoint()
            kmlGeom = self._pointToKml(point)
        elif wkbType in [QGis.WKBLineString, QGis.WKBLineString25D]:
            line = geometry.asPolyline()
            kmlGeom = self._lineToKml(line)
        elif  wkbType in [QGis.WKBPolygon, QGis.WKBPolygon25D]:
            polygon = geometry.asPolygon()
            kmlGeom = self._polygonToKml(polygon)
        elif wkbType in [QGis.WKBMultiPoint, QGis.WKBMultiPoint25D]:
            points = geometry.asMultiPoint()
            kmlGeom += '<MultiGeometry>\n'
            for point in points:
                kmlGeom += self._pointToKml(point)
            kmlGeom += '</MultiGeometry>\n'
        elif wkbType in [QGis.WKBMultiLineString, QGis.WKBMultiLineString25D]:
            lines = geometry.asMultiPolyline()
            kmlGeom += '<MultiGeometry>\n'
            for line in lines:
                kmlGeom += self._lineToKml(line)
            kmlGeom += '</MultiGeometry>\n'
        elif wkbType in [QGis.WKBMultiPolygon, QGis.WKBMultiPolygon25D]:
            polygons = geometry.asMultiPolygon()
            kmlGeom += '<MultiGeometry>\n'
            for polygon in polygons:
                kmlGeom += self._polygonToKml(point)
            kmlGeom += '</MultiGeometry>\n'
        else:
            # TODO: emit signal/write to log and continue
            print 'Unknow geometry type'

        return kmlGeom

    def _pointToKml(self, point):
        kml = '<Point>\n'
        kml += '<extrude>%d</extrude>\n' % extrude
        kml += '<gx:altitudeMode>%s</gx:altitudeMode>\n' % altMode
        kml += '<coordinates>'
        kml += '%f,%f,%f' % (point.x(), point.y(), altitude)
        kml += '</coordinates>\n'
        kml += '</Point>\n'
        return kml

    def _lineToKml(self, line):
        coords = ''
        for point in line:
            coords += '%f,%f,%f ' % (point.x(), point.y(), altitude)

        kml = '<LineString>\n'
        kml += '<extrude>%d</extrude>\n' % extrude
        kml += '<tessellate>%d</tessellate>\n' % tessellate
        kml += '<gx:altitudeMode>%s</gx:altitudeMode>\n' % altMode
        kml += '<coordinates>'
        kml += coords[:-1]
        kml += '</coordinates>\n'
        kml += '</LineString>\n'
        return kml

    def _polygonToKml(self, polygon):
        rings = []
        for line in polygon:
            coords = ''
            for point in line:
                coords += '%f,%f,%f ' % (point.x(), point.y(), altitude)
            rings.append(coords[:-1])

        kml = '<Polygon>\n'
        kml += '<extrude>%d</extrude>\n' % extrude
        kml += '<tessellate>%d</tessellate>\n' % tessellate
        kml += '<gx:altitudeMode>%s</gx:altitudeMode>\n' % altMode
        kml += '<outerBoundaryIs>\n'
        kml += '<LinearRing>\n'
        kml += '<coordinates>'
        kml += rings[0]
        kml += '</coordinates>\n'
        kml += '</outerBoundaryIs>\n'
        for i in xrange(1, len(rings)):
            kml += '<innerBoundaryIs>\n'
            kml += '<LinearRing>\n'
            kml += '<coordinates>'
            kml += rings[i]
            kml += '</coordinates>\n'
            kml += '</innerBoundaryIs>\n'
        kml += '</Polygon>\n'
        return kml

    def _stylesToKml(self):
        geometryType = self.layer.geometryType()
        renderer = self.layer.rendererV2()
        rendererType = renderer.type()

        styleMap = dict()
        if rendererType == 'singleSymbol':
            pass
        elif rendererType == 'categorizedSymbol':
            pass
        elif rendererType == 'graduatedSymbol':
            pass
        elif rendererType == 'RuleRenderer':
            pass
        else:
            # TODO: emit signal/write to log and write deafault styles
            print 'Unsupported renderer'

    def _symbolToKml(self, symbol):
        pass

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

import os
import codecs

from PyQt4.QtCore import *
from qgis.core import *

from getools.gui.optionsdialog import OptionsDialog
import geutils as utils


class KMLWriter(QObject):
    exportError = pyqtSignal(str)
    exportFinished = pyqtSignal(str)

    def __init__(self):
        QObject.__init__(self)

        self.settings = QSettings('alexbruy', 'getools')
        self.geoCrs = QgsCoordinateReferenceSystem(4326)

        self.point = None
        self.layer = None
        self.crsTransform = None
        self.onlySelected = False
        self.needsTransform = False

    def setLayer(self, layer):
        self.layer = layer
        sourceCrs = self.layer.crs()
        if sourceCrs.authid() != 'EPSG:4326':
            self.crsTransform = QgsCoordinateTransform(sourceCrs, self.geoCrs)
            self.needsTransform = True

    def setOnlySelected(self, onlySelected):
        self.onlySelected = onlySelected

    def setPoint(self, point):
        self.point = point

    def exportPoint(self):
        mode = self.settings.value('points/altitude_mode', 0, int)
        altMode = OptionsDialog.ALTITUDE_MODES[mode]
        altitude = self.settings.value('points/altitude', 0.0, float)
        extrude = self.settings.value('points/extrude', False, bool)

        geomSettings = '<extrude>%d</extrude>\n' % extrude
        geomSettings += '<gx:altitudeMode>%s</gx:altitudeMode>\n' % altMode

        fileName = utils.tempFileName()
        with codecs.open(fileName, 'w', encoding='utf-8') as kmlFile:
            kmlFile.write(self._kmlHeader())

            kmlFile.write('<name>%s</name>\n' % self.tr('Cursor coordinates'))

            # TODO: write style

            kmlFile.write('<Placemark>\n')
            kmlFile.write('<name>%s</name>\n' % self.tr('Custom point'))
            kmlFile.write('<description>%s</description>\n' %
                          self.point.toString())
            # TODO: write point style
            kmlFile.write('<Point>\n')
            kmlFile.write(geomSettings)
            kmlFile.write('<coordinates>')
            kmlFile.write('%f,%f,%f' % (self.point.x(), self.point.y(),
                          altitude))
            kmlFile.write('</coordinates>\n')
            kmlFile.write('</Point>\n')
            kmlFile.write('</Placemark>\n')

            kmlFile.write(self._kmlFooter())

        self._cleanup()
        self.exportFinished.emit(fileName)

    def exportLayer(self):
        layerType = self.layer.type()
        if layerType == QgsMapLayer.VectorLayer:
            if self.layer.hasGeometryType():
                self._exportVectorLayer(self.onlySelected)
            else:
                self.exportError.emit(self.tr('Layer has no geometry'))
        elif layerType == QgsMapLayer.RasterLayer:
            providerType = self.layer.providerType()
            if providerType == 'gdal':
                self._exportRasterLayer()
            else:
                self.exportError.emit(
                    self.tr('Unsupported provider %s') % providerType)
        else:
            self.exportError.emit(
                    self.tr('Unsupported layer type %s') % layerType)

    def _exportVectorLayer(self, onlySelected):
        # Read geometry settings
        self.geomSettings = ''
        geometryType = self.layer.geometryType()
        if geometryType == QGis.Point:
            mode = self.settings.value('points/altitude_mode', 0, int)
            altMode = OptionsDialog.ALTITUDE_MODES[mode]
            self.altitude = self.settings.value('points/altitude', 0.0, float)
            extrude = self.settings.value('points/extrude', False, bool)

            self.geomSettings += '<extrude>%d</extrude>\n' % extrude
            self.geomSettings += \
                '<gx:altitudeMode>%s</gx:altitudeMode>\n' % altMode
        elif geometryType == QGis.Line:
            mode = self.settings.value('lines/altitude_mode', 0, int)
            altMode = OptionsDialog.ALTITUDE_MODES[mode]
            self.altitude = self.settings.value('lines/altitude', 0.0, float)
            extrude = self.settings.value('lines/extrude', False, bool)
            tessellate = self.settings.value('lines/tessellate', False, bool)

            self.geomSettings += '<extrude>%d</extrude>\n' % extrude
            self.geomSettings += '<tessellate>%d</tessellate>\n' % tessellate
            self.geomSettings += \
                '<gx:altitudeMode>%s</gx:altitudeMode>\n' % altMode
        elif geometryType == QGis.Polygon:
            mode = self.settings.value('polygons/altitude_mode', 0, int)
            altMode = OptionsDialog.ALTITUDE_MODES[mode]
            self.altitude = self.settings.value(
                'polygons/altitude', 0.0, float)
            extrude = self.settings.value('polygons/extrude', False, bool)
            tessellate = self.settings.value(
                'polygons/tessellate', False, bool)

            self.geomSettings += '<extrude>%d</extrude>\n' % extrude
            self.geomSettings += '<tessellate>%d</tessellate>\n' % tessellate
            self.geomSettings += \
                '<gx:altitudeMode>%s</gx:altitudeMode>\n' % altMode
        else:
            self.exportError.emit(
                self.tr('Unsupported geometry type %s') % geometryType)

        fileName = utils.tempFileName()
        with codecs.open(fileName, 'w', encoding='utf-8') as kmlFile:
            kmlFile.write(self._kmlHeader())
            s = utils.encodeStringForXml(self.layer.name())
            kmlFile.write('<name>%s</name>\n' % s)

            # TODO: write layer styles

            self.hasName = self.layer.fieldNameIndex('name') != -1
            self.hasDescription = self.layer.fieldNameIndex('descr') != -1

            if self.onlySelected:
                for f in self.layer.selectedFeatures():
                    kmlFile.write(self._featureToKml(f))
            else:
                for f in self.layer.getFeatures():
                    kmlFile.write(self._featureToKml(f))
            kmlFile.write(self._kmlFooter())

        self._cleanup()
        self.exportFinished.emit(fileName)

    def _exportRasterLayer(self):
        # Read ettings
        rendered = self.settings.value('rasters/rendered', False, bool)

        mode = self.settings.value('rasters/altitude_mode', 0, int)
        altMode = OptionsDialog.ALTITUDE_MODES[mode]
        altitude = self.settings.value('rasters/altitude', 0.0, float)

        geomSettings = '<altitude>%f</altitude>\n' % altitude
        geomSettings += '<gx:altitudeMode>%s</gx:altitudeMode>\n' % altMode

        rasterPath = self.layer.source()

        if rendered:
            tmpDir = utils.tempDirectory()
            fileName = os.path.splitext(os.path.basename(rasterPath))[0]
            rasterPath = os.path.join(tmpDir, fileName + '.tif')
            if not utils.writeRenderedRaster(self.layer, rasterPath):
                self.exportError.emit(
                    self.tr('Export of rendered raster failed.'))

        bbox = self.layer.extent()
        if self.needsTransform:
            bbox = self.crsTransform.transformBoundingBox(bbox)

        fileName = utils.tempFileName()
        with codecs.open(fileName, 'w', encoding='utf-8') as kmlFile:
            kmlFile.write(self._kmlHeader())
            s = utils.encodeStringForXml(self.layer.name())
            kmlFile.write('<name>%s</name>\n' % s)
            kmlFile.write('<GroundOverlay>\n')
            # TODO: write style
            kmlFile.write('<Icon>\n')
            kmlFile.write('<href>%s</href>\n' % rasterPath)
            kmlFile.write('</Icon>\n')
            # Altitude settings
            kmlFile.write(geomSettings)
            # Bounding box
            kmlFile.write('<LatLonBox>\n')
            kmlFile.write('<north>%s</north>\n' % bbox.yMaximum())
            kmlFile.write('<south>%s</south>\n' % bbox.yMinimum())
            kmlFile.write('<east>%s</east>\n' % bbox.xMaximum())
            kmlFile.write('<west>%s</west>\n' % bbox.xMinimum())
            kmlFile.write('<rotation>%s</rotation>\n' % 0.0)
            kmlFile.write('</LatLonBox>\n')
            kmlFile.write('</GroundOverlay>\n')
            kmlFile.write(self._kmlFooter())

        self._cleanup()
        self.exportFinished.emit(fileName)

    def _kmlHeader(self):
        return '<?xml version="1.0" encoding="UTF-8"?>\n' \
               '<kml xmlns="http://www.opengis.net/kml/2.2"\n' \
               'xmlns:gx="http://www.google.com/kml/ext/2.2">\n' \
               '<Document>'

    def _kmlFooter(self):
        return '</Document>\n</kml>'

    def _featureToKml(self, feature):
        geom = feature.geometry()
        if self.needsTransform:
            geom.transform(self.crsTransform)

        kml = ''
        kml += '<Placemark>\n'
        if self.hasName:
            s = utils.encodeStringForXml(feature['name'])
            kml += '<name>%s</name>\n' % s
        if self.hasDescription:
            s = utils.encodeStringForXml(feature['descr'])
            kml += '<description>%s</description>\n' % s
        # TODO: write feature style
        kml += self._geometryToKml(geom)
        kml += '</Placemark>\n'
        return kml

    def _geometryToKml(self, geometry):
        wkbType = geometry.wkbType()

        kmlGeom = ''

        if wkbType in [QGis.WKBPoint, QGis.WKBPoint25D]:
            point = geometry.asPoint()
            kmlGeom = self._pointToKml(point)
        elif wkbType in [QGis.WKBLineString, QGis.WKBLineString25D]:
            line = geometry.asPolyline()
            kmlGeom = self._lineToKml(line)
        elif wkbType in [QGis.WKBPolygon, QGis.WKBPolygon25D]:
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
                kmlGeom += self._polygonToKml(polygon)
            kmlGeom += '</MultiGeometry>\n'
        else:
            # TODO: emit signal/write to log and continue
            print 'Unknow geometry type'

        return kmlGeom

    def _pointToKml(self, point):
        kml = '<Point>\n'
        kml += self.geomSettings
        kml += '<coordinates>'
        kml += '%f,%f,%f' % (point.x(), point.y(), self.altitude)
        kml += '</coordinates>\n'
        kml += '</Point>\n'
        return kml

    def _lineToKml(self, line):
        coords = ''
        for point in line:
            coords += '%f,%f,%f ' % (point.x(), point.y(), self.altitude)

        kml = '<LineString>\n'
        kml += self.geomSettings
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
                coords += '%f,%f,%f ' % (point.x(), point.y(), self.altitude)
            rings.append(coords[:-1])

        kml = '<Polygon>\n'
        kml += self.geomSettings
        kml += '<outerBoundaryIs>\n'
        kml += '<LinearRing>\n'
        kml += '<coordinates>'
        kml += rings[0]
        kml += '</coordinates>\n'
        kml += '</LinearRing>\n'
        kml += '</outerBoundaryIs>\n'
        for i in xrange(1, len(rings)):
            kml += '<innerBoundaryIs>\n'
            kml += '<LinearRing>\n'
            kml += '<coordinates>'
            kml += rings[i]
            kml += '</coordinates>\n'
            kml += '</LinearRing>\n'
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

    def _cleanup(self):
        self.point = None
        self.layer = None
        self.crsTransform = None
        self.onlySelected = False
        self.needsTransform = False

        self.geomSettings = ''
        self.altitude = 0.0

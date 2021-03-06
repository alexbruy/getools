# -*- coding: utf-8 -*-

"""
***************************************************************************
    kmlwritertask.py
    ---------------------
    Date                 : September 2018
    Copyright            : (C) 2018 by Alexander Bruy
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
__date__ = 'September 2018'
__copyright__ = '(C) 2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import shutil
from string import Template

from qgis.PyQt.QtCore import pyqtSignal, QVariant, QCoreApplication

from qgis.core import (QgsTask,
                       QgsPointXY,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsProject,
                       QgsSettings,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem,
                       QgsRasterPipe,
                       QgsRasterNuller,
                       QgsRasterRange,
                       QgsRasterFileWriter,
                       QgsWkbTypes,
                       QgsFeatureRequest,
                      )

from getools.styleutils import defaultStyle, kmlStyle
from getools import geutils as utils

GEO_CRS = QgsCoordinateReferenceSystem(4326)


class KmlWriterTask(QgsTask):

    exportComplete = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)

    def __init__(self, data, onlySelected=False):
        name = self.tr('position') if isinstance(data, QgsPointXY) else data.name()
        QgsTask.__init__(self, 'GETools - {}'.format(name))

        self.data = data
        self.onlySelected = onlySelected

        self.fileName = ''
        self.error = ''

    def run(self):
        result = False

        if isinstance(self.data, QgsPointXY):
            result = self.positionToKml()
        elif isinstance(self.data, QgsVectorLayer):
            result = self.vectorToKml()
        elif isinstance(self.data, QgsRasterLayer):
            result = self.rasterToKml()

        return result

    def finished(self, result):
        if result:
            self.exportComplete.emit(self.fileName)
        else:
            self.errorOccurred.emit(self.error)

    def tr(self, text):
        return QCoreApplication.translate('KmlWriterTask', text)

    def positionToKml(self):
        settings = QgsSettings()
        altitude = settings.value('getools/pointAltitude', 0.0, float)
        extrude = settings.value('getools/pointExtrude', False, bool)
        altitudeMode = settings.value('getools/pointAltitudeMode', 'clampToGround', str)

        tpl = None
        with open(utils.templateFile('placemark.kml'), 'r', encoding='utf-8') as f:
            tpl = Template(f.read())

        subst = {'name': utils.encodeForXml('Clicked position'),
                 'description': utils.encodeForXml('Clicked position — ({})'.format(self.data.toString(6))),
                 'extrude': extrude,
                 'altitudeMode': altitudeMode,
                 'coordinates': '{},{},{}'.format(self.data.x(), self.data.y(), altitude),
                }

        self.fileName = os.path.normpath(utils.tempFileName('position.kml'))
        with open(self.fileName, 'w', encoding='utf-8') as f:
            f.write(tpl.substitute(subst))

        return True

    def rasterToKml(self):
        if self.data.providerType() != 'gdal':
            self.error = self.tr('Currently only GDAL rasters are supported.')
            return False

        settings = QgsSettings()
        altitude = settings.value('getools/rasterAltitude', 0.0, float)
        altitudeMode = settings.value('getools/rasterAltitudeMode', 'clampToGround', str)
        exportRendered = settings.value('getools/rasterRendered', False, bool)

        rasterFile = self.data.source()
        kmlFile = utils.tempFileName('{}.kml'.format(utils.safeLayerName(self.data.name())))

        if exportRendered:
            tmp = os.path.split(kmlFile)
            rasterFile = os.path.join(tmp[0], '{}.tif'.format(os.path.splitext(tmp[1])[0]))
            result = self._exportRaster(rasterFile, False)
            if not result:
                return False

        transform = QgsCoordinateTransform(self.data.crs(), GEO_CRS, QgsProject.instance())
        bbox = transform.transformBoundingBox(self.data.extent())

        tpl = None
        with open(utils.templateFile('raster.kml'), 'r', encoding='utf-8') as f:
            tpl = Template(f.read())

        layerName = utils.encodeForXml(self.data.name())
        subst = {'name': layerName,
                 'description': 'QGIS raster — '.format(layerName),
                 'source': rasterFile,
                 'altitude': altitude,
                 'altitudeMode': altitudeMode,
                 'north': bbox.yMaximum(),
                 'south': bbox.yMinimum(),
                 'east': bbox.xMaximum(),
                 'west': bbox.xMinimum(),
                 'rotation': 0.0,
                }

        self.fileName = os.path.normpath(kmlFile)
        with open(kmlFile, 'w', encoding='utf-8') as f:
            f.write(tpl.substitute(subst))

        return True

    def vectorToKml(self):
        result = False
        geometryType = self.data.geometryType()
        if geometryType == QgsWkbTypes.PointGeometry:
            result = self._pointsToKml()
        elif geometryType == QgsWkbTypes.LineGeometry:
            result = self._linesToKml()
        elif geometryType == QgsWkbTypes.PolygonGeometry:
            result = self._polygonsToKml()
        else:
            self.error = self.tr('Unsupported geometry type "{}"'.format(QgsWkbTypes.geometryDisplayString(geometryType)))
            result = False

        return result

    def _exportRaster(self, filePath, rawMode=True):
        provider = self.data.dataProvider()
        cols = provider.xSize()
        rows = provider.ySize()

        pipe = None
        if rawMode:
            pipe = QgsRasterPipe()
            if not pipe.set(provider.clone()):
                self.error = self.tr('Failed to export layer "{layer}": Cannot set pipe provider.'.format(layer=self.data.name()))
                return False

            nodata = {}
            for i in range(1, provider.bandCount() + 1):
                if provider.sourceHasNoDataValue(i):
                    value = provider.sourceNoDataValue(i)
                    nodata[i] = QgsRasterRange(value, value)

            nuller = QgsRasterNuller()
            for band, value in nodata.items():
                nuller.setNoData(band, [value])

            if not pipe.insert(1, nuller):
                self.error = self.tr('Failed to export layer "{layer}": Cannot set pipe nuller.'.format(layer=self.data.name()))
                return False
        else:
            pipe = self.data.pipe()

        writer = QgsRasterFileWriter(filePath)
        writer.setOutputFormat('GTiff')

        error = writer.writeRaster(pipe, cols, rows, provider.extent(), provider.crs())
        if error != QgsRasterFileWriter.NoError:
            self.error = self.tr('Failed to export layer "{layer}": {message}.'.format(layer=self.data.name(), message=error))
            return False

        return True

    def _pointsToKml(self):
        settings = QgsSettings()
        altitude = settings.value('getools/pointAltitude', 0.0, float)
        extrude = settings.value('getools/pointExtrude', False, bool)
        altitudeMode = settings.value('getools/pointAltitudeMode', 'clampToGround', str)
        name = settings.value('getools/pointName', '', str)
        description = settings.value('getools/pointDescription', '', str)

        fields = self.data.fields()
        idxName = fields.indexFromName(name)
        idxDescription = fields.indexFromName(description)

        overrideStyle = settings.value('QgsCollapsibleGroupBox/getools/grpPointStyle/checked', False, bool)
        if overrideStyle:
            styleMap, style = defaultStyle(self.data)
        else:
            styleMap, style = kmlStyle(self.data)

        if styleMap is None:
            self.error = style
            return False

        layerName = utils.encodeForXml(self.data.name())
        kmlFile = utils.tempFileName('{}.kml'.format(utils.safeLayerName(self.data.name())))
        with open(kmlFile, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">\n')
            f.write('  <Document>\n')
            f.write('    <name>{}</name>\n'.format(layerName))
            f.write('    <description>QGIS vector — {}</description>\n'.format(layerName))
            f.write('{}\n'.format(style))

            request = QgsFeatureRequest()
            request.setDestinationCrs(GEO_CRS, QgsProject.instance().transformContext())
            if self.onlySelected:
                request.setFilterFids(self.data.selectedFeatureIds())

            attrs = []
            if idxName != -1:
                attrs.append(idxName)
            if idxDescription != -1:
                attrs.append(idxDescription)
            if len(attrs) > 0:
                request.setSubsetOfAttributes(attrs)

            for styleId, expression in styleMap.items():
                if expression != 'all':
                    request.setFilterExpression(expression)

                for feat in self.data.getFeatures(request):
                    geom = feat.geometry()
                    pnt = geom.constGet()

                    f.write('    <Placemark>\n')

                    if idxName != -1:
                        f.write('      <name>{}</name>\n'.format(feat[name]))
                    if idxDescription != -1:
                        f.write('      <description>{}</description>\n'.format(feat[description]))

                    f.write('      <styleUrl>#{}</styleUrl>\n'.format(styleId))

                    geometry = []
                    for v in pnt.vertices():
                        geometry.append('      <Point>\n')
                        geometry.append('        <extrude>{}</extrude>\n'.format(extrude))
                        geometry.append('        <gx:altitudeMode>{}</gx:altitudeMode>\n'.format(altitudeMode))
                        geometry.append('        <coordinates>{},{},{}</coordinates>\n'.format(v.x(), v.y(), v.z() if v.is3D() else altitude))
                        geometry.append('      </Point>\n')

                    if geom.isMultipart():
                        f.write('      <MultiGeometry>\n')
                        f.write(''.join(geometry))
                        f.write('      </MultiGeometry>\n')
                    else:
                        f.write(''.join(geometry))

                    f.write('    </Placemark>\n')

            f.write('  </Document>\n')
            f.write('</kml>\n')

        self.fileName = os.path.normpath(kmlFile)
        return True

    def _linesToKml(self):
        settings = QgsSettings()
        altitude = settings.value('getools/lineAltitude', 0.0, float)
        extrude = settings.value('getools/lineExtrude', False, bool)
        tessellate = settings.value('getools/lineTessellate', False, bool)
        altitudeMode = settings.value('getools/lineAltitudeMode', 'clampToGround', str)
        name = settings.value('getools/lineName', '', str)
        description = settings.value('getools/lineDescription', '', str)

        fields = self.data.fields()
        idxName = fields.indexFromName(name)
        idxDescription = fields.indexFromName(description)

        overrideStyle = settings.value('QgsCollapsibleGroupBox/getools/grpLineStyle/checked', False, bool)
        if overrideStyle:
            styleMap, style = defaultStyle(self.data)
        else:
            styleMap, style = kmlStyle(self.data)

        if styleMap is None:
            self.error = style
            return False

        layerName = utils.encodeForXml(self.data.name())
        kmlFile = utils.tempFileName('{}.kml'.format(utils.safeLayerName(self.data.name())))
        with open(kmlFile, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">\n')
            f.write('  <Document>\n')
            f.write('    <name>{}</name>\n'.format(layerName))
            f.write('    <description>QGIS vector — {}</description>\n'.format(layerName))
            f.write('{}\n'.format(style))

            request = QgsFeatureRequest()
            request.setDestinationCrs(GEO_CRS, QgsProject.instance().transformContext())
            if self.onlySelected:
                request.setFilterFids(self.data.selectedFeatureIds())

            attrs = []
            if idxName != -1:
                attrs.append(idxName)
            if idxDescription != -1:
                attrs.append(idxDescription)
            if len(attrs) > 0:
                request.setSubsetOfAttributes(attrs)

            for styleId, expression in styleMap.items():
                if expression != 'all':
                    request.setFilterExpression(expression)

                for feat in self.data.getFeatures(request):
                    geom = feat.geometry()
                    parts = geom.asGeometryCollection()

                    f.write('    <Placemark>\n')

                    if idxName != -1:
                        f.write('      <name>{}</name>\n'.format(feat[name]))
                    if idxDescription != -1:
                        f.write('      <description>{}</description>\n'.format(feat[description]))

                    f.write('      <styleUrl>#{}</styleUrl>\n'.format(styleId))

                    geometry = []
                    for part in parts:
                        geometry.append('      <LineString>\n')
                        geometry.append('        <extrude>{}</extrude>\n'.format(extrude))
                        geometry.append('        <tessellate>{}</tessellate>\n'.format(tessellate))
                        geometry.append('        <gx:altitudeMode>{}</gx:altitudeMode>\n'.format(altitudeMode))
                        geometry.append('        <coordinates>\n')
                        g = part.constGet()
                        for p in g.points():
                            geometry.append('          {},{},{}\n'.format(p.x(), p.y(), p.z() if p.is3D() else altitude))
                        geometry.append('        </coordinates>\n')
                        geometry.append('      </LineString>\n')

                    if geom.isMultipart():
                        f.write('      <MultiGeometry>\n')
                        f.write(''.join(geometry))
                        f.write('      </MultiGeometry>\n')
                    else:
                        f.write(''.join(geometry))

                    f.write('    </Placemark>\n')

            f.write('  </Document>\n')
            f.write('</kml>\n')

        self.fileName = os.path.normpath(kmlFile)
        return True

    def _polygonsToKml(self):
        settings = QgsSettings()
        altitude = settings.value('getools/polygonAltitude', 0.0, float)
        extrude = settings.value('getools/polygonExtrude', False, bool)
        tessellate = settings.value('getools/polygonTessellate', False, bool)
        altitudeMode = settings.value('getools/polygonAltitudeMode', 'clampToGround', str)
        name = settings.value('getools/plygonName', '', str)
        description = settings.value('getools/polygonDescription', '', str)

        fields = self.data.fields()
        idxName = fields.indexFromName(name)
        idxDescription = fields.indexFromName(description)

        overrideStyle = settings.value('QgsCollapsibleGroupBox/getools/grpPolygonStyle/checked', False, bool)
        if overrideStyle:
            styleMap, style = defaultStyle(self.data)
        else:
            styleMap, style = kmlStyle(self.data)

        if styleMap is None:
            self.error = style
            return False

        layerName = utils.encodeForXml(self.data.name())
        kmlFile = utils.tempFileName('{}.kml'.format(utils.safeLayerName(self.data.name())))
        with open(kmlFile, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">\n')
            f.write('  <Document>\n')
            f.write('    <name>{}</name>\n'.format(layerName))
            f.write('    <description>QGIS vector — {}</description>\n'.format(layerName))
            f.write('{}\n'.format(style))

            request = QgsFeatureRequest()
            request.setDestinationCrs(GEO_CRS, QgsProject.instance().transformContext())
            if self.onlySelected:
                request.setFilterFids(self.data.selectedFeatureIds())

            attrs = []
            if idxName != -1:
                attrs.append(idxName)
            if idxDescription != -1:
                attrs.append(idxDescription)
            if len(attrs) > 0:
                request.setSubsetOfAttributes(attrs)

            for styleId, expression in styleMap.items():
                if expression != 'all':
                    request.setFilterExpression(expression)

                for feat in self.data.getFeatures(request):
                    geom = feat.geometry()
                    parts = geom.asGeometryCollection()

                    f.write('    <Placemark>\n')

                    if idxName != -1:
                        f.write('      <name>{}</name>\n'.format(feat[name]))
                    if idxDescription != -1:
                        f.write('      <description>{}</description>\n'.format(feat[description]))

                    f.write('      <styleUrl>#{}</styleUrl>\n'.format(styleId))

                    geometry = []
                    for part in parts:
                        geometry.append('      <Polygon>\n')
                        geometry.append('        <extrude>{}</extrude>\n'.format(extrude))
                        geometry.append('        <tessellate>{}</tessellate>\n'.format(tessellate))
                        geometry.append('        <gx:altitudeMode>{}</gx:altitudeMode>\n'.format(altitudeMode))

                        geometry.append('        <outerBoundaryIs>\n')
                        geometry.append('          <LinearRing>\n')
                        geometry.append('            <coordinates>\n')
                        polygon = part.constGet()
                        ring = polygon.exteriorRing()
                        for p in ring.points():
                            geometry.append('          {},{},{}\n'.format(p.x(), p.y(), p.z() if p.is3D() else altitude))
                        geometry.append('            </coordinates>\n')
                        geometry.append('          </LinearRing>\n')
                        geometry.append('        </outerBoundaryIs>\n')
                        for i in range(polygon.numInteriorRings()):
                            ring = polygon.interiorRing(i)
                            geometry.append('        <innerBoundaryIs>\n')
                            geometry.append('          <LinearRing>\n')
                            geometry.append('            <coordinates>\n')
                            for p in ring.points():
                                geometry.append('          {},{},{}\n'.format(p.x(), p.y(), p.z() if p.is3D() else altitude))
                            geometry.append('            </coordinates>\n')
                            geometry.append('          </LinearRing>\n')
                            geometry.append('        </innerBoundaryIs>\n')
                        geometry.append('      </Polygon>\n')

                    if geom.isMultipart():
                        f.write('      <MultiGeometry>\n')
                        f.write(''.join(geometry))
                        f.write('      </MultiGeometry>\n')
                    else:
                        f.write(''.join(geometry))

                    f.write('    </Placemark>\n')

            f.write('  </Document>\n')
            f.write('</kml>\n')

        self.fileName = os.path.normpath(kmlFile)
        return True

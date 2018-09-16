# -*- coding: utf-8 -*-

"""
***************************************************************************
    kmlutils.py
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
import re
from string import Template

from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import (QgsProject,
                       QgsSettings,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem,
                       QgsRasterPipe,
                       QgsRasterRange,
                       QgsRasterNuller,
                       QgsRasterFileWriter
                      )

import getools.geutils as utils

pluginPath = os.path.dirname(__file__)

BAD_CHARS = re.compile(r'[&:\(\)\-\,\'\.\/ ]')
GEO_CRS = QgsCoordinateReferenceSystem(4326)


def templateFile(fileName):
    return os.path.join(pluginPath, 'resources', fileName)


def safeName(layerName):
    return BAD_CHARS.sub('', layerName).title().replace(' ', '')


def rasterToKml(layer):
    kmlFile = utils.tempFileName('{}.kml'.format(safeName(layer.name())))
    rasterFile = layer.source()

    settings = QgsSettings()
    altitude = settings.value('raster/altitude', 0.0, float)
    altitudeMode = settings.value('raster/altitudeMode', 'clampToGround', str)
    exportRendered = settings.value('raster/rendered', False, bool)
    if exportRendered:
        tmp = os.path.split(kmlFile)
        rasterFile = os.path.join(tmp[0], '{}.tif'.format(os.path.splitext(tmp[1])[0]))
        result, error = _exportRenderedRaster(layer, rasterFile)
        if not result:
            return False, error

    transform = QgsCoordinateTransform(layer.crs(), GEO_CRS, QgsProject.instance())
    bbox = transform.transformBoundingBox(layer.extent())

    tpl = None
    with open(templateFile('raster.kml'), 'r', encoding='utf-8') as f:
        tpl = Template(f.read())

    subst = {'layerName': _encodeForXml(layer.name()),
             'description': _encodeForXml(rasterFile),
             'source': rasterFile,
             'altitude': altitude,
             'altitudeMode': altitudeMode,
             'north': bbox.yMaximum(),
             'south': bbox.yMinimum(),
             'east': bbox.xMaximum(),
             'west': bbox.xMinimum(),
             'rotation': 0.0,
            }
    with open(kmlFile, 'w', encoding='utf-8') as f:
        f.write(tpl.substitute(subst))

    return True, kmlFile


def _exportRenderedRaster(layer, filePath):
    provider = layer.dataProvider()
    cols = provider.xSize()
    rows = provider.ySize()

    pipe = QgsRasterPipe()
    if not pipe.set(provider.clone()):
        return False, tr('Failed to export layer "{layer}": Cannot set pipe provider.'.format(layer=layer.name()))

    nodata = {}
    for i in range(1, provider.bandCount() + 1):
        if provider.sourceHasNoDataValue(i):
            value = provider.sourceNoDataValue(i)
            nodata[i] = QgsRasterRange(value, value)

    nuller = QgsRasterNuller()
    for band, value in nodata.items():
        nuller.setNoData(band, [value])

    if not pipe.insert(1, nuller):
        return False, tr('Failed to export layer "{layer}": Cannot set pipe nuller.'.format(layer=layer.name()))

    writer = QgsRasterFileWriter(filePath)
    writer.setOutputFormat('GTiff')

    error = writer.writeRaster(pipe, cols, rows, provider.extent(), provider.crs())
    if error != QgsRasterFileWriter.NoError:
        return False, tr('Failed to export layer "{layer}": {message}.'.format(layer=layer.name(), message=error))

    return True


def _encodeForXml(string):
    encodedString = string
    encodedString.replace('&', '&amp;')
    encodedString.replace('"', '&quot;')
    encodedString.replace("'", '&apos;')
    encodedString.replace('<', '&lt;')
    encodedString.replace('>', '&gt;')
    return encodedString


def tr(text):
    return QCoreApplication.translate('GETools', text)

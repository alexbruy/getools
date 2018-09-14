# -*- coding: utf-8 -*-

"""
***************************************************************************
    geutils.py
    ---------------------
    Date                 : October 2013
    Copyright            : (C) 2013-2014 by Alexander Bruy
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
__copyright__ = '(C) 2013-2014, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import uuid
import tempfile


def tempDirectory():
    tmp = os.path.join(tempfile.gettempdir(), 'getools')
    if not os.path.exists(tmp):
        os.makedirs(tmp)

    return os.path.abspath(tmp)


def tempFileName():
    tmpDir = tempDirectory()
    fName = os.path.join(tmpDir, '{}.kml'.format(uuid.uuid4().hex))
    return fName


def removeTempFiles():
    tmpDir = tempDirectory()
    if os.path.exists(tmpDir):
        shutil.rmtree(tmpDir, True)


def encodeStringForXml(string):
    encodedString = string
    encodedString.replace('&', '&amp;')
    encodedString.replace('"', '&quot;')
    encodedString.replace("'", '&apos;')
    encodedString.replace('<', '&lt;')
    encodedString.replace('>', '&gt;')
    return encodedString


# ~ def writeRenderedRaster(layer, fileName):
    # ~ provider = layer.dataProvider()
    # ~ fileWriter = QgsRasterFileWriter(fileName)
    # ~ pipe = QgsRasterPipe(layer.pipe())

    # ~ projector = pipe.projector()
    # ~ if not projector:
        # ~ print 'Cannot get pipe projector'
        # ~ return False

    # ~ projector.setCRS(provider.crs(), provider.crs())

    # ~ if not pipe.last():
        # ~ del pipe
        # ~ return False

    # ~ fileWriter.writeRaster(pipe, provider.xSize(), provider.ySize(),
        # ~ provider.extent(), provider.crs())
    # ~ return True

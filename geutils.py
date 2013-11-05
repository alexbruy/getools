# -*- coding: utf-8 -*-

"""
***************************************************************************
    geutils.py
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
import uuid
from PyQt4.QtCore import *


def tempDirectory():
    tmp = unicode(os.path.join(QDir.tempPath(), 'getools'))
    if not os.path.exists(tmp):
        QDir().mkpath(tmp)

    return os.path.abspath(tmp)


def tempFileName():
    tmpDir = tempDirectory()
    fName = os.path.join(tmpDir, str(uuid.uuid4()).replace('-', '') + '.kml')
    return fName


def encodeStringForXml(string):
    encodedString = string
    encodedString.replace('&', '&amp;')
    encodedString.replace('"', '&quot;')
    encodedString.replace("'", '&apos;')
    encodedString.replace('<', '&lt;')
    encodedString.replace('>', '&gt;')
    return encodedString

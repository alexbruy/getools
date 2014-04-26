# -*- coding: utf-8 -*-

"""
***************************************************************************
    clicktool.py
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
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *


class ClickTool(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        QgsMapToolEmitPoint.__init__(self, canvas)

        self.canvas = canvas
        self.cursor = Qt.ArrowCursor
        self.geoCrs = QgsCoordinateReferenceSystem(4326)

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def canvasPressEvent(self, event):
        pnt = self.toMapCoordinates(event.pos())
        sourceCrs = self.canvas.mapSettings().destinationCrs()
        if sourceCrs.authid() != 'EPSG:4326':
            crsTransform = QgsCoordinateTransform(sourceCrs, self.geoCrs)
            pnt = crsTransform.transform(pnt)

        self.canvasClicked.emit(pnt, event.button())

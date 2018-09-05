# -*- coding: utf-8 -*-

"""
***************************************************************************
    maptoolclick.py
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

from qgis.core import (QgsApplication,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem,
                       QgsProject
                      )
from qgis.gui import QgsMapToolEmitPoint


class MapToolClick(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        super(MapToolClick, self).__init__(canvas)

        self.canvas = canvas
        self.cursor = QgsApplication.getThemeCursor(QgsApplication.CapturePoint)

        self.geoCrs = QgsCoordinateReferenceSystem(4326)

    def activate(self):
        super(MapToolClick, self).activate()
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        super(MapToolClick, self).deactivate()
        self.canvas.unsetCursor()

    def canvasPressEvent(self, event):
        transform = QgsCoordinateTransform(self.canvas.mapSettings().destinationCrs(), self.geoCrs, QgsProject.instance())
        pnt = transform.transform(self.toMapCoordinates(event.pos()))
        self.canvasClicked.emit(pnt, event.button())

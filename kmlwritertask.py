# -*- coding: utf-8 -*-

"""
***************************************************************************
    kmlwritertask.py
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

import os

from qgis.PyQt.QtCore import pyqtSignal, QVariant, QCoreApplication

from qgis.core import QgsTask, QgsGeometry, QgsVectorLayer, QgsRasterLayer

from getools import geutils as utils
from getools import kmlutils as kmlutils


class KmlWriterTask(QgsTask):

    exportComplete = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)

    def __init__(self, data, onlySelected=False):
        name = self.tr('position') if isinstance(data, QgsGeometry) else data.name()
        QgsTask.__init__(self, 'GETools - {}'.format(name))

        self.data = data
        self.onlySelected = onlySelected

        self.fileName = ''
        self.error = ''

    def run(self):
        result = True

        if isinstance(self.data, QgsGeometry):
            result = self._exportPosition()
        elif isinstance(self.data, QgsVectorLayer):
            result = self._exportVectorLayer()
        elif isinstance(self.data, QgsRasterLayer):
            result = self._exportRasterLayer()

        return result

    def finished(self, result):
        if result:
            self.exportComplete.emit(self.fileName)
        else:
            self.errorOccurred.emit(self.error)

    def tr(self, text):
        return QCoreApplication.translate('KmlWriterTask', text)

    def _exportRasterLayer(self):
        result, msg = kmlutils.rasterToKml(self.data)
        if result:
            self.fileName = os.path.normpath(msg)
            return True
        else:
            self.error = msg
            return False

    def _exportVectorLayer(self):
        pass

    def _exportPosition(self):
        pass

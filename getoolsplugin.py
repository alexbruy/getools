# -*- coding: utf-8 -*-

"""
***************************************************************************
    getoolsplugin.py
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

from qgis.PyQt.QtCore import QCoreApplication, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsApplication, QgsMapLayer

from getools.gui.maptoolclick import MapToolClick
# ~ from getools.tools.selecttool import SelectTool
# ~ from getools.gui.optionsdialog import OptionsDialog
from getools.gui.aboutdialog import AboutDialog
# ~ from getools.kmlwriter import KMLWriter
# ~ import getools.geutils as utils

pluginPath = os.path.dirname(__file__)

class GeToolsPlugin:
    def __init__(self, iface):
        self.iface = iface

        locale = QgsApplication.locale()
        qmPath = '{}/i18n/getools_{}.qm'.format(pluginPath, locale)

        if os.path.exists(qmPath):
            self.translator = QTranslator()
            self.translator.load(qmPath)
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        self.actionPostionToGe = QAction(self.tr('Coords to the Google Earth'), self.iface.mainWindow())
        self.actionPostionToGe.setIcon(QIcon(os.path.join(pluginPath, 'icons', 'ge-click.svg')))
        self.actionPostionToGe.setObjectName('gePosition')
        self.actionPostionToGe.setCheckable(True)

        self.actionFeaturesToGe = QAction(self.tr('Feature(s) to the Google Earth'), self.iface.mainWindow())
        self.actionFeaturesToGe.setIcon(QIcon(os.path.join(pluginPath, 'icons', 'ge-selected.svg')))
        self.actionFeaturesToGe.setObjectName('geFeatures')
        self.actionFeaturesToGe.setCheckable(True)

        self.actionVectorToGe = QAction(self.tr('Vector layer to the Google Earth'), self.iface.mainWindow())
        self.actionVectorToGe.setIcon(QIcon(os.path.join(pluginPath, 'icons', 'ge-export-vector.svg')))
        self.actionVectorToGe.setObjectName('geVector')

        self.actionRasterToGe = QAction(self.tr('Raster layer to the Google Earth'), self.iface.mainWindow())
        self.actionRasterToGe.setIcon(QIcon(os.path.join(pluginPath, 'icons', 'ge-export-raster.svg')))
        self.actionRasterToGe.setObjectName('geRaster')

        self.actionSettings = QAction(self.tr('Settings…'), self.iface.mainWindow())
        self.actionSettings.setIcon(QgsApplication.getThemeIcon('/mActionOptions.svg'))
        self.actionSettings.setObjectName('geSettings')

        self.actionAbout = QAction(self.tr('About GETools…'), self.iface.mainWindow())
        self.actionAbout.setIcon(QgsApplication.getThemeIcon('/mActionHelpContents.svg'))
        self.actionAbout.setObjectName('geAbout')

        self.iface.addPluginToMenu(self.tr('GETools'), self.actionPostionToGe)
        self.iface.addPluginToMenu(self.tr('GETools'), self.actionFeaturesToGe)
        self.iface.addPluginToMenu(self.tr('GETools'), self.actionVectorToGe)
        self.iface.addPluginToMenu(self.tr('GETools'), self.actionRasterToGe)
        self.iface.addPluginToMenu(self.tr('GETools'), self.actionSettings)
        self.iface.addPluginToMenu(self.tr('GETools'), self.actionAbout)

        self.iface.addVectorToolBarIcon(self.actionPostionToGe)
        self.iface.addVectorToolBarIcon(self.actionFeaturesToGe)
        self.iface.addVectorToolBarIcon(self.actionVectorToGe)
        self.iface.addRasterToolBarIcon(self.actionRasterToGe)

        self.actionPostionToGe.triggered.connect(self.selectPosition)
        self.actionFeaturesToGe.triggered.connect(self.selectFeatures)
        self.actionVectorToGe.triggered.connect(self.processLayer)
        self.actionRasterToGe.triggered.connect(self.processLayer)
        self.actionSettings.triggered.connect(self.settings)
        self.actionAbout.triggered.connect(self.about)

        # Map tools
        self.toolClick = MapToolClick(self.iface.mapCanvas())
        self.toolClick.setAction(self.actionPostionToGe)
        self.toolClick.canvasClicked.connect(self.exportPosition)

        # ~ self.toolSelect = SelectTool(self.iface, self.canvas)
        # ~ self.toolSelect.featuresSelected.connect(self.processFeatures)

        # Handle layer changes
        self.iface.currentLayerChanged.connect(self.toggleButtons)

        # ~ self.toggleTools(self.canvas.currentLayer())

        # Prepare worker
        # ~ self.thread = QThread()
        # ~ self.writer = KMLWriter()
        # ~ self.writer.moveToThread(self.thread)
        # ~ self.writer.exportError.connect(self.thread.quit)
        # ~ self.writer.exportError.connect(self.showError)
        # ~ self.writer.exportFinished.connect(self.thread.quit)
        # ~ self.writer.exportFinished.connect(self.openResults)

    def unload(self):
        self.iface.removeVectorToolBarIcon(self.actionPostionToGe)
        self.iface.removeVectorToolBarIcon(self.actionFeaturesToGe)
        self.iface.removeVectorToolBarIcon(self.actionVectorToGe)
        self.iface.removeRasterToolBarIcon(self.actionRasterToGe)

        self.iface.removePluginMenu(self.tr('GETools'), self.actionPostionToGe)
        self.iface.removePluginMenu(self.tr('GETools'), self.actionFeaturesToGe)
        self.iface.removePluginMenu(self.tr('GETools'), self.actionVectorToGe)
        self.iface.removePluginMenu(self.tr('GETools'), self.actionRasterToGe)
        self.iface.removePluginMenu(self.tr('GETools'), self.actionSettings)
        self.iface.removePluginMenu(self.tr('GETools'), self.actionAbout)

        # ~ if self.iface.mapCanvas().mapTool() == self.toolClick:
            # ~ self.iface.mapCanvas().unsetMapTool(self.toolClick)
        # ~ if self.iface.mapCanvas().mapTool() == self.toolSelect:
            # ~ self.iface.mapCanvas().unsetMapTool(self.toolSelect)

        # ~ del self.toolClick
        # ~ del self.toolSelect

        # ~ self.thread.wait()
        # ~ self.writer = None
        # ~ self.thread = None

        # Delete temporary files

    def settings(self):
        pass
        # ~ dlg = OptionsDialog()
        # ~ dlg.exec_()

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def tr(self, text):
        return QCoreApplication.translate('GeTools', text)

    def selectPosition(self):
        self.iface.mapCanvas().setMapTool(self.toolClick)

    def selectFeatures(self):
        pass
        #self.canvas.setMapTool(self.toolSelect)

    # ~ def toggleMapTools(self, tool):
        # ~ if tool != self.toolClick:
            # ~ self.actionSelectCoords.setChecked(False)
        # ~ if tool != self.toolSelect:
            # ~ self.actionSelectFeatures.setChecked(False)

    def toggleButtons(self, layer):
        if layer and layer.type() == QgsMapLayer.VectorLayer:
            self.actionPostionToGe.setEnabled(True)
            self.actionFeaturesToGe.setEnabled(True)
            self.actionVectorToGe.setEnabled(True)
            self.actionRasterToGe.setEnabled(False)
        elif layer and layer.type() == QgsMapLayer.RasterLayer:
            self.actionPostionToGe.setEnabled(False)
            self.actionFeaturesToGe.setEnabled(False)
            self.actionVectorToGe.setEnabled(False)
            self.actionRasterToGe.setEnabled(True)
        else:
            self.actionPostionToGe.setEnabled(False)
            self.actionFeaturesToGe.setEnabled(False)
            self.actionVectorToGe.setEnabled(False)
            self.actionRasterToGe.setEnabled(False)

    def exportPosition(self, point, button):
        print(point)
        # ~ if self.thread.isRunning():
            # ~ self.iface.messageBar().pushMessage(
                # ~ self.tr('There is running export operation. Please wait when it finished.'),
                # ~ QgsMessageBar.WARNING, self.iface.messageTimeout())
        # ~ else:
            # ~ self.writer.setPoint(point)
            # ~ self.thread.started.connect(self.writer.exportPoint)
            # ~ self.thread.start()

    def processFeatures(self):
        pass
        # ~ if self.thread.isRunning():
            # ~ self.iface.messageBar().pushMessage(
                # ~ self.tr('There is running export operation. Please wait hen it finished.'),
                # ~ QgsMessageBar.WARNING, self.iface.messageTimeout())
        # ~ else:
            # ~ self.writer.setLayer(self.canvas.currentLayer())
            # ~ self.writer.setOnlySelected(True)
            # ~ self.thread.started.connect(self.writer.exportLayer)
            # ~ self.thread.start()

    def processLayer(self):
        pass
        # ~ if self.thread.isRunning():
            # ~ self.iface.messageBar().pushMessage(
                # ~ self.tr('There is running export operation. Please wait when it finished.'),
                # ~ QgsMessageBar.WARNING, self.iface.messageTimeout())
        # ~ else:
            # ~ self.writer.setLayer(self.canvas.currentLayer())
            # ~ self.writer.setOnlySelected(False)
            # ~ self.thread.started.connect(self.writer.exportLayer)
            # ~ self.thread.start()

    def showError(self, message):
        pass
        # ~ self.thread.started.disconnect()
        # ~ self.iface.messageBar().pushMessage(
            # ~ message, QgsMessageBar.WARNING, self.iface.messageTimeout())

    def openResults(self, fileName):
        pass
        # ~ self.thread.started.disconnect()
        # ~ self.iface.messageBar().pushMessage(
            # ~ self.tr('Export completed'), QgsMessageBar.INFO, self.iface.messageTimeout())

        # ~ QDesktopServices.openUrl(QUrl('file:///' + fileName))

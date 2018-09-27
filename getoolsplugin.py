# -*- coding: utf-8 -*-

"""
***************************************************************************
    getoolsplugin.py
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
import shutil

from qgis.PyQt.QtCore import QCoreApplication, QTranslator, QUrl
from qgis.PyQt.QtGui import QIcon, QDesktopServices
from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsApplication, QgsMapLayer

from getools.gui.maptoolclick import MapToolClick
from getools.gui.maptoolselect import MapToolSelect
# ~ from getools.gui.optionsdialog import OptionsDialog
from getools.gui.aboutdialog import AboutDialog
from getools.kmlwritertask import KmlWriterTask
import getools.geutils as utils

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
        self.actionVectorToGe.triggered.connect(self.exportLayer)
        self.actionRasterToGe.triggered.connect(self.exportLayer)
        self.actionSettings.triggered.connect(self.settings)
        self.actionAbout.triggered.connect(self.about)

        self.toolClick = MapToolClick(self.iface.mapCanvas())
        self.toolClick.setAction(self.actionPostionToGe)
        self.toolClick.canvasClicked.connect(self.exportPosition)

        self.toolSelect = MapToolSelect(self.iface.mapCanvas())
        self.toolSelect.setAction(self.actionFeaturesToGe)
        self.toolSelect.featuresSelected.connect(self.exportFeatures)

        self.iface.currentLayerChanged.connect(self.toggleButtons)

        self.taskManager = QgsApplication.taskManager()

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

        if self.iface.mapCanvas().mapTool() == self.toolClick:
            self.iface.mapCanvas().unsetMapTool(self.toolClick)
        if self.iface.mapCanvas().mapTool() == self.toolSelect:
            self.iface.mapCanvas().unsetMapTool(self.toolSelect)

        del self.toolClick
        del self.toolSelect

        utils.removeTempFiles()

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
        self.iface.mapCanvas().setMapTool(self.toolSelect)

    def toggleButtons(self, layer):
        if layer and layer.type() == QgsMapLayer.VectorLayer:
            self.actionFeaturesToGe.setEnabled(True)
            self.actionVectorToGe.setEnabled(True)
            self.actionRasterToGe.setEnabled(False)
        elif layer and layer.type() == QgsMapLayer.RasterLayer:
            self.actionFeaturesToGe.setEnabled(False)
            self.actionVectorToGe.setEnabled(False)
            self.actionRasterToGe.setEnabled(True)
        else:
            self.actionFeaturesToGe.setEnabled(False)
            self.actionVectorToGe.setEnabled(False)
            self.actionRasterToGe.setEnabled(False)

    def exportPosition(self, point, button):
        task = KmlWriterTask(point)
        task.exportComplete.connect(self.completed)
        task.errorOccurred.connect(self.errored)

        self.taskManager.addTask(task)

    def exportFeatures(self):
        task = KmlWriterTask(self.iface.activeLayer(), True)
        task.exportComplete.connect(self.completed)
        task.errorOccurred.connect(self.errored)

        self.taskManager.addTask(task)

    def exportLayer(self):
        task = KmlWriterTask(self.iface.activeLayer())
        task.exportComplete.connect(self.completed)
        task.errorOccurred.connect(self.errored)

        self.taskManager.addTask(task)

    def completed(self, fileName):
        uri = QUrl.fromLocalFile(fileName)
        self.iface.messageBar().pushSuccess(self.tr('GETools'), self.tr('Successfully exported to <a href="{}">{}</a>').format(uri.toString(), fileName))
        QDesktopServices.openUrl(uri)

    def errored(self, error):
        self.iface.messageBar().pushWarning(self.tr('GETools'), error)

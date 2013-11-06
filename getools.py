# -*- coding: utf-8 -*-

"""
***************************************************************************
    getools.py
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

import shutil

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

import clicktool
import selecttool
import kmlwriter
import optionsdialog
import aboutdialog
import geutils as utils

import resources_rc


class GEToolsPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        self.qgsVersion = unicode(QGis.QGIS_VERSION_INT)

        userPluginPath = QFileInfo(
                QgsApplication.qgisUserDbFilePath()).path() \
                + '/python/plugins/getools'
        systemPluginPath = QgsApplication.prefixPath() \
                + '/python/plugins/getools'

        overrideLocale = QSettings().value('locale/overrideFlag', False,
                                           type=bool)
        if not overrideLocale:
            localeFullName = QLocale.system().name()
        else:
            localeFullName = QSettings().value('locale/userLocale', '')

        if QFileInfo(userPluginPath).exists():
            translationPath = userPluginPath + '/i18n/getools_' \
                              + localeFullName + '.qm'
        else:
            translationPath = systemPluginPath + '/i18n/getools_' \
                              + localeFullName + '.qm'

        self.localePath = translationPath
        if QFileInfo(self.localePath).exists():
            self.translator = QTranslator()
            self.translator.load(self.localePath)
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        if int(self.qgsVersion) < 20000:
            qgisVersion = self.qgsVersion[0] + '.' + self.qgsVersion[2] \
                          + '.' + self.qgsVersion[3]
            QMessageBox.warning(self.iface.mainWindow(), 'GETools',
                    QCoreApplication.translate('GETools',
                            'QGIS %s detected.\n') % (qgisVersion) +
                    QCoreApplication.translate('GETools',
                            'This version of GETools requires at least '
                            'QGIS 2.0.\nPlugin will not be enabled.'))
            return None

        self.actionSelectCoords = QAction(QCoreApplication.translate(
                'GETools', 'Coords to Google Earth'), self.iface.mainWindow())
        self.actionSelectCoords.setIcon(QIcon(':/icons/getools-coords.svg'))
        self.actionSelectCoords.setWhatsThis(
                'Open mouse coordinates in Google Earth')
        self.actionSelectCoords.setCheckable(True)

        self.actionSelectFeatures = QAction(QCoreApplication.translate(
                'GETools', 'Feature to Google Earth'), self.iface.mainWindow())
        self.actionSelectFeatures.setIcon(QIcon(':/icons/getools-features.svg'))
        self.actionSelectFeatures.setWhatsThis(
                'Send selected feature to Google Earth')
        self.actionSelectFeatures.setCheckable(True)

        self.actionProcessLayer = QAction(QCoreApplication.translate(
                'GETools', 'Layer to Google Earth'), self.iface.mainWindow())
        self.actionProcessLayer.setIcon(QIcon(':/icons/getools-layer.svg'))
        self.actionProcessLayer.setWhatsThis('Send whole layer to Google Earth')

        self.actionSettings = QAction(QCoreApplication.translate(
                'GETools', 'Settings'), self.iface.mainWindow())
        self.actionSettings.setIcon(QIcon(':/icons/settings.svg'))
        self.actionSettings.setWhatsThis('GETools settings')

        self.actionAbout = QAction(QCoreApplication.translate(
                'GETools', 'About GETools...'), self.iface.mainWindow())
        self.actionAbout.setIcon(QIcon(':/icons/about.png'))
        self.actionAbout.setWhatsThis('About GETools')

        self.iface.addPluginToVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionSelectCoords)
        self.iface.addPluginToVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionSelectFeatures)
        self.iface.addPluginToVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionProcessLayer)
        self.iface.addPluginToVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionSettings)
        self.iface.addPluginToVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionAbout)

        self.iface.addVectorToolBarIcon(self.actionSelectCoords)
        self.iface.addVectorToolBarIcon(self.actionSelectFeatures)
        self.iface.addVectorToolBarIcon(self.actionProcessLayer)

        self.actionSelectCoords.triggered.connect(self.selectCoords)
        self.actionSelectFeatures.triggered.connect(self.selectFeatures)
        self.actionProcessLayer.triggered.connect(self.processLayer)
        self.actionSettings.triggered.connect(self.settings)
        self.actionAbout.triggered.connect(self.about)

        # Map tools
        self.toolClick = clicktool.ClickTool(self.canvas)
        self.toolClick.canvasClicked.connect(self.processCoords)

        self.toolSelect = selecttool.SelectTool(self.iface, self.canvas)
        self.toolSelect.featuresSelected.connect(self.processFeatures)

        # Handle tool changes
        self.iface.mapCanvas().mapToolSet.connect(self.mapToolChanged)

        # Handle layer changes
        self.iface.currentLayerChanged.connect(self.toggleTools)

        self.toggleTools(self.canvas.currentLayer())

        utils.tempDirectory()

        # prepare worker
        self.thread = QThread()
        self.writer = kmlwriter.KMLWriter()
        self.writer.moveToThread(self.thread)
        self.writer.exportError.connect(self.thread.quit)
        self.writer.exportError.connect(self.showMessage)
        self.writer.exportFinished.connect(self.thread.quit)
        self.writer.exportFinished.connect(self.openResults)

    def unload(self):
        self.iface.removeVectorToolBarIcon(self.actionSelectCoords)
        self.iface.removeVectorToolBarIcon(self.actionSelectFeatures)
        self.iface.removeVectorToolBarIcon(self.actionProcessLayer)

        self.iface.removePluginVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionSelectCoords)
        self.iface.removePluginVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionSelectFeatures)
        self.iface.removePluginVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionProcessLayer)
        self.iface.removePluginVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionSettings)
        self.iface.removePluginVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionAbout)

        if self.iface.mapCanvas().mapTool() == self.toolClick:
            self.iface.mapCanvas().unsetMapTool(self.toolClick)
        if self.iface.mapCanvas().mapTool() == self.toolSelect:
            self.iface.mapCanvas().unsetMapTool(self.toolSelect)

        del self.toolClick
        del self.toolSelect

        self.thread.wait()
        self.writer = None
        self.thread = None

        # Delete temporary files
        tmp = utils.tempDirectory()
        if QDir(tmp).exists():
            shutil.rmtree(tmp, True)

    def selectCoords(self):
        self.canvas.setMapTool(self.toolClick)

    def selectFeatures(self):
        self.canvas.setMapTool(self.toolSelect)

    def settings(self):
        dlg = optionsdialog.OptionsDialog()
        dlg.exec_()

    def about(self):
        dlg = aboutdialog.AboutDialog()
        dlg.exec_()

    def mapToolChanged(self, tool):
        if tool != self.toolClick:
            self.actionSelectCoords.setChecked(False)
        if tool != self.toolSelect:
            self.actionSelectFeatures.setChecked(False)

    def toggleTools(self, layer):
        if layer is None or layer.type() != QgsMapLayer.VectorLayer:
            self.actionSelectCoords.setEnabled(False)
            self.actionSelectFeatures.setEnabled(False)
            self.actionProcessLayer.setEnabled(False)
            if self.iface.mapCanvas().mapTool() == self.toolClick:
                self.iface.mapCanvas().unsetMapTool(self.toolClick)
            if self.iface.mapCanvas().mapTool() == self.toolSelect:
                self.iface.mapCanvas().unsetMapTool(self.toolSelect)
        else:
            self.actionSelectCoords.setEnabled(True)
            self.actionSelectFeatures.setEnabled(True)
            self.actionProcessLayer.setEnabled(True)

    def processCoords(self, point, button):
        pass

    def processFeatures(self):
        settings = QSettings()
        timeout = settings.value('/qgis/messageTimeout', 5, type=int)

        if self.thread.isRunning():
            self.iface.messageBar().pushMessage(
                    QCoreApplication.translate('GETools',
                            'There is running export operation. Please wait '
                            'when it finished.'),
                    QgsMessageBar.WARNING, timeout)
        else:
            self.writer.setLayer(self.canvas.currentLayer())
            self.writer.setOnlySelected(True)
            self.thread.started.connect(self.writer.exportLayer)
            self.thread.start()

    def processLayer(self):
        settings = QSettings()
        timeout = settings.value('/qgis/messageTimeout', 5, type=int)

        if self.thread.isRunning():
            self.iface.messageBar().pushMessage(
                    QCoreApplication.translate('GETools',
                            'There is running export operation. Please wait '
                            'when it finished.'),
                    QgsMessageBar.WARNING, timeout)
        else:
            self.writer.setLayer(self.canvas.currentLayer())
            self.writer.setOnlySelected(False)
            self.thread.started.connect(self.writer.exportLayer)
            self.thread.start()

    def showMessage(self, message):
        settings = QSettings()
        timeout = settings.value('/qgis/messageTimeout', 5, type=int)
        self.thread.started.disconnect()
        self.iface.messageBar().pushMessage(message, QgsMessageBar.WARNING,
                                          timeout)

    def openResults(self, fileName):
        settings = QSettings()
        timeout = settings.value('/qgis/messageTimeout', 5, type=int)

        self.thread.started.disconnect()
        self.iface.messageBar().pushMessage(
                QCoreApplication.translate('GETools', 'Export completed'),
                QgsMessageBar.INFO, timeout)

        QDesktopServices.openUrl(QUrl('file:///' + fileName))

# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__.py
    ---------------------
    Date                 : October 2013
    Copyright            : (C) 2013 by Alexander Bruy
    Email                : alexannder dot bruy at gmail dot com
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

import aboutdialog

import resources_rc


class GEToolsPlugin:
    def __init__(self, iface):
        self.iface = iface

        self.qgsVersion = unicode(QGis.QGIS_VERSION_INT)

        # For i18n support
        userPluginPath = QFileInfo(
                QgsApplication.qgisUserDbFilePath()).path() \
                + '/python/plugins/getools'
        systemPluginPath = QgsApplication.prefixPath() \
                + '/python/plugins/geptagphotos'

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
                            'This version of GETools requires at least \
                            QGIS 2.0.\nPlugin will not be enabled.'))
            return None

        self.actionOpenCoords = QAction(QCoreApplication.translate(
                'GETools', 'Coords to Google Earth'), self.iface.mainWindow())
        self.actionOpenCoords.setIcon(QIcon(':/icons/getools-coords.svg'))
        self.actionOpenCoords.setWhatsThis(
                'Open mouse coordinates in Google Earth')

        self.actionOpenFeature = QAction(QCoreApplication.translate(
                'GETools', 'Feature to Google Earth'), self.iface.mainWindow())
        self.actionOpenFeature.setIcon(QIcon(':/icons/getools-features.svg'))
        self.actionOpenFeature.setWhatsThis(
                'Send selected feature to Google Earth')
        self.actionOpenFeature.setCheckable(True)

        self.actionOpenLayer = QAction(QCoreApplication.translate(
                'GETools', 'Layer to Google Earth'), self.iface.mainWindow())
        self.actionOpenLayer.setIcon(QIcon(':/icons/getools-layer.svg'))
        self.actionOpenLayer.setWhatsThis('Send whole layer to Google Earth')

        self.actionSettings = QAction(QCoreApplication.translate(
                'GETools', 'Settings'), self.iface.mainWindow())
        self.actionSettings.setIcon(QIcon(':/icons/settings.svg'))
        self.actionSettings.setWhatsThis('GETools settings')

        self.actionAbout = QAction(QCoreApplication.translate(
                'GETools', 'About GETools...'), self.iface.mainWindow())
        self.actionAbout.setIcon(QIcon(':/icons/about.png'))
        self.actionAbout.setWhatsThis('About GETools')

        self.iface.addPluginToVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionOpenCoords)
        self.iface.addPluginToVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionOpenFeature)
        self.iface.addPluginToVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionOpenLayer)
        self.iface.addPluginToVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionSettings)
        self.iface.addPluginToVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionAbout)

        self.iface.addVectorToolBarIcon(self.actionOpenCoords)
        self.iface.addVectorToolBarIcon(self.actionOpenFeature)
        self.iface.addVectorToolBarIcon(self.actionOpenLayer)

        self.actionOpenCoords.triggered.connect(self.sendCoords)
        self.actionOpenFeature.triggered.connect(self.sendFeatures)
        self.actionOpenLayer.triggered.connect(self.sendLayer)
        self.actionSettings.triggered.connect(self.settings)
        self.actionAbout.triggered.connect(self.about)

    def unload(self):
        self.iface.removeVectorToolBarIcon(self.actionOpenCoords)
        self.iface.removeVectorToolBarIcon(self.actionOpenFeature)
        self.iface.removeVectorToolBarIcon(self.actionOpenLayer)

        self.iface.removePluginVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionOpenCoords)
        self.iface.removePluginVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionOpenFeature)
        self.iface.removePluginVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionOpenLayer)
        self.iface.removePluginVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionSettings)
        self.iface.removePluginVectorMenu(QCoreApplication.translate(
                'GETools', 'GETools'), self.actionAbout)

    def sendCoords(self):
        pass

    def sendFeatures(self):
        pass

    def sendLayer(self):
        pass

    def settings(self):
        pass

    def about(self):
        dlg = aboutdialog.AboutDialog()
        dlg.exec_()

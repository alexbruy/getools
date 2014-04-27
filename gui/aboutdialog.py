# -*- coding: utf-8 -*-

"""
***************************************************************************
    aboutdialog.py
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
import ConfigParser

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from getools.ui.ui_aboutdialogbase import Ui_Dialog

import getools.resources_rc


class AboutDialog(QDialog, Ui_Dialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)

        self.btnHelp = self.buttonBox.button(QDialogButtonBox.Help)

        self.lblLogo.setPixmap(QPixmap(':/icons/getools.svg'))

        cfg = ConfigParser.SafeConfigParser()
        cfg.read(os.path.join(
            os.path.split(os.path.dirname(__file__))[0], 'metadata.txt'))
        version = cfg.get('general', 'version')

        self.lblVersion.setText(self.tr('Version: %s') % (version))
        doc = QTextDocument()
        doc.setHtml(self.getAboutText())
        self.textBrowser.setDocument(doc)
        self.textBrowser.setOpenExternalLinks(True)

        self.buttonBox.helpRequested.connect(self.openHelp)

    def reject(self):
        QDialog.reject(self)

    def openHelp(self):
        overrideLocale = QSettings().value('locale/overrideFlag', False, bool)
        if not overrideLocale:
            localeFullName = QLocale.system().name()
        else:
            localeFullName = QSettings().value('locale/userLocale', '')

        localeShortName = localeFullName[0:2]
        if localeShortName in ['uk']:
            QDesktopServices.openUrl(
                QUrl('http://hub.qgis.org/projects/getools/wiki'))
        else:
            QDesktopServices.openUrl(
                QUrl('http://hub.qgis.org/projects/getools/wiki'))

    def getAboutText(self):
        return self.tr(
            '<p>View cursor position, selected feature(s), whole raster or '
            'vector layer in Google Earth application. It is possible to '
            'create and use custom styling for all types of vector layers.</p>'
            '<p>NOTE: supports only rasters loaded via gdal provider.</p>'
            '<p><strong>Developers</strong>: Alexander Bruy, icons by Robert '
            'Szczepanek.</p>'
            '<p><strong>Homepage</strong>: '
            '<a href="http://hub.qgis.org/projects/getools">'
            'http://hub.qgis.org/projects/getools</a>.</p>'
            '<p>Please report bugs at '
            '<a href="http://hub.qgis.org/projects/getools/issues">'
            'bugtracker</a>.</p>')

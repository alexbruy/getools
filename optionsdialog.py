# -*- coding: utf-8 -*-

"""
***************************************************************************
    optionsdialog.py
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

from ui.ui_optionsdialogbase import Ui_OptionsDialog


class OptionsDialog(QgsOptionsDialogBase, Ui_OptionsDialog):
    def __init__(self):
        QgsOptionsDialogBase.__init__(self, 'General')
        self.setupUi(self)
        self.initOptionsBase(False)

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        QDialog.accept(self)

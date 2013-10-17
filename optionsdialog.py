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
import resources_rc


class OptionsDialog(QgsOptionsDialogBase, Ui_OptionsDialog):

    COLOR_MODES = {0: 'normal',
                   1: 'random'}

    ALTITUDE_MODES = {0: 'clampToGround',
                      1: 'relativeToGround',
                      2: 'absolute',
                      3: 'clampToSeaFloor',
                      4: 'relativeToSeaFloor'
                     }

    def __init__(self):
        QgsOptionsDialogBase.__init__(self, 'Window')
        self.setupUi(self)

        self.settings = QSettings('alexbruy', 'getools')
        self.setSettings(self.settings)
        self.initOptionsBase(False)

        self.grpPointStyle.setSettings(self.settings)
        self.grpPointGeometry.setSettings(self.settings)
        self.grpLineStyle.setSettings(self.settings)
        self.grpLineGeometry.setSettings(self.settings)
        self.grpPolyStyle.setSettings(self.settings)
        self.grpPolyGeometry.setSettings(self.settings)

        self.accepted.connect(self.saveOptions)

        self.manageGui()

    def manageGui(self):
        item = self.mOptionsListWidget.findItems(self.tr('Points'),
                Qt.MatchFixedString | Qt.MatchCaseSensitive)[0]
        item.setIcon(QIcon(':/icons/points.svg'))
        item = self.mOptionsListWidget.findItems(self.tr('Lines'),
                Qt.MatchFixedString | Qt.MatchCaseSensitive)[0]
        item.setIcon(QIcon(':/icons/lines.svg'))
        item = self.mOptionsListWidget.findItems(self.tr('Polygons'),
                Qt.MatchFixedString | Qt.MatchCaseSensitive)[0]
        item.setIcon(QIcon(':/icons/polygons.svg'))
        item = self.mOptionsListWidget.findItems(self.tr('Labels'),
                Qt.MatchFixedString | Qt.MatchCaseSensitive)[0]
        item.setIcon(QIcon(':/icons/labels.svg'))

        # Points tab
        red = self.settings.value('points/point_color_red',
                                  255, type=int)
        green = self.settings.value('points/point_color_green',
                                    255, type=int)
        blue = self.settings.value('points/point_color_blue',
                                   0, type=int)
        alpha = self.settings.value('points/point_color_alpha',
                                    255, type=int)
        self.btnPointColor.setColor(QColor(red, green, blue, alpha))
        self.btnPointColor.setColorDialogOptions(QColorDialog.ShowAlphaChannel)

        self.cmbPointColorMode.addItem(self.tr('Normal'), 0)
        self.cmbPointColorMode.addItem(self.tr('Random'), 1)
        mode = self.settings.value('points/color_mode', 0, type=int)
        self.cmbPointColorMode.setCurrentIndex(
                self.cmbPointColorMode.findData(mode))

        self.spnPointScale.setValue(
                self.settings.value('points/scale', 1.0, type=float))

        self.cmbPointAltMode.addItem(self.tr('Clamp to ground'), 0)
        self.cmbPointAltMode.addItem(self.tr('Relative to ground'), 1)
        self.cmbPointAltMode.addItem(self.tr('Absolute'), 2)
        mode = self.settings.value('points/altitude_mode', 0, type=int)
        self.cmbPointAltMode.setCurrentIndex(
                self.cmbPointAltMode.findData(mode))

        self.spnPointAltitude.setValue(
                self.settings.value('points/altitude', 0.0, type=float))

        self.chkPointConnect.setChecked(
                self.settings.value('points/extrude', False, type=bool))

        # Lines tab
        red = self.settings.value('lines/line_color_red',
                                  255, type=int)
        green = self.settings.value('lines/line_color_green',
                                    255, type=int)
        blue = self.settings.value('lines/line_color_blue',
                                   0, type=int)
        alpha = self.settings.value('lines/line_color_alpha',
                                    255, type=int)
        self.btnLineColor.setColor(QColor(red, green, blue, alpha))
        self.btnLineColor.setColorDialogOptions(QColorDialog.ShowAlphaChannel)

        self.cmbLineColorMode.addItem(self.tr('Normal'), 0)
        self.cmbLineColorMode.addItem(self.tr('Random'), 1)
        mode = self.settings.value('lines/color_mode', 0, type=int)
        self.cmbLineColorMode.setCurrentIndex(
                self.cmbPointColorMode.findData(mode))

        self.spnLineWidth.setValue(
                self.settings.value('lines/width', 1.0, type=float))

        self.cmbLineAltMode.addItem(self.tr('Clamp to ground'), 0)
        self.cmbLineAltMode.addItem(self.tr('Relative to ground'), 1)
        self.cmbLineAltMode.addItem(self.tr('Absolute'), 2)
        self.cmbLineAltMode.addItem(self.tr('Clamp to sea floor'), 3)
        self.cmbLineAltMode.addItem(self.tr('Relative to sea floor'), 4)
        mode = self.settings.value('lines/altitude_mode', 0, type=int)
        self.cmbLineAltMode.setCurrentIndex(
                self.cmbLineAltMode.findData(mode))

        self.spnLineAltitude.setValue(
                self.settings.value('lines/altitude', 0.0, type=float))

        self.chkLineConnect.setChecked(
                self.settings.value('lines/extrude', False, type=bool))
        self.chkLineFollow.setChecked(
                self.settings.value('lines/tessellate', False, type=bool))

        # Polygons tab
        red = self.settings.value('polygons/polygon_color_red',
                                  255, type=int)
        green = self.settings.value('polygons/polygon_color_green',
                                    255, type=int)
        blue = self.settings.value('polygons/polygon_color_blue',
                                   0, type=int)
        alpha = self.settings.value('polygons/polygon_color_alpha',
                                    255, type=int)
        self.btnPolyColor.setColor(QColor(red, green, blue, alpha))
        self.btnPolyColor.setColorDialogOptions(QColorDialog.ShowAlphaChannel)

        self.cmbPolyColorMode.addItem(self.tr('Normal'), 0)
        self.cmbPolyColorMode.addItem(self.tr('Random'), 1)
        mode = self.settings.value('polygons/color_mode', 0, type=int)
        self.cmbPolyColorMode.setCurrentIndex(
                self.cmbPointColorMode.findData(mode))

        self.chkPolyFill.setChecked(
                self.settings.value('polygons/fill', False, type=bool))
        self.chkPolyOutline.setChecked(
                self.settings.value('polygons/outline', False, type=bool))

        self.cmbPolyAltMode.addItem(self.tr('Clamp to ground'), 0)
        self.cmbPolyAltMode.addItem(self.tr('Relative to ground'), 1)
        self.cmbPolyAltMode.addItem(self.tr('Absolute'), 2)
        self.cmbPolyAltMode.addItem(self.tr('Clamp to sea floor'), 3)
        self.cmbPolyAltMode.addItem(self.tr('Relative to sea floor'), 4)
        mode = self.settings.value('polygons/altitude_mode', 0, type=int)
        self.cmbPolyAltMode.setCurrentIndex(
                self.cmbPolyAltMode.findData(mode))

        self.spnPolyAltitude.setValue(
                self.settings.value('polygons/altitude', 0.0, type=float))

        self.chkPolyConnect.setChecked(
                self.settings.value('polygons/extrude', False, type=bool))
        self.chkPolyFollow.setChecked(
                self.settings.value('polygons/tessellate', False, type=bool))

        # Labels tab
        red = self.settings.value('labels/label_color_red',
                                  255, type=int)
        green = self.settings.value('labels/label_color_green',
                                    255, type=int)
        blue = self.settings.value('labels/label_color_blue',
                                   0, type=int)
        alpha = self.settings.value('labels/polygon_color_alpha',
                                    255, type=int)
        self.btnLabelColor.setColor(QColor(red, green, blue, alpha))
        self.btnLabelColor.setColorDialogOptions(QColorDialog.ShowAlphaChannel)

        self.cmbLabelColorMode.addItem(self.tr('Normal'), 0)
        self.cmbLabelColorMode.addItem(self.tr('Random'), 1)
        mode = self.settings.value('labels/color_mode', 0, type=int)
        self.cmbLabelColorMode.setCurrentIndex(
                self.cmbLabelColorMode.findData(mode))

        self.spnLabelScale.setValue(
                self.settings.value('labels/scale', 1.0, type=float))

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        QDialog.accept(self)

    def saveOptions(self):
        # Points tab
        color = self.btnPointColor.color()
        self.settings.setValue('points/point_color_red', color.red())
        self.settings.setValue('points/point_color_green', color.green())
        self.settings.setValue('points/point_color_blue', color.blue())
        self.settings.setValue('points/point_color_alpha', color.alpha())

        mode = self.cmbPointColorMode.itemData(
                self.cmbPointColorMode.currentIndex())
        self.settings.setValue('points/color_mode', mode)

        self.settings.setValue('points/scale', self.spnPointScale.value())

        mode = self.cmbPointAltMode.itemData(
                self.cmbPointAltMode.currentIndex())
        self.settings.setValue('points/altitude_mode', mode)

        self.settings.setValue('points/altitude',
                               self.spnPointAltitude.value())

        self.settings.setValue('points/extrude',
                               self.chkPointConnect.isChecked())

       # Lines tab
        color = self.btnLineColor.color()
        self.settings.setValue('lines/line_color_red', color.red())
        self.settings.setValue('lines/line_color_green', color.green())
        self.settings.setValue('lines/line_color_blue', color.blue())
        self.settings.setValue('lines/line_color_alpha', color.alpha())

        mode = self.cmbLineColorMode.itemData(
                self.cmbLineColorMode.currentIndex())
        self.settings.setValue('lines/color_mode', mode)

        self.settings.setValue('lines/width', self.spnLineWidth.value())

        mode = self.cmbLineAltMode.itemData(
                self.cmbLineAltMode.currentIndex())
        self.settings.setValue('lines/altitude_mode', mode)

        self.settings.setValue('lines/altitude',
                               self.spnLineAltitude.value())

        self.settings.setValue('lines/extrude',
                               self.chkLineConnect.isChecked())
        self.settings.setValue('lines/tessellate',
                               self.chkLineFollow.isChecked())

       # Polygons tab
        color = self.btnPolyColor.color()
        self.settings.setValue('polygons/polygon_color_red', color.red())
        self.settings.setValue('polygons/polygon_color_green', color.green())
        self.settings.setValue('polygons/polygon_color_blue', color.blue())
        self.settings.setValue('polygons/polygon_color_alpha', color.alpha())

        mode = self.cmbPolyColorMode.itemData(
                self.cmbPolyColorMode.currentIndex())
        self.settings.setValue('polygons/color_mode', mode)

        self.settings.setValue('polygons/fill',
                               self.chkPolyFill.isChecked())
        self.settings.setValue('polygons/outline',
                               self.chkPolyOutline.isChecked())

        mode = self.cmbPolyAltMode.itemData(
                self.cmbPolyAltMode.currentIndex())
        self.settings.setValue('polygons/altitude_mode', mode)

        self.settings.setValue('polygons/altitude',
                               self.spnPolyAltitude.value())

        self.settings.setValue('polygons/extrude',
                               self.chkPolyConnect.isChecked())
        self.settings.setValue('polygons/tessellate',
                               self.chkPolyFollow.isChecked())

       # Labels tab
        color = self.btnLabelColor.color()
        self.settings.setValue('labels/label_color_red', color.red())
        self.settings.setValue('labels/label_color_green', color.green())
        self.settings.setValue('labels/label_color_blue', color.blue())
        self.settings.setValue('labels/label_color_alpha', color.alpha())

        mode = self.cmbLabelColorMode.itemData(
                self.cmbLabelColorMode.currentIndex())
        self.settings.setValue('labels/color_mode', mode)

        self.settings.setValue('labels/scale', self.spnLabelScale.value())

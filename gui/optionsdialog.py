# -*- coding: utf-8 -*-

"""
***************************************************************************
    optionsdialog.py
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


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from getools.ui.ui_optionsdialogbase import Ui_OptionsDialog
import getools.resources_rc


class OptionsDialog(QgsOptionsDialogBase, Ui_OptionsDialog):

    def __init__(self, parent):
        QgsOptionsDialogBase.__init__(self, 'Window', parent)
        self.setupUi(self)

        self.settings = QSettings('alexbruy', 'getools')
        self.setSettings(self.settings)
        self.initOptionsBase(False)

        self.grpPointStyle.setSettings(self.settings)
        self.grpPointGeometry.setSettings(self.settings)
        self.grpLineStyle.setSettings(self.settings)
        self.grpLineGeometry.setSettings(self.settings)
        self.grpPolygonStyle.setSettings(self.settings)
        self.grpPolygonGeometry.setSettings(self.settings)

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
        item = self.mOptionsListWidget.findItems(self.tr('Rasters'),
            Qt.MatchFixedString | Qt.MatchCaseSensitive)[0]
        item.setIcon(QIcon(':/icons/rasters.svg'))

        # Points tab
        red = self.settings.value('points/point_color_red', 255, int)
        green = self.settings.value('points/point_color_green', 255, int)
        blue = self.settings.value('points/point_color_blue', 0, int)
        alpha = self.settings.value('points/point_color_alpha', 255, int)
        self.btnPointColor.setColor(QColor(red, green, blue, alpha))
        self.btnPointColor.setColorDialogOptions(QColorDialog.ShowAlphaChannel)

        self.cmbPointColorMode.addItem(self.tr('Normal'), 0)
        self.cmbPointColorMode.addItem(self.tr('Random'), 1)
        mode = self.settings.value('points/color_mode', 0, int)
        self.cmbPointColorMode.setCurrentIndex(
            self.cmbPointColorMode.findData(mode))

        self.spnPointScale.setValue(
            self.settings.value('points/scale', 1.0, float))

        self.cmbPointAltitudeMode.addItem(self.tr('Clamp to ground'), 0)
        self.cmbPointAltitudeMode.addItem(self.tr('Relative to ground'), 1)
        self.cmbPointAltitudeMode.addItem(self.tr('Absolute'), 2)
        mode = self.settings.value('points/altitude_mode', 0, int)
        self.cmbPointAltitudeMode.setCurrentIndex(
            self.cmbPointAltitudeMode.findData(mode))

        self.spnPointAltitude.setValue(
            self.settings.value('points/altitude', 0.0, float))

        self.chkPointConnect.setChecked(
            self.settings.value('points/extrude', False, bool))

        # Lines tab
        red = self.settings.value('lines/line_color_red', 255, int)
        green = self.settings.value('lines/line_color_green', 255, int)
        blue = self.settings.value('lines/line_color_blue', 0, int)
        alpha = self.settings.value('lines/line_color_alpha', 255, int)
        self.btnLineColor.setColor(QColor(red, green, blue, alpha))
        self.btnLineColor.setColorDialogOptions(QColorDialog.ShowAlphaChannel)

        self.cmbLineColorMode.addItem(self.tr('Normal'), 0)
        self.cmbLineColorMode.addItem(self.tr('Random'), 1)
        mode = self.settings.value('lines/color_mode', 0, int)
        self.cmbLineColorMode.setCurrentIndex(
            self.cmbLineColorMode.findData(mode))

        self.spnLineWidth.setValue(
            self.settings.value('lines/width', 1.0, float))

        self.cmbLineAltitudeMode.addItem(self.tr('Clamp to ground'), 0)
        self.cmbLineAltitudeMode.addItem(self.tr('Relative to ground'), 1)
        self.cmbLineAltitudeMode.addItem(self.tr('Absolute'), 2)
        self.cmbLineAltitudeMode.addItem(self.tr('Clamp to sea floor'), 3)
        self.cmbLineAltitudeMode.addItem(self.tr('Relative to sea floor'), 4)
        mode = self.settings.value('lines/altitude_mode', 0, int)
        self.cmbLineAltitudeMode.setCurrentIndex(
            self.cmbLineAltitudeMode.findData(mode))

        self.spnLineAltitude.setValue(
            self.settings.value('lines/altitude', 0.0, float))

        self.chkLineConnect.setChecked(
            self.settings.value('lines/extrude', False, bool))
        self.chkLineFollow.setChecked(
            self.settings.value('lines/tessellate', False, bool))

        # Polygons tab
        red = self.settings.value('polygons/polygon_color_red', 255, int)
        green = self.settings.value('polygons/polygon_color_green', 255, int)
        blue = self.settings.value('polygons/polygon_color_blue', 0, int)
        alpha = self.settings.value('polygons/polygon_color_alpha', 255, int)
        self.btnPolygonColor.setColor(QColor(red, green, blue, alpha))
        self.btnPolygonColor.setColorDialogOptions(
            QColorDialog.ShowAlphaChannel)

        self.cmbPolygonColorMode.addItem(self.tr('Normal'), 0)
        self.cmbPolygonColorMode.addItem(self.tr('Random'), 1)
        mode = self.settings.value('polygons/color_mode', 0, int)
        self.cmbPolygonColorMode.setCurrentIndex(
            self.cmbPolygonColorMode.findData(mode))

        self.chkPolygonFill.setChecked(
            self.settings.value('polygons/fill', False, bool))
        self.chkPolygonOutline.setChecked(
            self.settings.value('polygons/outline', False, bool))

        self.cmbPolygonAltitudeMode.addItem(self.tr('Clamp to ground'), 0)
        self.cmbPolygonAltitudeMode.addItem(self.tr('Relative to ground'), 1)
        self.cmbPolygonAltitudeMode.addItem(self.tr('Absolute'), 2)
        self.cmbPolygonAltitudeMode.addItem(self.tr('Clamp to sea floor'), 3)
        self.cmbPolygonAltitudeMode.addItem(self.tr('Relative to sea floor'), 4)
        mode = self.settings.value('polygons/altitude_mode', 0, int)
        self.cmbPolygonAltitudeMode.setCurrentIndex(
            self.cmbPolygonAltitudeMode.findData(mode))

        self.spnPolygonAltitude.setValue(
            self.settings.value('polygons/altitude', 0.0, float))

        self.chkPolygonConnect.setChecked(
            self.settings.value('polygons/extrude', False, bool))
        self.chkPolygonFollow.setChecked(
            self.settings.value('polygons/tessellate', False, bool))

        # Labels tab
        red = self.settings.value('labels/label_color_red', 255, int)
        green = self.settings.value('labels/label_color_green', 255, int)
        blue = self.settings.value('labels/label_color_blue', 0, int)
        alpha = self.settings.value('labels/label_color_alpha', 255, int)
        self.btnLabelColor.setColor(QColor(red, green, blue, alpha))
        self.btnLabelColor.setColorDialogOptions(QColorDialog.ShowAlphaChannel)

        self.cmbLabelColorMode.addItem(self.tr('Normal'), 0)
        self.cmbLabelColorMode.addItem(self.tr('Random'), 1)
        mode = self.settings.value('labels/color_mode', 0, int)
        self.cmbLabelColorMode.setCurrentIndex(
            self.cmbLabelColorMode.findData(mode))

        self.spnLabelScale.setValue(
            self.settings.value('labels/scale', 1.0, float))

        # Rasters tab
        red = self.settings.value('rasters/raster_color_red', 255, int)
        green = self.settings.value('rasters/raster_color_green', 255, int)
        blue = self.settings.value('rasters/raster_color_blue', 0, int)
        alpha = self.settings.value('rasters/raster_color_alpha', 255, int)
        self.btnRasterColor.setColor(QColor(red, green, blue, alpha))
        self.btnRasterColor.setColorDialogOptions(
            QColorDialog.ShowAlphaChannel)

        self.chkRasterRendered.setChecked(
            self.settings.value('rasters/rendered', False, bool))

        self.cmbRasterAltitudeMode.addItem(self.tr('Clamp to ground'), 0)
        self.cmbRasterAltitudeMode.addItem(self.tr('Absolute'), 2)
        self.cmbRasterAltitudeMode.addItem(self.tr('Clamp to sea floor'), 3)
        self.cmbRasterAltitudeMode.addItem(self.tr('Relative to sea floor'), 4)
        mode = self.settings.value('rasters/altitude_mode', 0, int)
        self.cmbRasterAltitudeMode.setCurrentIndex(
            self.cmbRasterAltitudeMode.findData(mode))

        self.spnRasterAltitude.setValue(
            self.settings.value('rasters/altitude', 0.0, float))

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        QDialog.accept(self)

    def saveOptions(self):
        # Points tab
        self.settings.setValue(
            'points/overrideStyle', self.grpPointStyle.isChecked())
        color = self.btnPointColor.color()
        self.settings.setValue('points/point_color_red', color.red())
        self.settings.setValue('points/point_color_green', color.green())
        self.settings.setValue('points/point_color_blue', color.blue())
        self.settings.setValue('points/point_color_alpha', color.alpha())

        mode = self.cmbPointColorMode.itemData(
            self.cmbPointColorMode.currentIndex())
        self.settings.setValue('points/color_mode', mode)

        self.settings.setValue('points/scale', self.spnPointScale.value())

        mode = self.cmbPointAltitudeMode.itemData(
            self.cmbPointAltitudeMode.currentIndex())
        self.settings.setValue('points/altitude_mode', mode)
        self.settings.setValue(
            'points/altitude', self.spnPointAltitude.value())
        self.settings.setValue(
            'points/extrude', self.chkPointConnect.isChecked())

        # Lines tab
        self.settings.setValue(
            'lines/overrideStyle', self.grpLineStyle.isChecked())
        color = self.btnLineColor.color()
        self.settings.setValue('lines/line_color_red', color.red())
        self.settings.setValue('lines/line_color_green', color.green())
        self.settings.setValue('lines/line_color_blue', color.blue())
        self.settings.setValue('lines/line_color_alpha', color.alpha())

        mode = self.cmbLineColorMode.itemData(
            self.cmbLineColorMode.currentIndex())
        self.settings.setValue('lines/color_mode', mode)
        self.settings.setValue('lines/width', self.spnLineWidth.value())

        mode = self.cmbLineAltitudeMode.itemData(
            self.cmbLineAltMode.currentIndex())
        self.settings.setValue('lines/altitude_mode', mode)
        self.settings.setValue('lines/altitude', self.spnLineAltitude.value())
        self.settings.setValue(
            'lines/extrude', self.chkLineConnect.isChecked())
        self.settings.setValue(
            'lines/tessellate', self.chkLineFollow.isChecked())

        # Polygons tab
        self.settings.setValue(
            'polygons/overrideStyle', self.grpPolygonStyle.isChecked())
        color = self.btnPolygonColor.color()
        self.settings.setValue('polygons/polygon_color_red', color.red())
        self.settings.setValue('polygons/polygon_color_green', color.green())
        self.settings.setValue('polygons/polygon_color_blue', color.blue())
        self.settings.setValue('polygons/polygon_color_alpha', color.alpha())

        mode = self.cmbPolygonColorMode.itemData(
            self.cmbPolygonColorMode.currentIndex())
        self.settings.setValue('polygons/color_mode', mode)
        self.settings.setValue(
            'polygons/fill', self.chkPolygonFill.isChecked())
        self.settings.setValue(
            'polygons/outline', self.chkPolygonOutline.isChecked())

        mode = self.cmbPolygonAltitudeMode.itemData(
            self.cmbPolygonAltitudeMode.currentIndex())
        self.settings.setValue('polygons/altitude_mode', mode)
        self.settings.setValue(
            'polygons/altitude', self.spnPolygonAltitude.value())
        self.settings.setValue(
            'polygons/extrude', self.chkPolygonConnect.isChecked())
        self.settings.setValue(
            'polygons/tessellate', self.chkPolygonFollow.isChecked())

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

        # Rasters tab
        color = self.btnRasterColor.color()
        self.settings.setValue('rasters/raster_color_red', color.red())
        self.settings.setValue('rasters/raster_color_green', color.green())
        self.settings.setValue('rasters/raster_color_blue', color.blue())
        self.settings.setValue('rasters/raster_color_alpha', color.alpha())

        self.settings.setValue(
            'rasters/rendered', self.chkRasterRendered.isChecked())

        mode = self.cmbRasterAltitudeMode.itemData(
            self.cmbRasterAltitudeMode.currentIndex())
        self.settings.setValue('rasters/altitude_mode', mode)
        self.settings.setValue(
            'rasters/altitude', self.spnRasterAltitude.value())

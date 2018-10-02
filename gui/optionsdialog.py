# -*- coding: utf-8 -*-

"""
***************************************************************************
    optionsdialog.py
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

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor

from qgis.core import QgsSettings, QgsApplication
from qgis.gui import QgsOptionsDialogBase

pluginPath = os.path.split(os.path.dirname(__file__))[0]
WIDGET, BASE = uic.loadUiType(os.path.join(pluginPath, 'ui', 'optionsdialogbase.ui'))


class OptionsDialog(QgsOptionsDialogBase, WIDGET):

    def __init__(self, parent=None):
        super(OptionsDialog, self).__init__(None, parent)
        self.setupUi(self)

        self.settings = QgsSettings()
        self.setSettings(self.settings)
        self.initOptionsBase(False)

        self.grpPointAttributes.setSettings(self.settings)
        self.grpPointStyle.setSettings(self.settings)
        self.grpPointGeometry.setSettings(self.settings)
        self.grpLineAttributes.setSettings(self.settings)
        self.grpLineStyle.setSettings(self.settings)
        self.grpLineGeometry.setSettings(self.settings)
        self.grpPolygonAttributes.setSettings(self.settings)
        self.grpPolygonStyle.setSettings(self.settings)
        self.grpPolygonGeometry.setSettings(self.settings)
        self.grpLabelStyle.setSettings(self.settings)
        self.grpRasterStyle.setSettings(self.settings)
        self.grpRasterGeometry.setSettings(self.settings)

        self.grpPointAttributes.setSettingGroup('getools')
        self.grpPointStyle.setSettingGroup('getools')
        self.grpPointGeometry.setSettingGroup('getools')
        self.grpLineAttributes.setSettingGroup('getools')
        self.grpLineStyle.setSettingGroup('getools')
        self.grpLineGeometry.setSettingGroup('getools')
        self.grpPolygonAttributes.setSettingGroup('getools')
        self.grpPolygonStyle.setSettingGroup('getools')
        self.grpPolygonGeometry.setSettingGroup('getools')
        self.grpLabelStyle.setSettingGroup('getools')
        self.grpRasterStyle.setSettingGroup('getools')
        self.grpRasterGeometry.setSettingGroup('getools')

        item = self.mOptionsListWidget.findItems(self.tr('Points'), Qt.MatchFixedString)[0]
        item.setIcon(QgsApplication.getThemeIcon('/mIconPointLayer.svg'))
        item = self.mOptionsListWidget.findItems(self.tr('Lines'), Qt.MatchFixedString)[0]
        item.setIcon(QgsApplication.getThemeIcon('/mIconLineLayer.svg'))
        item = self.mOptionsListWidget.findItems(self.tr('Polygons'), Qt.MatchFixedString)[0]
        item.setIcon(QgsApplication.getThemeIcon('/mIconPolygonLayer.svg'))
        item = self.mOptionsListWidget.findItems(self.tr('Labels'), Qt.MatchFixedString)[0]
        item.setIcon(QgsApplication.getThemeIcon('/mActionLabeling.svg'))
        item = self.mOptionsListWidget.findItems(self.tr('Rasters'), Qt.MatchFixedString)[0]
        item.setIcon(QgsApplication.getThemeIcon('/mIconRaster.svg'))

        self.accepted.connect(self.saveOptions)

        modes = ((self.tr('Normal'), 'normal'),
                 (self.tr('Random'), 'random')
                )
        for k, v in modes:
            self.cmbPointColorMode.addItem(k, v)
            self.cmbLineColorMode.addItem(k, v)
            self.cmbPolygonFillColorMode.addItem(k, v)
            self.cmbPolygonStrokeColorMode.addItem(k, v)
            self.cmbLabelColorMode.addItem(k, v)

        modes = ((self.tr('Clamp to ground'), 'clampToGround'),
                 (self.tr('Relative to ground'), 'relativeToGround'),
                 (self.tr('Absolute'), 'absolute'),
                 (self.tr('Relative to sea floor'), 'relativeToSeaFloor'),
                 (self.tr('Clamp to sea floor'), 'clampToSeaFloor'),
                )
        for k, v in modes:
            self.cmbPointAltitudeMode.addItem(k, v)
            self.cmbLineAltitudeMode.addItem(k, v)
            self.cmbPolygonAltitudeMode.addItem(k, v)
            self.cmbRasterAltitudeMode.addItem(k, v)

        # Points tab
        self.lePointName.setText(self.settings.value('getools/pointName', '', str))
        self.lePointDescription.setText(self.settings.value('getools/pointDescription', '', str))

        red = self.settings.value('getools/pointColorRed', 255, int)
        green = self.settings.value('getools/pointColorGreen', 255, int)
        blue = self.settings.value('getools/pointColorBlue', 0, int)
        alpha = self.settings.value('getools/pointColorAlpha', 255, int)
        self.btnPointColor.setColor(QColor(red, green, blue, alpha))

        mode = self.settings.value('getools/pointColorMode', 'normal', str)
        self.cmbPointColorMode.setCurrentIndex(self.cmbPointColorMode.findData(mode))

        self.spnPointScale.setValue(self.settings.value('getools/pointScale', 1.0, float))

        mode = self.settings.value('getools/pointAltitudeMode', 'clampToGround', str)
        self.cmbPointAltitudeMode.setCurrentIndex(self.cmbPointAltitudeMode.findData(mode))

        self.spnPointAltitude.setValue(self.settings.value('getools/pointAltitude', 0.0, float))
        self.chkPointConnect.setChecked(self.settings.value('getools/pointExtrude', False, bool))

        # Lines tab
        self.leLineName.setText(self.settings.value('getools/lineName', '', str))
        self.leLineDescription.setText(self.settings.value('getools/lineDescription', '', str))

        red = self.settings.value('getools/lineColorRed', 255, int)
        green = self.settings.value('getools/lineColorGreen', 255, int)
        blue = self.settings.value('getools/lineColorBlue', 0, int)
        alpha = self.settings.value('getools/lineColorAlpha', 255, int)
        self.btnLineColor.setColor(QColor(red, green, blue, alpha))

        mode = self.settings.value('getools/lineColorMode', 'normal', str)
        self.cmbLineColorMode.setCurrentIndex(self.cmbLineColorMode.findData(mode))

        self.spnLineWidth.setValue(self.settings.value('getools/lineWidth', 1, int))

        mode = self.settings.value('getools/lineAltitudeMode', 'clampToGround', str)
        self.cmbLineAltitudeMode.setCurrentIndex(self.cmbLineAltitudeMode.findData(mode))

        self.spnLineAltitude.setValue(self.settings.value('getools/lineAltitude', 0.0, float))
        self.chkLineConnect.setChecked(self.settings.value('getools/lineExtrude', False, bool))
        self.chkLineFollow.setChecked(self.settings.value('getools/lineTessellate', False, bool))

        # Polygons tab
        self.lePolygonName.setText(self.settings.value('getools/polygonName', '', str))
        self.lePolygonDescription.setText(self.settings.value('getools/polygonDescription', '', str))

        red = self.settings.value('getools/polygonFillColorRed', 255, int)
        green = self.settings.value('getools/polygonFillColorGreen', 255, int)
        blue = self.settings.value('getools/polygonFillColorBlue', 0, int)
        alpha = self.settings.value('getools/polygonFillColorAlpha', 255, int)
        self.btnPolygonFillColor.setColor(QColor(red, green, blue, alpha))

        red = self.settings.value('getools/polygonStrokeColorRed', 255, int)
        green = self.settings.value('getools/polygonStrokeColorGreen', 255, int)
        blue = self.settings.value('getools/polygonStrokeColorBlue', 0, int)
        alpha = self.settings.value('getools/polygonStrokeColorAlpha', 255, int)
        self.btnPolygonStrokeColor.setColor(QColor(red, green, blue, alpha))

        mode = self.settings.value('getools/polygonFillColorMode', 'normal', str)
        self.cmbPolygonFillColorMode.setCurrentIndex(self.cmbPolygonFillColorMode.findData(mode))
        mode = self.settings.value('getools/polygonStrokeColorMode', 'normal', str)
        self.cmbPolygonStrokeColorMode.setCurrentIndex(self.cmbPolygonStrokeColorMode.findData(mode))

        self.spnPolygonStrokeWidth.setValue(self.settings.value('getools/polygonStrokeWidth', 1, int))

        self.chkPolygonFill.setChecked(self.settings.value('getools/polygonFill', True, bool))
        self.chkPolygonOutline.setChecked(self.settings.value('getools/polygonOutline', True, bool))

        mode = self.settings.value('getools/altitude_mode', 'clampToGround', str)
        self.cmbPolygonAltitudeMode.setCurrentIndex(self.cmbPolygonAltitudeMode.findData(mode))

        self.spnPolygonAltitude.setValue(self.settings.value('getools/polygonAltitude', 0.0, float))
        self.chkPolygonConnect.setChecked(self.settings.value('getools/polygonExtrude', False, bool))
        self.chkPolygonFollow.setChecked(self.settings.value('getools/polygonTessellate', False, bool))

        # Labels tab
        red = self.settings.value('getools/labelColorRed', 255, int)
        green = self.settings.value('getools/labelColorGreen', 255, int)
        blue = self.settings.value('getools/labelColorBlue', 0, int)
        alpha = self.settings.value('getools/labelColorAlpha', 255, int)
        self.btnLabelColor.setColor(QColor(red, green, blue, alpha))

        mode = self.settings.value('getools/labelColorMode', 'normal', str)
        self.cmbLabelColorMode.setCurrentIndex(self.cmbLabelColorMode.findData(mode))

        self.spnLabelScale.setValue(self.settings.value('getools/labelScale', 1.0, float))

        # Rasters tab
        self.chkRasterRendered.setChecked(self.settings.value('getools/rasterRendered', False, bool))

        mode = self.settings.value('getools/rasterAltitudeMode', 'clampToGround', str)
        self.cmbRasterAltitudeMode.setCurrentIndex(self.cmbRasterAltitudeMode.findData(mode))

        self.spnRasterAltitude.setValue(self.settings.value('getools/rasterAltitude', 0.0, float))

    def saveOptions(self):
        # Points tab
        self.settings.setValue('getools/pointName', self.lePointName.text())
        self.settings.setValue('getools/pointDescription', self.lePointDescription.text())

        color = self.btnPointColor.color()
        self.settings.setValue('getools/pointColorRed', color.red())
        self.settings.setValue('getools/pointColorGreen', color.green())
        self.settings.setValue('getools/pointColorBlue', color.blue())
        self.settings.setValue('getools/pointColorAlpha', color.alpha())

        mode = self.cmbPointColorMode.itemData(self.cmbPointColorMode.currentIndex())
        self.settings.setValue('getools/pointColorMode', mode)

        self.settings.setValue('getools/pointScale', self.spnPointScale.value())

        mode = self.cmbPointAltitudeMode.itemData(self.cmbPointAltitudeMode.currentIndex())
        self.settings.setValue('getools/pointAltitudeMode', mode)
        self.settings.setValue('getools/pointAltitude', self.spnPointAltitude.value())
        self.settings.setValue('getools/pointExtrude', self.chkPointConnect.isChecked())

        # Lines tab
        self.settings.setValue('getools/lineName', self.leLineName.text())
        self.settings.setValue('getools/lineDescription', self.leLineDescription.text())

        color = self.btnLineColor.color()
        self.settings.setValue('getools/lineColorRed', color.red())
        self.settings.setValue('getools/lineColorGreen', color.green())
        self.settings.setValue('getools/lineColorBlue', color.blue())
        self.settings.setValue('getools/lineColorAlpha', color.alpha())

        mode = self.cmbLineColorMode.itemData(self.cmbLineColorMode.currentIndex())
        self.settings.setValue('getools/lineColorMode', mode)

        self.settings.setValue('getools/lineWidth', self.spnLineWidth.value())

        mode = self.cmbLineAltitudeMode.itemData(self.cmbLineAltitudeMode.currentIndex())
        self.settings.setValue('getools/lineAltitudeMode', mode)
        self.settings.setValue('getools/lineAltitude', self.spnLineAltitude.value())
        self.settings.setValue('getools/lineExtrude', self.chkLineConnect.isChecked())
        self.settings.setValue('getools/lineTessellate', self.chkLineFollow.isChecked())

        # Polygons tab
        self.settings.setValue('getools/polygonName', self.lePolygonName.text())
        self.settings.setValue('getools/polygonDescription', self.lePolygonDescription.text())

        color = self.btnPolygonFillColor.color()
        self.settings.setValue('getools/polygonFillColorRed', color.red())
        self.settings.setValue('getools/polygonFillColorGreen', color.green())
        self.settings.setValue('getools/polygonFillColorBlue', color.blue())
        self.settings.setValue('getools/polygonFillColorAlpha', color.alpha())

        color = self.btnPolygonStrokeColor.color()
        self.settings.setValue('getools/polygonStrokeColorRed', color.red())
        self.settings.setValue('getools/polygonStrokeColorGreen', color.green())
        self.settings.setValue('getools/polygonStrokeColorBlue', color.blue())
        self.settings.setValue('getools/polygonStrokeColorAlpha', color.alpha())

        mode = self.cmbPolygonFillColorMode.itemData(self.cmbPolygonFillColorMode.currentIndex())
        self.settings.setValue('getools/polygonFillColorMode', mode)
        mode = self.cmbPolygonStrokeColorMode.itemData(self.cmbPolygonStrokeColorMode.currentIndex())
        self.settings.setValue('getools/polygonStrokeColorMode', mode)

        self.settings.setValue('getools/polygonStrokeWidth', self.spnPolygonStrokeWidth.value())

        self.settings.setValue('getools/polygonFill', self.chkPolygonFill.isChecked())
        self.settings.setValue('getools/polygonOutline', self.chkPolygonOutline.isChecked())

        mode = self.cmbPolygonAltitudeMode.itemData(self.cmbPolygonAltitudeMode.currentIndex())
        self.settings.setValue('getools/polygonAltitudeMode', mode)
        self.settings.setValue('getools/polygonAltitude', self.spnPolygonAltitude.value())
        self.settings.setValue('getools/polygonExtrude', self.chkPolygonConnect.isChecked())
        self.settings.setValue('getools/polygonTessellate', self.chkPolygonFollow.isChecked())

        # Labels tab
        color = self.btnLabelColor.color()
        self.settings.setValue('getools/labelColorRed', color.red())
        self.settings.setValue('getools/labelColorGreen', color.green())
        self.settings.setValue('getools/labelColorBlue', color.blue())
        self.settings.setValue('getools/labelColorAlpha', color.alpha())

        mode = self.cmbLabelColorMode.itemData(self.cmbLabelColorMode.currentIndex())
        self.settings.setValue('getools/labelColorMode', mode)
        self.settings.setValue('getools/labelScale', self.spnLabelScale.value())

        # Rasters tab
        self.settings.setValue('getools/rasterRendered', self.chkRasterRendered.isChecked())

        mode = self.cmbRasterAltitudeMode.itemData(self.cmbRasterAltitudeMode.currentIndex())
        self.settings.setValue('getools/rasterAltitudeMode', mode)
        self.settings.setValue('getools/rasterAltitude', self.spnRasterAltitude.value())

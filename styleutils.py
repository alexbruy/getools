# -*- coding: utf-8 -*-

"""
***************************************************************************
    styleutils.py
    ---------------------
    Date                 : May 2019
    Copyright            : (C) 2019 by Alexander Bruy
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
__date__ = 'May 2019'
__copyright__ = '(C) 2019, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import QgsSettings, QgsExpression, QgsUnitTypes, QgsWkbTypes
from qgis.utils import iface


def tr(text):
    return QCoreApplication.translate('StyleUtils', text)


def defaultStyle(layer):
    style = []
    settings = QgsSettings()
    r = settings.value('getools/labelColorRed', 255, int)
    g = settings.value('getools/labelColorGreen', 255, int)
    b = settings.value('getools/labelColorBlue', 0, int)
    a = settings.value('getools/labelColorAlpha', 255, int)
    mode = settings.value('getools/labelColorMode', 'normal', str)
    scale = settings.value('getools/labelScale', 1.0, float)

    style.append('    <Style id="default">')
    style.append('      <LabelStyle>')
    style.append('        <сolor>{:02x}{:02x}{:02x}{:02x}</color>'.format(a, b, g, r))
    style.append('        <сolorMode>{}</colorMode>'.format(mode))
    style.append('        <scale>{}</scale>'.format(scale))
    style.append('      </LabelStyle>')

    geometryType = self.data.geometryType()
    if geometryType == QgsWkbTypes.PointGeometry:
        r = settings.value('getools/pointColorRed', 255, int)
        g = settings.value('getools/pointColorGreen', 255, int)
        b = settings.value('getools/pointColorBlue', 0, int)
        a = settings.value('getools/pointColorAlpha', 255, int)
        mode = settings.value('getools/pointColorMode', 'normal', str)
        scale = settings.value('getools/pointScale', 1.0, float)

        style.append('      <IconStyle>')
        style.append('        <color>{:02x}{:02x}{:02x}{:02x}</color>'.format(a, b, g, r))
        style.append('        <colorMode>{}</colorMode>'.format(mode))
        style.append('        <scale>{}</scale>'.format(scale))
        style.append('      </IconStyle>')
    elif geometryType == QgsWkbTypes.LineGeometry:
        r = settings.value('getools/lineColorRed', 255, int)
        g = settings.value('getools/lineColorGreen', 255, int)
        b = settings.value('getools/lineColorBlue', 0, int)
        a = settings.value('getools/lineColorAlpha', 255, int)
        mode = settings.value('getools/lineColorMode', 'normal', str)
        width = settings.value('getools/lineWidth', 1, int)

        style.append('      <LineStyle>')
        style.append('        <color>{:02x}{:02x}{:02x}{:02x}</color>'.format(a, b, g, r))
        style.append('        <colorMode>{}</colorMode>'.format(mode))
        style.append('        <width>{}</width>'.format(width))
        style.append('      </LineStyle>')
    elif geometryType == QgsWkbTypes.PolygonGeometry:
        r = settings.value('getools/polygonStrokeColorRed', 255, int)
        g = settings.value('getools/polygonStrokeColorGreen', 255, int)
        b = settings.value('getools/polygonStrokeColorBlue', 0, int)
        a = settings.value('getools/polygonStrokeColorAlpha', 255, int)
        mode = settings.value('getools/polygonStrokeColorMode', 'normal', str)
        width = settings.value('getools/polygonStrokeWidth', 1, int)

        style.append('      <LineStyle>')
        style.append('        <color>{:02x}{:02x}{:02x}{:02x}</color>'.format(a, b, g, r))
        style.append('        <colorMode>{}</colorMode>'.format(mode))
        style.append('        <width>{}</width>'.format(width))
        style.append('      </LineStyle>')

        r = settings.value('getools/polygonFillColorRed', 255, int)
        g = settings.value('getools/polygonFillColorGreen', 255, int)
        b = settings.value('getools/polygonFillColorBlue', 0, int)
        a = settings.value('getools/polygonFillColorAlpha', 255, int)
        mode = settings.value('getools/polygonFillColorMode', 'normal', str)
        fill = settings.value('getools/polygonFill', True, bool)
        outline = settings.value('getools/polygonOutline', True, bool)

        style.append('      <PolyStyle>')
        style.append('        <color>{:02x}{:02x}{:02x}{:02x}</color>'.format(a, b, g, r))
        style.append('        <colorMode>{}</colorMode>'.format(mode))
        style.append('        <fill>{:d}</fill>'.format(fill))
        style.append('        <outline>{:d}</outline>'.format(outline))
        style.append('      </PolyStyle>')

    style.append('    </Style>')
    return {'default': 'all'}, '\n'.join(style)


def kmlStyle(layer):
    rendererType = layer.renderer().type()

    if rendererType == 'singleSymbol':
        return _simpleStyle(layer)
    elif rendererType == 'categorizedSymbol':
        return _categorizedStyle(layer)
    elif rendererType == 'graduatedSymbol':
        return _graduatedStyle(layer)
    #elif rendererType == 'RuleRenderer':
    #    return None, '"{}" renderer is not supported.'.format(rendererType)
    else:
        return None, tr('"{}" renderer is not supported.'.format(rendererType))


def _simpleStyle(layer):
    symbolLayer = layer.renderer().symbol().symbolLayer(0)
    labeling = layer.labeling()
    ok, style = _symbolLayerToStyle(symbolLayer, labeling)
    if not ok:
        return None, style

    styleDefinition = '    <Style id="simpleStyle">\n{}\n    </Style>'.format(style)
    return {'simpleStyle': 'all'}, styleDefinition


def _categorizedStyle(layer):
    renderer = layer.renderer()
    labeling = layer.labeling()
    classAttribute = renderer.classAttribute()

    fields = layer.fields()
    fieldNames = [f.name() for f in fields]
    if classAttribute in fieldNames:
        classAttribute = '"{}"'.format(classAttribute)

    elseValues = []
    styles = []
    styleMap = {}

    categories = renderer.categories()
    for i, c in enumerate(categories):
        styleId = 'category{}'.format(i)

        symbolLayer = c.symbol().symbolLayer(0)
        ok, style = _symbolLayerToStyle(symbolLayer, labeling)
        if not ok:
            return None, style

        styleDefinition = '    <Style id="{}">\n{}\n    </Style>'.format(styleId, style)
        styles.append(styleDefinition)

        if c.value() is not None:
            v = QgsExpression.quotedValue(c.value())
            elseValues.append(v)
            styleMap[styleId] = '{} = {}'.format(classAttribute, v)
        else:
            styleMap[styleId] = '{} NOT IN ({})'.format(classAttribute, ','.join(elseValues))

    return styleMap, '\n'.join(styles)


def _graduatedStyle(layer):
    renderer = layer.renderer()
    labeling = layer.labeling()
    classAttribute = renderer.classAttribute()

    fields = layer.fields()
    fieldNames = [f.name() for f in fields]
    if classAttribute in fieldNames:
        classAttribute = '"{}"'.format(classAttribute)

    styles = []
    styleMap = {}

    ranges = renderer.ranges()
    for i, r in enumerate(ranges):
        styleId = 'range{}'.format(i)

        symbolLayer = r.symbol().symbolLayer(0)
        ok, style = _symbolLayerToStyle(symbolLayer, labeling)
        if not ok:
            return None, style
        styleDefinition = '    <Style id="{}">\n{}\n    </Style>'.format(styleId, style)
        styles.append(styleDefinition)
        styleMap[styleId] = '{attr} >= {lower} AND {attr} <= {upper}'.format(attr=classAttribute, lower=r.lowerValue(), upper=r.upperValue())

    return styleMap, '\n'.join(styles)


def _symbolLayerToStyle(symbolLayer, labeling):
    style = []

    if labeling is not None:
        color = labeling.settings().format().color()
        style.append('      <LabelStyle>')
        style.append('        <сolor>{:02x}{:02x}{:02x}{:02x}</color>'.format(color.alpha(), color.blue(), color.green(), color.red()))
        style.append('        <сolorMode>normal</colorMode>')
        style.append('        <scale>1</scale>')
        style.append('      </LabelStyle>')

    layerType = symbolLayer.layerType()
    if layerType == 'SimpleMarker':
        color = symbolLayer.color()
        style.append('      <IconStyle>')
        style.append('        <color>{:02x}{:02x}{:02x}{:02x}</color>'.format(color.alpha(), color.blue(), color.green(), color.red()))
        style.append('        <colorMode>normal</colorMode>')
        style.append('        <scale>1</scale>')
        style.append('      </IconStyle>')
    elif layerType == 'SimpleLine':
        color = symbolLayer.color()
        width = _unitToPixels(symbolLayer.width(), symbolLayer.outputUnit())
        style.append('      <LineStyle>')
        style.append('        <color>{:02x}{:02x}{:02x}{:02x}</color>'.format(color.alpha(), color.blue(), color.green(), color.red()))
        style.append('        <colorMode>normal</colorMode>')
        style.append('        <width>{}</width>'.format(width))
        style.append('      </LineStyle>')
    elif layerType == 'SimpleFill':
        color = symbolLayer.strokeColor()
        width = _unitToPixels(symbolLayer.strokeWidth(), symbolLayer.outputUnit())
        style.append('      <LineStyle>')
        style.append('        <color>{:02x}{:02x}{:02x}{:02x}</color>'.format(color.alpha(), color.blue(), color.green(), color.red()))
        style.append('        <colorMode>normal</colorMode>')
        style.append('        <width>{}</width>'.format(width))
        style.append('      </LineStyle>')

        color = symbolLayer.fillColor()
        fill = 1 if symbolLayer.brushStyle() != Qt.NoBrush else 0
        outline = 1 if symbolLayer.strokeStyle() != Qt.NoPen else 0
        style.append('      <PolyStyle>')
        style.append('        <color>{:02x}{:02x}{:02x}{:02x}</color>'.format(color.alpha(), color.blue(), color.green(), color.red()))
        style.append('        <colorMode>normal</colorMode>')
        style.append('        <fill>{:d}</fill>'.format(fill))
        style.append('        <outline>{:d}</outline>'.format(outline))
        style.append('      </PolyStyle>')
    else:
        return False, tr('Symbol layer "{}" is not supported.'.format(layerType))

    return True, '\n'.join(style)


def _unitToPixels(value, fromUnit):
    dpi = iface.mainWindow().physicalDpiX()

    if fromUnit ==  QgsUnitTypes.RenderMillimeters:
        return int((value * dpi) / 25.4)
    elif fromUnit == QgsUnitTypes.RenderPixels:
        return value
    elif fromUnit == QgsUnitTypes.RenderPoints:
        return int((value * dpi) / 72)
    elif fromUnit == QgsUnitTypes.RenderInches:
        return int(value * dpi)
    elif fromUnit == QgsUnitTypes.RenderMapUnits:
        factor = QgsUnitTypes.fromUnitToUnitFactor(iface.mapCanvas().mapSettings().mapUnit(), QgsUnitTypes.DistanceMillimeters)
        return int((value * factor * dpi) / 25.4)
    else:
        return 1

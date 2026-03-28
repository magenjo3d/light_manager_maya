"""
Light Manager +
(c) 2023 - Maya PySide2/PySide6 Version
Miguel Agenjo, 3D Generalist / Lighting TD
www.miguelagenjo.com
"""

import os
import random
import json
import tempfile
from typing import List, Dict
from pathlib import Path
from datetime import datetime

# Maya imports
try:
    import maya.cmds as cmds
    import maya.mel as mel
    from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False
    MayaQWidgetBaseMixin = object

# Arnold imports
try:
    import mtoa.ui.arnoldmenu as arnoldmenu
    import mtoa.utils as mutils
    ARNOLD_AVAILABLE = True
except ImportError:
    ARNOLD_AVAILABLE = False

# Qt imports – support both PySide6 (Maya 2025+) and PySide2 (Maya 2017-2024)
try:
    from PySide6.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QComboBox, QListWidget,
        QMessageBox, QDoubleSpinBox, QSpinBox,
        QSlider, QCheckBox, QLineEdit, QScrollArea, QColorDialog,
        QFrame, QGroupBox, QDialogButtonBox, QStyle
    )
    from PySide6.QtCore import Qt, Signal, QEvent, QSize
    from PySide6.QtGui import QFont, QColor, QIcon
    try:
        from PySide6.QtCore import QLocale
    except ImportError:
        QLocale = None
except ImportError:
    from PySide2.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QComboBox, QListWidget,
        QMessageBox, QDoubleSpinBox, QSpinBox,
        QSlider, QCheckBox, QLineEdit, QScrollArea, QColorDialog,
        QFrame, QGroupBox, QDialogButtonBox, QStyle
    )
    from PySide2.QtCore import Qt, Signal, QEvent, QSize, QLocale
    from PySide2.QtGui import QFont, QColor, QIcon

# Resolve MayaQWidgetBaseMixin base: handles both Maya 2022 (mixin without QWidget)
# and newer Maya versions (mixin already inherits QWidget) without MRO conflicts.
if not MAYA_AVAILABLE:
    MayaQWidgetBaseMixin = QWidget

if QWidget in getattr(MayaQWidgetBaseMixin, '__mro__', ()):
    _WindowBase = MayaQWidgetBaseMixin
else:
    class _WindowBase(MayaQWidgetBaseMixin, QWidget):
        pass


# ==================== Stylesheet ====================

DARK_STYLESHEET = """
    QWidget {
        background-color: #333333;
        color: #CCCCCC;
    }
    QLabel {
        color: #CCCCCC;
    }
    QPushButton {
        background-color: #4D4D4D;
        color: #CCCCCC;
        border: 1px solid #1A1A1A;
        border-radius: 3px;
        padding: 3px;
    }
    QPushButton:hover {
        background-color: #5D5D5D;
    }
    QPushButton:pressed {
        background-color: #3D3D3D;
    }
    QListWidget {
        background-color: #2A2A2A;
        color: #CCCCCC;
        border: 1px solid #1A1A1A;
    }
    QListWidget::item:selected {
        background-color: #555555;
    }
    QComboBox {
        background-color: #4D4D4D;
        color: #CCCCCC;
        border: 1px solid #1A1A1A;
        padding: 2px;
    }
    QTextEdit {
        background-color: #2A2A2A;
        color: #CCCCCC;
        border: 1px solid #1A1A1A;
        padding: 5px;
    }
    QLineEdit {
        background-color: #2A2A2A;
        color: #CCCCCC;
        border: 1px solid #1A1A1A;
        padding: 3px;
    }
    QTabWidget::pane {
        border: 1px solid #1A1A1A;
    }
    QTabBar::tab {
        background-color: #282828;
        color: #CCCCCC;
        padding: 5px 15px;
        margin-right: 2px;
    }
    QTabBar::tab:selected {
        background-color: #333333;
    }
    QDoubleSpinBox, QSpinBox {
        background-color: #2A2A2A;
        color: #CCCCCC;
        border: 1px solid #0A0A0A;
        padding: 2px;
    }
    QSlider::groove:horizontal {
        background-color: #2D2D2D;
        height: 6px;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background-color: #AAAAAA;
        width: 14px;
        margin: -4px 0;
        border-radius: 7px;
    }
    QCheckBox {
        color: #CCCCCC;
    }
    QScrollArea {
        border: none;
    }
"""


# ==================== Qt Helper Widgets ====================

class FloatFieldSlider(QWidget):
    """Float field + horizontal slider combination"""
    valueChanged = Signal(float)
    SLIDER_RESOLUTION = 10000

    def __init__(self, label="", value=0.0, min_val=0.0, max_val=1.0, decimals=3, parent=None):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        if label:
            lbl = QLabel(label)
            lbl.setMinimumWidth(90)
            layout.addWidget(lbl)

        self.field = QDoubleSpinBox()
        if QLocale is not None:
            self.field.setLocale(QLocale.c())
        self.field.setRange(-1e9, 1e9)
        self.field.setDecimals(decimals)
        self.field.setValue(value)
        self.field.setMinimumWidth(65)
        layout.addWidget(self.field, 2)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, self.SLIDER_RESOLUTION)
        self.slider.setValue(self._value_to_slider(value))
        layout.addWidget(self.slider, 3)

        self.field.valueChanged.connect(self._on_field_changed)
        self.slider.valueChanged.connect(self._on_slider_changed)

    def _value_to_slider(self, value):
        value = max(self._min, min(self._max, value))
        if self._max == self._min:
            return 0
        return int((value - self._min) / (self._max - self._min) * self.SLIDER_RESOLUTION)

    def _slider_to_value(self, pos):
        return self._min + (pos / self.SLIDER_RESOLUTION) * (self._max - self._min)

    def _on_field_changed(self, v):
        self.slider.blockSignals(True)
        self.slider.setValue(self._value_to_slider(v))
        self.slider.blockSignals(False)
        self.valueChanged.emit(v)

    def _on_slider_changed(self, pos):
        v = self._slider_to_value(pos)
        self.field.blockSignals(True)
        self.field.setValue(v)
        self.field.blockSignals(False)
        self.valueChanged.emit(v)

    def value(self):
        return self.field.value()

    def setValue(self, v):
        self.field.setValue(v)


class IntFieldSlider(QWidget):
    """Integer field + horizontal slider combination"""
    valueChanged = Signal(int)

    def __init__(self, label="", value=0, min_val=0, max_val=10, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        if label:
            lbl = QLabel(label)
            lbl.setMinimumWidth(90)
            layout.addWidget(lbl)

        self.field = QSpinBox()
        self.field.setRange(min_val, max_val * 10)
        self.field.setValue(value)
        self.field.setMinimumWidth(50)
        layout.addWidget(self.field, 2)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.slider.setValue(value)
        layout.addWidget(self.slider, 3)

        self.field.valueChanged.connect(self._on_field_changed)
        self.slider.valueChanged.connect(self._on_slider_changed)

    def _on_field_changed(self, v):
        sv = max(self.slider.minimum(), min(self.slider.maximum(), v))
        self.slider.blockSignals(True)
        self.slider.setValue(sv)
        self.slider.blockSignals(False)
        self.valueChanged.emit(v)

    def _on_slider_changed(self, v):
        self.field.blockSignals(True)
        self.field.setValue(v)
        self.field.blockSignals(False)
        self.valueChanged.emit(v)

    def value(self):
        return self.field.value()

    def setValue(self, v):
        self.field.setValue(v)


class ColorButton(QPushButton):
    """Color swatch button that opens a color picker dialog"""
    colorChanged = Signal(float, float, float)

    def __init__(self, r=1.0, g=1.0, b=1.0, parent=None):
        super().__init__(parent)
        self._color = (r, g, b)
        self.setMinimumSize(60, 25)
        self._update_style()
        self.clicked.connect(self._pick_color)

    def _update_style(self):
        r, g, b = self._color
        self.setStyleSheet(
            f"QPushButton {{ background-color: rgb({int(r*255)},{int(g*255)},{int(b*255)}); "
            f"border: 1px solid #1A1A1A; min-width: 30px; min-height: 15px; }}"
            f"QPushButton:hover {{ background-color: rgb({int(r*255)},{int(g*255)},{int(b*255)}); "
            f"border: 1px solid #5D5D5D; }}"
            f"QPushButton:pressed {{ background-color: rgb({int(r*255)},{int(g*255)},{int(b*255)}); "
            f"border: 1px solid #AAAAAA; }}"
        )

    def _pick_color(self):
        r, g, b = self._color
        initial = QColor(int(r * 255), int(g * 255), int(b * 255))
        dialog = QColorDialog(initial, self)
        dialog.setWindowTitle("Pick Light Color")
        dialog.setStyleSheet(
            "QPushButton {"
            "  background-color: #4D4D4D;"
            "  color: #CCCCCC;"
            "  border: 1px solid #1A1A1A;"
            "  border-radius: 3px;"
            "  padding: 4px 10px;"
            "}"
            "QPushButton:hover { background-color: #4D4D4D; border: 1px solid #5D5D5D; }"
            "QPushButton:pressed { background-color: #4D4D4D; border: 1px solid #AAAAAA; }"
        )

        fixed_btn_style = (
            "QPushButton {"
            "  background-color: #4D4D4D;"
            "  color: #CCCCCC;"
            "  border: 1px solid #1A1A1A;"
            "  border-radius: 3px;"
            "  padding: 4px 10px;"
            "}"
            "QPushButton:hover { background-color: #4D4D4D; border: 1px solid #1A1A1A; }"
            "QPushButton:pressed { background-color: #4D4D4D; border: 1px solid #1A1A1A; }"
        )
        for button_box in dialog.findChildren(QDialogButtonBox):
            for button in button_box.buttons():
                button.setStyleSheet(fixed_btn_style)

        if (dialog.exec() if hasattr(dialog, 'exec') else dialog.exec_()) == QColorDialog.Accepted:
            color = dialog.selectedColor()
            self._color = (color.redF(), color.greenF(), color.blueF())
            self._update_style()
            self.colorChanged.emit(*self._color)

    def color(self):
        return self._color

    def setColor(self, r, g, b):
        self._color = (r, g, b)
        self._update_style()


# ==================== Light Manager Functions ====================

class LightManagerFunctions:
    """Core functionality for Light Manager +. All methods accept direct Python values."""

    DEFAULT_LIGHT_SET = "defaultLightSet"
    BLACK_LIST = ["exposure", "intensity", "aiSamples", "aiUserOptions", "aiFilters",
                  "aiTranslator", "aiAov", "aiColorTemperature", "aiUseColorTemperature"]
    ARNOLD_ATTRS = ["coneAngle", "penumbraAngle", "dropoff", "decayRate"]
    RGB = ["R", "G", "B"]
    XYZ = ["X", "Y", "Z"]
    DEFAULT_VALUES = {"intensity": 1, "aiExposure": 1, "aiSamples": 1,
                      "color": (1, 1, 1), "aiColorTemperature": 6500, "aiUseColorTemperature": 0,
                      "coneAngle": 30, "penumbraAngle": 0, "dropoff": 0, "decayRate": 2,
                      "aiSpread": 1, "normalize": 1, "aiRoundness": 0,
                      "aiSoftEdge": 0, "aiCastShadows": 1, "aiShadowDensity": 1, "aiShadowColor": (0, 0, 0),
                      "aiCamera": 0, "aiDiffuse": 1, "aiSpecular": 1, "aiSss": 1, "aiVolume": 1, "aiIndirect": 1}

    def __init__(self):
        pass

    @staticmethod
    def _normalize_attr_value(value):
        """Flatten Maya getAttr outputs like [(r, g, b)] to JSON-friendly values."""
        if isinstance(value, list) and len(value) == 1 and isinstance(value[0], (list, tuple)):
            return list(value[0])
        if isinstance(value, tuple):
            return list(value)
        return value

    @staticmethod
    def _resolve_light_node(node):
        """Resolve a transform or shape to a light shape node."""
        try:
            if not cmds.objExists(node):
                return None

            node_type = cmds.objectType(node)
            if "light" in node_type.lower():
                return node

            shapes = cmds.listRelatives(node, shapes=True, fullPath=False) or []
            for shape in shapes:
                shape_type = cmds.objectType(shape)
                if "light" in shape_type.lower():
                    return shape
        except:
            pass
        return None

    def get_selected_light_nodes(self):
        """Return unique selected light shape nodes."""
        selected = cmds.ls(selection=True) or []
        resolved = []
        for node in selected:
            light_node = self._resolve_light_node(node)
            if light_node and light_node not in resolved:
                resolved.append(light_node)
        return resolved

    def get_arnold_attributes(self, shapes):
        """Get Arnold attributes available on the first light shape."""
        arnold_attrs = []
        try:
            if not shapes:
                return arnold_attrs

            shape = shapes[0]
            attrs = cmds.listAttr(shape) or []
            for attr_name in attrs:
                if attr_name.startswith("ai") and attr_name not in self.BLACK_LIST and attr_name not in arnold_attrs:
                    arnold_attrs.append(attr_name)
        except:
            pass
        return arnold_attrs

    def collect_light_properties(self, lights: List[str]) -> Dict:
        """Collect all properties from selected lights"""
        properties = {"lights": []}

        for light in lights:
            try:
                shapes = cmds.listRelatives(light, shapes=True)
                if shapes:
                    shape = shapes[0]
                    light_data = {
                        "name": light,
                        "type": cmds.objectType(shape),
                        "attributes": {},
                        "transform": {}
                    }
                    
                    # Collect transform attributes from the light's transform node
                    transform_attrs = cmds.listAttr(light, keyable=True) or []
                    for attr in transform_attrs:
                        if any(keyword in attr.lower() for keyword in ["translate", "rotate", "scale", "shear"]):
                            try:
                                attr_path = light + "." + attr
                                attr_value = cmds.getAttr(attr_path)
                                if isinstance(attr_value, (list, tuple)):
                                    if len(attr_value) == 1:
                                        light_data["transform"][attr] = attr_value[0]
                                    else:
                                        light_data["transform"][attr] = list(attr_value)
                                else:
                                    light_data["transform"][attr] = attr_value
                            except:
                                pass

                    # Get all keyable attributes from the light shape
                    all_attrs = cmds.listAttr(shape, keyable=True) or []
                    for attr in all_attrs:
                        try:
                            attr_path = shape + "." + attr
                            attr_value = cmds.getAttr(attr_path)
                            if isinstance(attr_value, (list, tuple)):
                                if len(attr_value) == 1:
                                    light_data["attributes"][attr] = attr_value[0]
                                else:
                                    light_data["attributes"][attr] = list(attr_value)
                            else:
                                light_data["attributes"][attr] = attr_value
                        except:
                            pass

                    # Get Arnold attributes
                    arnold_attrs = self.get_arnold_attributes(shapes)
                    
                    for attr in arnold_attrs:
                        try:
                            attr_path = shape + "." + attr
                            attr_value = cmds.getAttr(attr_path)
                            if isinstance(attr_value, (list, tuple)):
                                if len(attr_value) == 1:
                                    light_data["attributes"][attr] = attr_value[0]
                                else:
                                    light_data["attributes"][attr] = list(attr_value)
                            else:
                                light_data["attributes"][attr] = attr_value
                        except:
                            pass

                    # Hardcode exposure once per light in the saved JSON
                    light_data["attributes"]["exposure"] = None
                    for node in [light, shape]:
                        try:
                            attr_path = node + ".exposure"
                            if cmds.objExists(attr_path):
                                attr_value = cmds.getAttr(attr_path)
                                if isinstance(attr_value, (list, tuple)):
                                    if len(attr_value) == 1:
                                        light_data["attributes"]["exposure"] = attr_value[0]
                                    else:
                                        light_data["attributes"]["exposure"] = list(attr_value)
                                else:
                                    light_data["attributes"]["exposure"] = attr_value
                                break
                        except:
                            pass

                    properties["lights"].append(light_data)
            except:
                pass

        return properties

    def get_light_snapshot(self, light):
        """Capture keyable attributes from a light node in a simple JSON-ready format."""
        light_node = self._resolve_light_node(light)
        if not light_node:
            return None

        transform_node = None
        parents = cmds.listRelatives(light_node, parent=True, fullPath=False) or []
        if parents:
            transform_node = parents[0]

        snapshot = {"node": light_node, "transform": {}, "attrs": {}}

        if transform_node:
            transform_attrs = cmds.listAttr(transform_node, keyable=True) or []
            for attr in transform_attrs:
                if not (attr.startswith("translate") or attr.startswith("rotate") or attr.startswith("scale")):
                    continue

                plug = transform_node + "." + attr
                try:
                    value = self._normalize_attr_value(cmds.getAttr(plug, silent=True))
                except:
                    continue

                if isinstance(value, (int, float, bool, str, list, tuple)):
                    snapshot["transform"][attr] = value

        attrs = cmds.listAttr(light_node, keyable=True) or []

        for attr in attrs:
            plug = light_node + "." + attr
            try:
                value = self._normalize_attr_value(cmds.getAttr(plug, silent=True))
            except:
                continue

            if isinstance(value, (int, float, bool, str, list, tuple)):
                snapshot["attrs"][attr] = value

        return snapshot

    def apply_snapshot_to_light(self, light, snapshot):
        """Apply a previously saved snapshot to a light node."""
        light_node = self._resolve_light_node(light)
        if not light_node:
            return

        parents = cmds.listRelatives(light_node, parent=True, fullPath=False) or []
        transform_node = parents[0] if parents else None

        transform_attrs = snapshot.get("transform", {})
        if transform_node:
            for attr, value in transform_attrs.items():
                plug = transform_node + "." + attr
                try:
                    if not cmds.objExists(plug):
                        continue
                    if not cmds.getAttr(plug, settable=True):
                        continue

                    if isinstance(value, str):
                        cmds.setAttr(plug, value, type="string")
                    elif isinstance(value, (list, tuple)):
                        if len(value) > 0:
                            cmds.setAttr(plug, *value)
                    else:
                        cmds.setAttr(plug, value)
                except:
                    pass

        attrs = snapshot.get("attrs", {})
        for attr, value in attrs.items():
            plug = light_node + "." + attr
            try:
                if not cmds.objExists(plug):
                    continue
                if not cmds.getAttr(plug, settable=True):
                    continue

                if isinstance(value, str):
                    cmds.setAttr(plug, value, type="string")
                elif isinstance(value, (list, tuple)):
                    if len(value) > 0:
                        cmds.setAttr(plug, *value)
                else:
                    cmds.setAttr(plug, value)
            except:
                pass

    # ==================== Utility Methods ====================

    @staticmethod
    def _get_selected_lights():
        """Get currently selected lights"""
        return cmds.ls(selection=True)

    @staticmethod
    def _deselect_default_set():
        """Deselect the default light set"""
        cmds.select(LightManagerFunctions.DEFAULT_LIGHT_SET, d=True)

    # ==================== Light Info Methods ====================

    def get_values_existing(self):
        """Get intensity, exposure, and samples from first selected light"""
        default_values = [1.0, 0.0, 1]
        try:
            cmds.select(self.DEFAULT_LIGHT_SET)
            selected = self._get_selected_lights()
            if selected:
                intensity = cmds.getAttr(selected[0] + ".intensity")
                exposure = cmds.getAttr(selected[0] + ".aiExposure")
                samples = cmds.getAttr(selected[0] + ".aiSamples")
                self._deselect_default_set()
                return [intensity, exposure, samples]
        except:
            pass
        return default_values

    def get_total_lights_list(self):
        """Get sorted list of all lights in the default light set"""
        try:
            cmds.select(self.DEFAULT_LIGHT_SET)
            total_lights_list = sorted(self._get_selected_lights())
            self._deselect_default_set()
            return total_lights_list
        except:
            return []

    def list_custom_attrs(self):
        """List custom Arnold attributes available on lights"""
        try:
            sel = cmds.ls(self.DEFAULT_LIGHT_SET)
            shapes = cmds.listRelatives(sel, shapes=True)
            attr = cmds.listAttr(shapes)

            custom_attrs = list(self.ARNOLD_ATTRS)
            for attr_name in attr:
                if attr_name.startswith("ai") and attr_name not in self.BLACK_LIST and attr_name not in custom_attrs:
                    custom_attrs.append(attr_name)

            return sorted(custom_attrs)
        except:
            print("WARNING! Rename your lights")
            return self.ARNOLD_ATTRS

    # ==================== Color/Attribute Setting Methods ====================

    def set_color(self, r, g, b):
        """Set color on all selected lights"""
        try:
            selected = self._get_selected_lights()
            for light in selected:
                try:
                    cmds.setAttr(light + ".color", r, g, b)
                except:
                    pass
        except:
            pass

    def set_intensity(self, intensity):
        """Set intensity on all selected lights"""
        try:
            selected = self._get_selected_lights()
            for light in selected:
                try:
                    cmds.setAttr(light + ".intensity", intensity)
                except:
                    pass
        except:
            pass

    def set_exposure(self, exposure):
        """Set exposure on all selected lights"""
        try:
            selected = self._get_selected_lights()
            for light in selected:
                try:
                    cmds.setAttr(light + ".aiExposure", exposure)
                except:
                    pass
        except:
            pass

    def set_samples(self, samples):
        """Set samples on all selected lights"""
        try:
            selected = self._get_selected_lights()
            for light in selected:
                cmds.setAttr(light + ".aiSamples", samples)
        except:
            pass

    def set_custom_attr(self, attr_name, value):
        """Set custom attribute on all selected lights"""
        try:
            selected = self._get_selected_lights()
            for light in selected:
                try:
                    cmds.setAttr(light + "." + attr_name, value)
                except:
                    pass
        except:
            pass

    def set_custom_unique_attr(self, attr_name, value):
        """Set specific custom attribute on all selected lights"""
        try:
            selected = self._get_selected_lights()
            for light in selected:
                try:
                    cmds.setAttr(light + "." + attr_name, value)
                except:
                    pass
        except:
            pass

    def set_all_attributes(self, samples, exposure, intensity, r, g, b):
        """Set all attributes at once"""
        self.set_samples(samples)
        self.set_exposure(exposure)
        self.set_intensity(intensity)
        self.set_color(r, g, b)

    def set_default_attributes(self):
        """Reset all attributes to default values"""
        selected = self._get_selected_lights()
        for light in selected:
            for attr, value in self.DEFAULT_VALUES.items():
                if attr == "color":
                    cmds.setAttr(light + ".color", *value)
                else:
                    try:
                        cmds.setAttr(light + "." + attr, value)
                    except:
                        pass

    # ==================== Toggle Methods ====================

    def enable_disable_attr(self, attr_name, state):
        """Toggle custom attribute on/off"""
        try:
            value = 1 if state else 0
            selected = self._get_selected_lights()
            for light in selected:
                try:
                    cmds.setAttr(light + "." + attr_name, value)
                except:
                    pass
        except:
            pass

    def enable_disable_unique_attr(self, attr_name, state):
        """Toggle specific attribute on/off"""
        try:
            value = 1 if state else 0
            selected = self._get_selected_lights()
            for light in selected:
                try:
                    cmds.setAttr(light + "." + attr_name, value)
                except:
                    pass
        except:
            pass

    # ==================== Randomization Methods ====================

    def random_color(self):
        """Set random color on all selected lights"""
        selected = self._get_selected_lights()
        for light in selected:
            try:
                r, g, b = random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)
                cmds.setAttr(light + ".color", r, g, b)
            except:
                pass

    def randomize_intensity(self, base, range_val):
        """Set random intensity between base and range values"""
        try:
            selected = self._get_selected_lights()
            for light in selected:
                cmds.setAttr(light + ".intensity", random.uniform(base, range_val))
        except:
            pass

    def randomize_exposure(self, base, range_val):
        """Set random exposure between base and range values"""
        try:
            selected = self._get_selected_lights()
            for light in selected:
                cmds.setAttr(light + ".aiExposure", random.uniform(base, range_val))
        except:
            pass

    # ==================== File Browser Methods ====================

    def browse_photometry_file(self):
        """Browse and set photometry file path"""
        try:
            file_path = cmds.fileDialog2(fileMode=1, caption="Select File", fileFilter="All Files (*.*)")[0]
            selected = self._get_selected_lights()
            if file_path:
                for light in selected:
                    shapes = cmds.listRelatives(light)
                    if shapes:
                        cmds.setAttr(shapes[0] + '.aiFilename', file_path, type='string')
        except:
            pass

    def browse_color_file(self):
        """Browse and set color texture file"""
        try:
            file_path = cmds.fileDialog2(fileMode=1, caption="Select File", fileFilter="All Files (*.*)")[0]
            selected = self._get_selected_lights()
            if file_path:
                file_node = cmds.shadingNode('file', asTexture=True)
                cmds.setAttr(file_node + '.fileTextureName', file_path, type='string')
                for light in selected:
                    cmds.connectAttr(file_node + '.outColor', light + '.color')
        except:
            pass

    # ==================== Animation Keyframe Methods ====================

    def key_attribute(self, attr_name):
        """Set keyframe on attribute"""
        try:
            selected = self._get_selected_lights()
            for light in selected:
                try:
                    cmds.setKeyframe(attr_name)
                except:
                    pass
        except:
            pass

    def disconnect_files(self):
        """Disconnect file textures from light colors"""
        try:
            selected = self._get_selected_lights()
            for light in selected:
                shapes = cmds.listRelatives(light)
                if shapes:
                    connections = cmds.listConnections(shapes)
                    if connections:
                        for node in connections:
                            try:
                                cmds.disconnectAttr(node + ".outColor", light + ".color")
                            except:
                                pass
        except:
            pass

    def delete_all_keys(self, custom_attr_name):
        """Delete all animation keys from selected lights"""
        try:
            selected = self._get_selected_lights()
            attrs_to_disconnect = ["exposure", "aiExposure", "intensity", "aiSamples"]

            for light in selected:
                shapes = cmds.listRelatives(light)
                if shapes:
                    connections = cmds.listConnections(shapes)
                    if connections:
                        for node in connections:
                            if "_" in node:
                                try:
                                    cmds.disconnectAttr(node + ".output", light + "." + custom_attr_name)
                                except:
                                    pass

                                for std_attr in attrs_to_disconnect:
                                    try:
                                        cmds.disconnectAttr(node + ".output", light + "." + std_attr)
                                    except:
                                        pass

                                for rgb in self.RGB:
                                    try:
                                        cmds.disconnectAttr(node[0:-1] + rgb + ".output", light + ".color" + rgb)
                                    except:
                                        pass

                                    try:
                                        cmds.disconnectAttr(node + ".output", light + ".color.color" + rgb)
                                    except:
                                        pass

            print("Animation Keys deleted")
        except:
            pass

    # ==================== Light Population Methods ====================

    def create_mesh_light(self, obj):
        """Create Arnold mesh light from geometry"""
        try:
            mesh_transform = obj
            shapes = cmds.listRelatives(mesh_transform, fullPath=True)
            mesh_shape = shapes[0]

            light_name = cmds.shadingNode("aiMeshLight", n=mesh_transform + "_MeshLightShape", asLight=True)
            cmds.connectAttr('%s.outMesh' % mesh_shape, '%s.inMesh' % light_name)

            parent = cmds.parent(light_name, mesh_transform, relative=True)
            light_shape = cmds.listRelatives(parent[0], shapes=True, fullPath=True)[0]
            cmds.connectAttr('%s.showOriginalMesh' % light_shape, '%s.visibility' % mesh_shape)

            cmds.setAttr('%s.showOriginalMesh' % light_shape, 1)
            cmds.setAttr('%s.showOriginalMesh' % light_shape, 0)
        except:
            pass

    def populate_lights(self, parent_to_object, light_type, use_locator):
        """Populate lights around selected objects"""
        try:
            selected_objs = self._get_selected_lights()
            cmds.CenterPivot(selected_objs)
            lights_created = []
            counter = 0

            group_node = None
            if not parent_to_object:
                group_node = cmds.group(empty=True, name=light_type + "Lgt_grp")
                cmds.setAttr(group_node + ".useOutlinerColor", 1)
                cmds.setAttr(group_node + ".outlinerColor", 1, 1, 0)

            for obj in selected_objs:
                if not obj.endswith("Shape"):
                    counter += 1

                    pos = [cmds.getAttr(obj + ".translate" + axis) for axis in self.XYZ]
                    rot = [cmds.getAttr(obj + ".rotate" + axis) for axis in self.XYZ]

                    if light_type == "Mesh Light":
                        self.create_mesh_light(obj)
                        if group_node:
                            try:
                                cmds.delete(group_node)
                            except:
                                pass
                    else:
                        if light_type == "Point":
                            light_name = cmds.pointLight()
                        elif light_type == "Area":
                            light_name = cmds.shadingNode("aiAreaLight", name="aiAreaLightShape" + str(counter), asLight=True)
                        elif light_type == "Spot":
                            light_name = cmds.spotLight()
                        elif light_type == "Photometric":
                            light_name = cmds.shadingNode("aiPhotometricLight", name="aiPhotometricLightShape" + str(counter), asLight=True)

                        lights_created.append(light_name)

                        if use_locator:
                            locator = cmds.spaceLocator()[0]
                            cmds.parent(light_name, locator)

                            if not parent_to_object:
                                cmds.parent(locator, group_node)
                            else:
                                cmds.parent(locator, obj)

                            for i, coord in enumerate(pos):
                                cmds.setAttr(locator + ".translate" + self.XYZ[i], coord)

                            for i, coord in enumerate(rot):
                                cmds.setAttr(locator + ".rotate" + self.XYZ[i], coord)

                            cmds.matchTransform(locator, obj, pos=True, rot=True, scl=True)
                            cmds.rename(locator, light_name.replace("Shape", "") + "_locator")
                        else:
                            if parent_to_object:
                                cmds.parent(light_name, obj)

                            light_base_name = light_name.replace("Shape", "")
                            for i, coord in enumerate(pos):
                                cmds.setAttr(light_base_name + ".translate" + self.XYZ[i], coord)

                            for i, coord in enumerate(rot):
                                cmds.setAttr(light_base_name + ".rotate" + self.XYZ[i], coord)

                            cmds.matchTransform(light_name, obj, pos=True, rot=True, scl=True)
            

            if group_node and not use_locator:
                cmds.parent(lights_created, group_node)
        except Exception as e:
            print(f"Error populating lights: {e}")

    # ==================== Selection / UI Methods ====================

    def select_by_name(self, search_text):
        """Select lights by name pattern"""
        try:
            print(search_text)
            cmds.select("*" + search_text + "*")
            cmds.select("*Shape*", d=True)
        except:
            pass

    def delete_selected_lights(self):
        """Delete selected lights"""
        try:
            selected = self._get_selected_lights()
            cmds.delete(selected)
        except:
            pass

    def sanity_check(self):
        """Validate and fix light names with issues. Returns (success, message)."""
        try:
            all_lights = cmds.listRelatives(self.DEFAULT_LIGHT_SET)
            failed = []

            for light in all_lights:
                try:
                    cmds.select(light.replace("Shape", ""))
                except:
                    failed.append(light.replace("Shape", ""))
                    print(light.replace("Shape", "") + " Sanity check")

            for i, light in enumerate(failed, 1):
                obj = cmds.ls(light)
                cmds.rename(obj[0], light + "_" + str(i))

            return True, "Sanity check passed successfully!\nLights renamed with unique id"
        except Exception as e:
            return False, str(e)


# ==================== Light Manager Tab ====================

class LightManagerTab(QWidget):
    """Light Manager tab - full PySide2/PySide6 port of the original cmds UI"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lm = LightManagerFunctions()
        self._syncing_ui_from_selection = False
        self._backup_temp_file = Path(tempfile.gettempdir()) / "light_manager_state.json"
        print("Light Manager temp config:", str(self._backup_temp_file))
        self._build_ui()
        self._refresh_light_list()

    @staticmethod
    def _make_separator():
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #555555;")
        return line

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(3)

        # === Utils Shelf at the very top ===
        self._build_toolbar(main_layout)

        # === Top area: light list (left) + controls (right) ===
        content_layout = QHBoxLayout()

        # -- Left: Light list --
        left_layout = QVBoxLayout()

        # Refresh / Sanity Check row above the list
        list_top_row = QHBoxLayout()
        list_top_row.setSpacing(3)
        list_top_row.addWidget(
            self._icon_btn("SVGRefresh_200.png", "Refresh light list", self._refresh_light_list))
        list_top_row.addWidget(
            self._icon_btn("MayaStartupDoneCheck_150.png", "Sanity Check", self._sanity_check))
        self.lights_count_label = QLabel("Lights: 0")
        list_top_row.addWidget(self.lights_count_label)
        list_top_row.addStretch()
        left_layout.addLayout(list_top_row)

        self.light_list = QListWidget()
        self.light_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.light_list.setMinimumWidth(140)
        self.light_list.installEventFilter(self)
        self.light_list.itemSelectionChanged.connect(self._on_list_selection_changed)
        left_layout.addWidget(self.light_list)

        self.backUp(left_layout)

        content_layout.addLayout(left_layout, 1)

        # -- Right: scrollable controls area --
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(4)

        self._build_selection_row(right_layout)
        right_layout.addWidget(self._make_separator())
        self._build_light_populator(right_layout)
        right_layout.addWidget(self._make_separator())
        self._build_light_attributes(right_layout)

        right_scroll.setWidget(right_widget)
        content_layout.addWidget(right_scroll, 3)

        main_layout.addLayout(content_layout)

    # ---- Section builders ----

    def backUp(self, parent_layout):
        """Build Save/Load state controls under the light list."""
        row = QHBoxLayout()

        btn_save_state = QPushButton("Snap state")
        btn_save_state.clicked.connect(self._save_state)
        row.addWidget(btn_save_state)

        btn_load_state = QPushButton("Load state")
        btn_load_state.clicked.connect(self._load_state)
        row.addWidget(btn_load_state)

        parent_layout.addLayout(row)

    @staticmethod
    def _make_group_box(title):
        """Create a styled group box for toolbar sections"""
        group = QGroupBox(title)
        group.setStyleSheet(
            "QGroupBox { "
            "  border: 1px solid #555555; border-radius: 4px; "
            "  margin-top: 10px; padding: 8px 4px 4px 4px; "
            "  font-weight: bold; color: #AAAAAA; "
            "} "
            "QGroupBox::title { "
            "  subcontrol-origin: margin; left: 8px; "
            "  padding: 0 4px; "
            "}"
        )
        return group

    @staticmethod
    def _find_maya_icon(icon_name):
        """Resolve full path to a Maya or plugin icon via XBMLANGPATH."""
        for env_var in ("XBMLANGPATH", "MAYA_ICON_PATH"):
            paths = os.environ.get(env_var, "")
            for p in paths.split(os.pathsep):
                p = p.replace("%B", "")
                full = os.path.join(p, icon_name)
                if os.path.isfile(full):
                    return full
        # Fallback to Qt resource prefix
        return ":" + icon_name

    @staticmethod
    def _icon_btn(icon_name, tooltip, callback, size=32):
        """Create a QPushButton with a Maya shelf icon"""
        btn = QPushButton()
        icon_path = LightManagerTab._find_maya_icon(icon_name)
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(size, size))
        btn.setToolTip(tooltip)
        btn.setFixedSize(size + 10, size + 10)
        btn.setStyleSheet(
            "QPushButton { background-color: #4D4D4D; border: 1px solid #1A1A1A; border-radius: 3px; }"
            "QPushButton:hover { background-color: #5D5D5D; }"
            "QPushButton:pressed { background-color: #3D3D3D; }"
        )
        btn.clicked.connect(callback)
        return btn

    def _build_toolbar(self, parent_layout):
        lbl = QLabel("Utils Shelf")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("background-color: #4A4A4A; padding: 3px;")
        parent_layout.addWidget(lbl)

        shelf_layout = QHBoxLayout()
        shelf_layout.setSpacing(6)

        # --- Group 1: Arnold Lights ---
        arnold_group = self._make_group_box("Arnold Lights")
        arnold_row = QHBoxLayout(arnold_group)
        arnold_row.setSpacing(3)

        arnold_btns = [
            ("AreaLightShelf.png",        "Area Light",        lambda: (mutils.createLocator("aiAreaLight", asLight=True), self._refresh_light_list()) if ARNOLD_AVAILABLE else None),
            ("MeshLightShelf.png",        "Mesh Light",        lambda: (mutils.createMeshLight(), self._refresh_light_list()) if ARNOLD_AVAILABLE else None),
            ("PhotometricLightShelf.png", "Photometric Light",  lambda: (mutils.createLocator("aiPhotometricLight", asLight=True), self._refresh_light_list()) if ARNOLD_AVAILABLE else None),
            ("SkydomeLightShelf.png",     "Skydome Light",      lambda: (mutils.createLocator("aiSkyDomeLight", asLight=True), self._refresh_light_list()) if ARNOLD_AVAILABLE else None),
            ("PhysicalSkyShelf.png",      "Physical Sky",       lambda: (arnoldmenu.doCreatePhysicalSky(), self._refresh_light_list()) if ARNOLD_AVAILABLE else None),
            ("LightPortalShelf.png",      "Light Portal",       lambda: (arnoldmenu.doCreateLightPortal(), self._refresh_light_list()) if ARNOLD_AVAILABLE else None),
        ]

        for icon, tooltip, func in arnold_btns:
            arnold_row.addWidget(self._icon_btn(icon, tooltip, func))

        shelf_layout.addWidget(arnold_group)

        # --- Group 2: Maya Lights ---
        maya_group = self._make_group_box("Maya Lights")
        maya_row = QHBoxLayout(maya_group)
        maya_row.setSpacing(3)

        maya_btns = [
            ("directionallight.png", "Directional Light", lambda: (cmds.directionalLight(), self._refresh_light_list())),
            ("pointlight.png",       "Point Light",       lambda: (cmds.pointLight(), self._refresh_light_list())),
            ("spotlight.png",        "Spot Light",        lambda: (cmds.spotLight(), self._refresh_light_list())),
            ("ambientlight.png",     "Ambient Light",     lambda: (cmds.ambientLight(), self._refresh_light_list())),
        ]

        for icon, tooltip, func in maya_btns:
            maya_row.addWidget(self._icon_btn(icon, tooltip, func))

        shelf_layout.addWidget(maya_group)

        # --- Group 3: Arnold Utils ---
        if ARNOLD_AVAILABLE:
            utils_group = self._make_group_box("Arnold Utils")
            utils_row = QHBoxLayout(utils_group)
            utils_row.setSpacing(3)

            
            utils_row.addWidget(
                self._icon_btn("RenderViewShelf.png", "Render View", lambda: arnoldmenu.arnoldOpenMtoARenderView()))
            utils_row.addWidget(
                self._icon_btn("renderGlobals.png", "Render Settings", lambda: cmds.RenderGlobalsWindow()))
            utils_row.addWidget(
                self._icon_btn("TXManagerShelf.png", "TX Manager", lambda: arnoldmenu.arnoldTxManager()))
            utils_row.addWidget(
                self._icon_btn("menuIconWindow.png", "Node Editor", lambda: cmds.NodeEditorWindow()))
            utils_row.addWidget(
                self._icon_btn("standardSurface.svg", "Create aiStandardSurface", self._create_ai_standard_surface))
            utils_row.addWidget(
                self._icon_btn("deleteTextRefObj.png", "Delete Unused Nodes", self._delete_unused_nodes))

            shelf_layout.addWidget(utils_group)

        parent_layout.addLayout(shelf_layout)



    def _delete_unused_nodes(self):
        mel.eval("MLdeleteUnused()")
 
    def _create_ai_standard_surface(self):

        selected_geo = cmds.ls(selection=True, type="transform")
        shader_name = cmds.shadingNode("aiStandardSurface", asShader=True)

        if selected_geo:
            shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shader_name + "SG")
            cmds.connectAttr(shader_name + ".outColor", shading_group + ".surfaceShader")
            for geo in selected_geo:
                cmds.sets(geo, edit=True, forceElement=shading_group)
        else:
            cmds.select(shader_name)

    def _build_selection_row(self, parent_layout):
        row = QHBoxLayout()

        btn_select_all = QPushButton("Select All Lights")
        btn_select_all.setMinimumHeight(30)
        btn_select_all.setStyleSheet("background-color: #006633;")
        btn_select_all.clicked.connect(lambda: cmds.select("defaultLightSet"))
        row.addWidget(btn_select_all)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search by name...")
        self.search_field.returnPressed.connect(self._select_by_name)
        row.addWidget(self.search_field, 1)

        btn_search = QPushButton("Select by name")
        btn_search.clicked.connect(self._select_by_name)
        row.addWidget(btn_search)

        parent_layout.addLayout(row)

    def _build_light_populator(self, parent_layout):
        lbl = QLabel("Light Populator")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("background-color: #4A4A4A; padding: 3px;")
        lbl.setFixedHeight(20)
        parent_layout.addWidget(lbl)

        row = QHBoxLayout()

        row.addWidget(QLabel("Light Type:"))
        self.light_type_combo = QComboBox()
        self.light_type_combo.addItems(["Point", "Area", "Spot", "Mesh Light", "Photometric"])
        row.addWidget(self.light_type_combo)

        self.parent_check = QCheckBox("Parent to Object")
        row.addWidget(self.parent_check)

        self.locator_check = QCheckBox("Locator")
        self.locator_check.setChecked(True)
        row.addWidget(self.locator_check)

        btn_populate = QPushButton("Populate")
        btn_populate.clicked.connect(self._populate_lights)
        row.addWidget(btn_populate)

        parent_layout.addLayout(row)

    def _build_light_attributes(self, parent_layout):
        lbl = QLabel("Light Attributes")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("background-color: #4A4A4A; padding: 3px;")
        lbl.setFixedHeight(20)
        parent_layout.addWidget(lbl)

        # -- Color row --
        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Color"))

        self.color_btn = ColorButton()
        self.color_btn.colorChanged.connect(self._on_color_changed)
        color_row.addWidget(self.color_btn)

        btn_key_color = QPushButton("Key")
        btn_key_color.setStyleSheet("background-color: #4D1A1A;")
        btn_key_color.setMaximumWidth(26)
        btn_key_color.clicked.connect(lambda: self.lm.key_attribute(".color"))
        color_row.addWidget(btn_key_color)

        folder_icon = self.style().standardIcon(QStyle.SP_DirOpenIcon)
        btn_browse_file = QPushButton()
        btn_browse_file.setIcon(folder_icon)
        btn_browse_file.setToolTip("Browse File")
        btn_browse_file.setMaximumWidth(32)
        btn_browse_file.clicked.connect(lambda: self.lm.browse_color_file())
        color_row.addWidget(btn_browse_file)

        btn_disconnect = QPushButton("Disconnect")
        btn_disconnect.clicked.connect(lambda: self.lm.disconnect_files())
        color_row.addWidget(btn_disconnect)

        btn_random_color = QPushButton("Random")
        btn_random_color.clicked.connect(lambda: self.lm.random_color())
        color_row.addWidget(btn_random_color)

        parent_layout.addLayout(color_row)

        # -- Temperature row --
        temp_row = QHBoxLayout()
        self.temp_slider = FloatFieldSlider("Temperature (K)", value=6500, min_val=0, max_val=15000, decimals=0)
        self.temp_slider.valueChanged.connect(lambda v: self.lm.set_custom_unique_attr("aiColorTemperature", v))
        temp_row.addWidget(self.temp_slider, 1)

        self.temp_check = QCheckBox("on/off")
        self.temp_check.stateChanged.connect(
            lambda state: self.lm.enable_disable_unique_attr("aiUseColorTemperature", 1 if state else 0)
        )
        temp_row.addWidget(self.temp_check)

        parent_layout.addLayout(temp_row)

        # -- Photometric file row --
        photo_row = QHBoxLayout()
        photo_row.addWidget(QLabel("Photometric File  "))
        btn_browse_photo = QPushButton()
        btn_browse_photo.setIcon(folder_icon)
        btn_browse_photo.setToolTip("Browse File")
        btn_browse_photo.setMaximumWidth(32)
        btn_browse_photo.clicked.connect(lambda: self.lm.browse_photometry_file())
        photo_row.addWidget(btn_browse_photo)
        photo_row.addStretch()
        parent_layout.addLayout(photo_row)

        # -- Get initial values --
        init_vals = self.lm.get_values_existing()

        # -- Intensity row --
        int_row = QHBoxLayout()
        self.intensity_slider = FloatFieldSlider("Intensity", value=init_vals[0], min_val=0, max_val=25)
        self.intensity_slider.valueChanged.connect(lambda v: self.lm.set_intensity(v))
        int_row.addWidget(self.intensity_slider, 3)

        btn_key_int = QPushButton("Key")
        btn_key_int.setStyleSheet("background-color: #4D1A1A;")
        btn_key_int.setMaximumWidth(40)
        btn_key_int.clicked.connect(lambda: self.lm.key_attribute(".intensity"))
        int_row.addWidget(btn_key_int)

        self.int_range_slider = FloatFieldSlider("", value=10, min_val=0, max_val=25)
        int_row.addWidget(self.int_range_slider, 2)

        btn_random_int = QPushButton("Random")
        btn_random_int.clicked.connect(self._randomize_intensity)
        int_row.addWidget(btn_random_int)

        parent_layout.addLayout(int_row)

        # -- Exposure row --
        exp_row = QHBoxLayout()
        self.exposure_slider = FloatFieldSlider("Exposure", value=init_vals[1], min_val=-5, max_val=30)
        self.exposure_slider.valueChanged.connect(lambda v: self.lm.set_exposure(v))
        exp_row.addWidget(self.exposure_slider, 3)

        btn_key_exp = QPushButton("Key")
        btn_key_exp.setStyleSheet("background-color: #4D1A1A;")
        btn_key_exp.setMaximumWidth(40)
        btn_key_exp.clicked.connect(lambda: self.lm.key_attribute(".aiExposure"))
        exp_row.addWidget(btn_key_exp)

        self.exp_range_slider = FloatFieldSlider("", value=10, min_val=-5, max_val=30)
        exp_row.addWidget(self.exp_range_slider, 2)

        btn_random_exp = QPushButton("Random")
        btn_random_exp.clicked.connect(self._randomize_exposure)
        exp_row.addWidget(btn_random_exp)

        parent_layout.addLayout(exp_row)

        # -- Samples row --
        sam_row = QHBoxLayout()
        self.samples_slider = IntFieldSlider("Samples", value=init_vals[2], min_val=0, max_val=10)
        self.samples_slider.valueChanged.connect(lambda v: self.lm.set_samples(v))
        sam_row.addWidget(self.samples_slider, 1)

        btn_key_sam = QPushButton("Key")
        btn_key_sam.setStyleSheet("background-color: #4D1A1A;")
        btn_key_sam.setMaximumWidth(40)
        btn_key_sam.clicked.connect(lambda: self.lm.key_attribute(".aiSamples"))
        sam_row.addWidget(btn_key_sam)

        parent_layout.addLayout(sam_row)

        # -- Custom attribute row --
        custom_row = QHBoxLayout()
        custom_row.addWidget(QLabel("Custom Attr"))

        self.custom_attr_combo = QComboBox()
        try:
            attrs = self.lm.list_custom_attrs()
            self.custom_attr_combo.addItems(attrs)
        except:
            self.custom_attr_combo.addItems(LightManagerFunctions.ARNOLD_ATTRS)
        custom_row.addWidget(self.custom_attr_combo)

        self.custom_check = QCheckBox("on/off")
        self.custom_check.setChecked(True)
        self.custom_check.stateChanged.connect(self._on_custom_enable_changed)
        custom_row.addWidget(self.custom_check)

        self.custom_value_slider = FloatFieldSlider("", value=1, min_val=0, max_val=500)
        self.custom_value_slider.valueChanged.connect(self._on_custom_value_changed)
        custom_row.addWidget(self.custom_value_slider, 1)

        btn_key_custom = QPushButton("Key")
        btn_key_custom.setStyleSheet("background-color: #4D1A1A;")
        btn_key_custom.setMaximumWidth(40)
        btn_key_custom.clicked.connect(self._key_custom_attr)
        custom_row.addWidget(btn_key_custom)

        parent_layout.addLayout(custom_row)

        # -- Action buttons --
        parent_layout.addWidget(self._make_separator())

        action_row = QHBoxLayout()
        btn_default = QPushButton("Set Default")
        btn_default.clicked.connect(lambda: self.lm.set_default_attributes())
        action_row.addWidget(btn_default)

        btn_del_keys = QPushButton("Delete All Keys")
        btn_del_keys.clicked.connect(self._delete_all_keys)
        action_row.addWidget(btn_del_keys)

        parent_layout.addLayout(action_row)

        # -- Set All button --
        parent_layout.addWidget(self._make_separator())
        btn_set_all = QPushButton("Set All Selected")
        btn_set_all.setMinimumHeight(30)
        btn_set_all.setStyleSheet("background-color: #3A3A3A; font-weight: bold;")
        btn_set_all.clicked.connect(self._set_all_attributes)
        parent_layout.addWidget(btn_set_all)

    # ---- Callback methods ----

    def _refresh_light_list(self):
        self.light_list.clear()
        lights = self.lm.get_total_lights_list()
        for name in lights:
            self.light_list.addItem(name)
        self.lights_count_label.setText(f"Lights: {len(lights)}")

    def _save_state(self):
        selected = cmds.ls(selection=True) or []
        if not selected:
            QMessageBox.warning(self, "Save state", "Select at least one light to save its state.")
            return

        payload = self.lm.collect_light_properties(selected)
        if not payload.get("lights"):
            QMessageBox.warning(self, "Save state", "No valid light data could be captured.")
            return

        try:
            with self._backup_temp_file.open("w", encoding="utf-8") as backup_file:
                json.dump(payload, backup_file, indent=2)
            QMessageBox.information(self, "Save state", "Current light configuration saved.")
        except Exception as e:
            QMessageBox.warning(self, "Save state", f"Failed to save state:\n{e}")

    def _load_state(self):
        if not self._backup_temp_file.exists():
            QMessageBox.warning(self, "Load state", "No saved temp state was found.")
            return

        selected = self.lm.get_selected_light_nodes()
        if not selected:
            QMessageBox.warning(self, "Load state", "Select at least one light to load state into.")
            return

        try:
            with self._backup_temp_file.open("r", encoding="utf-8") as backup_file:
                payload = json.load(backup_file)
        except Exception as e:
            QMessageBox.warning(self, "Load state", f"Failed to load state:\n{e}")
            return

        saved_lights = payload.get("lights", [])
        if not saved_lights:
            QMessageBox.warning(self, "Load state", "Saved state file is empty.")
            return

        if len(saved_lights) == len(selected):
            for target_light, light_data in zip(selected, saved_lights):
                snapshot = {
                    "transform": light_data.get("transform", {}),
                    "attrs": light_data.get("attributes", {})
                }
                self.lm.apply_snapshot_to_light(target_light, snapshot)
            QMessageBox.information(self, "Load state", "Last saved state applied to selected lights.")
            return

        # Fallback: apply first saved light snapshot to all selected lights.
        first_snapshot = {
            "transform": saved_lights[0].get("transform", {}),
            "attrs": saved_lights[0].get("attributes", {})
        }
        for target_light in selected:
            self.lm.apply_snapshot_to_light(target_light, first_snapshot)
        QMessageBox.information(
            self,
            "Load state",
            "Saved state count does not match current selection. Applied first saved state to all selected lights."
        )

    def _create_backup_payload(self, snapshots):
        """Create backup payload following the publish JSON structure style."""
        return {
            "_published": datetime.now().isoformat(),
            "_asset_name": "light_manager_temp_state",
            "version": 1,
            "count": len(snapshots),
            "lights": snapshots
        }

    def cleanup_backup_file(self):
        """Delete temporary backup file when the manager closes."""
        try:
            if self._backup_temp_file.exists():
                self._backup_temp_file.unlink()
        except:
            pass


    def _on_list_selection_changed(self):
        items = self.light_list.selectedItems()
        names = [item.text() for item in items]
        valid = [n for n in names if cmds.objExists(n)]
        if valid:
            cmds.select(valid)
            self._set_ui_from_selected_light(valid[0])

    def _set_ui_from_selected_light(self, light_name):
        """Set UI attribute widgets to match the selected light's current values."""
        widgets_to_block = [
            self.intensity_slider,
            self.exposure_slider,
            self.samples_slider,
            self.temp_slider,
            self.temp_check,
            self.custom_value_slider,
        ]

        self._syncing_ui_from_selection = True
        for widget in widgets_to_block:
            widget.blockSignals(True)

        try:
            # Resolve shape node
            shape = self.lm._resolve_light_node(light_name)
            if not shape:
                return

            # Color
            try:
                color = cmds.getAttr(shape + ".color")[0]
                self.color_btn.setColor(*color)
            except Exception:
                pass

            # Intensity
            try:
                intensity = cmds.getAttr(shape + ".intensity")
                self.intensity_slider.setValue(intensity)
            except Exception:
                pass

            # Exposure
            try:
                exposure = cmds.getAttr(shape + ".aiExposure")
                self.exposure_slider.setValue(exposure)
            except Exception:
                pass

            # Samples
            try:
                samples = cmds.getAttr(shape + ".aiSamples")
                self.samples_slider.setValue(samples)
            except Exception:
                pass

            # Temperature
            try:
                temp = cmds.getAttr(shape + ".aiColorTemperature")
                self.temp_slider.setValue(temp)
            except Exception:
                pass

            # Temperature on/off
            try:
                temp_on = cmds.getAttr(shape + ".aiUseColorTemperature")
                self.temp_check.setChecked(bool(temp_on))
            except Exception:
                pass

            # Custom attribute (current combo selection)
            try:
                attr_name = self.custom_attr_combo.currentText()
                if attr_name:
                    val = cmds.getAttr(shape + "." + attr_name)
                    if isinstance(val, (list, tuple)):
                        val = val[0] if len(val) == 1 else val
                    self.custom_value_slider.setValue(val)
            except Exception:
                pass
        except Exception:
            pass
        finally:
            for widget in widgets_to_block:
                widget.blockSignals(False)
            self._syncing_ui_from_selection = False

    def _select_by_name(self):
        text = self.search_field.text().strip()
        if text:
            self.lm.select_by_name(text)

    def _on_color_changed(self, r, g, b):
        if self._syncing_ui_from_selection:
            return
        self.lm.set_color(r, g, b)

    def _randomize_intensity(self):
        base = self.intensity_slider.value()
        range_val = self.int_range_slider.value()
        self.lm.randomize_intensity(base, range_val)

    def _randomize_exposure(self):
        base = self.exposure_slider.value()
        range_val = self.exp_range_slider.value()
        self.lm.randomize_exposure(base, range_val)

    def _on_custom_value_changed(self, value):
        if self._syncing_ui_from_selection:
            return
        attr_name = self.custom_attr_combo.currentText()
        self.lm.set_custom_attr(attr_name, value)

    def _on_custom_enable_changed(self, state):
        if self._syncing_ui_from_selection:
            return
        attr_name = self.custom_attr_combo.currentText()
        self.lm.enable_disable_attr(attr_name, 1 if state else 0)

    def _key_custom_attr(self):
        attr_name = self.custom_attr_combo.currentText()
        self.lm.key_attribute("." + attr_name)

    def _delete_all_keys(self):
        attr_name = self.custom_attr_combo.currentText()
        self.lm.delete_all_keys(attr_name)

    def _set_all_attributes(self):
        r, g, b = self.color_btn.color()
        self.lm.set_all_attributes(
            self.samples_slider.value(),
            self.exposure_slider.value(),
            self.intensity_slider.value(),
            r, g, b
        )

    def _populate_lights(self):
        parent = self.parent_check.isChecked()
        light_type = self.light_type_combo.currentText()
        locator = self.locator_check.isChecked()
        self.lm.populate_lights(parent, light_type, locator)

    def _sanity_check(self):
        success, msg = self.lm.sanity_check()
        QMessageBox.information(self, "Status", msg)

        # Relaunch the full tool to guarantee a fresh UI instance.
        create_light_manager_window()

    def _delete_selected_lights(self):
        self.lm.delete_selected_lights()
        self._refresh_light_list()

    def eventFilter(self, obj, event):
        if obj == self.light_list and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                self._delete_selected_lights()
                return True
        return super().eventFilter(obj, event)


# ==================== Main Window ====================

class LightManagerWindow(_WindowBase):
    """Light Manager + standalone window - Dockable"""

    WINDOW_NAME = "LightManagerWindow"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Light Manager +")
        self.setGeometry(100, 100, 700, 650)
        self.setMinimumHeight(650)

        self.setStyleSheet(DARK_STYLESHEET)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(3)

        # Title
        title = QLabel("< LIGHT MANAGER + >")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #1A1A1A; padding: 8px;")
        main_layout.addWidget(title)

        # Content
        self.light_tab = LightManagerTab()
        main_layout.addWidget(self.light_tab)

        # Footer
        footer = QLabel("www.miguelagenjo.com")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("background-color: #1A1A1A; padding: 8px; font-size: 12px; color: #777777;")
        main_layout.addWidget(footer)

    def closeEvent(self, event):
        super().closeEvent(event)


# ==================== Application Entry Point ====================

_current_window = None


def create_light_manager_window():
    """Create the Light Manager window - ensures only one instance exists at a time"""
    global _current_window

    if not MAYA_AVAILABLE:
        print("Missing some core maya libraries import")
        return None

    app = QApplication.instance()
    if app:
        for widget in app.topLevelWidgets():
            if widget.objectName() == LightManagerWindow.WINDOW_NAME:
                try:
                    widget.close()
                    widget.deleteLater()
                except:
                    pass

    if _current_window is not None:
        try:
            _current_window.close()
            _current_window.deleteLater()
        except:
            pass
        _current_window = None

    window = LightManagerWindow()
    window.setObjectName(LightManagerWindow.WINDOW_NAME)
    window.show()

    _current_window = window

    return window


if __name__ == "__main__":
    window = create_light_manager_window()

#### Light Manager + (c) 2023
#### Miguel Agenjo, 3D Generalist/ Lighting TD
#### www.artstation.com/magenjo


#///////////////// STARTS CODE //////////////////////#


import maya.cmds as cmds
import mtoa.ui.arnoldmenu as arnoldmenu
import mtoa.utils as mutils
import random


class LightManagerFunctions: # Core functionality for Light Manager +
    
    
    # Constants
    DEFAULT_LIGHT_SET = "defaultLightSet"
    BLACK_LIST = ["exposure", "intensity", "aiSamples", "aiUserOptions", "aiFilters", 
                  "aiTranslator", "aiAov", "aiColorTemperature", "aiUseColorTemperature"]
    ARNOLD_ATTRS = ["coneAngle", "penumbraAngle", "dropoff", "decayRate"]
    RGB = ["R", "G", "B"]
    XYZ = ["X", "Y", "Z"]
    DEFAULT_VALUES = {"intensity": 1, "aiExposure": 1, "aiSamples": 1, 
                      "color": (1, 1, 1), "aiColorTemperature": 6500, "aiUseColorTemperature": 0}
    
    def __init__(self):
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
    
    @staticmethod
    def _get_slider_value(slider, is_int=False):
        """Extract value from slider widget"""
        if is_int:
            return int(cmds.intSliderGrp(slider, query=True, value=True))
        return float(cmds.floatSliderGrp(slider, query=True, value=True))
    
    @staticmethod
    def _parse_color_value(color_widget):
        """Parse color slider group value to RGB tuple"""
        raw_value = str(cmds.colorSliderGrp(color_widget, query=True, rgbValue=True))
        color_split = raw_value.split("[")[1][0:-1]
        color_rgb = color_split.split(",")
        return tuple(float(c[0:5]) for c in color_rgb)
    
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
    
    def set_color(self, color_widget):
        """Set color on all selected lights"""
        try:
            rgb = self._parse_color_value(color_widget)
            selected = self._get_selected_lights()
            for light in selected:
                try:
                    cmds.setAttr(light + ".color", *rgb)
                except:
                    pass
        except:
            pass
    
    def set_intensity(self, intensity_slider):
        """Set intensity on all selected lights"""
        try:
            intensity = self._get_slider_value(intensity_slider)
            selected = self._get_selected_lights()
            for light in selected:
                try:
                    cmds.setAttr(light + ".intensity", intensity)
                except:
                    pass
        except:
            pass
    
    def set_exposure(self, exposure_slider):
        """Set exposure on all selected lights"""
        try:
            exposure = self._get_slider_value(exposure_slider)
            selected = self._get_selected_lights()
            for light in selected:
                try:
                    cmds.setAttr(light + ".aiExposure", exposure)
                except:
                    pass
        except:
            pass
    
    def set_samples(self, samples_slider):
        """Set samples on all selected lights"""
        try:
            samples = self._get_slider_value(samples_slider, is_int=True)
            selected = self._get_selected_lights()
            for light in selected:
                cmds.setAttr(light + ".aiSamples", samples)
        except:
            pass
    
    def set_custom_attr(self, attr_menu, value_slider):
        """Set custom attribute on all selected lights"""
        try:
            attr_name = cmds.optionMenu(attr_menu, query=True, value=True)
            value = self._get_slider_value(value_slider)
            selected = self._get_selected_lights()
            for light in selected:
                try:
                    cmds.setAttr(light + "." + attr_name, value)
                except:
                    pass
        except:
            pass
    
    def set_custom_unique_attr(self, attr_name, value_slider):
        """Set specific custom attribute on all selected lights"""
        try:
            value = self._get_slider_value(value_slider)
            selected = self._get_selected_lights()
            for light in selected:
                try:
                    cmds.setAttr(light + "." + attr_name, value)
                except:
                    pass
        except:
            pass
    
    def set_all_attributes(self, samples_slider, exposure_slider, intensity_slider, color_widget):
        """Set all attributes at once"""
        self.set_samples(samples_slider)
        self.set_exposure(exposure_slider)
        self.set_intensity(intensity_slider)
        self.set_color(color_widget)
    
    def set_default_attributes(self):
        """Reset all attributes to default values"""
        selected = self._get_selected_lights()
        for light in selected:
            for attr, value in self.DEFAULT_VALUES.items():
                if attr == "color":
                    cmds.setAttr(light + ".color", *value)
                else:
                    cmds.setAttr(light + "." + attr, value)
    
    # ==================== Toggle Methods ====================
    
    def enable_disable_attr(self, attr_menu, checkbox):
        """Toggle custom attribute on/off"""
        try:
            state = cmds.checkBox(checkbox, query=True, value=True)
            attr_name = cmds.optionMenu(attr_menu, query=True, value=True)
            value = 1 if state else 0
            
            selected = self._get_selected_lights()
            for light in selected:
                try:
                    cmds.setAttr(light + "." + attr_name, value)
                except:
                    pass
        except:
            pass
    
    def enable_disable_unique_attr(self, attr_name, checkbox):
        """Toggle specific attribute on/off"""
        try:
            state = cmds.checkBox(checkbox, query=True, value=True)
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
    
    def randomize_intensity(self, intensity_slider, range_slider):
        """Set random intensity between base and range values"""
        try:
            base = self._get_slider_value(intensity_slider)
            range_val = self._get_slider_value(range_slider)
            
            selected = self._get_selected_lights()
            for light in selected:
                cmds.setAttr(light + ".intensity", random.uniform(base, range_val))
        except:
            pass
    
    def randomize_exposure(self, exposure_slider, range_slider):
        """Set random exposure between base and range values"""
        try:
            base = self._get_slider_value(exposure_slider)
            range_val = self._get_slider_value(range_slider)
            
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
    
    def key_attribute(self, attr):
        """Set keyframe on attribute"""
        try:
            selected = self._get_selected_lights()
            if "optionMenu" in attr:
                attr_name = cmds.optionMenu(attr, query=True, value=True)
                for light in selected:
                    try:
                        cmds.setKeyframe("." + attr_name)
                    except:
                        pass
            else:
                for light in selected:
                    cmds.setKeyframe(attr)
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
    
    def delete_all_keys(self, attr_menu):
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
                                # Try to disconnect custom attribute
                                try:
                                    attr_name = cmds.optionMenu(attr_menu, query=True, value=True)
                                    cmds.disconnectAttr(node + ".output", light + "." + attr_name)
                                except:
                                    pass
                                
                                # Disconnect standard attributes
                                for std_attr in attrs_to_disconnect:
                                    try:
                                        cmds.disconnectAttr(node + ".output", light + "." + std_attr)
                                    except:
                                        pass
                                
                                # Disconnect color channels
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
    
    def populate_lights(self, parent_checkbox, light_type_menu, locator_checkbox):
        """Populate lights around selected objects"""
        try:
            parent_state = cmds.checkBox(parent_checkbox, query=True, value=True)
            locator_state = cmds.checkBox(locator_checkbox, query=True, value=True)
            light_type = cmds.optionMenu(light_type_menu, query=True, value=True)
            
            selected_objs = self._get_selected_lights()
            cmds.CenterPivot(selected_objs)
            lights_created = []
            counter = 0
            
            # Create group if not parenting to original object
            group_node = None
            if not parent_state:
                group_node = cmds.group(empty=True, name=light_type + "Lgt_grp")
                cmds.setAttr(group_node + ".useOutlinerColor", 1)
                cmds.setAttr(group_node + ".outlinerColor", 1, 1, 0)
            
            for obj in selected_objs:
                if not obj.endswith("Shape"):
                    counter += 1
                    
                    # Get transform values
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
                        # Create appropriate light type
                        if light_type == "Point":
                            light_name = cmds.pointLight()
                        elif light_type == "Area":
                            light_name = cmds.shadingNode("aiAreaLight", name="aiAreaLightShape" + str(counter), asLight=True)
                        elif light_type == "Spot":
                            light_name = cmds.spotLight()
                        elif light_type == "Photometric":
                            light_name = cmds.shadingNode("aiPhotometricLight", name="aiPhotometricLightShape" + str(counter), asLight=True)
                        
                        lights_created.append(light_name)
                        
                        # Apply locator or direct transform
                        if locator_state:
                            locator = cmds.spaceLocator()[0]
                            cmds.parent(light_name, locator)
                            
                            if not parent_state:
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
                            if parent_state:
                                cmds.parent(light_name, obj)
                            
                            light_base_name = light_name.replace("Shape", "")
                            for i, coord in enumerate(pos):
                                cmds.setAttr(light_base_name + ".translate" + self.XYZ[i], coord)
                            
                            for i, coord in enumerate(rot):
                                cmds.setAttr(light_base_name + ".rotate" + self.XYZ[i], coord)
                            
                            cmds.matchTransform(light_name, obj, pos=True, rot=True, scl=True)
            
            if group_node and not locator_state:
                cmds.parent(lights_created, group_node)
        except Exception as e:
            print(f"Error populating lights: {e}")
    
    # ==================== UI Management Methods ====================
    
    def select_in_text_list(self, light_selector):
        """Select lights from text list in UI"""
        try:
            select_items = cmds.textScrollList(light_selector, query=True, selectItem=True) or []
            new_selection = [obj for obj in select_items if cmds.objExists(obj)]
            cmds.select(new_selection)
        except:
            pass
    
    def select_by_name(self, text_field):
        """Select lights by name pattern"""
        try:
            search_text = cmds.textFieldGrp(text_field, query=True, text=True)
            print(search_text)
            cmds.select("*" + search_text + "*")
            cmds.select("*Shape*", d=True)
        except:
            pass
    
    def refresh_ui(self, light_selector, lights_found_text):
        """Refresh light list in UI"""
        try:
            cmds.textScrollList(light_selector, e=True, removeAll=True)
            total_lights_list = self.get_total_lights_list()
            cmds.textScrollList(light_selector, e=True, append=total_lights_list)
            cmds.text(lights_found_text, e=True, label="               Lights: " + str(len(total_lights_list)))
        except:
            cmds.textScrollList(light_selector, e=True, removeAll=True)
            cmds.text(lights_found_text, e=True, label="               Lights: 0")
    
    def delete_selected_lights(self, light_selector, lights_found_text):
        """Delete selected lights and refresh UI"""
        try:
            selected = self._get_selected_lights()
            cmds.delete(selected)
            self.refresh_ui(light_selector, lights_found_text)
        except:
            pass
    
    def sanity_check(self):
        """Validate and fix light names with issues"""
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
            
            cmds.confirmDialog(title="Status", message='Sanity check passed successfully!\nLights renamed with unique id')
        except:
            pass


# ==================== Functions Wrappers ====================

_light_manager = LightManagerFunctions()

def getValuesExisting():
    return _light_manager.get_values_existing()

def setColor(color):
    _light_manager.set_color(color)

def browse_PhotometryFile():
    _light_manager.browse_photometry_file()

def browse_file():
    _light_manager.browse_color_file()

def setIntensity(intensity):
    _light_manager.set_intensity(intensity)

def setExposure(exposure):
    _light_manager.set_exposure(exposure)

def setSamples(samples):
    _light_manager.set_samples(samples)

def setCustom(attr, value):
    _light_manager.set_custom_attr(attr, value)

def setCustomUnique(attr, value):
    _light_manager.set_custom_unique_attr(attr, value)

def enableDisable(attr, checkbox):
    _light_manager.enable_disable_attr(attr, checkbox)

def enableDisableUnique(attr, checkbox):
    _light_manager.enable_disable_unique_attr(attr, checkbox)

def randomColor():
    _light_manager.random_color()

def selectByName(text):
    _light_manager.select_by_name(text)

def randomizeExpo(exposure, range_exp):
    _light_manager.randomize_exposure(exposure, range_exp)

def randomizeInt(intensity, range_int):
    _light_manager.randomize_intensity(intensity, range_int)

def keyAttr(attr):
    _light_manager.key_attribute(attr)

def disconnectFiles():
    _light_manager.disconnect_files()

def deleteAllKeys(attr_menu):
    _light_manager.delete_all_keys(attr_menu)

def setAllAttributes(samples, exposure, intensity, color):
    _light_manager.set_all_attributes(samples, exposure, intensity, color)

def byDefaultAttr():
    _light_manager.set_default_attributes()

def meshLights(obj):
    _light_manager.create_mesh_light(obj)

def lightPopulate(parent_checkbox, light_type_menu, locator_checkbox):
    _light_manager.populate_lights(parent_checkbox, light_type_menu, locator_checkbox)

def selectInTextList(light_selector):
    _light_manager.select_in_text_list(light_selector)

def sanityCheck():
    _light_manager.sanity_check()

def listCustomAttr():
    return _light_manager.list_custom_attrs()

def deleteSelected(light_selector, lights_found_text):
    _light_manager.delete_selected_lights(light_selector, lights_found_text)

def refreshUI(light_selector, lights_found_text):
    _light_manager.refresh_ui(light_selector, lights_found_text)

def totalLightsF():
    return _light_manager.get_total_lights_list()

            
class LightManagerUI(): #  Main UI class for Light Manager +
    def __init__(self):
        self.window = "LightManagerPlus"
        self.selected = cmds.ls(selection=True)
        self.getLights = totalLightsF()
        self.totalLightslist = self.getLights
        self.totalLights = len(self.getLights)
    
    def createUI(self):
        """Create the main UI window and all its components"""
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)
        
        cmds.window(self.window, width=780, height=600, bgc=[0.2, 0.2, 0.2], sizeable=True)
        cmds.scrollLayout(childResizable=True)
        layout = cmds.columnLayout(adjustableColumn=True)
        
        # Main Title
        cmds.separator(4)
        cmds.text(label="", bgc=[0.1, 0.1, 0.1])
        cmds.text(label="<  LIGHT MANAGER + >", fn="boldLabelFont", width=80, bgc=[0.1, 0.1, 0.1])
        cmds.text(label="", bgc=[0.1, 0.1, 0.1])
        
        # Light creation shelf
        cmds.separator(4)
        cmds.text(label="Utils Shelf", h=20, bgc=[0.3, 0.3, 0.3])
        cmds.text(label="", bgc=[0.2, 0.2, 0.2], h=5)
        
        # Light selector buttons
        cmds.columnLayout(adjustableColumn=True)
        cmds.rowLayout(numberOfColumns=1)
        self.lgtsFound = cmds.text(label="             Lights: " + str(self.totalLights))
        cmds.setParent("..")
        
        cmds.columnLayout(adjustableColumn=True)
        cmds.rowLayout(numberOfColumns=2, adj=1)
        
        # Creation textScrollList
        self.lightSelector = cmds.textScrollList(numberOfRows=30, allowMultiSelection=True, h=480, w=120, 
                                                 append=self.totalLightslist, showIndexedItem=1,
                                                 selectCommand=lambda *args: selectInTextList(self.lightSelector),
                                                 dkc=lambda *args: deleteSelected(self.lightSelector, self.lgtsFound))
        cmds.columnLayout(adjustableColumn=True)
        
        cmds.rowLayout(numberOfColumns=18)
        cmds.iconTextButton(image="SVGRefresh_200.png", command=lambda *args: self.refreshUI())
        cmds.iconTextButton(image="MayaStartupDoneCheck_150.png", command=lambda *args: sanityCheck())
        cmds.text("                                 ")
        cmds.iconTextButton(image="AreaLightShelf.png", command=lambda *args: mutils.createLocator("aiAreaLight", asLight=True))
        cmds.iconTextButton(image="MeshLightShelf.png", command=lambda *args: mutils.createMeshLight())
        cmds.iconTextButton(image="PhotometricLightShelf.png", command=lambda *args: mutils.createLocator("aiPhotometricLight", asLight=True))
        cmds.iconTextButton(image="SkydomeLightShelf.png", command=lambda *args: mutils.createLocator("aiSkyDomeLight", asLight=True))
        cmds.iconTextButton(image="PhysicalSkyShelf.png", command=lambda *args: arnoldmenu.doCreatePhysicalSky())
        cmds.iconTextButton(image="directionallight.png", command=lambda *args: cmds.directionalLight())
        cmds.iconTextButton(image="pointlight.png", command=lambda *args: cmds.pointLight())
        cmds.iconTextButton(image="spotlight.png", command=lambda *args: cmds.spotLight())
        cmds.iconTextButton(image="TXManagerShelf.png", command=lambda *args: arnoldmenu.arnoldTxManager())
        cmds.iconTextButton(image="RenderViewShelf.png", command=lambda *args: arnoldmenu.arnoldOpenMtoARenderView())
        cmds.iconTextButton(image="menuIconWindow.png", command=lambda *args: cmds.NodeEditorWindow())
        
        cmds.setParent("..")
        cmds.separator(4)
        cmds.text(label="", h=2)
        cmds.columnLayout(adjustableColumn=True)
        cmds.rowLayout(numberOfColumns=4)
        
        cmds.button(label="Select All Lights", command=lambda *args: cmds.select("defaultLightSet"), w=135, h=40, bgc=[0, 0.5, 0.3])
        cmds.text("                ")
        self.searchByName = cmds.textFieldGrp(changeCommand=lambda *args: selectByName(self.searchByName))
        cmds.button(label="Select by name", command=lambda *args: selectByName(self.searchByName))
        
        cmds.setParent("..")
        cmds.text(label="", h=2)
        cmds.separator(4)
        
        # Light Populate Tab
        cmds.text(label="Light Populator", h=20, bgc=[0.3, 0.3, 0.3])
        cmds.text(label="", bgc=[0.2, 0.2, 0.2], h=5)
        cmds.rowLayout(numberOfColumns=5)
        
        self.lightType = cmds.optionMenu(label='    Light Type:', bgc=[0.3, 0.3, 0.3], h=30)
        cmds.menuItem(label='Point')
        cmds.menuItem(label='Area')
        cmds.menuItem(label='Spot')
        cmds.menuItem(label='Mesh Light')
        cmds.menuItem(label='Photometric')
        
        self.checkerBox = cmds.checkBox(label="Parent to Object", value=0)
        self.checkerBox2 = cmds.checkBox(label="Locator", value=1)
        cmds.button(label="Populate", command=lambda *args: lightPopulate(self.checkerBox, self.lightType, self.checkerBox2))
        cmds.setParent("..")
        cmds.text(label="", bgc=[0.2, 0.2, 0.2], h=3)
        cmds.separator(4)
        
        # Attributes Tab
        cmds.text(label="Light Attributes", h=20, bgc=[0.3, 0.3, 0.3])
        cmds.text(label="", bgc=[0.2, 0.2, 0.2])
        
        # Color slider
        cmds.rowLayout(numberOfColumns=6)
        
        self.colorPicker = cmds.colorSliderGrp(label="Color     ", changeCommand=lambda *args: setColor(self.colorPicker), w=325)
        cmds.button(label="Key", command=lambda *args: keyAttr(".color"), bgc=[0.3, 0.1, 0.1])
        cmds.button(label="Browse File", command=lambda *args: browse_file(), bgc=[0.3, 0.3, 0.3])
        cmds.iconTextButton(image="fpe_brokenPaths.png", command=lambda *args: disconnectFiles())
        cmds.button(label="Random", command=lambda *args: randomColor())
        cmds.setParent("..")
        
        # Temperature slider
        cmds.rowLayout(numberOfColumns=6)
        self.tempSlider = cmds.floatSliderGrp(label="Temperature (K)     ", field=True, value=6500, max=15000, 
                                              changeCommand=lambda *args: setCustomUnique("aiColorTemperature", self.tempSlider), w=325)
        self.checkerBox4 = cmds.checkBox(label="on/off", value=0, 
                                         changeCommand=lambda *args: enableDisableUnique("aiUseColorTemperature", self.checkerBox4))
        cmds.setParent("..")
        
        # IES Light path
        cmds.rowLayout(numberOfColumns=5)
        
        cmds.text("               Photometric File     ")
        cmds.button(label="Browse File", command=lambda *args: browse_PhotometryFile(), bgc=[0.3, 0.3, 0.3])
        cmds.setParent("..")
        
        
        # Intensity slider
        cmds.rowLayout(numberOfColumns=5)
        
        self.intensitySlider = cmds.floatSliderGrp(label="Intensity     ", value=getValuesExisting()[0],
                                                    changeCommand=lambda *args: setIntensity(self.intensitySlider), 
                                                    field=True, w=325)
        cmds.button(label="Key", command=lambda *args: keyAttr(".intensity"), bgc=[0.3, 0.1, 0.1])
        self.rangeSlider1 = cmds.floatSliderGrp(field=True, w=170)
        cmds.button(label="Random", command=lambda *args: randomizeInt(self.intensitySlider, self.rangeSlider1))
        cmds.setParent("..")
        
        # Exposure slider
        cmds.rowLayout(numberOfColumns=5)
        
        self.expSlider = cmds.floatSliderGrp(label="Exposure     ", field=True, value=getValuesExisting()[1],
                                             changeCommand=lambda *args: setExposure(self.expSlider), w=325)
        cmds.button(label="Key", command=lambda *args: keyAttr(".aiExposure"), bgc=[0.3, 0.1, 0.1])
        self.rangeSlider = cmds.floatSliderGrp(field=True, w=170)
        cmds.button(label="Random", command=lambda *args: randomizeExpo(self.expSlider, self.rangeSlider))
        cmds.setParent("..")
        
        # Samples slider
        cmds.rowLayout(numberOfColumns=2)
        
        self.sampleSlider = cmds.intSliderGrp(label="Samples     ", value=getValuesExisting()[2], field=True,
                                              maxValue=10, changeCommand=lambda *args: setSamples(self.sampleSlider),
                                              w=325)
        cmds.button(label="Key", command=lambda *args: keyAttr(".aiSamples"), bgc=[0.3, 0.1, 0.1])
        cmds.setParent("..")
        
        # Custom attr slider
        cmds.rowLayout(numberOfColumns=6)
        
        cmds.text("            ")
        self.custonName = cmds.optionMenu(label="Custom attribute   ", bgc=[0.25, 0.25, 0.25], h=30, w=220)
        try:
            for j in listCustomAttr():
                cmds.menuItem(label=j, parent=self.custonName)
        except:
            "TypeError"
        self.checkerBox3 = cmds.checkBox(label="on/off", value=1, 
                                         changeCommand=lambda *args: enableDisable(self.custonName, self.checkerBox3))
        self.valueSlider = cmds.floatSliderGrp(value=1, field=True, 
                                               changeCommand=lambda *args: setCustom(self.custonName, self.valueSlider),
                                               w=180, max=500)
        cmds.button(label="Key", command=lambda *args: keyAttr(self.custonName), bgc=[0.3, 0.1, 0.1])
        cmds.setParent("..")
        
        # Delete Keys
        cmds.text(label="", bgc=[0.2, 0.2, 0.2])
        cmds.separator(4)
        cmds.rowLayout(numberOfColumns=4)
        cmds.button(label="Set Default", bgc=[0.3, 0.3, 0.3], h=20, command=lambda *args: byDefaultAttr())
        cmds.button(label="Delete All Keys", bgc=[0.3, 0.3, 0.3], h=20,
                    command=lambda *args: deleteAllKeys(self.custonName))
        cmds.setParent("..")
        
        # Set all button
        cmds.separator(4)
        cmds.button(label="Set All Selected", bgc=[0.3, 0.3, 0.3], h=30,
                    command=lambda *args: setAllAttributes(self.sampleSlider, self.expSlider, 
                                                           self.intensitySlider, self.colorPicker))
        
        cmds.separator(1)
        cmds.text(label="", bgc=[0.2, 0.2, 0.2])
        cmds.text(label="Miguel Agenjo - www.artstation.com/magenjo", bgc=[0.2, 0.2, 0.2])
        cmds.setParent("..")
        
        cmds.showWindow(self.window)
    
    def refreshUI(self):
        """Refresh the light list in the UI"""
        refreshUI(self.lightSelector, self.lgtsFound)


if __name__ == "__main__":
    launcher = LightManagerUI()
    launcher.createUI()


#///////////////// ENDS CODE //////////////////////#
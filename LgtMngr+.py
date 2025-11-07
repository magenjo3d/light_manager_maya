#### Light Manager + (c) 2023
#### Miguel Agenjo, 3D Generalist/ Lighting TD
#### www.artstation.com/magenjo






#///////////////// STARTS CODE //////////////////////#


import maya.cmds as cmds
import mtoa.ui.arnoldmenu as arnoldmenu
import random
import mtoa.utils as mutils

## Get values for existing lights

def getValuesExisting():
    
    IES = [1.0,0.0,1]
    try:
        cmds.select("defaultLightSet")
        selected = cmds.ls(selection = True)
        if selected:
            
            intensity = cmds.getAttr(selected[0]+".intensity")
            exposure = cmds.getAttr(selected[0]+".aiExposure")
            samples = cmds.getAttr(selected[0]+".aiSamples")

            IES = [intensity, exposure, samples]
            cmds.select("defaultLightSet", d = True)
            return IES
            
            
    except:
        "TypeError"

    return  IES


## Set color method

def setColor(Color):
    
    selected = cmds.ls(selection = True)
    ####### get color values operations ######
    getColorRawValue = str(cmds.colorSliderGrp(Color, query=True, rgbValue=True))
    getColorSplit = getColorRawValue.split("[")[1][0:-1]
    getColorRGB = getColorSplit.split(",")
    ############################### 
     
    for light in selected:
        try:
            cmds.setAttr(light + ".color", float(getColorRGB[0][0:5]),float(getColorRGB[1][0:5]),float(getColorRGB[2][0:5]))
        except:
            "RuntimeError"

## Browse and set a file path

def browse_PhotometryFile():
    
    file_path = cmds.fileDialog2(fileMode=1, caption="Select File", fileFilter="All Files (*.*)")[0]
    selected = cmds.ls(selection = True)
    if file_path:
        for lgt in selected:
            shapes = cmds.listRelatives(lgt)
            cmds.setAttr(shapes[0] + '.aiFilename', file_path, type='string')
            

            
def browse_file():
    
    file_path = cmds.fileDialog2(fileMode=1, caption="Select File", fileFilter="All Files (*.*)")[0]
    selected = cmds.ls(selection = True)
    if file_path:
        file_node = cmds.shadingNode('file', asTexture=True)

        for lgt in selected:
            cmds.setAttr(file_node + '.fileTextureName', file_path, type='string')
            cmds.connectAttr(file_node + '.outColor', lgt + '.color')


## Set intensity method

def setIntensity(Intensity):
    
    getIntensity = float(cmds.floatSliderGrp(Intensity, query=True, value=True))
    selected = cmds.ls(selection = True)
    
    for light in selected:
        try:
            cmds.setAttr(light + ".intensity", getIntensity)
        except:
            pass


## Set exposure method

def setExposure(Exposure):
    
    getExposure = float(cmds.floatSliderGrp(Exposure, query=True, value=True))
    selected = cmds.ls(selection = True)
    
    for light in selected:
        try:
            cmds.setAttr(light + ".aiExposure", getExposure)
        except:
            pass

## Set samples method

def setSamples(Samples):
    
    getIndexSamples = int(cmds.intSliderGrp(Samples, query=True, value=True))
    selected = cmds.ls(selection = True)
    
    for light in selected:
        cmds.setAttr(light + ".aiSamples", getIndexSamples)


## Set custom attr method

def setCustom(attr, value):
    
    getTextFieldName = cmds.optionMenu(attr, query=True, value=True)
    getValue = float(cmds.floatSliderGrp(value, query=True, value=True))
    
    selected = cmds.ls(selection = True)
    
    for light in selected:
        try:
            cmds.setAttr(light + "." + getTextFieldName, getValue)
        except:
            "RuntimeError"
            

## Set Unique Custom attr

def setCustomUnique(attr, value):
    
    
    getValue = float(cmds.floatSliderGrp(value, query=True, value=True))
    
    selected = cmds.ls(selection = True)
    
    for light in selected:
        try:
            cmds.setAttr(light + "." + attr, getValue)
        except:
            "RuntimeError"


def enableDisable(attr,checkerBox):
    
    checkerBoxState = cmds.checkBox(checkerBox, query=True, value=True)
    getTextFieldName = cmds.optionMenu(attr, query=True, value=True)
    selected = cmds.ls(selection = True)
    if checkerBoxState is True:
        for light in selected:
            try:
                cmds.setAttr(light + "." + getTextFieldName, 1)
            except:
                "RuntimeError"
            
    else:
        for light in selected:
            try:
                cmds.setAttr(light + "." + getTextFieldName, 0)
            except:
                "RuntimeError"
    
    
def enableDisableUnique(attr,checkerBox):
    
    checkerBoxState = cmds.checkBox(checkerBox, query=True, value=True)
    selected = cmds.ls(selection = True)
    if checkerBoxState is True:
        for light in selected:
            try:
                cmds.setAttr(light + "." + attr, 1)
            except:
                "RuntimeError"
            
    else:
        for light in selected:
            try:
                cmds.setAttr(light + "." + attr, 0)
            except:
                "RuntimeError"    
    

## Random color method

def randomColor():
    
    selected = cmds.ls(selection = True)
    for light in selected:
        
        randR = random.uniform(0,1)
        randG = random.uniform(0,1)
        randB = random.uniform(0,1)
        try:
            cmds.setAttr(light + ".color", randR,randG,randB)
        except:
            "RuntimeError"

## Selection by name method

def selectByName(text):
    
    getTextFieldName = cmds.textFieldGrp(text, query=True, text=True)
    print(getTextFieldName)
    cmds.select("*"+getTextFieldName+"*")
    cmds.select("*Shape*", d = True) 

## Random Exposure method  
  
def randomizeExpo(Exposure, rangeExp):
    
    getExposicion = float(cmds.floatSliderGrp(Exposure, query=True, value=True))
    getExpRange = float(cmds.floatSliderGrp(rangeExp, query=True, value=True))

    selected = cmds.ls(selection = True)
    for light in selected:
        
        cmds.setAttr(light + ".aiExposure", random.uniform(getExposicion, getExpRange))


## Random intensity method

def randomizeInt(Intensity, rangeInt):
    
    getIntensity = float(cmds.floatSliderGrp(Intensity, query=True, value=True))
    getRange = float(cmds.floatSliderGrp(rangeInt, query=True, value=True))

    selected = cmds.ls(selection = True)
    for light in selected:
        
        cmds.setAttr(light + ".intensity", random.uniform(getIntensity, getRange))

## Set animation keyframe on attribute

def keyAttr(attr):
    
    selected = cmds.ls(selection = True)
    if "optionMenu" in attr:
        getTextFieldName = cmds.optionMenu(attr, query=True, value=True)
        for lgt in selected:
            try:
                cmds.setKeyframe("."+getTextFieldName)
            except:
                "ValueError"
    else:
        
        for lgt in selected:
            cmds.setKeyframe(attr)
     
## disconnects files from color

def disconnectFiles():
    
    selected = cmds.ls(selection = True)
    for lgt in selected:
        attrConnected = cmds.listRelatives(lgt)
        connection = cmds.listConnections(attrConnected)
        
        for i in connection:

            try:
                cmds.disconnectAttr(i+".outColor", lgt+".color")
            except:
                pass

## Delete all animation keys

def deleteAllKeys(custonName):
    
    selected = cmds.ls(selection = True)
    for lgt in selected:
        attrConnected = cmds.listRelatives(lgt)
        connection = cmds.listConnections(attrConnected)
        
        for i in connection:
            if "_" in i:
                
                RGB = ["R","G","B"]
                try:
                    getTextFieldName = cmds.optionMenu(custonName, query=True, value=True)
                    cmds.disconnectAttr(i+".output", lgt+"."+getTextFieldName)
                except:
                    "ValueError"
                
                try:
                    cmds.disconnectAttr(i+".output", lgt+".exposure")
                except:
                    "RuntimeError"
                try:
                    cmds.disconnectAttr(i+".output", lgt+".aiExposure")
                except:
                    "RuntimeError"
                try:
                    cmds.disconnectAttr(i+".output", lgt+".intensity")
                except:
                    "RuntimeError"
                
                for c in RGB:
                    try:

                        cmds.disconnectAttr(i[0:-1]+c+".output", lgt+".color"+c)
                                    
                    except:
                        "RuntimeError"

                    try:
                        
                        cmds.disconnectAttr(i+".output", lgt+".color.color"+c)
                
                    except:
                        "RuntimeError"
                    
                try:
                    cmds.disconnectAttr(i+".output", lgt+".aiSamples")
                except:
                    "RuntimeError"
                    
    print("Animation Keys deleted")                

## Set all attributes

def setAllAttributes(Samples, Exposure, Intensity, Color):
    
    setSamples(Samples)
    setExposure(Exposure)
    setIntensity(Intensity)
    setColor(Color)
    

def byDefaultAttr():
    
    selected = cmds.ls(selection = True)
    for lgt in selected:
        cmds.setAttr(lgt + ".intensity", 1)
        cmds.setAttr(lgt + ".aiExposure", 1)
        cmds.setAttr(lgt + ".aiSamples", 1)
        cmds.setAttr(lgt + ".color", 1,1,1)
           
            
## Light populate

def meshLights(obj):
    
    meshTransform = obj
    shs = cmds.listRelatives(meshTransform, fullPath=True)
    meshShape = shs[0]
    lightName = cmds.shadingNode("aiMeshLight", n = meshTransform + "_MeshLightShape", asLight= True)
        

    cmds.connectAttr('%s.outMesh' % meshShape, '%s.inMesh' % lightName)

    p = cmds.parent(lightName, meshTransform, relative=True)
    lightShape = cmds.listRelatives(p[0], shapes=True, fullPath=True)[0]
    cmds.connectAttr('%s.showOriginalMesh' % lightShape, '%s.visibility' % meshShape)

    cmds.setAttr('%s.showOriginalMesh' % lightShape, 1)
    cmds.setAttr('%s.showOriginalMesh' % lightShape, 0)


def lightPopulate(checkerBox, lightType, checkerBox2):
    
    checkerBoxState = cmds.checkBox(checkerBox, query=True, value=True)
    checkerBoxState2 = cmds.checkBox(checkerBox2, query=True, value=True)
    
    lgtTypeMenu = cmds.optionMenu(lightType, query=True, value=True)
        
    selectedObjts = cmds.ls(selection = True)
    cmds.CenterPivot(selectedObjts)
    selectedLight = min(cmds.ls(selection = True))[:-1]
    lightsCreated = []
    y = 0
    
    if checkerBoxState is False:
        groupNode = cmds.group(empty = True, name = lgtTypeMenu + "Lgt_grp")
        
        cmds.setAttr(groupNode + ".useOutlinerColor", 1)
        cmds.setAttr(groupNode + ".outlinerColor", 1,1,0)
       
    for obj in selectedObjts:
        print(obj)
        if not obj.endswith("Shape"):
            posX = cmds.getAttr(obj + ".translateX")
            posY = cmds.getAttr(obj + ".translateY")
            posZ = cmds.getAttr(obj + ".translateZ")
            
            rotX = cmds.getAttr(obj + ".rotateX")
            rotY = cmds.getAttr(obj + ".rotateY")
            rotZ = cmds.getAttr(obj + ".rotateZ")
            
            posXYZ = [posX, posY, posZ]
            rotXYZ = [rotX, rotY, rotZ]
            XYZ = ["X","Y","Z"]
            n = 0
            y = y + 1
                   
            if lgtTypeMenu == "Mesh Light":
                meshLights(obj)
                try:
                    cmds.delete(groupNode)
                except:
                    pass
            else:
                if lgtTypeMenu == "Point":
                    LightName = cmds.pointLight()
               
                elif lgtTypeMenu == "Area":
                    LightName = cmds.shadingNode("aiAreaLight", name = "aiAreaLightShape"+str(y), asLight = True)
                
                elif lgtTypeMenu == "Spot":
                    LightName = cmds.spotLight()
                
                elif lgtTypeMenu == "Photometric":
                    LightName = cmds.shadingNode("aiPhotometricLight", name = "aiPhotometricLightShape"+str(y), asLight = True)
                
                lightsCreated.append(LightName)
              
               
               
                if checkerBoxState2 is True:
                    locator = cmds.spaceLocator()[0]
                    cmds.parent(LightName, locator) 
                    
                    if checkerBoxState is False:
                        cmds.parent(locator, groupNode)
                    else:
                        cmds.parent(locator, obj)
                        
                    for coords in posXYZ:
                        cmds.setAttr(locator + ".translate" + XYZ[n], coords) 
                        n = n+1
                        
                    n = 0    
                    for coords in rotXYZ:
                        cmds.setAttr(locator + ".rotate" + XYZ[n], coords) 
                        n = n+1
                    cmds.matchTransform(locator, obj,pos = True, rot = True, scl = True)
                    cmds.rename(locator, LightName.replace("Shape","") + "_locator")
                
                else:
                    
                    if checkerBoxState is True:
                        cmds.parent(LightName, obj)
                        
                   
                    for coords in posXYZ:
                        cmds.setAttr(LightName.replace("Shape","") + ".translate" + XYZ[n], coords) 
                        n = n+1
                        
                    n = 0    
                    for coords in rotXYZ:
                        cmds.setAttr(LightName.replace("Shape","") + ".rotate" + XYZ[n], coords) 
                        n = n+1
                    cmds.matchTransform(LightName, obj,pos = True, rot = True, scl = True)
    if checkerBoxState2 is False:
        cmds.parent(lightsCreated, groupNode)


def selectInTextList(lightSelector):
    
    selectItems = cmds.textScrollList(lightSelector, query=True, selectItem=True) or []
    
    newSelection = [obj for obj in selectItems if cmds.objExists(obj)]
    
    cmds.select(newSelection)
    
    selectIp = cmds.ls(newSelection)
 
    
def sanityCheck():
    
    allLgtList = cmds.listRelatives("defaultLightSet")
    failed = []
    n = 1
    
    for i in range(0, len(allLgtList)):
        try:
            
            cmds.select(allLgtList[i].replace("Shape",""))
        except:
            if "ValueError":
                failed.append(allLgtList[i].replace("Shape",""))
           
                print(allLgtList[i].replace("Shape","") + " Sanity check")
    
      
    for lgt in failed:
        
        mcObj = cmds.ls(lgt)
        cmds.rename(mcObj[0], lgt+ "_"+ str(n))
        n = n + 1
    
    
    cmds.confirmDialog(title="Status", message='Sanity passed sucessfully!')
    createUI()
        
        
def listCustomAttr():

    sel = cmds.ls("defaultLightSet")
    shapes = cmds.listRelatives(sel, shapes = True)
    try:
        attr = cmds.listAttr(shapes)
    
        blackList = ["exposure", "intensity", "aiSamples", "aiUserOptions", "aiFilters", "aiTranslator", "aiAov", "aiColorTemperature", "aiUseColorTemperature"]

        listaAttrArnold = ["coneAngle","penumbraAngle","dropoff", "decayRate"]
        for i in attr:
            if i.startswith("ai") and i not in blackList and i not in listaAttrArnold:
                
                listaAttrArnold.append(i)
        listaAttrArnold.sort()
        return(listaAttrArnold)
    except:
        "TypeError"
        print("WARNING! Rename your lights")
    
def deleteSelected(lightSelector,lgtsFound):
    
    selected = cmds.ls(selection = True)
    cmds.delete(selected)
    refreshUI(lightSelector,lgtsFound)
        
def refreshUI(lightSelector,lgtsFound):
    
    cmds.textScrollList(lightSelector, e=True, removeAll=True)
    try:
        totalLights = len(cmds.listRelatives("defaultLightSet"))
        lgtSet = cmds.select("defaultLightSet") 
        totalLightslist = sorted(cmds.ls(selection = True))
        cmds.select("defaultLightSet", d = True)
    except:
        totalLights = 0
        totalLightslist=[]
        
    cmds.textScrollList(lightSelector, e=True, append=totalLightslist)
    cmds.text(lgtsFound,e = True,label = "               Lights: "+ str(totalLights))
    cmds.select("defaultLightSet", d = True)
    

def totalLightsF():
    
    try:
        totalLights = len(cmds.listRelatives("defaultLightSet"))
        lgtSet = cmds.select("defaultLightSet") 
        totalLightslist = sorted(cmds.ls(selection = True))
        cmds.select("defaultLightSet", d = True)
    except:
        totalLights = 0
        totalLightslist=[]
    
    return totalLightslist             

################ CREATE UI ################
def createUI():
    
    ## Variables   
    selected = cmds.ls(selection = True)
    
    getLights = totalLightsF()
    totalLightslist = getLights
    totalLights = len(getLights)     
     
    window = "LightManagerPlus"

    if cmds.window(window, exists=True):
        cmds.deleteUI(window)
    
    cmds.window(window, width=500, height=475,bgc = [0.2,0.2,0.2], sizeable = True)
    cmds.scrollLayout(childResizable=True)
    layout = cmds.columnLayout(adjustableColumn = True)
    
    ## Main Title 
    cmds.separator(4)
    cmds.text(label="",bgc= [0.1,0.1,0.1])
    cmds.text(label="<  LIGHT MANAGER + >",fn = "boldLabelFont", width=80, bgc= [0.1,0.1,0.1])
    cmds.text(label="",bgc= [0.1,0.1,0.1])
    
    ## Light creation shelf   
    cmds.separator(4)
    cmds.text(label="Utils Shelf", h = 20,  bgc= [0.3,0.3,0.3])
    cmds.text(label="",bgc= [0.2,0.2,0.2], h = 5)


    ## Light selector buttons  
    
    cmds.columnLayout(adjustableColumn = True)
    cmds.rowLayout(numberOfColumns = 1)
    lgtsFound = cmds.text(label = "             Lights: "+ str(totalLights))
    cmds.setParent("..")
    


    cmds.columnLayout(adjustableColumn = True)
    
    cmds.rowLayout(numberOfColumns = 2, adj = 1) 
    
    #creation textScrollList
    lightSelector = cmds.textScrollList(numberOfRows=30, allowMultiSelection=True, h =480,w = 120, append=totalLightslist,
    showIndexedItem=1, selectCommand=lambda *args: selectInTextList(lightSelector), dkc=lambda *args: deleteSelected(lightSelector, lgtsFound))    
    cmds.columnLayout(adjustableColumn = True)
 
    cmds.rowLayout(numberOfColumns = 18)
    cmds.iconTextButton(image = "SVGRefresh_200.png", command=lambda *args: refreshUI(lightSelector, lgtsFound))
    cmds.iconTextButton(image = "MayaStartupDoneCheck_150.png", command=lambda *args: sanityCheck())
    cmds.text("                                 ")
    cmds.iconTextButton(image = "AreaLightShelf.png", command=lambda *args:  mutils.createLocator("aiAreaLight", asLight=True))
    cmds.iconTextButton(image = "MeshLightShelf.png", command=lambda *args:  mutils.createMeshLight())
    cmds.iconTextButton(image = "PhotometricLightShelf.png", command=lambda *args: mutils.createLocator("aiPhotometricLight", asLight=True))
    cmds.iconTextButton(image = "SkydomeLightShelf.png", command=lambda *args:  mutils.createLocator("aiSkyDomeLight", asLight=True) )
    cmds.iconTextButton(image = "PhysicalSkyShelf.png", command=lambda *args:   arnoldmenu.doCreatePhysicalSky() )
    cmds.iconTextButton(image = "directionallight.png", command=lambda *args: cmds.directionalLight() )
    cmds.iconTextButton(image = "pointlight.png", command=lambda *args: cmds.pointLight())
    cmds.iconTextButton(image = "spotlight.png" , command=lambda *args: cmds.spotLight())
    cmds.iconTextButton(image = "TXManagerShelf.png", command=lambda *args: arnoldmenu.arnoldTxManager())
    cmds.iconTextButton(image = "RenderViewShelf.png", command=lambda *args: arnoldmenu.arnoldOpenMtoARenderView())
    cmds.iconTextButton(image = "menuIconWindow.png", command=lambda *args: cmds.NodeEditorWindow())
    
    cmds.setParent("..") 
    cmds.separator(4)
    cmds.text(label = "", h = 2)
    cmds.columnLayout(adjustableColumn = True)
    cmds.rowLayout(numberOfColumns = 4)
    
    cmds.button(label = "Select All Lights", command=lambda *args: cmds.select("defaultLightSet"), w= 135,h = 40, bgc=[0,0.5,0.3])
    cmds.text("                ")
    searchByName = cmds.textFieldGrp(changeCommand =lambda *args:selectByName(searchByName))
    cmds.button(label = "Select by name", command=lambda *args: selectByName(searchByName))
    
    cmds.setParent("..") 
    cmds.text(label="", h = 2)
    cmds.separator(4)
    
        
    ## ***********LIGHT POPULATE TAB**********
    
    cmds.text(label="Light Populator", h = 20,  bgc= [0.3,0.3,0.3])
    cmds.text(label="",bgc= [0.2,0.2,0.2], h = 5)
    cmds.rowLayout(numberOfColumns = 5)

    lightType = cmds.optionMenu( label='    Light Type:', bgc = [0.3,0.3,0.3], h = 30)
    cmds.menuItem( label='Point' )
    cmds.menuItem( label='Area' )
    cmds.menuItem( label='Spot' )
    cmds.menuItem( label='Mesh Light' )
    cmds.menuItem( label='Photometric' )
      
    checkerBox = cmds.checkBox(label = "Parent to Object", value = 0)
    checkerBox2 = cmds.checkBox(label = "Locator", value = 1)
    cmds.button(label = "Populate", command=lambda *args: lightPopulate(checkerBox, lightType, checkerBox2))
    cmds.setParent("..") 
    cmds.text(label="",bgc= [0.2,0.2,0.2], h = 3)
    cmds.separator(4)
    
    ## ********ATTRIBUTES TAB***********
    
    cmds.text(label="Light Attributes", h = 20,  bgc= [0.3,0.3,0.3])
    cmds.text(label="",bgc= [0.2,0.2,0.2])
    
    ## Color slider  
    cmds.rowLayout(numberOfColumns = 6)
    
    colorPicker = cmds.colorSliderGrp(label = "Color     ", changeCommand =lambda *args: setColor(colorPicker), w = 325)
    cmds.button(label = "Key", command =lambda *args: keyAttr(".color"), bgc = [0.3,0.1,0.1])
    """cmds.iconTextButton(image = "out_simplexNoise_150.png", command=lambda *args: setNoiseColor())""" ### UNUSED 
    cmds.button(label="Browse File", command =lambda *args:browse_file(),  bgc = [0.3,0.3,0.3])
    cmds.iconTextButton(image = "fpe_brokenPaths.png", command=lambda *args: disconnectFiles())
    cmds.button(label = "Random", command=lambda *args: randomColor())
    cmds.setParent("..") 
    
    ## Temperature slider  
    cmds.rowLayout(numberOfColumns = 6)
    tempSlider = cmds.floatSliderGrp(label = "Temperature (K)     ", field = True, value = 6500, max = 15000, changeCommand =lambda *args: setCustomUnique("aiColorTemperature", tempSlider), w = 325)
    checkerBox4 = cmds.checkBox(label = "on/off", value = 0, changeCommand =lambda *args: enableDisableUnique("aiUseColorTemperature",checkerBox4))
    cmds.setParent("..") 
    
    ## IES Light path   
    cmds.rowLayout(numberOfColumns = 5)
    
    cmds.text("               Photometric File     ")
    cmds.button(label="Browse File", command =lambda *args:browse_PhotometryFile(),  bgc = [0.3,0.3,0.3])
    cmds.setParent("..") 
    
    
    ## Intensity slider
    cmds.rowLayout(numberOfColumns = 5)

    intensitySlider = cmds.floatSliderGrp(label = "Intensity     ", value = getValuesExisting()[0] , changeCommand =lambda *args: setIntensity(intensitySlider), field = True, w = 325)
    cmds.button(label = "Key", command =lambda *args: keyAttr(".intensity"), bgc = [0.3,0.1,0.1])
    rangeSlider1 = cmds.floatSliderGrp(field = True, w = 170)
    cmds.button(label = "Random", command=lambda *args: randomizeInt(intensitySlider, rangeSlider1))
    cmds.setParent("..")
    
    ## Exposure slider
    cmds.rowLayout(numberOfColumns = 5) 

    expSlider = cmds.floatSliderGrp(label = "Exposure     ", field = True, value = getValuesExisting()[1], changeCommand =lambda *args: setExposure(expSlider), w = 325)
    cmds.button(label = "Key", command =lambda *args: keyAttr(".aiExposure"), bgc = [0.3,0.1,0.1])
    rangeSlider = cmds.floatSliderGrp(field = True, w = 170)
    cmds.button(label = "Random", command=lambda *args: randomizeExpo(expSlider, rangeSlider))
    cmds.setParent("..")

    ## Samples slider
    cmds.rowLayout(numberOfColumns = 2)   
    
    sampleSlider = cmds.intSliderGrp(label = "Samples     ", value = getValuesExisting()[2], field = True,maxValue = 10, changeCommand =lambda *args: setSamples(sampleSlider),w = 325)
    cmds.button(label = "Key", command =lambda *args: keyAttr(".aiSamples"), bgc = [0.3,0.1,0.1])
    cmds.setParent("..")

    ## Custom attr slider
    cmds.rowLayout(numberOfColumns = 6) 
    
    cmds.text("            ")
    custonName = cmds.optionMenu( label="Custom attribute   ", bgc = [0.25,0.25,0.25], h = 30, w = 220)
    try:     
        for j in listCustomAttr():
            
            cmds.menuItem( label= j, parent = custonName)
    except:
        "TypeError"
    checkerBox3 = cmds.checkBox(label = "on/off", value = 1, changeCommand =lambda *args: enableDisable(custonName,checkerBox3))
    valueSlider = cmds.floatSliderGrp( value = 1, field = True, changeCommand =lambda *args: setCustom(custonName, valueSlider), w = 180, max = 500)
    cmds.button(label = "Key", command =lambda *args: keyAttr(custonName), bgc = [0.3,0.1,0.1])
    cmds.setParent("..")


    ## Delete Keys
    cmds.text(label="",bgc= [0.2,0.2,0.2])
    cmds.separator(4)
    cmds.rowLayout(numberOfColumns = 4)
    cmds.button(label = "Set Default", bgc = [0.3,0.3,0.3], h = 20,command=lambda *args: byDefaultAttr())
    cmds.button(label = "Delete All Keys", bgc = [0.3,0.3,0.3], h = 20,command=lambda *args: deleteAllKeys(custonName))
    cmds.setParent("..")
    

    ## Set all button
    cmds.separator(4)
    cmds.button(label = "Set All Selected", bgc = [0.3,0.3,0.3], h = 30,command=lambda *args: setAllAttributes(sampleSlider, expSlider, intensitySlider, colorPicker))
    
    
    cmds.separator(1)
    cmds.text(label="",bgc= [0.2,0.2,0.2])
    cmds.text(label="Miguel Agenjo - www.artstation.com/magenjo",bgc= [0.2,0.2,0.2])
    cmds.setParent("..")
    
    cmds.showWindow(window)

createUI()
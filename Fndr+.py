#### Light Finder + (c) 2023
#### Miguel Agenjo, 3D Generalist/ Lighting TD
#### www.artstation.com/magenjo


#------------------- ## PROJECT CUSTOM PATH HERE ## ------------------##
                    
MY_CUSTOM_PATH = r"YOUR/CUSTOM/DIRECTORY/FOLDER/HERE"                                      

#---------------------------------------------------------------------##








#///////////////// STARTS CODE //////////////////////#

import maya.cmds as cmds
import os

## global variables

getPath = cmds.workspace(q = True, rd = True) ## Get path of the current Maya project
pathSplit = getPath.split("/")
findAsset = getPath.find("maya")
pathToList = getPath[0:findAsset].split("/")
lastInList = len(pathToList)
path = MY_CUSTOM_PATH + "/"

defaultName = pathToList[lastInList-2] ## Default proyect name

allPublishedLights = os.listdir(str(path))
listVersions = []
print(allPublishedLights)

## Selection by name method

def selectByName(text):
    
    getTextFieldName = cmds.textFieldGrp(text, query=True, text=True)
    print(getTextFieldName)
    cmds.select("*"+getTextFieldName+"*")  
    
    cmds.select("*Shape*", d = True) 
      
## Search for latest version existing (if not, creates v1)
      
def getExsistingVersion(publishPath): 

    try:
        try:
            listVersions = map(int,os.listdir(publishPath))
            
        except:
           
           if "WindowsError": 
            
            return False
            
        else:
                    
            lastVersionInFolder = max(listVersions)
            
            return lastVersionInFolder
    
    except:
        "ValueError"
            
## from "getExistingVersion()", creates version folder and returns it
       
def createVersionFolder(publishPath): 
     
    LastFolderVersion = getExsistingVersion(publishPath)
    
    if LastFolderVersion is False:
    
        cmds.sysFile(publishPath + "/1", makeDir = True)
        folderForFile = publishPath + "/1"
        
    else:
        
        cmds.sysFile(publishPath + "/" + str(int(LastFolderVersion)+1), makeDir = True)
        folderForFile = publishPath + "/" + str(int(LastFolderVersion)+1)
        print(folderForFile)
    
    
    return folderForFile
    
## from "createVersionFolder()" gets folder path and write the publication inside

def publishFile(publishPath, getTextFieldName):  

    activeSelection = cmds.ls(selection = True)
       
    if activeSelection:
        
        for sel in activeSelection:
            cmds.setAttr(sel + ".useOutlinerColor", 1)
            cmds.setAttr(sel + ".outlinerColor", 0,1,1)
        
        result= cmds.confirmDialog(title = "Publishing", message = "Continue publishing?", button = ["Continue", "Cancel"])
            
        if result == "Continue":
        
            filePath = createVersionFolder(publishPath)
            try: 
                cmds.file(filePath + "/"+ getTextFieldName + ".mb" , exportSelected = True, type= "mayaBinary", f = True)
            except:
                cmds.file(filePath + "/"+ getTextFieldName , exportSelected = True, type= "mayaAscii")
            
            cmds.confirmDialog(title="Publisher", message="     Version published!     " ,bgc=[0.2, 0.2, 0.2])
         
            refreshUI()
            print("New version published")   
    else:
        
        cmds.confirmDialog(title="Error", message="     Nothing is currently selected!     ", bgc=[0.2, 0.2, 0.2])
        
## get folder name from textfield to publish

def getFolderName(textFieldName):
    
    getTextFieldName = cmds.textField(textFieldName, query=True, text=True)
    publishPath = path + str(getTextFieldName)
    
    publishFile(publishPath, getTextFieldName)
    
## To load version (imports .ma file )

def loadVersion(selectedAsset, version, r):  
    
    global path
    lights = []
    nVersionSelected = cmds.optionMenu(version, query=True, value=True)
    refImport = cmds.optionMenu(r, query=True, value=True)
    
    
    assetPath = path + selectedAsset
    try:
        lastFichPath = assetPath + "/" + str(nVersionSelected) + "/" +selectedAsset +".mb"
    except:
        lastFichPath = assetPath + "/" + str(nVersionSelected) + "/" +selectedAsset +".ma"
    
    if refImport == "import":
        cmds.file(lastFichPath, i =True)
    else:
        cmds.file(lastFichPath, r =True)
    
            
    cmds.confirmDialog(title="Status", message="     Version loaded!        " ,bgc=[0.2, 0.2, 0.2])
    
## get all versions from published assets/lighting
   
def getLastVersion(assetName): 
    
    try:
        allPublishedVersions = map(int,os.listdir(path + assetName))
        if allPublishedVersions == []:
            return "None"
        
        else:
        
            return max(allPublishedVersions)
            
    except:
        "ValueError"
        
## shows path of publications    
    
def showPath(selectedAsset,lastVersion): 
    
    lastVersionPath = path + selectedAsset + "/" + str(lastVersion) 
    copyAction = cmds.confirmDialog(title='Published path', message= lastVersionPath, button = ["Copy path","Cancel"])
    
    if copyAction == "Copy path":
        os.system('echo ' + lastVersionPath.strip() + '| clip')
    

## Refresh UI

def refreshUI():
    
    cmds.deleteUI("FindrPlus")
    
    
# Define a function to update the textField

def update_textfield(m):
    selected_item = cmds.optionMenu(m, query=True, value=True)
    cmds.textField(textFieldName, edit=True, text=selected_item)
        
########## Window UI #############

def createUI():
    
    global textFieldName
    window1 = "FindrPlus"


    if cmds.window(window1, exists=True):
        cmds.deleteUI(window1)

    
    cmds.window(window1, h = 305,width=350, bgc = [0.2,0.2,0.2], sizeable = False)
        
    cmds.shelfTabLayout()
    
    cmds.setParent( '..' )

    layout = cmds.rowColumnLayout("Publisher")

    
    cmds.separator(4)
    cmds.text(label="",bgc= [0.1,0.1,0.1])
    cmds.text(label="< PUBLISHER  >",fn = "boldLabelFont",w = 350, h=15, bgc= [0.1,0.1,0.1])
    cmds.text(label="",bgc= [0.1,0.1,0.1])
    cmds.separator(1)
    cmds.text(label="")
    cmds.text(label="1. Select the items for publishing",fn = "boldLabelFont", h=15)
    cmds.text(label="2. Insert a custom name for your publication version",fn = "boldLabelFont", h=15)
    
    cmds.text(label="Careful! The naming must be the same in order to increment version",fn = "obliqueLabelFont", h=25)
    cmds.text(label="")
    cmds.separator(1)

    cmds.rowLayout(numberOfColumns = 3)
    cmds.text(" Publishing Name ") 

    # Create a textField
    textFieldName = cmds.textField()
    cmds.textField(textFieldName, edit=True, w = 150)
    
    # Create an optionMenu
    menu_selector = cmds.optionMenu(w = 111)
    for name in allPublishedLights:
        
        cmds.menuItem(label=name, parent=menu_selector)
 
    # Add a callback to the optionMenu
    cmds.optionMenu(menu_selector, edit=True, changeCommand=lambda *args: update_textfield(menu_selector))
    cmds.setParent("..")   
    
    cmds.separator(1)
    cmds.rowLayout(numberOfColumns = 3)    
    cmds.button(label = "Select All Lights", command=lambda *args: cmds.select("defaultLightSet"), h = 25, bgc=[0,0.5,0.5])
    searchByName = cmds.textFieldGrp(changeCommand =lambda *args:selectByName(searchByName), w = 150)
    cmds.button(label = "Select by name", command=lambda *args: selectByName(searchByName))
    cmds.setParent("..")     
    cmds.separator(1)
    cmds.button(label = "Publish",command=lambda *args: getFolderName(textFieldName),h = 45, bgc=[0.3,0.5,0.3])    
    
    cmds.separator(1)
    cmds.text(label="",bgc= [0.2,0.2,0.2])
    cmds.text(label="Miguel Agenjo - www.artstation.com/magenjo",bgc= [0.2,0.2,0.2])  
    cmds.setParent( '..' )
    layout = cmds.rowColumnLayout("Loader", visible = True)
    
    cmds.separator(1)
    cmds.text(label="",bgc= [0.1,0.1,0.1])
    cmds.text(label="< LOADER  >",fn = "boldLabelFont", w = 357,h=15, bgc= [0.1,0.1,0.1])
    cmds.text(label="",bgc= [0.1,0.1,0.1])
    cmds.separator(1)
    cmds.text(label="")
    
    cmds.text(label = "Select version and click on the published item to load" ,fn = "boldLabelFont") 
    
    cmds.text(label = "")
    cmds.separator(1)    
     
    for i in allPublishedLights:
        
        last_version = getLastVersion(i)
        cmds.rowLayout(numberOfColumns = 5)
        nVersion = cmds.optionMenu( label=' v:', bgc = [0.25,0.25,0.25], h = 30, w = 50)
          
        for j in range(last_version, 0, -1):
        
            cmds.menuItem( label=j )
            
        refnImport = cmds.optionMenu( bgc = [0.3,0.3,0.3], h = 30, w = 70)
        cmds.menuItem( label="import" )
        cmds.menuItem( label="reference" )
        cmds.button(label=i , command=lambda x, i=i, v=nVersion, r = refnImport: loadVersion(i, v, r), h = 30, width=200, bgc=[0.3,0.4,0.3])
        
        cmds.button(label="info", command=lambda x, i=i, v=last_version: showPath(i, v),w=30, h=30, bgc=[0.15,0.15,0.15])
        cmds.separator(2)
        cmds.setParent("..")
        cmds.separator(2)
        
    cmds.text(label="",bgc= [0.2,0.2,0.2], h = 25)
    cmds.setParent( '..' )
      
    cmds.showWindow(window1)

createUI()

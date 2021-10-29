from PIL import Image, ImageDraw, ImageFilter
import pathlib
import copy
import math
import py_compile
import os
import re
from collections import defaultdict


try:
    if not os.path.exists('Output/Nodes/Collectible Network'):
        os.makedirs('Output/Nodes/Collectible Network')
    if not os.path.exists('Output/Nodes/Individual Node'):
        os.makedirs('Output/Nodes/Individual Node')
    if not os.path.exists('Output/Nodes/ProvinceList'):
        os.makedirs('Output/Nodes/ProvinceList')
    if not os.path.exists('Output/Nodes/ProvinceMap'):
        os.makedirs('Output/Nodes/ProvinceMap')
except:
    print("Folder Creation Error.")


class TradeNode:
    name = ""
    outNodes = []
    provinces = []
    parityCheck = False
    upStream = []
    immediatelyUpstream = []
    centerProv = 0
    centerX = 0
    centerY = 0
    defaultColor = []
    def __init__(self, name):
        self.name
        self.outNodes = []
        self.provinces = []
        self.upStream = []
        self.immediatelyUpstream = []
        self.defaultColor = []
    def addOut(self, out):
        self.outNodes.append(out)
    def addProvinces (self, province):
        self.provinces.append(province)
    def addUpStream(self, node):
        self.upStream.append(node)
    def addImmediatelyUpstream(self, node):
        self.immediatelyUpstream.append(node)
    def setDefaultColor(self, rgb):
        self.defaultColor.append(rgb)
class ProvinceDefinition:
    id = 0
    red = 0
    green = 0
    blue = 0
    name = ""
    other_info = ""

doDrawLines = [True]
doRemoveWater = [True]
doShowMaps = [True]
specificNodes = []
specificNodeNetwork = [True]
doShowSingleNode = [False]
doDrawIndividualNodes = [False]
vertAssumption = [20]
indexingValue = [60]

edges = []

tmpMapColor = []
ColorLength = []
deffList = []

def getConfig():
    Config = open("config.cfg", "r", encoding='utf-8-sig')
    lineList =[]
    for line in Config:
        if line.strip().startswith("#") or line.strip() == "":
            pass
        else:
            lineList.append(line.strip())
    for line in lineList:
        if "doDrawLines" in line:
            doDrawLines.clear()
            if "T" in line.split("=")[1].upper():
                doDrawLines.append(True)
            else:
                doDrawLines.append(False)
        if "doRemoveWater" in line:
            doRemoveWater.clear()
            if "T" in line.split("=")[1].upper():
                doRemoveWater.append(True)
            else:
                doRemoveWater.append(False)
        if "doShowMaps" in line:
            doShowMaps.clear()
            if "T" in line.split("=")[1].upper():
                doShowMaps.append(True)
            else:
                doShowMaps.append(False)
        if "specificNodeNetwork" in line:
            specificNodeNetwork.clear()
            if "T" in line.split("=")[1].upper():
                specificNodeNetwork.append(True)
            else:
                specificNodeNetwork.append(False)
        if "doShowSingleNode" in line:
            doShowSingleNode.clear()
            if "T" in line.split("=")[1].upper():
                doShowSingleNode.append(True)
            else:
                doShowSingleNode.append(False)
        if "doDrawIndividualNodes" in line:
            doDrawIndividualNodes.clear()
            if "T" in line.split("=")[1].upper():
                doDrawIndividualNodes.append(True)
            else:
                doDrawIndividualNodes.append(False)
        if "vertAssumption" in line:
            vertAssumption.clear()
            tmpList = line.split("=")
            for element in tmpList:
                try:
                    float(element.strip())
                    vertAssumption.append(float(element.strip()))
                except:
                    pass
        if "indexingValue" in line:
            indexingValue.clear()
            tmpList = line.split("=")
            for element in tmpList:
                try:
                    float(element.strip())
                    indexingValue.append(float(element.strip()))
                except:
                    pass
        if "specificNodes" in line:
            specificNodes.clear()
            tmpNames = line.split("=")[1]
            nodeNames = (re.split(r'[\<\>\{\}\(\)\[\];,\s]\s*', tmpNames.strip()))
            for node in nodeNames:
                if node == "":
                    pass
                else:
                    specificNodes.append(node)
    pass


def DFS(G,v,seen=None,path=None):
    if seen is None: seen = []
    if path is None: path = [v]
   
    seen.append(v)

    paths = []

    for t in G[v]:
        if t not in seen:
            try:
                t_path=path+[t]
                paths.append(tuple(t_path))
                paths.extend(DFS(G,t,seen[:],t_path))
            except:
                print("\texception:%g\t%s"%(t))
                break
                
    return paths


def graphEdges(nodeList):
    #Define graph by edges
    #edges = [['1', '2'], ['2', '4'], ['1', '11'], ['4', '11']]

    for node in nodeList:
        for out in node.outNodes:
            print("%s - %s"%(node.name, out))
            edges.append(tuple((node.name, out)))
        print()

    #Build graph dictionary
    G = defaultdict(list)
    for (s,t) in edges:
        G[s].append(t)
        #G[t].append(s)

    # Run DFS, compute metrics
    #all_paths = [p for ps in [DFS(G, n) for n in set(G)] for p in ps]
    all_paths = []
    for node in set(G.keys()):
        print(node)
        for path in DFS(G, node):
            if not all_paths:
                all_paths.append(path)
            if len(path) >= len(all_paths[0]):
                if len(path) > len(all_paths[0]):
                    all_paths.clear()
                all_paths.append(path)
    max_len   = max(len(p) for p in all_paths)
    max_paths = [p for p in all_paths if len(p) == max_len]

    # Output
    #print("All Paths:")
    #print(all_paths)
    print("Longest Paths:")
    for p in max_paths: print("  ", p)
    print("Longest Path Length:")
    print(max_len)

def printTradeList(nodeList):
    for line in nodeList:
        print(line.name)
        for element in line.outNodes:
            print("\t"+element)
def printNode(node, nodeList):
    for line in nodeList:
        if node == line.name:
            print(line.name)
            print(line.provinces)
            for element in line.outNodes:
                print("\t"+element)
    j=0
def writeNodeHierarchy(nodeList, node, file, depth):
    for x in range(0,depth):
        file.write("\t")

    file.write("%s\n"%node)
    #print(node)
    depth +=1
    for nodeEl in nodeList:
        if nodeEl.name == node:
            #print(nodeEl.immediatelyUpstream)
            #print(len(nodeEl.immediatelyUpstream))
            if len(nodeEl.immediatelyUpstream)>0:
                for element in nodeEl.immediatelyUpstream:
                    if not element == node:
                        #print(element)
                        writeNodeHierarchy(nodeList, element, file, depth)
i=0 


def accessableTradeArea(node, nodeList):
    accessableTradeNodeList = [node]
    for accessableNodes in accessableTradeNodeList:
        for line in nodeList:
            if accessableNodes in line.outNodes:
                if line.name not in accessableTradeNodeList:
                    accessableTradeNodeList.append(line.name)
                    #print(line.name)
    return(accessableTradeNodeList)
def priviousNodesArea(node, nodeList):
    priviousNodesList = [node]
    for line in nodeList:
        if node in line.outNodes:
            if line.name not in priviousNodesList:
                priviousNodesList.append(line.name)
    while node in priviousNodesList:
        priviousNodesList.remove(node)
    return(priviousNodesList)

def centerColection(nodeName,allXY):
    tmpImage = Image.open("Output/Nodes/ProvinceMap/%s.png"%nodeName)
    drawOveride = ImageDraw.Draw(tmpImage)
    alpha = tmpImage.split()[-1]
    drawReader = alpha.load()

    xRange= range(0,tmpImage.size[0],1)
    yRange= range(0,tmpImage.size[1],1)

    for y in yRange:
        for x in xRange:
            #print(drawOveride[x,y])
            if drawReader[x,y] >100:
                #allX.append(x)
                #allY.append(y)
                allXY.append([x,y])
                #print(allXY)

i=0
def centerColection2(nodeName,nodeList,allXY):
    mapDefinition = open("Input/definition.csv")
    tmpImage = Image.open("Input/provinces.bmp")
    drawReader = tmpImage.load()

    centerProv = 0
    for node in nodeList:
        if node.name ==nodeName:
            centerProv =node.centerProv

    red=0
    green=0
    blue=0
    xRange= range(0,tmpImage.size[0],1)
    yRange= range(0,tmpImage.size[1],1)

    for province in mapDefinition:
        tmpline = province.strip().split(';')
        try:
            if int(tmpline[0].lstrip("#"))==centerProv:
                red = int(tmpline[1])
                green = int(tmpline[2])
                blue = int(tmpline[3])
                #print("%i - %i,%i,%i"%(centerProv,red,green,blue))
                break
        except:
            pass
    for y in yRange:
        for x in xRange:
            #print(drawOveride[x,y])
            if drawReader[x,y] == (red, green, blue):
                #allX.append(x)
                #allY.append(y)
                allXY.append([x,y])
                #print(allXY)
i=0


def getCenterOfWeight(nodeName, nodeList):
    allXY = []
    allXYLand = []
    centerColection(nodeName,allXYLand)
    centerColection2(nodeName,nodeList,allXY)
    sumX=0
    sumY=0
    for i in range(0,len(allXY)):
        sumX +=allXY[i][0]
        sumY +=allXY[i][1]
    try:
        sumX = int(sumX/len(allXY))
        sumY = int(sumY/len(allXY))
    except:
        pass
    print("%s: %g, %g"%(nodeName, sumX,sumY))

    notFound=0
    dist = 999999
    savedCord = [sumX,sumY]
    #check if CoM is inside of shape
    if len(allXYLand) > 0:
        for j in allXYLand:
            if sumX == j[0] and sumY == j[1]:
                notFound=0
                break
            else:
                tmpDist = math.sqrt(((sumX - j[0])**2 + (sumY - j[1])**2))
                if tmpDist <= dist:
                    #print("%g, %g"tmpDist,dist)
                    dist = tmpDist
                    savedCord[0] = j[0]
                    savedCord[1] = j[1]
                    #print(savedCord)
                notFound+=1
        #move CoM to closes point inside of shape
        if notFound > 0:
            sumX = savedCord[0]
            sumY = savedCord[1]
            print("\tMoving %s: %g, %g"%(nodeName, sumX,sumY))


    for node in nodeList:
        if node.name is nodeName:
            node.centerX = sumX
            node.centerY = sumY
            break

    

i=0
def getWater():
    waterList =[]
    indintation = 0 
    mapDefault = open("Input/default.map")
    waterSection = False
    for line in mapDefault:
        commentFound = False
        if "sea_starts" in line or "lakes" in line:
            waterSection = True
        if waterSection:
            for element in line.strip().split():
                if not commentFound:
                    try:
                        waterList.append(int(element))
                    except:
                        if "#" in element:
                            commentFound = True
                        pass
        if "{" in line:
            indintation +=1
        if "}" in line:
            indintation -=1
            waterSection = False
    #print(waterList)
    return waterList

def nodeParityCheck(node):
    tmpFile = pathlib.Path("Output/Nodes/ProvinceList/%s.txt"%node.name)
    tmpProvinceList = []
    if tmpFile.exists():
        #print("file %s found"%node.name)
        provinceList = open("Output/Nodes/ProvinceList/%s.txt"%node.name, "r", encoding='utf-8-sig')
        
        for line in provinceList:
            try:
                tmpProvinceList.append(int(line.strip()))
            except:
                pass
        if tmpProvinceList == node.provinces and node.provinces == tmpProvinceList:
            #print("%s met parity check"%node.name)
            node.parityCheck = True
        else:
            print("%s diffrent from last time will need to be redrawn"%node.name)
            node.parityCheck = False
    else:
        print("file %s Not found"%node.name)


def drawNodes(nodeList, nodeName, single):
    red = 0
    green = 0
    blue = 0
    offset = indexingValue[0] #for indexing through trade node colors
    mapDefinition = open("Input/definition.csv")
    provinceMap = Image.open("Input/provinces.bmp")
    pixOveride = provinceMap.load()
    
    xRange= range(0,provinceMap.size[0],1)
    yRange= range(0,provinceMap.size[1],1)

    tmpWater = getWater()
    if single:
        shortNodeList = [nodeName]
        remainingNodesList = shortNodeList
    else:
        shortNodeList = accessableTradeArea(nodeName, nodeList)
        remainingNodesList = accessableTradeArea(nodeName, nodeList)

    j=0
    jtotal = len(shortNodeList)
    
    #print("\n%s"%accessableTradeArea(nodeName, nodeList))

    deffList = []
    for province in mapDefinition:
        tmpline = province.strip().split(';')
        try:
            province = ProvinceDefinition()
            province.red = int(tmpline[1])
            province.id = int(tmpline[0].lstrip("#"))
            province.green = int(tmpline[2])
            province.blue = int(tmpline[3])
            province.name = tmpline[4]
            deffList.append(province)
            #print(province.name)
        except:
            pass
    colorAlt = True
    for node in nodeList:
        red +=offset
        if colorAlt:
            green +=int(offset/2)
            colorAlt = False
        else:
            blue +=int(offset/2)
            colorAlt = True
        if red>=256:
            green += offset
            red -=256
        if green>=256:
            blue +=offset
            green -=256
        if blue>=256:
            red +=int(offset/2)
            blue -=256
        tmpFile = pathlib.Path("Output/Nodes/ProvinceMap/%s.png"%node.name)
        if node.name in shortNodeList:
            nodeParityCheck(node)
        if tmpFile.exists() and node.parityCheck:
            #print("Image %s found"%node.name)
            if node.name in shortNodeList:
                j+=1
                try:
                    remainingNodesList.remove(node.name)
                except:
                    pass
        else:
            if node.name in shortNodeList:
                j+=1
                #print("%s"%remainingNodesList) 
                print("%s"%shortNodeList)
                if len(node.defaultColor) >=3:
                    print("\n%s - %s - %g/%g"%(node.name,node.defaultColor,j,jtotal))
                else:
                    print("\n%s - %g,%g,%g - %g/%g"%(node.name,red,green,blue,j,jtotal))
                tmpProvinces = copy.deepcopy(node.provinces)
                
                if doRemoveWater[0]:
                    for province in tmpWater:
                        while province in tmpProvinces:
                            print("Water Removed: %g"%province)
                            tmpProvinces.remove(province)

                drawingMap = Image.open("Input/clear.png")
                drawOveride = drawingMap.load()
                i=0
                #print(deffList)

                tupleList = []
                for prov in deffList:
                    if prov.id in tmpProvinces:
                        tupleList.append((prov.red,prov.green,prov.blue))

                #print(nodeName)
                lastY = -1
                counter = provinceMap.size[1]/10
                for y in yRange:
                    if y%232 == 0:
                        print("%i%%"%((y*10)/counter))
                    if y == provinceMap.size[1]-1:
                        print("100%")
                    for x in xRange:
                        if pixOveride[x,y] in tupleList:
                            lastY = y
                            if len(node.defaultColor) >=3:
                                drawOveride[x,y] = (node.defaultColor[0],node.defaultColor[1],node.defaultColor[2],255)
                            else:
                                drawOveride[x,y] = (int(red),int(green),int(blue),255)
                            #print(tupleList.index(pixOveride[x,y]))
                    if lastY >-1 and y > lastY + provinceMap.size[1]/vertAssumption[0]:
                        print("%i%% Likely Finished Node"%((y*100)/provinceMap.size[1]))
                        break
                    
                                    
                                
                #drawingMap.show()
                drawingMap.save("Output/Nodes/ProvinceMap/%s.png"%node.name)
                provinceList = open("Output/Nodes/ProvinceList/%s.txt"%node.name, "w", encoding='utf-8-sig')
                for province in node.provinces:
                    provinceList.write("%g\n"%province)
                provinceList.close()
                remainingNodesList.remove(node.name)
                print("\n")
    pass
def drawNodes2(nodeList, nodeName, single):
    red = 0
    green = 0
    blue = 0
    offset = indexingValue[0] #for indexing through trade node colors
    
    if not tmpMapColor:
        mapDefinition = open("Input/definition.csv")
        provinceMap = Image.open("Input/provinces.bmp")
        pixOveride = provinceMap.load()


        for province in mapDefinition:
            tmpline = province.strip().split(';')
            try:
                province = ProvinceDefinition()
                province.red = int(tmpline[1])
                province.id = int(tmpline[0].lstrip("#"))
                province.green = int(tmpline[2])
                province.blue = int(tmpline[3])
                province.name = tmpline[4]
                deffList.append(province)
                #print(province.name)
            except:
                pass

        for y in range(0,provinceMap.size[1]):
            mapLine = []
            ColorlengthLine = []
            length = 1
            color = pixOveride[0,y]
            for x in range(1,provinceMap.size[0]):
                if pixOveride[x,y] == color:
                    length+=1
                else:
                    mapLine.append(color)
                    ColorlengthLine.append(length)

                    length=1
                    color = pixOveride[x,y]

            mapLine.append(color)
            ColorlengthLine.append(length)

            tmpMapColor.append(mapLine)
            ColorLength.append(ColorlengthLine)
                    
    
    #xRange= range(0,provinceMap.size[0],1)
    #yRange= range(0,provinceMap.size[1],1)

    tmpWater = getWater()
    if single:
        shortNodeList = [nodeName]
        remainingNodesList = shortNodeList
    else:
        shortNodeList = accessableTradeArea(nodeName, nodeList)
        remainingNodesList = accessableTradeArea(nodeName, nodeList)

    j=0
    jtotal = len(shortNodeList)
    
    colorAlt = True
    for node in nodeList:
        red +=offset
        if colorAlt:
            green +=int(offset/2)
            colorAlt = False
        else:
            blue +=int(offset/2)
            colorAlt = True
        if red>=256:
            green += offset
            red -=256
        if green>=256:
            blue +=offset
            green -=256
        if blue>=256:
            red +=int(offset/2)
            blue -=256
        tmpFile = pathlib.Path("Output/Nodes/ProvinceMap/%s.png"%node.name)
        if node.name in shortNodeList:
            nodeParityCheck(node)
        if tmpFile.exists() and node.parityCheck:
            #print("Image %s found"%node.name)
            if node.name in shortNodeList:
                j+=1
                try:
                    remainingNodesList.remove(node.name)
                except:
                    pass
        else:
            if node.name in shortNodeList:
                j+=1
                #print("%s"%remainingNodesList) 
                print("%s"%shortNodeList)
                if len(node.defaultColor) >=3:
                    print("\n%s - %s - %g/%g"%(node.name,node.defaultColor,j,jtotal))
                else:
                    print("\n%s - %g,%g,%g - %g/%g"%(node.name,red,green,blue,j,jtotal))
                tmpProvinces = copy.deepcopy(node.provinces)
                
                if doRemoveWater[0]:
                    for province in tmpWater:
                        while province in tmpProvinces:
                            print("Water Removed: %g"%province)
                            tmpProvinces.remove(province)

                drawingMap = Image.open("Input/clear.png")
                drawOveride = drawingMap.load()
                i=0
                #print(deffList)

                tupleList = []
                for prov in deffList:
                    if prov.id in tmpProvinces:
                        tupleList.append((prov.red,prov.green,prov.blue))

                #print(nodeName)
                lastY = -1
                counter = len(ColorLength)/10
                for y in range(0,len(tmpMapColor)):
                    if y%232 == 0:
                        print("%i%%"%((y*10)/counter))
                    if y == len(ColorLength)-1:
                        print("100%")
                    tx=0
                    for x in range(0,len(tmpMapColor[y])):
                        if tmpMapColor[y][x] in tupleList:
                            for i in range(0,ColorLength[y][x]):
                                if len(node.defaultColor) >=3:
                                    drawOveride[tx+i,y] = (node.defaultColor[0],node.defaultColor[1],node.defaultColor[2],255)
                                else:
                                    drawOveride[tx+i,y] = (int(red),int(green),int(blue),255)
                            lastY = y
                        tx+=ColorLength[y][x]
                    if lastY >-1 and y > lastY + len(ColorLength)/vertAssumption[0]:
                        print("%i%% Likely Finished Node"%((y*100)/len(ColorLength)))
                        break
                    
                                    
                                
                #drawingMap.show()
                drawingMap.save("Output/Nodes/ProvinceMap/%s.png"%node.name)
                provinceList = open("Output/Nodes/ProvinceList/%s.txt"%node.name, "w", encoding='utf-8-sig')
                for province in node.provinces:
                    provinceList.write("%g\n"%province)
                provinceList.close()
                remainingNodesList.remove(node.name)
                print("\n")
    pass
tradeRoutes = open("Input/00_tradenodes.txt",'r',encoding='utf-8',errors='ignore')

def drawWestEast(drawingMap,drawNodeLines,x1,x2,y1,y2,yA):
    tde = drawingMap.size[0] - x1
    tdw = drawingMap.size[0] - x2
    #yA = (y1+y2)*.5#tdw/(tdw-tde)
    drawNodeLines.line((x1, y1, drawingMap.size[0], yA), fill="white", width=3)
    drawNodeLines.line((0, yA, x2, y2), fill="white", width=3)
    #print("\t\tWW1 %i,%i - %i,%i"%(x1,y1,drawingMap.size[0],yA))
    #print("\t\tWW2 %i,%i - %i,%i"%(0,yA,x2,y2))

    dx2 = x2 - 4*(drawingMap.size[0]-x1)/5
    dy2 = y2 + 4*(y1-yA)/5
    #tmpDy = yA + 4.25*(y1-yA)/5
    #tmpDy = yA + 4*(y1-yA)/5
                                
    tmpDx = drawingMap.size[0] - x2/3
    #tmpDy = yA + tmpDx*(x1-drawingMap.size[0])/(y1-yA)
    #tmpDy = yA + 4.25/5*(x1-drawingMap.size[0])/(y1-yA)
    tmpDy = yA + 4.25/5*(y1-yA)
    #print("%g, %g - %g, %g - %g"%(x1, y1, tmpDx,tmpDy,yA))
    #drawNodeLines.line((x1, y1, dx2, dy2), fill="black", width=7)

    #drawNodeLines.line((x1, y1, tmpDx, tmpDy), fill="black", width=7)
    #drawNodeLines.line((x1, y1, tmpDx, yA), fill="black", width=7)

    drawNodeLines.line((x1, y1, drawingMap.size[0], yA), fill="black", width=7)
    

def drawEastWest(drawingMap,drawNodeLines,x1,x2,y1,y2,yA):
    tde = drawingMap.size[0] - x2
    tdw = drawingMap.size[0] - x1
    #yA = (y1+y2)*.5#tde/(tde-tdw)
    drawNodeLines.line((x2, y2, drawingMap.size[0], yA), fill="white", width=3)
    drawNodeLines.line((0, yA, x1, y1), fill="white", width=3)
    #print("\t\tWE1 %i,%i - %i,%i"%(x2,y2,drawingMap.size[0],yA))
    #print("\t\tWE2 %i,%i - %i,%i"%(0,yA,x1,y1))
    #print("\t\tE %i,%i - %i,%i"%(x1,y1,dx2,dy2))

    dx2 = x2 - 4.5*(drawingMap.size[0]-x1)/5
    dy2 = y2 + 4.5*(y1-yA)/5
    #drawNodeLines.line((x1, y1, dx2, dy2), fill="black", width=7)

    #drawNodeLines.line((x1, y1, dx2, dy2), fill="black", width=7)
    #drawNodeLines.line((x1, y1, dx2, yA), fill="black", width=7)

    drawNodeLines.line((0, yA, x1, y1), fill="black", width=7)
     

def drawNetworkLines(nodeList,drawingMap,accTA):
    drawNodeLines = ImageDraw.Draw(drawingMap)
    aroundWorldWest = drawingMap.size[0]/3
    aroundWorldEast = 2*drawingMap.size[0]/3
    for node in nodeList:
        if node.name in accTA:
            for tmpUpNode in node.immediatelyUpstream:
                for node2 in nodeList:
                    if node2.name == tmpUpNode:
                        #draw line between 2 nodes
                        x1 = node.centerX
                        if x1 >drawingMap.size[0]:
                            print(x1)
                            x1 = drawingMap.size[0]
                        elif x1 <0:
                            print(x1)
                            x1 = 0
                        x2 = node2.centerX
                        if x2 >drawingMap.size[0]:
                            print(x2)
                            x2 = drawingMap.size[0]
                        elif x2 <0:
                            print(x2)
                            x2 = 0
                        y1 = node.centerY
                        if y1 >drawingMap.size[1]:
                            y1 = drawingMap.size[1]
                        elif y1 <0:
                            y1 = 0
                        y2 = node2.centerY
                        if y2 >drawingMap.size[1]:
                            y2 = drawingMap.size[1]
                        elif y2 <0:
                            y2 = 0
                        if (node2.centerX > aroundWorldEast and node.centerX < aroundWorldWest) or (node.centerX > aroundWorldEast and node2.centerX < aroundWorldWest):
                            yA = (y1+y2)*.5

                            if x1 > x2:
                                drawWestEast(drawingMap,drawNodeLines,x1,x2,y1,y2,yA)  
                                print("  %s - %s"%(node.name,node2.name))
                            else:
                                drawEastWest(drawingMap,drawNodeLines,x1,x2,y1,y2,yA)   
                                print("  %s - %s"%(node.name,node2.name))

                        else:
                            drawNodeLines.line((x1, y1, x2, y2), fill="white", width=3)
                            #draw direction
                            dx2 = x2 + 4*(x1-x2)/5
                            dy2 = y2 + 4*(y1-y2)/5
                            drawNodeLines.line((x1, y1, dx2, dy2), fill="black", width=7)
ii=0
def drawTradeNetwork(nodeList, nodeName, ShowMapAfter):
    
    #drawingMap = Image.open("Input/Province_ID_map.png")
    drawingMap = Image.open("Input/heightmap.bmp").convert('RGB')

    drawingClear = Image.open("Input/clear.png")
    #drawingClear.putalpha(0)
    #drawingClear.save("Input/clear.png")

    accTA = accessableTradeArea(nodeName, nodeList)


    
    for node in nodeList:
        if node.name in accTA:
            tmpNode = pathlib.Path("Output/Nodes/ProvinceMap/%s.png"%node.name)
            nodeParityCheck(node)
            if tmpNode.exists() and node.parityCheck:
                #print("Image %s found"%node.name)
                pass
            else:
                #drawingMap.show()
                drawNodes2(nodeList, node.name, False)
            tmpImage = Image.open("Output/Nodes/ProvinceMap/%s.png"%node.name)
            drawingMap.paste(tmpImage,(0,0),tmpImage)
            if node.centerX == 0:
                getCenterOfWeight(node.name,nodeList)
    if doDrawLines[0]:
        drawNetworkLines(nodeList,drawingMap,accTA)

    if ShowMapAfter:  
        drawingMap.show()
    drawingMap.save("Output/Nodes/Collectible Network/%s_Trade_Network.png"%nodeName, "png")

def drawSingleNode(nodeList, nodeName, ShowMapAfter):
    drawingMap = Image.open("Input/heightmap.bmp").convert('RGB')

    drawingClear = Image.open("Input/clear.png")
    #drawingClear = Image.open("Input/provinces.bmp")
    #drawingClear.putalpha(0)
    #drawingClear.save("Input/clear.png")
    for node in nodeList:
        if node.name == nodeName:
            tmpNode = pathlib.Path("Output/Nodes/ProvinceMap/%s.png"%node.name)
            nodeParityCheck(node)
            if tmpNode.exists() and node.parityCheck:
                #print("Image %s found"%node.name)
                pass
            else:
                #drawingMap.show()
                drawNodes2(nodeList, node.name, True)
            tmpImage = Image.open("Output/Nodes/ProvinceMap/%s.png"%node.name)
            drawingMap.paste(tmpImage,(0,0),tmpImage)
    if ShowMapAfter:
        drawingMap.show()
    drawingMap.save("Output/Nodes/Individual Node/%s_Trade_Node.png"%nodeName, "png")

def drawAllNodes(nodeList):
    drawingMap = Image.open("Input/heightmap.bmp").convert('RGB')

    drawingClear = Image.open("Input/provinces.bmp")
    drawingClear.putalpha(0)
    drawingClear.save("Input/clear.png")
    accTA = []
    for node in nodeList:
        accTA.append(node.name)
        tmpNode = pathlib.Path("Output/Nodes/ProvinceMap/%s.png"%node.name)
        nodeParityCheck(node)
        if tmpNode.exists() and node.parityCheck:
            #print("Image %s found"%node.name)
            print(node.name)
            pass
        else:
            drawingMap.show()
            drawNodes2(nodeList, node.name, False)
        tmpImage = Image.open("Output/Nodes/ProvinceMap/%s.png"%node.name)
        drawingMap.paste(tmpImage,(0,0),tmpImage)
        if node.centerX == 0:
            getCenterOfWeight(node.name,nodeList)

    if doDrawLines[0]:
        drawNetworkLines(nodeList,drawingMap,accTA)

    drawingMap.show()
    drawingMap.save("Output/Nodes/Full_Trade_Network.png")

try:
    getConfig()
except:
    print("Config not fould using default values")

indintation = 0 

nodeList = []
currentNode = ""
outgoingSection = False
MemberSection = False
colorSection = False
for line in tradeRoutes:
    if indintation == 0:
        if "=" in line:
            if "#" in line and line.find("#")<line.find("="):
                pass
            else:
                tmpLine = line.strip().split()
                for element in tmpLine:
                    #if "={" in element:
                        #print(line.strip().rstrip("={"))
                        #tmpTradenode = TradeNode(element.strip().rstrip("={"))
                        #tmpTradenode.name = element.strip().rstrip("={")
                        #currentNode = element.strip().rstrip("={")
                        #nodeList.append(tmpTradenode)
                    if "=" in element:
                        tmpTradenode = TradeNode(line.strip().split("=")[0].strip())
                        tmpTradenode.name = line.strip().split("=")[0].strip()
                        currentNode = line.strip().split("=")[0].strip()
                        nodeList.append(tmpTradenode)
                        #print(currentNode)
    if indintation == 1:
        #if "location=" in line:
        if line.strip().startswith("location"):
            for element in line.strip().split("="):
                try:
                    if "#" in element:
                        break
                    tmpTradenode.centerProv = int(element)
                except:
                    pass
        #if "outgoing={" in line:
        if line.strip().startswith("outgoing"):
            if "#" in line and line.find("#")<line.find("outgoing"):
                pass
            else:
                outgoingSection = True
                #tmpTradenode.addOut(next(tradeRoutes).strip().split("\"")[1])
                #print(TradeNode(currentNode).outNodes)
        #if "members={" in line or "members =" in line:
        if line.strip().startswith("members"):
            if "#" in line and line.find("#")<line.find("members"):
                pass
            else:
                MemberSection = True
        #if "color={" in line:
        if line.strip().startswith("color"):
            if "#" in line and line.find("#")<line.find("color"):
                pass
            else:
                colorSection = True
    if outgoingSection:
        if "#" in line and line.find("#")<line.find("name"):
                pass
        else:
            if line.strip().startswith("name"):
                tmpTradenode.addOut(line.split("=")[1].strip().strip("\""))
                #print(line.split("=")[1].strip().strip("\""))
    if MemberSection:
        #print(line.strip().split())
        for element in line.strip().split():
            try:
                #print(int(element))
                if "#" in element:
                    break
                tmpTradenode.addProvinces(int(element))
            except:
                pass
    if colorSection:
        #print(line.strip().split())
        for element in line.strip().split():
            try:
                #print(int(element))
                if "#" in element:
                    break
                tmpTradenode.setDefaultColor(int(element))
            except:
                pass
    if "{" in line or "}" in line:
        #print("l: "+line)
        for element in list(line.strip()):
            if "{" in element:
                indintation +=1
                #print("s: "+element)
            elif "}" in element:
                indintation -=1
                outgoingSection = False
                MemberSection = False
                colorSection = False
                #print("e: "+element)
            elif "#" in element:
                #print("c: "+element)
                break

j=0


drawingClear = Image.open("Input/provinces.bmp")
drawingClear.putalpha(0)
drawingClear.save("Input/clear.png")
drawingClear.close()

print(len(nodeList))
for node in nodeList:
    node.upStream = accessableTradeArea(node.name, nodeList)
    node.immediatelyUpstream = priviousNodesArea(node.name, nodeList)
    #print(node.upStream)

#print list of nodes upstream of input node for image updating purposes
if specificNodes:
    updateList = open("Output/Nodes/update Image List.txt", "w", encoding='utf-8-sig')
    tmpUpdateList = []
    for node in nodeList:
        for name in specificNodes:
            if name in node.upStream:
                if node.name in tmpUpdateList:
                    pass
                else:
                    #print(node.name)
                    tmpUpdateList.append(node.name)
                    updateList.write("%s\n"%node.name)
    updateList.close()
i=0

properOrder = open("Output/Nodes/Node Info.csv", "w", encoding='utf-8-sig')
properOrder.write("Node Name;Total Accessible Nodes;Number of Inputs;Number of Outputs;Total Connections;Number of Provinces\n\n")
if True:
    for x in range(0,len(nodeList)+1):
        numNodes = 0
        for node in nodeList:
            
            tmpNode = pathlib.Path("Output/Nodes/Collectible Network/%s_Trade_Network.png"%node.name)
            if len(node.upStream) == x:
                if not tmpNode.exists() and ((len(specificNodes)==0)or(node.name in specificNodes)): 
                    print("%s - %g - %g"%(node.name,x,len(node.provinces)))
                    if not specificNodes or specificNodeNetwork[0]:
                        drawTradeNetwork(nodeList,node.name, doShowMaps[0])
                    if doDrawIndividualNodes[0]:
                        drawSingleNode(nodeList,node.name, doShowSingleNode[0])
                properOrder.write("%s;%i;%i;%i;%i;%i\n"%(node.name,x,len(node.immediatelyUpstream),len(node.outNodes),(len(node.immediatelyUpstream)+len(node.outNodes)),len(node.provinces)))
                numNodes +=1
        if numNodes>0:
            print("\t%g - %g"%(numNodes,x))
            properOrder.write("\n")
properOrder.close()
if not specificNodes:
    drawAllNodes(nodeList)


if True:
    for node in nodeList:
        print(node.name)
        HierarchyFile = open("Output/Nodes/Hierarchy/%s.txt"%node.name, "w", encoding='utf-8-sig')
        writeNodeHierarchy(nodeList,node.name,HierarchyFile,0)
        HierarchyFile.close()


graphEdges(nodeList)
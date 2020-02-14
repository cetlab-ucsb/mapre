########################################################
## Produce potential maps under different constraints ##
########################################################
## Description:
## Produces the following outputs depending on the control settings:
## 1) LULC exclusion files for each technology and clipped to country boundaries; saved to input fgdb folder (will make if you ask it to)
## 2) Transmission buffers given buffer width; saved to input fgdb folder (will make buffer files only once)
## 3) shapefiles and rasters of suitable areas within countries both buffered and unbuffered using the transmission and road data
## 4) Total areas of potential as .csv file in your main OUTPUTS folder or "gdbPath" (it cannot be saved in a fgdb)
## 5) Maps for all technologies for scenario 1 and 2 thresholds. Scenario 1 threshold is common across ACEC. Scenario 2 threshold depends on the 2030 demand. 

## Tasks for user
## 1) Define country name and country abbreviation
## 2) Define "your space" and ensure that the directory structure under it matchs with the script. 
##    a) IRENA\INPUTS\Countries\"country name"
##    b) IRENA\INPUTS\    has 4 gdbs i) electricityInfrastructure.gdb ii) Environmental.gdb iii) Resources.gdb iv) technoeconomic.gdb
##    c) IRENA\OUTPUTS\"country name"
## 3) Define date
## 4) Place the 2030 demand file under INPUTS\Countries folder
## 5) Define the input files in the country csv file, and place the file under the INPUTS\Countries\"country name" folder. 
#     For country specific data, just define the file name. For default data, define the gdb folder and file name.

## "##^^" symbol symbolizes an input that requires your attention

### Preamble:
import arcpy
import os.path
import time
start_time = time.time()
print(start_time)
## Check out any necessary licenses:
arcpy.CheckOutExtension("spatial")

from arcpy import env
from arcpy.sa import *
arcpy.env.overwriteOutput = True
import arcpy.cartography as CA
# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

### Set workspace for saving outputs: create file geodatabase (fgdb) for run session outputs
country = "southAfrica"
countryAbv = "za" ##^^ set country abbreviation here for purposes of file naming
dateAnalysis = "02122020" ##^^ this date will be used to create the output database
yourSpace = "R:\\users\\anagha.uppal\\MapRE\\southAfrica.gdb\\" ##^^ This is the directory path containing all files for country being processed

### Create OUTPUT folder (with date_abb) and gdb (with date_abb)

outputFolder = yourSpace + "OUTPUTS\\" + country + "\\" + dateAnalysis + "_" + countryAbv + "\\"
print(outputFolder)
if not os.path.exists(outputFolder):
    os.makedirs(outputFolder)
    print("creating " + outputFolder)

gdbName = dateAnalysis + "_" + countryAbv + "\\" ## ^^ Name of the fgdb to store outputs 
print(gdbName)
gdbNameForCreatingFGDB = dateAnalysis + "_" + countryAbv ## ^^ here re-write the name of the file geodatabase
print(gdbNameForCreatingFGDB)
if not(os.path.exists(outputFolder + gdbName)): # Create new fgdb if one does not already exist
    print("creating fgdb " + gdbName)
    os.makedirs(outputFolder + gdbNameForCreatingFGDB)
outputFGDB = outputFolder + gdbName # sets workspace as your fgdb
print(outputFGDB)
env.scratchWorkspace = outputFGDB # sets scratchworkspace to your output workspace 
print(env.scratchWorkspace)
env.workspace = outputFGDB # sets environment workspace to your output workspace
print(env.workspace)

# set INPUT paths:
defaultInputWorkspace = yourSpace ##^^ enter the path to your DEFAULT INPUT path
countryWorkspace = defaultInputWorkspace + "Created" ##^^ enter the path to your COUNTRY INPUT fgdb here (should be countryName.fgdb)
if not(os.path.exists(countryWorkspace)): # Create new fgdb if one does not already exist
    print("creating country workspace " + countryWorkspace)
    os.makedirs(countryWorkspace)
countryBounds = defaultInputWorkspace + countryAbv + "_GADM_countryBounds" ##^^ enter the path to your COUNTRY boundary shapefile
print(countryBounds)
templateRaster = defaultInputWorkspace + "mergedDEM_GADM_500" ##^^ enter path to DEM data
print(templateRaster)

arcpy.env.snapRaster = templateRaster
arcpy.env.cellSize = templateRaster

##----------------------------------- Controls ----------------------------
## Change the following depending on wind or solar:
technologyList = ["solarPV"] ##^^ input "wind" or "solarPV" or "solarCSP" or add all for the code to loop through each technology
#"wind","solarPV", "solarCSP"
processLulc = "Yes" ##^^ "Yes" or "No" depending on whether you want to create new lulc euclidean distance exclusions
thresholdTest = "No" ##^^ "More", "Less,", "No", "All":
                        ## "No" for running the default ACEC resoure thresholds 
                        # "More" to test multiple RE resource thresholds and adjust thresholds down to achieve "More" potential
                        ## "Less" to test multiple RE resource thresholds and adjust thresholds up to achieve "Less  potential"

#----------------------------------- Process LULC data ----------------------------
# global map:
# Code   Class Name
# 1  Broadleaf Evergreen Forest
# 2  Broadleaf Deciduous Forest
# 3  Needleleaf Evergreen Forest
# 4  Needleleaf Deciduous Forest
# 5  Mixed Forest
# 6  Tree Open
# 7  Shrub
# 8  Herbaceous
# 9  Herbaceous with Sparse Tree/Shrub
# 10 Sparse vegetation
# 11   Cropland
# 12  Paddy field
# 13  Cropland / Other Vegetation Mosaic
# 14  Mangrove
# 15  Wetland
# 16  Bare area,consolidated(gravel,rock)
# 17  Bare area,unconsolidated (sand)
# 18  Urban
# 19  Snow / Ice
# 20  Water bodies

lulc_solar = 'NOT("VALUE" IN (7,8,9,10,16,17))' ##^^ choose exclusions (not(inclusions)) if you need to change them from the default for your own lulc layer
lulc_wind = 'NOT("VALUE" IN (6,7,8,9,10,16,17))' ##^^ choose exclusions (not(inclusions))
lulc_windAg = 'NOT("VALUE" IN (6,7,8,9,10,11,13,16,17))' ##^^ choose exclusions (not(inclusions))
lulc = defaultInputWorkspace + "LULC_Projected2" ##^^ put your lulc data here, if you're using country-specific lulc, if not, use default
lulcOut = countryWorkspace + "\\LULCout" ##^^ change the filename of the lulc output if using another lulc file
lulcListNames = ["_solarExclusions_500ed", "_windExclusions_500ed", "_windExclusionsAg_500ed"]
lulcList = [lulc_solar, lulc_wind, lulc_windAg]
if processLulc == "Yes":
    print("start processing lulc data")
    i = 0
    for each in lulcList:
        print("Creating " + lulcOut + lulcListNames[i])
        env.workspace = countryWorkspace
        env.scratchWorkspace = countryWorkspace
        lulc_intermediate = ExtractByAttributes(lulc, each) # select exclusions from nrsc mosaic file
        ##lulc_intermediate.save(lulc + lulcListNames[i][:-2]) # save entire ACEC file to default gdb, cause extract by mask does not work on Ranjit's arc
        ##lulc_intermediate = lulc + lulcListNames[i][:-2] # use the lulc for entire ACEC
        outExtractByMask = ExtractByMask(lulc_intermediate, countryBounds)
        outExtractByMask.save(lulcOut + lulcListNames[i][:-2])
        outED = EucDistance(outExtractByMask, "", 500, "") # get Euclidean Distance raster
        outED.save(lulcOut + lulcListNames[i])
        i = i+ 1
    print("Finished processing lulc data")
env.scratchWorkspace = outputFGDB # sets scratchworkspace to your output workspace 
env.workspace = outputFGDB # sets environment workspace to your output workspace


##-------------------------Country demand data import -----------------------------------------------
#### import 2030 demand data for the country so as to set the threshold levels for scenario 2 maps, later in the script. 
import csv
csvInput2 = r"R:\users\anagha.uppal\MapRE\demand2030.csv"
with open(csvInput2, "rt") as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    fields = next(reader)
    demandData = []
    for row in reader:
        demandData.append(dict(zip(fields, row)))
for i in range(len(demandData)):
    if demandData[i]['Country'] == country:
        demand2030 = demandData[i]['demand2030']
        print("Demand in " + country + " will be " + demand2030 + " GWh for 2030")
        break
    if i == range(len(demandData)):
        print("Country demand data not found")

## -------------------------Set local variables----------------------------

# set environments for raster analyses
arcpy.env.extent = countryBounds
arcpy.env.mask = countryBounds

### Set paths for non-technology-specific inputs (certain inputs may be blank in the csv input file due to lack of data):
## Import the csv for the country. The csv file should have the local paths for the data. Note: use single forward slashes in csv file
## If default data is used, then include path after the defaultInputWorkspace. If country specifc data is used, include the path after the countryWorkspace
import csv
csvInput = r"R:\users\anagha.uppal\MapRE\{}.csv".format(country)
with open(csvInput, "rt") as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    fields = next(reader)
    inputData = []
    for row in reader:
        inputData.append(dict(zip(fields, row)))

## inputDataPath is a list of all the input datasets, whether they exist or not for that country
inputDataPath = {'rails': "yes", 'waterArea': "no", 'waterLine': "no", 'slope': "no", 'elevation': "no", 'environmental': "no", 'environmental2': "no", 'airports': "no", 'population': "no", 'transmission': "no", 'roads': "no"}

## populate the inputDataPath for each of the data categories. 
for dataCategory in fields:
    print(dataCategory)
    if not(inputData[0][dataCategory] == "no"):
        if (inputData[1][dataCategory] == "default"):
            inputDataPath[dataCategory] = defaultInputWorkspace + inputData[2][dataCategory] ##^^ enter local path for rail file.
        elif (inputData[1][dataCategory] == "country"):
            inputDataPath[dataCategory] = countryWorkspace + inputData[2][dataCategory] ##^^ enter local path for rail file.
        else: print(dataCategory + "no data")
    print(inputDataPath[dataCategory])


rails = inputDataPath["rails"] ##^^ enter local path for rail file.
waterArea = inputDataPath["waterArea"] ##^^ enter local path for rivers file.
waterLine = inputDataPath["waterLine"] ##^^ enter local path for lakes file.
slope = inputDataPath["slope"] ##^^ enter local path for slope file.
elevation = inputDataPath["elevation"] ##^^ enter local path for elevation file.
environmental = inputDataPath["environmental"] ##^^ enter local path for environmentally protected areas.
environmental2 = inputDataPath["environmental2"] ##^^ enter local path for environmentally protected areas.
airports = inputDataPath["airports"] ##^^ enter local path for airports file.
population = inputDataPath["population"] ##^^ enter local path for population density file.
transmission = inputDataPath["transmission"] ##^^ enter local path for country's transmission file.
roads = inputDataPath["roads"] ##^^ enter local path for roads file.


### Other conditional clauses. Change as needed:
ifTrue = 1
ifFalse = 0
## basecase conditions (units are in meters)
whereClause = "Value > 500" # buffer clause (buffer 500m)
whereClauseAirports = "Value > 5000"
whereDem = "Value <= 2000" # DEM threshold in meters
wherePop = "Value <= 100"

## buffering:
buff_width = "100000 meters"
sideType = "FULL"
endType = "ROUND"
dissolveType = "ALL"

## Create transmission and road buffers for the country if they have not be previously created:
if not(arcpy.Exists(countryWorkspace + countryAbv + "_bufferedTransmission_" + buff_width[:-7])):
    print("Creating transmission buffer")
    countryTransmission = arcpy.Clip_analysis(transmission, countryBounds, "in_memory/countryTransmission")
    transBuffer = arcpy.Buffer_analysis(countryTransmission, countryWorkspace + countryAbv + "_bufferedTransmission_" + buff_width[:-7], buff_width, sideType, endType, dissolveType)
transBuffer = countryWorkspace + countryAbv + "_bufferedTransmission_" + buff_width[:-7]
# if not(arcpy.Exists(countryWorkspace + countryAbv + "_bufferedRoads_" + buff_width[:-7])):
#     print"Creating road buffer")
#     countryRoads = arcpy.Clip_analysis(roads, countryBounds, "in_memory/countryRoads")
#     roadBuffer = arcpy.Buffer_analysis(countryRoads, countryWorkspace + countryAbv + "_bufferedRoads_" + buff_width[:-7], buff_width, sideType, endType, dissolveType)
# roadBuffer = countryWorkspace + countryAbv + "_bufferedRoads_" + buff_width[:-7]


 ## Calculate the non-technology-specific conditional rasters for the data categories that may or may not have any datasets. If the data for that category does not exist, then the conditional raster variable is assigned a scalar value of 1

if not(environmental == "no"):
    environmentalCon = Con(environmental, ifTrue, ifFalse, whereClause)
 ##   arcpy.Copyraster_management(,"in_memory/")
else: environmentalCon = 1  
if not(environmental2 == "no"):
    environmental2Con = Con(environmental2, ifTrue, ifFalse, whereClause)
else: environmental2Con = 1  
if not(population == "no"):
    populationCon = Con(population, ifTrue, ifFalse, wherePop)
else: populationCon = 1  
if not(roads == "no"):
    roadsCon = Con(roads, ifTrue, ifFalse, whereClause)
else: roadsCon = 1  
if not(rails == "no"):
    railsCon = Con(rails, ifTrue, ifFalse, whereClause)
else: railsCon = 1  
if not(waterArea == "no"):
    waterAreaCon = Con(waterArea, ifTrue, ifFalse, whereClause)
else: waterAreaCon = 1  
if not(waterLine == "no"):
    waterLineCon = Con(waterLine, ifTrue, ifFalse, whereClause)
else: waterLineCon = 1  
if not(airports == "no"):
    airportsCon = Con(airports, ifTrue, ifFalse, whereClauseAirports)
else: airportsCon = 1  

### Technology-specific calculations. Entire code below this loops through the technologies in the technologyList
for tech in technologyList:
    technology = tech 

    ### set paths for technology-specific inputs:

    if technology == "wind":
        if thresholdTest == "All":
            whereResource = ["Value >= 200", "Value >= 225", "Value >= 250", "Value >= 275", "Value >= 300", "Value >= 350", "Value >= 400"]
        if thresholdTest == "More":
            whereResource = ["Value >= 275", "Value >= 250", "Value >= 225", "Value >= 200"]
        if thresholdTest == "Less":
            whereResource = ["Value >= 350", "Value >= 400"]
        if thresholdTest =="No":
            whereResource = ["Value >= 0"] ## enter resource threshold [w/m2 or m/sec]
        resource = defaultInputWorkspace + "wind_powerdensity_100m_Pr" ##^^ enter local path to resource file (either wind speed or wind power density)
        whereSlope = "Value <= 20" # slope threshold in percent
        minArea = "5"
        ##^^ enter lulc paths below:
        lulc_wind = lulcOut + "_windExclusions_500ed"## enter lulc paths 
        lulc_windAg =  lulcOut + "_windExclusionsAg_500ed" ## enter lulc paths
        lulcList = [lulc_wind , lulc_windAg]#, lulc_globCover] ## remove from list if not running all inputs

    if technology == "solarPV":
        if thresholdTest == "All":
            whereResource = ["Value >= 230", "Value >= 240", "Value >= 250", "Value >= 260", "Value >= 270"]
        if thresholdTest == "More":
            whereResource = ["Value >= 230", "Value >= 240"]
        if thresholdTest == "Less":
            whereResource = ["Value >= 260", "Value >= 270"]
        if thresholdTest =="No":
            whereResource = ["Value >= 0"]  ## enter resource threshold [w/m2 or m/sec]
        resource = defaultInputWorkspace + "GHI_Projected" ##^^ enter local path to resource file
        whereSlope = "Value <= 5" # slope threshold in percent

    if technology == "solarCSP":
        if thresholdTest == "All":
            whereResource = ["Value >= 260", "Value >= 270", "Value >= 280", "Value >= 290", "Value >= 300"]
        if thresholdTest == "More":
            whereResource = ["Value >= 270", "Value >= 260"]
        if thresholdTest == "Less":
            whereResource = ["Value >= 290", "Value >= 300"]
        if thresholdTest =="No":
            whereResource = ["Value >= 280"]## enter resource threshold for solar CSP in w/m2 (averaged per hour)
        resource = defaultInputWorkspace + "DNI_Projected" ##^^ enter local path to resource file
        whereSlope = "Value <= 5" # slope threshold in percent

    if technology == "solarPV" or technology == "solarCSP":
        minArea = "2"
        ##^^ enter lulc files below:
        lulc_wind = lulcOut + "_windExclusions_500ed"## enter lulc paths 
        lulc_solar = lulcOut + "_solarExclusions_500ed" ## enter lulc paths
        lulcList = [lulc_solar]#, lulc_globCover] ## remove from list if not running all inputs
        


    ## ---------------------------------- GEOPROCESSES FOR SITE SUITABILITY -----------------------------------
    ## These functions create binary exclusions and produce a polygon file of suitable areas


    print("Starting Resource Potential Estimates")
    areaSumList = []
    areaLabelList = []
    generationSumList = []

    ## Calculate the technology-specific conditional rasters for the data categories that may or may not have any datasets. If the data for that category does not exist, then the conditional raster variable is assigned a scalar value of 1


    outConIntermediate1 = Con(slope, ifTrue, ifFalse, whereSlope)*\
                     Con(elevation, ifTrue, ifFalse, whereDem)*\
                     environmentalCon*\
                     environmental2Con*\
                     populationCon

    for idx, each in enumerate(lulcList):
        outConIntermediate2 = outConIntermediate1 * Con(each, ifTrue, ifFalse, whereClause)
        for threshold in whereResource:
            print("Processing " + each + " " + threshold)
            env.workspace = outputFGDB
            outCon = outConIntermediate2 * Con(resource, ifTrue, ifFalse, threshold)*\
                        railsCon * waterAreaCon * waterLineCon * airportsCon
    ##                    *roadsCon  ## Road areas are not excluded

            outExtractByMask = ExtractByMask(outCon, countryBounds)
            instances = each.count("\\") # this line counts the number of "\\" in the path in order to split up the pathname
            lulcFileName = each.split('\\',instances)[-1][:-6] # This line gets just the name of the lulc file and removes the "_500ed" (use of the [-6])
            thresholdFileName = threshold[9:12]
            outExtractByMask.save(countryAbv + "_" + technology + "_" + lulcFileName + "_threshold" + str(thresholdFileName) + "_raster")
            ## Raster to polygon conversion 
            intermediate = arcpy.RasterToPolygon_conversion(outExtractByMask, "in_memory/intermediate", "NO_SIMPLIFY", "Value")
            ## Process: select gridcode = 1
            selectIntermediate = arcpy.Select_analysis(intermediate, "in_memory/selectIntermediate",'"gridcode" = 1')
            # Process: Add Field
            arcpy.AddField_management(selectIntermediate, "Area", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
            # Process: Calculate Field
            arcpy.CalculateField_management(selectIntermediate, "Area", "!Shape.Area@squarekilometers!", "PYTHON_9.3", "")
            # Process: select areas above minimum contiguous area:
            select = arcpy.Select_analysis(selectIntermediate, countryAbv + "_" + technology + "_" + lulcFileName + "_threshold" + str(thresholdFileName),'"Area" >= ' + minArea)
            # get total area of potential:
            print("Finished resource estimate, start calculating area")
            cursor = arcpy.SearchCursor(select)
            areaList = []
            generationList = []
            for row in cursor:
                area = row.getValue("Area")
                if technology == "wind":
                    generation = area*9*0.25*8760/1000  * 0.25
                if technology == "solarPV":
                    generation = area*30*0.20*8760/1000 * 0.1
                if technology == "solarCSP":
                    generation = area*30*0.20*8760/1000 * 0.1
                generationList.append(generation)
                areaList.append(area)
            areaSumList.append(sum(areaList))
            generationSumList.append(sum(generationList))
            areaLabelList.append(lulcFileName + "_" + threshold + "_noBuffer")
            # Create transmission and road buffers:
            print("Creating buffered potential")
            transPotential = arcpy.Intersect_analysis([transBuffer,select], countryAbv + "_" + technology + "_" + lulcFileName + "_threshold" + str(thresholdFileName) + "_buffered")
            ## Get resource potential within x km of transmission and roads
            ## transRoadPotential = arcpy.Intersect_analysis([transPotential,roadBuffer], countryAbv + "_" + technology + "_" + lulcFileName + "_threshold" + str(thresholdFileName) + "_buffered")
            ## get total area of potential:
            arcpy.CalculateField_management(transPotential, "Area", "!Shape.Area@squarekilometers!", "PYTHON_9.3", "")
            
            # get buffered areas (closer to transmission):
            cursor = arcpy.SearchCursor(transPotential)
            areaList = []
            generationList = []
            for row in cursor:
                area = row.getValue("Area")
                if technology == "wind":
                    generation = area*9*0.25*8760/1000 * 0.25
                if technology == "solarPV":
                    generation = area*30*0.20*8760/1000 * 0.1
                if technology == "solarCSP":
                    generation = area*30*0.20*8760/1000 * 0.1
                generationList.append(generation)
                areaList.append(area)
            areaSumList.append(sum(areaList))
            generationSumList.append(sum(generationList))
            areaLabelList.append(lulcFileName + "_" + threshold + "_buffer")
            print("Completed " + each + " " + threshold)

        #### Creating country maps for each option - technology, buffered or not, scenarios = 16
        if technology == "solarCSP":
            inRaster = defaultInputWorkspace + "DNI_Projected"
            thresholdSc1 = 280
            thresholdList = [260, 270, 280, 290, 300]
        if technology == "solarPV":
            inRaster = defaultInputWorkspace + "GHI_Projected"
            thresholdSc1 = 250
            thresholdList = [230, 240, 250, 260, 270]
        if technology == "wind":
            inRaster = defaultInputWorkspace + "wind_powerdensity_100m_Pr"
            thresholdSc1 = 300
            thresholdList = [200, 225, 250, 275, 300, 350, 400]    

        ### For scenario 2, select the threshold based on 90% of 2030 demand. 
        for j in range((len(thresholdList)*2-2),-1,-2):
            if idx > 0:
                print("wind Ag")
                break
            if generationSumList[j] > (0.9*int(demand2030)):
                thresholdSc2 = thresholdList[j//2]
                break
            thresholdSc2 = thresholdList[j//2]

        print("Threshold level for Scenario two for " + technology + " is " + str(thresholdSc2))

        ## Map with no transmission buffer for Scenario 1
        inMaskData = outputFGDB + countryAbv + "_" + technology + "_" + lulcFileName + "_threshold" + str(thresholdSc1)
        # Execute ExtractByMask
        outExtractByMask = ExtractByMask(inRaster, inMaskData)
        # Save the output 
        outExtractByMask.save(outputFGDB + countryAbv + "_MAP_" + technology + "_S1_" + lulcFileName + "_threshold" + str(thresholdSc1))

        ## Map with transmission buffer for Scenario 1
        inMaskData = outputFGDB + countryAbv + "_" + technology + "_" + lulcFileName + "_threshold" + str(thresholdSc1) + "_buffered"
        # Execute ExtractByMask
        outExtractByMask = ExtractByMask(inRaster, inMaskData)
        # Save the output 
        outExtractByMask.save(outputFGDB + countryAbv + "_MAP_" + technology + "_S1_" + lulcFileName + "_threshold" + str(thresholdSc1) + "_buffered")

        ## Map with no transmission buffer for Scenario 2
        inMaskData = outputFGDB + countryAbv + "_" + technology + "_" + lulcFileName + "_threshold" + str(thresholdSc2)
        # Execute ExtractByMask
        outExtractByMask = ExtractByMask(inRaster, inMaskData)
        # Save the output 
        outExtractByMask.save(outputFGDB + countryAbv + "_MAP_S2_" + technology + "_S2_" + lulcFileName + "_threshold" + str(thresholdSc2))

        ## Map with transmission buffer for Scenario 2
        inMaskData = outputFGDB + countryAbv + "_" + technology + "_" + lulcFileName + "_threshold" + str(thresholdSc2) + "_buffered"
        # Execute ExtractByMask
        outExtractByMask = ExtractByMask(inRaster, inMaskData)
        # Save the output 
        outExtractByMask.save(outputFGDB + countryAbv + "_MAP_S2_" + technology + "_S2_" + lulcFileName + "_threshold" + str(thresholdSc2) + "_buffered")


    del intermediate
    del outCon
    del outConIntermediate1
    del outConIntermediate2
    del outExtractByMask
    del select

    areaTable = [areaLabelList, areaSumList, generationSumList]

    import csv
    # Write Area Sums table as CSV file
    csvOutput = outputFolder + dateAnalysis + "_" + countryAbv + "_" + technology + "_" + thresholdTest + "Threshold_areaSums.csv"
    with open(csvOutput, 'w') as csvfile:
        writer = csv.writer(csvfile)
        [writer.writerow(r) for r in areaTable]

del environmentalCon
del environmental2Con
del populationCon
del roadsCon
del railsCon
del waterLineCon
del waterAreaCon
del airportsCon

elapsed_time = (time.time() - start_time)/(60)
print(str(elapsed_time) + " minutes")

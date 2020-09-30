'''
##############################################
## This script creates zones using projects ##
##############################################
'''
## Description: This script creates zones for a specified technology
## using proximity buffering and clustering analysis in R
## part b of this script aggregates the individual feature classes that
## were clustered in R and the zones that didn't require clustering
## and calculates the spatially averaged values and scores for the ranking criteria by zone

##--------------------------------Preamble ----------------------------------
import arcpy
import numpy as np
import time
import os
import subprocess
import shutil
import math
import sys  ## to delete created objects
import re  ## regular expressions
from itertools import count, product, islice
from string import ascii_uppercase

start_time = time.time()
print(start_time)

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")
from arcpy import env
from arcpy.sa import *
import arcpy.cartography as CA

arcpy.env.overwriteOutput = True
import arcpy.stats as SS

'''
################################################################################
##---------------------Local Parameters and workspace------------------------###
################################################################################
'''
##---------------------Controls----------------------------------------------
technology = "wind"  ##^^ input "wind" or "solarPV" or "solarCSP"
electricityInfrastructureType = "transmission"  ## enter "transmission", "substation", or "both"
windThreshold = "250"
solarPVthreshold = "250"
solarCSPthreshold = "280"
Ag = "yes"  # "yes" if specifying wind-ag, otherwise, "no"
# buffered = "no"
country = "southAfrica"
inputGDB = "South_Africa"
countryAbv = "sa"  ##^^ set country abbreviation here for purposes of file naming
dateAnalysis = "06022020"  ##^^ this date will be used to create the output database
# yourSpace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS"  ##^^ This is the directory path before the IRENA folder structure
# pathToRscripts = "G:\\IRENA\\PythonScripts\\"
# spatialUnit = "projects_calculated"
arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\SA_Outputs.gdb"
arcpy.env.scratchWorkspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\Scratch.gdb"
original_projects = "wind_0_suitability_areas_attr"
clustered_zones = "wind_0_skater_clustered"
fields_to_add = ["d_road", "d_water", "m_elev", "m_slope", "m_popden", "m_humfoot", "m_cf", "egen", "incap", "l_road", "l_gen"]

##---------------------Local Parameters and workspace------------------------

# workspace for saving ouptuts. set for each technology
# outputFolder = yourSpace + "\\" + country + "\\" + dateAnalysis + "_" + countryAbv + "\\"
# if not os.path.exists(outputFolder):
#     print("outputFolder does not exist. Ensure you have selected the right date's resource potential feature class")

# gdbName = dateAnalysis + "_" + countryAbv + ".gdb\\"  ## ^^ Name of the fgdb to store outputs
# gdbNameForCreatingFGDB = dateAnalysis + "_" + countryAbv + ".gdb"  ## ^^ here re-write the name of the file geodatabase
# if not (os.path.exists(outputFolder + gdbName)):  # Create new fgdb if one does not already exist
#     print(gdbName + " does not exist. Ensure you have selected the right date's resource potential feature class")

# outputFGDB = outputFolder + gdbName  # sets workspace as your fgdb
# env.scratchWorkspace = outputFGDB  # sets scratchworkspace to your output workspace
# env.workspace = outputFGDB  # sets environment workspace to your output workspace

# set input paths:
defaultInputWorkspace = r"R:\users\anagha.uppal\MapRE"  ##^^ enter the path to your DEFAULT INPUT path
countryWorkspace = defaultInputWorkspace + "\\" + inputGDB + ".gdb"  ##^^ enter the path to your COUNTRY INPUT fgdb here (should be countryName.fgdb)
countryBounds = countryWorkspace + "\\" + inputGDB + "_country_boundaries_Projected_Clipped"  ##^^ enter the path to your COUNTRY boundary shapefile
templateRaster = countryWorkspace + inputGDB + "elevation500_DEMGADM_Projected_Clipped"  ##^^ enter path to DEM data

# set environments for raster analyses
arcpy.env.snapRaster = templateRaster
arcpy.env.extent = countryBounds
arcpy.env.mask = countryBounds
arcpy.env.cellSize = templateRaster


## function to get list of all fields
def getFields(data):
    fieldList = []
    fields = arcpy.ListFields(data)
    for field in fields:
        fieldList.append(field.name)
    return fieldList


if technology == "solarPV":
    project_orig = original_projects
    projectFile = arcpy.CopyFeatures_management(project_orig, "in_memory/copiedProjects")
    projectFileName = original_projects
    ## The following are fields that should be SUMMED, NOT averaged
    excludeFromSum_dict = {"ElectGen": "ElectGen", "InstalledC": "InstalledCapacity", "ScWater": "ScWater"}

if technology == "solarCSP":
    project_orig = original_projects
    projectFile = arcpy.CopyFeatures_management(project_orig, "in_memory/copiedProjects")
    projectFileName = original_projects
    excludeFromSum_dict = {"ElectGen_0": "ElectGen_0h", "ElectGen_6": "ElectGen_6h",
                           "InstalledC": "InstalledCapacity_0h", "Installe_1": "InstalledCapacity_6h",
                           "ScWater": "ScWater"}

if technology == "wind":
    project_orig = original_projects
    projectFile = arcpy.CopyFeatures_management(project_orig, "in_memory/copiedProjects")
    projectFileName = original_projects
    excludeFromSum_dict = {"area_chose": "area_chosenClsII", "area_cho_2": "area_chosenClsI",
                           "area_cho_1": "area_chosenClsIII", "InstalledC": "InstalledCapacity",
                           "ElectGen_c": "ElectGen_chosen", "ElectGen_1": "ElectGen_clsII", "ScWater": "ScWater"}

'''
###########################################################
### Spatially average project scores/attributes by zone ###
###########################################################
'''
## get the list of clustered zones:
# *****************
# env.workspace = outputFolder  # change workspace in order to use ListFeatureClasses
# env.scratchWorkspace = env.workspace
outputList_noPath1 = arcpy.ListFeatureClasses(clustered_zones)

#################
## SMALL ZONES ##
#################

outputList_noPath2 = arcpy.ListFeatureClasses("smallZones.shp")
## Recreate GroupVal column for small zones:
# cursor = arcpy.UpdateCursor(outputFolder + outputList_noPath2[0])
# for row in cursor:
#   if row.getValue("clustered_") is None:
#     print "Addressing null values 'clustered_' column in small zones"
#     row.setValue("clustered_", 0)
#     cursor.updateRow(row)
# arcpy.CalculateField_management(outputFolder + outputList_noPath2[0], "GroupVal", "str(!ZONE_ID!) + '.' + str(int(!clustered_!))", "PYTHON_9.3")

###########
## MERGE ##
###########

## merge clustered zones with small zones:
outputList_noPath = outputList_noPath2 + outputList_noPath1

## create list of file paths (not just file names)
outputList = []
print("Merging the following: ")
for each in outputList_noPath:
    print(each)
    outputList.append(each)

deleteList = ["Name", "Name_1", "Name_12"]
for each in outputList:
    for fieldname in deleteList:
        if fieldname in getFields(each):
            arcpy.DeleteField_management(each, fieldname)
            print("Deleted field: " + fieldname)

# env.workspace = outputFGDB  # change workspace again
# env.scratchWorkspace = env.workspace

## merge the clustered zones and the small zones:
merged = arcpy.Merge_management(outputList, "in_memory/merged")

'''
###******************** RE-CALCULATE PROJECT VALUES (SCRIPT 3) ************************ 
'''

## 5. Calculations
# ^^Name of field that holds area values (km2)
projectArea = "Shape_Area" # Anagha?
largestArea = 25
# Parameters for non-wind technologies:
outageRate = 0.96
days = 365
hours = 8760
PD_CSP_0h = 30  # Power Density: MW/km2
PD_CSP_6h = 17  # Power Density: MW/km2
PD_PV = 30  # Power Density: MW/km2
effLoss_CSP = 1  # derating (loss) factor for CSP
effLoss_PV = 0.96  # derating (loss) factor for PV (includes inverter and AC wiring)
maxInsol = 1000  # w/m2 for solar
landUse_discountFactor_solar = 0.1

# Parameters for wind:
PD_wind = 9  # MW/km2
pturbine_wind = 1.65  # MW (power per turbine)
corrFactor_wind = 1.91  ## changed this from 1.95 to 1.91 on 5/20/2014
wind_losses = 0.83  ## loss and availability factor Tejen et al. 2013
landUse_discountFactor_wind = 0.25
##CF_wind <- 0.33
##bladeRadius_wind <- 35 #m
p = 1.225  # air density
##pi <- 3.14
##sweptArea_wind <- pi*bladeRadius_wind^2 #m2

# Parameters for transmission and road costs:
newTransCost = 990  # $/MW/km # modified from 3000
newSubstationCost = 71000  # per pair of substations
newRoadCost = 407000  # $/km (fromJohannessen, B. (2008) Building Rural Roads. International Labor Organization.
# from http://www.ilo.org/wcmsp5/groups/public/---asia/---ro-bangkok/documents/genericdocument/wcms_103551.pdf, pg. 69
discount = 0.10  # rate used in the tariff model
plantLifetime = 25  # years
fixedTransOMCosts = 100  # $/km/year (^^arbitrary)
fixedRoadOMCosts = newRoadCost * 0.05  # $/km/year (^^arbitrary)

# Parameters for LCOE calculations:
if technology == "wind":
    capCost_classI = 1250 * 1000
    capCost_classII = 1450 * 1000  # USD/MW
    capCost_classIII = 1700 * 1000
    variableGenOMcost = 0
    fixedGenOMcost = 60000  # $/MW
if technology == "solarCSP":
    capCost_6h = 7400 * 1000  # USD/MW ## 6 hr storage
    capCost_0h = 3700 * 1000  # USD/MW ## 0 hr storage
    variableGenOMcost = 4  # $/MWh from SAM
    fixedGenOMcost = 50000  # $/MW


# Calculate CF from DNI for CSP using empirical function (from SAM simulations using African weather data and 3 US data points)
def CSPcfCalc_0h(DNI):  ## for 0h storage
    DNIconverted_0h = DNI * (365 * 24 / 1000)
    CF_0h = (22.193 * math.log(DNIconverted_0h) - 145.69) / 100  # to make it a fraction
    return CF_0h


def CSPcfCalc_6h(DNI):  ## for 6h storage
    DNIconverted_6h = DNI * (365 * 24 / 1000)
    CF_6h = (33.431 * math.log(DNIconverted_6h) - 212.57) / 100  # to make it a fraction
    return CF_6h


CRF = (discount * (1 + discount) ** plantLifetime) / (
            ((1 + discount) ** plantLifetime) - 1)  # or the fixed charge factor
cursor = arcpy.UpdateCursor(merged)

##########################
## RECALCULATE FOR WIND ##
##########################

if technology == "wind":
    # fieldList = ["TransCost_chosen", "SubCost_chosen", "RoadCost_chosen"]
    # for each in fieldList:
    #   print "Adding " + each + " as new field"
    #   arcpy.AddField_management(merged, each, "DOUBLE")

    for row in cursor:
        area = row.getValue(projectArea)
        areaRatio = area / largestArea
        roadDist = row.getValue("NEAR_Road") / 1000  # to convert from m to km
        CF_chosen = row.getValue("CF_chosen")
        CF_ClsII = row.getValue("CF_ClsII")
        print(str(CF_chosen) + " and " + str(CF_ClsII))

        if row.getValue("area_cho_2") is None:
            area_clsI = 0
        else:
            area_clsI = row.getValue("area_cho_2")

        if row.getValue("area_chose") is None:
            area_clsII = 0
        else:
            area_clsII = row.getValue("area_chose")

        if row.getValue("area_cho_1") is None:
            area_clsIII = 0
        else:
            area_clsIII = row.getValue("area_cho_1")

        if row.getValue("CF_chose_2") is None:
            CF_clsI = 0
        else:
            CF_clsI = row.getValue("CF_chose_2")

        if row.getValue("CF_chosenC") is None:
            CF_clsII = 0
        else:
            CF_clsII = row.getValue("CF_chosenC")

        if row.getValue("CF_chose_1") is None:
            CF_clsIII = 0
        else:
            CF_clsIII = row.getValue("CF_chose_1")

        sum_windArea = area_clsI + area_clsII + area_clsIII
        turbineClasses = {area_clsI: [capCost_classI, CF_clsI], \
                          area_clsII: [capCost_classII, CF_clsII], \
                          area_clsIII: [capCost_classIII, CF_clsIII]}
        turbineClasses_LCOE = []

        for each in turbineClasses:
            proportion = each / sum_windArea
            if proportion == 0:
                LCOEgen = 0
            else:
                LCOEgen = (turbineClasses[each][0] * CRF + fixedGenOMcost) / (
                            8760 * turbineClasses[each][1]) + variableGenOMcost
            turbineClasses_LCOE.append(proportion * LCOEgen)
        LCOEgen_chosen = sum(turbineClasses_LCOE)
        LCOEgen_clsII = (capCost_classII * CRF + fixedGenOMcost) / (hours * CF_ClsII)

        capacity = PD_wind * area * landUse_discountFactor_wind

        ElectGen_chosen = capacity * CF_chosen * hours
        ElectGen_clsII = capacity * CF_ClsII * hours

        roadCost = (newRoadCost * CRF) * roadDist / (CF_chosen * 50 * hours)

        if "RoadCost_c" in getFields(merged):
            row.setValue("RoadCost_c", roadCost)
        else:
            row.setValue("RoadCost", roadCost)

        row.setValue("ElectGen_c", ElectGen_chosen)
        row.setValue("ElectGen_1", ElectGen_clsII)
        row.setValue("LCOEgen_ch", LCOEgen_chosen)
        row.setValue("LCOEgen_cl", LCOEgen_clsII)
        row.setValue("InstalledC", capacity)

        LCOEtotTrans_List = {"LCOEtotTra": [CF_chosen, LCOEgen_chosen, ElectGen_chosen],
                             "LCOEtotT_1": [CF_ClsII, LCOEgen_clsII, ElectGen_clsII]}

        if electricityInfrastructureType == "transmission" or electricityInfrastructureType == "both":
            transDist = row.getValue("NEAR_Trans") / 1000  # to convert from m to km
            for each in LCOEtotTrans_List:
                transCost = (newTransCost * transDist + newSubstationCost) * CRF / (LCOEtotTrans_List[each][0] * hours)
                roadCost = (newRoadCost * CRF) * roadDist / (LCOEtotTrans_List[each][0] * 50 * hours)
                LCOEtotTrans = LCOEtotTrans_List[each][1] + roadCost + transCost
                row.setValue(each, LCOEtotTrans)
            if "TransCost_" in getFields(merged):
                transField = "TransCost_"
            else:
                transField = "TransCost"
            row.setValue(transField, (newTransCost * transDist + newSubstationCost) * CRF / (
                        CF_chosen * hours))  ## calculate the "TransCost" using the chosen turbine"

        LCOEtotSub_List = {"LCOEtotSub": [CF_chosen, LCOEgen_chosen, ElectGen_chosen],
                           "LCOEtotS_1": [CF_ClsII, LCOEgen_clsII, ElectGen_clsII]}

        if electricityInfrastructureType == "substation" or electricityInfrastructureType == "both":
            subDist = row.getValue("NEAR_Sub") / 1000
            for each in LCOEtotSub_List:
                subCost = (newTransCost * subDist + newSubstationCost) * CRF / (LCOEtotSub_List[each][0] * hours)
                roadCost = (newRoadCost * CRF) * roadDist / (LCOEtotSub_List[each][0] * 50 * hours)
                LCOEtotSub = LCOEtotSub_List[each][1] + roadCost + subCost
                row.setValue(each, LCOEtotSub)
            if "SubCost_ch" in getFields(merged):
                subField = "SubCost_ch"
            else:
                subField = "SubCost"
            row.setValue(subField, (newTransCost * subDist + newSubstationCost) * CRF / (
                        CF_chosen * hours))  ## calculate the "SubCost" using the chosen turbine"
        cursor.updateRow(row)

    # deleteFields = ["TransCost", "SubCost", "RoadCost"]
    # for field in deleteFields:
    #   if field in getFields(merged):
    #     arcpy.DeleteField_management(merged, field)

#########################
## RECALCULATE FOR CSP ##
#########################

if technology == "solarCSP":
    # fieldList = ["TransCost_6h", "SubCost_6h", "RoadCost_6h"]
    # for each in fieldList:
    #   print "Adding " + each + " as new field"
    #   arcpy.AddField_management(merged, each, "DOUBLE")

    for row in cursor:
        RQ_row = row.getValue("RQ_Wm2")
        area = row.getValue(projectArea)
        areaRatio = area / largestArea
        roadDist = row.getValue("NEAR_Road") / 1000  # to convert from m to km

        CF_0h = effLoss_CSP * CSPcfCalc_0h(RQ_row)
        CF_6h = effLoss_CSP * CSPcfCalc_6h(RQ_row)
        print(str(CF_0h) + " and " + str(CF_6h))

        # ElectGen = CF * PD_CSP(MW/km2) * Area(km2) * 8760 hours
        capacity_0h = PD_CSP_0h * area * landUse_discountFactor_solar  ## in MW
        capacity_6h = PD_CSP_6h * area * landUse_discountFactor_solar  ## in MW

        ElectGen_0h = capacity_0h * CF_0h * hours  # MWh
        ElectGen_6h = capacity_6h * CF_6h * hours  # MWh

        # LCOE of generation: LCOEgen = (capital cost*CRF)/(8760 hours * 0.001 kW to MW * CF) + variable OM
        LCOEgen_0h = (capCost_0h * CRF + fixedGenOMcost) / (8760 * CF_0h) + variableGenOMcost
        LCOEgen_6h = (capCost_6h * CRF + fixedGenOMcost) / (8760 * CF_6h) + variableGenOMcost

        roadCost = (newRoadCost * CRF) * roadDist / (CF_6h * 50 * hours)

        if "RoadCost_6" in getFields(merged):
            row.setValue("RoadCost_6", roadCost)
        else:
            row.setValue("RoadCost", roadCost)

        # Add calculations to fields:
        row.setValue("CF_0h", CF_0h)
        row.setValue("CF_6h", CF_6h)
        row.setValue("ElectGen_0", ElectGen_0h)
        row.setValue("ElectGen_6", ElectGen_6h)
        row.setValue("LCOEgen_0h", LCOEgen_0h)
        row.setValue("LCOEgen_6h", LCOEgen_6h)
        row.setValue("InstalledC", capacity_0h)
        row.setValue("Installe_1", capacity_6h)

        # Calculate Transmission and/or Substation connection costs: TransCost = [newTransCost + fixed OM ($/MW/km)] * transDist(km) * CRF/ (8760*CF) [=] $/MWh

        LCOEtotTrans_List = {"LCOEtotTra": [CF_0h, LCOEgen_0h, ElectGen_0h],
                             "LCOEtotT_1": [CF_6h, LCOEgen_6h, ElectGen_6h]}

        if electricityInfrastructureType == "transmission" or electricityInfrastructureType == "both":
            transDist = row.getValue("NEAR_Trans") / 1000  # to convert from m to km
            for each in LCOEtotTrans_List:
                transCost = (newTransCost * transDist + newSubstationCost) * CRF / (LCOEtotTrans_List[each][0] * hours)
                roadCost = (newRoadCost * CRF) * roadDist / (LCOEtotTrans_List[each][0] * 50 * hours)
                LCOEtotTrans = LCOEtotTrans_List[each][1] + roadCost + transCost
                row.setValue(each, LCOEtotTrans)
            if "TransCost_" in getFields(merged):
                transField = "TransCost_"
            else:
                transField = "TransCost"
            row.setValue(transField, (newTransCost * transDist + newSubstationCost) * CRF / (
                        CF_6h * hours))  ## calculate the "TransCost" using the chosen turbine"

        LCOEtotSub_List = {"LCOEtotSub": [CF_0h, LCOEgen_0h, ElectGen_0h],
                           "LCOEtotS_1": [CF_6h, LCOEgen_6h, ElectGen_6h]}

        if electricityInfrastructureType == "substation" or electricityInfrastructureType == "both":
            subDist = row.getValue("NEAR_Sub") / 1000
            for each in LCOEtotSub_List:
                subCost = (newTransCost * subDist + newSubstationCost) * CRF / (LCOEtotSub_List[each][0] * hours)
                roadCost = (newRoadCost * CRF) * roadDist / (LCOEtotSub_List[each][0] * 50 * hours)
                LCOEtotSub = LCOEtotSub_List[each][1] + roadCost + subCost
                row.setValue(each, LCOEtotSub)
            if "SubCost_6h" in getFields(merged):
                subField = "SubCost_6h"
            else:
                subField = "SubCost"
            row.setValue(subField, (newTransCost * subDist + newSubstationCost) * CRF / (
                        CF_6h * hours))  ## calculate the "SubCost" using the chosen turbine"
        cursor.updateRow(row)

    # deleteFields = ["TransCost", "SubCost", "RoadCost"]
    # for field in deleteFields:
    #   if field in getFields(merged):
    #     arcpy.DeleteField_management(merged, field)

'''
###******************** RETURN TO ZONE AGGREGATION CALCULATIONS ************************ 
'''
################
## ADD FIELDS ##
################
# add fields to hold zone averages
print(merged)
print("Here")
## GET LIST OF OLD FIELDS TO AVERAGE:
originalFields = []
fields = arcpy.ListFields(merged)  ## these are the fields that will have truncated names
for field in fields:
    if field.type == "Double" and not (field.name in excludeFromSum_dict.keys()):
        print(field.name)
        originalFields.append(str(field.name))  ## get the field names in the projects shapefile
## subset the original merged fieldnames to just those common to the projects and merged files (beginning with NEAR_Trans onwards)
originalFields = originalFields[originalFields.index("NEAR_Trans"):]

projectFieldList = []  ## list to hold projects_calculated fields
zoneFieldList = []  ## list to hold new zone averaged field names ("z*"")
fields = arcpy.ListFields(projectFile)  ## these are the fields that will have the entire name
for field in fields:
    if field.type == "Double" and not (
            field.name in excludeFromSum_dict.values()):  ## don't include these fields in the fieldlist and those that aren't numerical fields
        print(field.name)
        projectFieldList.append(str(field.name))
        zoneFieldList.append("z" + str(field.name))
projectFieldList = projectFieldList[projectFieldList.index("NEAR_Trans"):]
## subset the fieldnames to just those common to the projects and merged files
zoneFieldList = zoneFieldList[zoneFieldList.index("zNEAR_Trans"):]

#################################
## CALCULATE AREA OF NEW ZONES ##
#################################
## Calculate area of new zones (using GroupVal)
arcpy.DeleteField_management(merged,
                             "SUM_Area")  # delete old "SUM_Area" because it sums the area of the large zones before clustering
statsArea = arcpy.Statistics_analysis(merged, "in_memory/merged_areaTable", [["Area", "SUM"]],
                                      "GroupVal")  ## calculate new areas of clustered zones using GroupVal(unique zone id)
arcpy.JoinField_management(merged, "GroupVal", statsArea, "GroupVal")  ## add new "SUM_Area" to the merged feature class

############################################
## CALCULATE NEW CRITERIA VALUES OF ZONES ##
############################################
## add each zone average field to merged file and then calculate the zone average value per project using SUM_Area
i = 0
for each in zoneFieldList:
    print("Adding " + each + " as new field")
    arcpy.AddField_management(merged, each,
                              "DOUBLE")  ## create fields in fieldList if not already in original project shapefile
    # multiply each field by the area and divide by the total area of the zone (SUM_Area) to get spatially averaged criteria values
    print("Calculate from field: " + originalFields[i])
    arcpy.CalculateField_management(merged, each, "(!" + originalFields[i] + "! * !Area!) / !SUM_Area!", "PYTHON_9.3")
    i = i + 1

# TO GET ZONES AVERAGES, sum across all projects in each zone ("GroupVal") using summary statistics
statsFields = []

for each in zoneFieldList:
    fieldStatement = [each, "SUM"]  ##
    statsFields.append(fieldStatement)
stats = arcpy.Statistics_analysis(merged, "in_memory/merged_table", statsFields, "GroupVal")

###############################
## CREATE DISSOLVED ZONES FC ##
###############################

# then dissolve projects fc using group_val/zones, summing fields that were not area-averaged
# (I would want to delete all the project specific fields in the dissolve such that only the area-averaged fields remain)

summedFieldStatements = []

for each in excludeFromSum_dict.keys():
    if excludeFromSum_dict[each] not in getFields(merged):
        ## add new field with the correct field name using the dictionary:
        arcpy.AddField_management(merged, excludeFromSum_dict[each], "DOUBLE")
        ## calculate the new field using the value (new field) of the key (old field)
        arcpy.CalculateField_management(merged, excludeFromSum_dict[each], "!" + each + "!", "PYTHON_9.3")
        ## create a field statement for the dissolve function using the new field
        fieldStatement = [excludeFromSum_dict[each], "SUM"]  ##
        ## Delete the old field (key)
        arcpy.DeleteField_management(merged, each)
        summedFieldStatements.append(fieldStatement)
        print("Created " + excludeFromSum_dict[each] + " and deleted " + each)
    else:
        summedFieldStatements.append([excludeFromSum_dict[each], "SUM"])
        print("Just added " + excludeFromSum_dict[each] + " to summed Field statements list")

## take just a single value of the SUM_Area field, which is already the sum area of the entire zone

# statistics_fields=[["m_cf", "SUM"], ["m_cf", "MEAN"]]
## create zone polygons, summing the relevant fields
dissolveOut = arcpy.Dissolve_management(merged, projectFileName + "_zones", dissolve_field = "CLUSTER_ID",
                          statistics_fields=summedFieldStatements.append(["SUM_Area", "FIRST"]),
                                        multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")


## join the zone polygons with the z* area-weighted averaged criteria fields from Summary stats
arcpy.JoinField_management(dissolveOut, "GroupVal", stats, "GroupVal")

######################################
## CREATE ZONE AVERAGES PROJECTS FC ##
######################################

## CREATE THE PROJECTS_CALCULATED_ZONEAVERAGES fc with the correct (whole) field names:
i = 0
list_fields = getFields(merged)
for each in projectFieldList:
    print("Adding " + each + " as new field")
    arcpy.AddField_management(merged, "p_" + each,
                              "DOUBLE")  ## create fields in fieldList if not already in original project shapefile
    # multiply each field by the area and divide by the total area of the zone (SUM_Area) to get spatially averaged criteria values
    print("Calculate from field: " + originalFields[i])
    arcpy.CalculateField_management(merged, "p_" + each, "!" + originalFields[i] + "!", "PYTHON_9.3")
    arcpy.DeleteField_management(merged, originalFields[i])
    i = i + 1

## delete the z-Fields
for each in zoneFieldList:
    arcpy.DeleteField_management(merged, each)

# join the summary statistics table with the copied project shapefile so that the project file contains the zone averages
arcpy.JoinField_management(merged, "GroupVal", stats, "GroupVal")

## save to disk the project fc with the zone averages calculated
merged_inGDB = arcpy.CopyFeatures_management(merged, projectFileName + "_zoneAverages")


#########################
## CREATE NEW ZONE IDS ##
#########################

def multiletters(seq):
    for n in count(1):
        for s in product(seq, repeat=n):
            yield ''.join(s)


numRows = arcpy.GetCount_management(dissolveOut)
zoneIDlist = list(islice(multiletters('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), int(
    str(numRows))))  ## numRows is a "result," so need to convert it to a string first then integer
print(zoneIDlist)
print("number of zones: " + str(len(zoneIDlist)))
arcpy.AddField_management(dissolveOut, "zoneIdentification", "Text")
i = 0
cursor = arcpy.UpdateCursor(dissolveOut)
for row in cursor:
    row.setValue("zoneIdentification", str(zoneIDlist[i]))
    cursor.updateRow(row)
    i = i + 1
# create an excel table directly (since converting to dbf will limit the number of characters in a fieldname to 10)
arcpy.TableToExcel_conversion(dissolveOut, projectFileName + ".xls")

print("Finished aggregating criteria by zones")

elapsed_time = (time.time() - start_time) / (60)
print(str(elapsed_time) + " minutes")

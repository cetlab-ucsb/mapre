# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 00:38:19 2015

@author: Grace
"""
##--------------------------------Preamble ----------------------------------
import arcpy, numpy, math, time, os, csv
# import scipy.stats as stats
from collections import OrderedDict

start_time = time.time()
print(start_time)
# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")
from arcpy import env
from arcpy.sa import *

arcpy.env.overwriteOutput = True
'''
############################################################################################################
## --------------------------------------- GET ALL INPUTS ----------------------------------------------- ##
############################################################################################################
'''
#####################
## USER SET INPUTS ##
#####################

# technology = arcpy.GetParameterAsText(0) ## required

## SPATIAL INPUTS
technology = "Solar PV"  ##
projectsIn = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\SA_Outputs.gdb\solarPV_2_suitability_areas"  ##
projectsOut = projectsIn + "_attr"  ##
resourceInput = "R:\\users\\anagha.uppal\\MapRE\\MapRE_Data\\INPUTS\\Resources.gdb\\GHI_Projected_Africa"  ## MUST BE A RASTER
csvInput = r"R:\\users\\anagha.uppal\\MapRE\\inputs_projectAreaAttributes.csv"  ## required
templateRaster = "R:\\users\\anagha.uppal\\MapRE\\MapRE_Data\\INPUTS\\Resources.gdb\\GHI_Projected_Africa"  ## required
scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\Scratch.gdb"

################
## PARAMETERS ##
################

RQtype = "kWh/m2-day"  ## capacityFactor" or "windPowerDensity"
transmissionDistMultiplier = 1.3
cellSize = int(500)  ## 500
largestArea = 25  ## 500

## COSTS
capCost = 1700000
variableGenOMcost = 0
fixedGenOMcost = 50000
omer = 0  # Fixed O&M costs escalation rate

effLoss = 1 - 0.17  ## Assume wind losses (15%) without outage rate (2%). So default value should be 0.85;
outageRate = 1 - 0.02  ## solar PV only # RD: for both wind and solar. Give option to user to set this to zero for the IRENA dataset.
cfdr = 0  # Capacity factor degradation rate

transCost = 990
subCost = 71000
roadCost = 407000
discountRate = 0.1
plantLifetime = 25

## OTHERS
powerDensity = 9 #Land use efficiency (MW/km2)
landUseDiscount = 0.1

hours = 8760
maxInsol = 1000
maxInsol_kWh = 24

## Calculate total losses
losses = outageRate * effLoss  # RD 052019: Add outage rates. User can choose to set this as 1


### FUNCTIONS
def CSPcfCalc_6h(DNI, units):  ## for 6h storage
    if units == "kWh/m2-day":
        DNI_kWhm2y_6h = DNI * 365  ## convert to kWh/m2/year
    if units == "W/m2":
        DNI_kWhm2y_6h = DNI * (365 * 24 / 1000)  ## convert to kWh/m2/year
    CF_6h = (33.431 * math.log(
        DNI_kWhm2y_6h) - 212.57) / 100  # to make it a fraction # RD; Does this include outage rate? losses?
    return CF_6h


'''
#####################################################################################
#### --------------------------------GEOPROCESSES--------------------------------####
#####################################################################################
'''
'''
###########################################################
## Set environments and scratch workspace, copy projects ##
###########################################################
'''

# set environments for raster analyses
# arcpy.env.extent = countryBounds
# arcpy.env.mask = countryBounds
arcpy.env.snapRaster = templateRaster
arcpy.env.cellSize = templateRaster

env.scratchWorkspace = scratch
arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\SA_Outputs.gdb"

## COPY SUITABLE SITES FEATURE CLASS TO MEMORY
projects = arcpy.CopyFeatures_management(projectsIn, "projects") ## in_memory/

'''
##############
## Read CSV ##
##############
'''
with open(csvInput, "rt") as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    fields = next(reader)
    inputData = []
    for row in reader:
        inputData.append(dict(zip(fields, row)))

## inputDataPath is a dictionary of all the input datasets
inputDataPath = OrderedDict()

## populate the inputDataPath for each of the data categories.
for dataCategory in fields:
    inputDataPath[dataCategory] = [inputData[0][dataCategory], \
                                   inputData[1][dataCategory], inputData[2][dataCategory]]
'''
#########################
## Calculate distances ##
#########################
'''
for dataCategory in inputDataPath:
    if inputDataPath[dataCategory][0] == "yes" and inputDataPath[dataCategory][1] == "distance":
        dist_feature = inputDataPath[dataCategory][2]
        dist_fieldName = dataCategory
        arcpy.Near_analysis(projects, dist_feature, "", "NO_LOCATION", "NO_ANGLE")
        # Add new field for transmission distance:
        arcpy.AddField_management(projects, dist_fieldName, "DOUBLE")
        distMultiplier = 1
        ## commented out the following two lines on 08/25/2017 and moved the transmission distance multiplier to only the LCOE calculation.
        ##if dist_fieldName == "d_trans" or dist_fieldName == "d_sub":
        ##    distMultiplier = transmissionDistMultiplier
        arcpy.CalculateField_management(projects, dist_fieldName, "!NEAR_DIST!/1000 * " + str(distMultiplier),
                                        "PYTHON_9.3")
        arcpy.DeleteField_management(projects, "NEAR_DIST")
        arcpy.AddMessage(dist_fieldName + " distance calculations are complete")
'''
#################
## ZONAL STATS ##
#################
'''
## Check whether projects file is a fc in fgdb or a shapefile and set the id field accordingly
if projectsIn.find(
        ".shp") == -1:  ## .find is a Python method for finding a substring within a string (-1 indicates string not found)
    idField = "OBJECTID"
else:
    idField = "FID"

## Convert projects file to raster
projects_raster = arcpy.PolygonToRaster_conversion(projects, idField, "in_memory/raster", \
                                                   "MAXIMUM_AREA", "", cellSize)

arcpy.CopyRaster_management(projects_raster, projectsOut + "_raster")

for dataCategory in inputDataPath:
    if inputDataPath[dataCategory][0] == "yes" and inputDataPath[dataCategory][1] == "mean":
        mean_feature = inputDataPath[dataCategory][2]
        mean_fieldName = dataCategory

        ## Calculate average values
        arcpy.sa.ZonalStatisticsAsTable(projects_raster, "Value", \
                                        mean_feature, "in_memory/zonalStats", "DATA", "MEAN")
        # Join zonal statistics table of "MEAN" values to target project polygon, projects
        arcpy.JoinField_management(projects, idField, \
                                   "in_memory/zonalStats", "Value", "MEAN")
        arcpy.AddField_management(projects, mean_fieldName, "DOUBLE")
        arcpy.CalculateField_management(projects, mean_fieldName, "!MEAN!", "PYTHON_9.3")
        arcpy.DeleteField_management(projects, "MEAN")
        arcpy.AddMessage("Zonal stats for " + mean_fieldName + " is complete")
'''
##################################################
## CALCULATE CF OR RESOURCE QUALITY PER PROJECT ##
##################################################
'''
## Calculate average values
arcpy.sa.ZonalStatisticsAsTable(projects_raster, "Value", \
                                resourceInput, "in_memory/RQ", "DATA", "MEAN")
# Join zonal statistics table of "MEAN" values to target project polygon, projects
arcpy.JoinField_management(projects, idField, \
                           "in_memory/RQ", "Value", "MEAN")
if RQtype == "Capacity Factor":
    arcpy.AddField_management(projects, "m_cf", "DOUBLE")
    ## Calculate the final CF field from mean by applying the wind losses value
    arcpy.CalculateField_management(projects, "m_cf", "!MEAN!", "PYTHON_9.3")

if RQtype == "W/m2":
    arcpy.AddField_management(projects, "m_rq_wm2", "DOUBLE")
    ## Calculate the final CF field from mean by applying the wind losses value
    arcpy.CalculateField_management(projects, "m_rq_wm2", "!MEAN!", "PYTHON_9.3")

if RQtype == "kWh/m2-day" and (technology == "Solar PV" or technology == "CSP"):
    arcpy.AddField_management(projects, "m_rq_kwh", "DOUBLE")
    ## Calculate the final CF field from mean by applying the wind losses value
    arcpy.CalculateField_management(projects, "m_rq_kWh", "!MEAN!", "PYTHON_9.3")

if RQtype == "Wind speed (m/s)" and technology == "Wind":
    arcpy.AddField_management(projects, "m_rq_ms", "DOUBLE")
    ## Calculate the final CF field from mean by applying the wind losses value
    arcpy.CalculateField_management(projects, "m_rq_ms", "!MEAN!", "PYTHON_9.3")

arcpy.DeleteField_management(projects, "MEAN")
arcpy.AddMessage("Zonal stats for capacity factor is complete")

# arcpy.CopyFeatures_management(projects, projectsOut)

'''
################
## ADD FIELDS ##
################
'''
## Add fields called "CF", "ElectGen", "TransCost", "RoadCost"
# originalFields = []
# for field in fields:
#        originalFields.append(str(field.name)) ## get the field names in the projects shapefile

fieldList = ["m_cf", "egen", "incap", "l_tra", "l_sub", "l_road", \
             "l_gen", "lt_tra", "lt_sub"]

## create fields in fieldList if not already in original projects
for each in fieldList:
    #    if each not in originalFields:
    arcpy.AddMessage("Adding " + each + " as new field")
    arcpy.AddField_management(projects, each, "DOUBLE")
'''
###########################################################################################
## Calculate capacity factor, electricity generation, transmission, road costs, and LCOE ##
###########################################################################################
'''
## CRF calculation
CRF = (discountRate * (1 + discountRate) ** plantLifetime) / (
            ((1 + discountRate) ** plantLifetime) - 1)  # or the fixed charge factor

#### RD modification 05272019 ####
# Discount rate modified with CF degradation rate
dr_mod_cf_degrad = (discountRate + cfdr) / (1 - cfdr)
# CRF modified for CF degradation
crf_mod_cf_degrad = (dr_mod_cf_degrad * (1 + dr_mod_cf_degrad) ** plantLifetime) / (
            ((1 + dr_mod_cf_degrad) ** plantLifetime) - 1)

# Discount rate modified with OM escalation rate
dr_mod_omer = (discountRate - omer) / (1 + omer)
# CRF modified for O&M escalation
crf_mod_omer = (dr_mod_omer * (1 + dr_mod_omer) ** plantLifetime) / (((1 + dr_mod_omer) ** plantLifetime) - 1)
#### RD modification end ####

cursor = arcpy.UpdateCursor(projects)
#cursor = arcpy.da.UpdateCursor(projects, "*")
for row in cursor:
    area = row.getValue("Area")
    areaRatio = area / largestArea
    if inputDataPath["d_road"][0] == "yes":  ## If road file exists
        roadDist = row.getValue("d_road")
    else:
        roadDist = 0

    ## If resource quality type is capacity factor then simply retrieve the CF from the attribute table
    if RQtype == "Capacity Factor":
        CF = row.getValue("m_cf") * losses

    else:
        ## Calculate Capacity factors
        if technology == "Solar PV":
            if RQtype == "W/m2":
                RQ_row = row.getValue("m_rq_wm2")
                CF = (RQ_row / (maxInsol)) * losses  # derating factor*ResourceQuality/maxInsolation
            if RQtype == "kWh/m2-day":
                RQ_row = row.getValue("m_rq_kwh")
                CF = (RQ_row / (maxInsol_kWh)) * losses  # derating factor*ResourceQuality/maxInsolation

        if technology == "CSP":
            if RQtype == "W/m2":
                RQ_row = row.getValue("m_rq_wm2")
                CF = CSPcfCalc_6h(RQ_row, RQtype) * losses
            if RQtype == "kWh/m2-day":
                RQ_row = row.getValue("m_rq_kwh")
                CF = CSPcfCalc_6h(RQ_row, RQtype) * losses

        if technology == "Wind":
            if RQtype == "W/m2":
                RQ_row = row.getValue("m_rq_wm2")
                CF = sdfaf * losses

            if RQtype == "Wind speed (m/s)":
                RQ_row = row.getValue("m_rq_kwh")

        ## Set the calculate Capacity factor value
        row.setValue("m_cf", CF)

    LCOEgen = (capCost * CRF + fixedGenOMcost) / (8760 * CF) + variableGenOMcost

    #### RD modification 05272019 #####
    # NPV of electricity generation
    electGenPkWPyr = CF * hours
    electGenPkW_npv = electGenPkWPyr / (1 - cfdr) / crf_mod_cf_degrad

    # NPV of O&M fixed
    fixedGenOMcost_npv = fixedGenOMcost / (1 + omer) / crf_mod_omer

    # NPV of O&M variable
    variableGenOMcost_npv = variableGenOMcost * CF / (1 - cfdr) / crf_mod_cf_degrad

    # LCOE generation
    LCOEgenNew = (capCost + fixedGenOMcost_npv + variableGenOMcost_npv) / electGenPkW_npv

    #### RD modification end ####

    capacity = powerDensity * area * landUseDiscount

    #### GW modification 06242019 ####
    ## Calculate average annual electricity generation
    electGen_yr1 = capacity * CF * hours


    ## Create array of annual generation with degradation
    def calcElecGen(n, p, r):
        # return 1752000*(1-0.005)**n-1  # np.exp() is a built-in ufunc
        return p * (numpy.power((1 - r), n)) - 1


    electGen_new = numpy.mean(calcElecGen(range(0, int(plantLifetime), 1), electGen_yr1, cfdr))
    #### GW modification end ####

    electGen = capacity * CF * hours

    roadLCOE = (roadCost * CRF) * roadDist / (CF * 50 * hours)
    roadLCOEnew = (
                              roadCost * roadDist) / 50 / electGenPkW_npv  # RD 05272019: Verify if roadLCOEnew is same as roadLCOE with 0 degradation. If same, change roadLCOEnew to roadLCOE.

    ## Add calculations to fields:

    row.setValue("egen", electGen_new)
    row.setValue("l_road", roadLCOEnew)
    row.setValue("l_gen", LCOEgenNew)
    row.setValue("incap", capacity)

    ## Calculate Transmission and/or Substation connection costs:
    ## TransCost = [newTransCost + fixed OM ($/MW/km)] * transDist(km) * CRF/ (8760*CF) [=] $/MWh

    if inputDataPath["d_trans"][0] == "yes":
        transDist = row.getValue("d_trans") * transmissionDistMultiplier
        transLCOE = (transCost * transDist + subCost) * CRF / (CF * hours)
        transLCOEnew = (
                                   transCost * transDist + subCost) / electGenPkW_npv  # RD 05272019: Verify if transLCOEnew is same as transLCOE with 0 degradation. If same, change transLCOEnew to transLCOE.
        LCOEtotTrans = LCOEgen + roadLCOE + transLCOE
        LCOEtotTransNew = LCOEgenNew + roadLCOEnew + transLCOEnew
        row.setValue("lt_tra", LCOEtotTransNew)
        row.setValue("l_tra", transLCOEnew)

    if inputDataPath["d_sub"][0] == "yes":
        subDist = row.getValue("d_sub") * transmissionDistMultiplier
        subLCOE = (transCost * subDist + subCost) * CRF / (CF * hours)
        subLCOEnew = (
                                 transCost * subDist + subCost) / electGenPkW_npv  # RD 05272019: Verify if subLCOEnew is same as subLCOE with 0 degradation. If same, change subLCOEnew to subLCOE.
        LCOEtotSub = LCOEgen + roadLCOE + subLCOE
        LCOEtotSubNew = LCOEgenNew + roadLCOEnew + subLCOEnew
        row.setValue("lt_sub", LCOEtotSubNew)
        row.setValue("l_sub", subLCOEnew)  ## calculate the "SubCost" using the chosen turbine"

    cursor.updateRow(row)

## COPY CALCULATED PROJECTS TO HARD DRIVE
arcpy.CopyFeatures_management(projects, projectsOut)

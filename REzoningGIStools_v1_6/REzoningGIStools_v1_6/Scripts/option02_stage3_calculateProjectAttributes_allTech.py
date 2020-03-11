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
print start_time
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
technology = arcpy.GetParameterAsText(0) ##
projectsIn = arcpy.GetParameterAsText(1) ##
projectsOut = arcpy.GetParameterAsText(2) ##
resourceInput = arcpy.GetParameterAsText(3) ## MUST BE A RASTER
csvInput = arcpy.GetParameterAsText(4) ## required
templateRaster = arcpy.GetParameterAsText(5) ## required
scratch = arcpy.GetParameterAsText(6)

################
## PARAMETERS ##
################

RQtype = arcpy.GetParameterAsText(7) ## capacityFactor" or "windPowerDensity" 
transmissionDistMultiplier = arcpy.GetParameter(8)
cellSize = int(arcpy.GetParameter(9)) ## 500
largestArea = arcpy.GetParameter(10) ## 500

## COSTS
capCost = arcpy.GetParameter(11)
# capCost_classII = arcpy.GetParameter(15)
# capCost_classIII = arcpy.GetParameter(16) 
variableGenOMcost = arcpy.GetParameter(12)
fixedGenOMcost = arcpy.GetParameter(13)
transCost = arcpy.GetParameter(14)
subCost =  arcpy.GetParameter(15)
roadCost = arcpy.GetParameter(16)
discountRate = arcpy.GetParameter(17)
plantLifetime = arcpy.GetParameter(18) 

## OTHERS
powerDensity = arcpy.GetParameter(19)
windLosses = arcpy.GetParameter(20)
outageRate = arcpy.GetParameter(21) ## solar PV only
effLoss_PV = arcpy.GetParameter(22) #derating (loss) factor for PV (includes inverter and AC wiring)
effLoss_CSP = arcpy.GetParameter(23)
landUseDiscount = arcpy.GetParameter(24)

hours = 8760
maxInsol = 1000
maxInsol_kWh = 24

if technology == "Wind":
    losses = windLosses
if technology == "Solar PV":
    losses = outageRate*effLoss_PV
if technology == "CSP":
    losses = effLoss_CSP
    
### FUNCTIONS
def CSPcfCalc_6h(DNI, units): ## for 6h storage
    if units == "kWh/m2-day": 
        DNI_kWhm2y_6h = DNI*365 ## convert to kWh/m2/year
    if units == "W/m2":
        DNI_kWhm2y_6h = DNI*(365*24/1000) ## convert to kWh/m2/year
    CF_6h = (33.431*math.log(DNI_kWhm2y_6h) - 212.57)/100 # to make it a fraction
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
#arcpy.env.extent = countryBounds
#arcpy.env.mask = countryBounds
arcpy.env.snapRaster = templateRaster
arcpy.env.cellSize = templateRaster

env.scratchWorkspace = scratch

## COPY SUITABLE SITES FEATURE CLASS TO MEMORY
projects = arcpy.CopyFeatures_management(projectsIn, "in_memory/projects")

'''
##############
## Read CSV ##
##############
'''        
with open(csvInput, "rb") as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    fields = reader.next()
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
        arcpy.CalculateField_management(projects, dist_fieldName, "!NEAR_DIST!/1000 * " + str(distMultiplier), "PYTHON_9.3")
        arcpy.DeleteField_management(projects, "NEAR_DIST")
        arcpy.AddMessage(dist_fieldName + " distance calculations are complete") 
'''
#################
## ZONAL STATS ##
#################
'''    
## Check whether projects file is a fc in fgdb or a shapefile and set the id field accordingly
if projectsIn.find(".shp") == -1: ## .find is a Python method for finding a substring within a string (-1 indicates string not found)
    idField = "OBJECTID"
else:
    idField = "FID"
    
## Convert projects file to raster 
projects_raster = arcpy.PolygonToRaster_conversion(projects, idField, "in_memory/raster", \
                "MAXIMUM_AREA", "", cellSize)

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
    
'''
################
## ADD FIELDS ##
################
'''
## Add fields called "CF", "ElectGen", "TransCost", "RoadCost"
#originalFields = []
#for field in fields:
#        originalFields.append(str(field.name)) ## get the field names in the projects shapefile

fieldList = ["m_cf","egen", "incap", "l_tra", "l_sub", "l_road", \
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
CRF = (discountRate*(1 + discountRate)**plantLifetime) / (((1 + discountRate)**plantLifetime)-1) # or the fixed charge factor 

cursor = arcpy.UpdateCursor(projects) 
for row in cursor:        
    area = row.getValue("Area")
    areaRatio = area/largestArea
    if inputDataPath["d_road"][0] == "yes": ## If road file exists
        roadDist = row.getValue("d_road")
    else:
        roadDist = 0
    
    ## If resource quality type is capacity factor then simply retrieve the CF from the attribute table
    if RQtype == "Capacity Factor":
        CF = row.getValue("m_cf")*losses
    
    else:
        ## Calculate Capacity factors
        if technology == "Solar PV":
            if RQtype == "W/m2":
                RQ_row = row.getValue("m_rq_wm2")
                CF = (RQ_row/(maxInsol))*losses # derating factor*ResourceQuality/maxInsolation
            if RQtype == "kWh/m2-day":
                RQ_row = row.getValue("m_rq_kwh")
                CF = (RQ_row/(maxInsol_kWh))*losses # derating factor*ResourceQuality/maxInsolation
                
        if technology == "CSP":
            if RQtype == "W/m2":
                RQ_row = row.getValue("m_rq_wm2")
                CF = CSPcfCalc_6h(RQ_row, RQtype)*losses
            if RQtype == "kWh/m2-day":
                RQ_row = row.getValue("m_rq_kwh")
                CF = CSPcfCalc_6h(RQ_row, RQtype)*losses
        
        if technology == "Wind":
            if RQtype == "W/m2":
                RQ_row = row.getValue("m_rq_wm2")
                CF = sdfaf*losses

            if RQtype == "Wind speed (m/s)":
                RQ_row = row.getValue("m_rq_kwh")
        
        ## Set the calculate Capacity factor value 
        row.setValue("m_cf", CF)


    LCOEgen = (capCost*CRF + fixedGenOMcost)/(8760*CF) + variableGenOMcost
    
    capacity = powerDensity*area*landUseDiscount
                    
    electGen = capacity*CF*hours
    
    roadLCOE = (roadCost*CRF)*roadDist/(CF*50*hours)

    ## Add calculations to fields:

    row.setValue("egen", electGen)
    row.setValue("l_road", roadLCOE)
    row.setValue("l_gen", LCOEgen)
    row.setValue("incap", capacity)

    ## Calculate Transmission and/or Substation connection costs: 
    ## TransCost = [newTransCost + fixed OM ($/MW/km)] * transDist(km) * CRF/ (8760*CF) [=] $/MWh
    
    if inputDataPath["d_trans"][0] == "yes":
            transDist = row.getValue("d_trans") * transmissionDistMultiplier                      
            transLCOE = (transCost*transDist + subCost)*CRF/(CF*hours)
            LCOEtotTrans = LCOEgen + roadLCOE + transLCOE
            row.setValue("lt_tra", LCOEtotTrans)
            row.setValue("l_tra", transLCOE)
                
    if inputDataPath["d_sub"][0] == "yes":
            subDist = row.getValue("d_sub") * transmissionDistMultiplier
            subLCOE = (transCost*subDist + subCost)*CRF/(CF*hours)
            LCOEtotSub = LCOEgen + roadLCOE + subLCOE
            row.setValue("lt_sub", LCOEtotSub)
            row.setValue("l_sub", subLCOE) ## calculate the "SubCost" using the chosen turbine"

    cursor.updateRow(row)

## COPY CALCULATED PROJECTS TO HARD DRIVE
arcpy.CopyFeatures_management(projects, projectsOut)
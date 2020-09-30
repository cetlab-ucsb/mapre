# -*- coding: utf-8 -*-
"""
Created on Friday May 08 11:51:15 2020

Recalculates solar PV zone parameters


@author: Grace and Anagha
"""
## Preamble
import arcpy
import math

arcpy.env.overwriteOutput = True

'''
####################################################################################################################
## ---------------------------------------ZONE level calculations ----------------------------------------------- ##
####################################################################################################################
'''
################
## GET INPUTS ##
################

### FEATURE CLASS INPUTS AND OUTPUTS

## ZONE FEATURE CLASS INPUTS with NO attributes except zoneID and capacity factor (and capacity value for wind)
zoneInput = arcpy.GetParameterAsText(0)

## PROJECT FEATURE CLASS WITH ALL ATTRIBUTES UPDATED (output of the project-level calculations)
projectInput = arcpy.GetParameterAsText(1)

## OUTPUT ZONE FEATURE CLASS NAME
zoneOutput = arcpy.GetParameterAsText(2)

### CHANGEABLE PARAMETERS

## DISTANCES
projectOutput = arcpy.GetParameterAsText(3)

trans = arcpy.GetParameterAsText(4)
sub = arcpy.GetParameterAsText(5)
transmissionDistMultiplier = arcpy.GetParameter(6)
road = arcpy.GetParameterAsText(7)
PVplant = arcpy.GetParameterAsText(8)
## CSPplant = GetParameterAsText()
## windPlant = arcpy.GetParameterAsText(8)
geothermalPlant = arcpy.GetParameterAsText(9)
anyRE = arcpy.GetParameterAsText(10)
loadCenter = arcpy.GetParameterAsText(11)
water = arcpy.GetParameterAsText(12)
newFC = arcpy.GetParameterAsText(13)
newFieldName = arcpy.GetParameterAsText(14)

## COSTS
capCost = arcpy.GetParameter(15)
variableGenOMcost = arcpy.GetParameter(16)
fixedGenOMcost = arcpy.GetParameter(17)
transCost = arcpy.GetParameter(18)
subCost = arcpy.GetParameter(19)
roadCost = arcpy.GetParameter(20)
discountRate = arcpy.GetParameter(21)
plantLifetime = arcpy.GetParameter(22)

## OTHERS
outageRate = arcpy.GetParameter(23)
effLoss_PV = arcpy.GetParameter(24)  # derating (loss) factor for PV (includes inverter and AC wiring)
powerDensity = arcpy.GetParameter(25)
landUseDiscount = arcpy.GetParameter(26)

##########################
## SET FIXED PARAMETERS ##
##########################

## FIXED PARAMETERS
days = 365
hours = 8760
maxInsol = 1000  # w/m2 for solar


###############
## FUNCTIONS ##
###############
## function for rounding a value (x) to n-number of sig figs.
def round_to_n(x, n):
    if not (x == 0):
        rounded = round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))
        if rounded > 100:
            return int(rounded)
        else:
            return rounded
    else:
        return x


## function to get list of all fields
def getFields(data):
    fieldList = []
    fields = arcpy.ListFields(data)
    for field in fields:
        fieldList.append(field.name)
    return fieldList


'''
#####################################################################################
#### --------------------------------GEOPROCESSES--------------------------------####
#####################################################################################
'''
## Copy input files to memory:

zones = arcpy.CopyFeatures_management(zoneInput, "in_memory/zoneInputs")
projects = arcpy.CopyFeatures_management(projectInput, "in_memory/projectInputs")

'''
#########################
## Calculate distances ##
#########################
'''
## Create dictionary with input feature classes and their names to use as fields
input_dict = {"d_tra": trans, "d_sub": sub, "d_roa": road, "d_pv": PVplant, \
              "d_geo": geothermalPlant, "d_any": anyRE, "d_loa": loadCenter, "d_wat": water, \
              newFieldName: newFC}

## get all the fields in Project FC:
projectFields = arcpy.ListFields(projects)
projectFieldNames = []
for field in projectFields:
    projectFieldNames.append(field.name)

for inputFC in input_dict:
    if input_dict[inputFC] != "":  ## if input is provided, then calculate the distance
        feature = input_dict[inputFC]
        fieldName = inputFC
        ## calculate distances
        arcpy.Near_analysis(projects, feature, "", "NO_LOCATION", "NO_ANGLE")

        ## Add the new field
        if not (fieldName in projectFieldNames):
            arcpy.AddField_management(projects, fieldName, "DOUBLE")

        if (fieldName == "d_tra" or fieldName == "d_sub"):
            arcpy.CalculateField_management(projects, fieldName, "!NEAR_DIST! * " + str(transmissionDistMultiplier),
                                            "PYTHON_9.3")
        else:
            arcpy.CalculateField_management(projects, fieldName, "!NEAR_DIST!", "PYTHON_9.3")

        arcpy.DeleteField_management(projects, "NEAR_DIST")
        arcpy.AddMessage("Distance calculations are complete for " + fieldName)

## for debugging:
# arcpy.CopyFeatures_management(projects, r"A:\IRENA\PythonScripts\GIS_REzoningWorkshop\REzoningGIStools\Outputs\Outputs.gdb\projects_solarpv_za_update_prejoin")
# arcpy.AddMessage("copied projects file pre spatial join")
'''
#######################################
## GET ATTRIBUTES FROM PROJECTS FILE ##
#######################################
'''
## SPATIAL JOIN ZONES' ZONEID FIELD TO PROJECTS FILE
# create the fieldmap and fieldmapings object
fmJoin = arcpy.FieldMap()
fms = arcpy.FieldMappings()

# add all the fields in the projects file to the input and output field list in the fieldmappings object
fms.addTable(projects)
# add only the zone_identification field from the zone as the input field to the Join Field Map
fmJoin.addInputField(zones, "zoneid")

## add zone_identification as the output field
## make an outputField, zone_identification
zone_identification = fmJoin.outputField

## give the output field a name, zone_identification
zone_identification.name = 'zoneid'

## set the output field as zone_identification
fmJoin.outputfield = zone_identification

# add the fieldmap objects to fieldmappings
fms.addFieldMap(fmJoin)

## PERFORM SPATIAL JOIN
## join_type = "KEEP_COMMON" is an inner join (keep only those that have the spatial relationship)
## match type needs to be "WITHIN", otherwise the script assigns projects the wrong zone ID (do NOT use the default INTERSECT)
mergedProjects = arcpy.SpatialJoin_analysis(projects, zones, "in_memory/projectsSpatialJoinWithZones",
                                            "JOIN_ONE_TO_ONE", "KEEP_COMMON", fms, "WITHIN")

## for debugging:
# arcpy.CopyFeatures_management(mergedProjects, r"A:\IRENA\PythonScripts\GIS_REzoningWorkshop\REzoningGIStools\Outputs\Outputs.gdb\projects_solarpv_za_update_midjoin")
# arcpy.AddMessage("copied projects file immediately after spatial join")

#################################
## CALCULATE AREA OF NEW ZONES ##
#################################

fields_mergedProjects = getFields(mergedProjects)
if "sum_area" in fields_mergedProjects:
    arcpy.DeleteField_management(mergedProjects, "sum_area")  # delete old "sum_area" if it exists
    ## Calculate area of new zones (using zone_identification)
    statsArea = arcpy.Statistics_analysis(mergedProjects, "in_memory/merged_areaTable", [["area", "SUM"]],
                                          "zoneid")  ## calculate new areas of clustered zones using GroupVal(unique zone id)

if "SUM_Area" in fields_mergedProjects:
    arcpy.DeleteField_management(mergedProjects, "SUM_Area")  # delete old "sum_area" if it exists
    arcpy.AddMessage("Deleted the old SUM_Area field")
    ## Calculate area of new zones (using zone_identification)
    statsArea = arcpy.Statistics_analysis(mergedProjects, "in_memory/merged_areaTable", [["Area", "SUM"]],
                                          "zoneid")  ## calculate new areas of clustered zones using GroupVal(unique zone id)

arcpy.JoinField_management(mergedProjects, "zoneid", statsArea,
                           "zoneid")  ## add new "SUM_Area" to the merged feature class
arcpy.DeleteField_management(mergedProjects, "zoneid_1")

## for debugging:
##arcpy.CopyFeatures_management(mergedProjects, r"A:\IRENA\PythonScripts\GIS_REzoningWorkshop\REzoningGIStools\Outputs\Outputs.gdb\projects_solarpv_za_update_afterAreaCalc")
##arcpy.AddMessage("copied projects file immediately after spatial join")

######################################################################
## CALCULATE AREA WEIGHTED VALUES OF EACH CRITERIA FOR EACH PROJECT ##
######################################################################


## list to hold new zone averaged field names ("z*"")
zoneFieldList = []
for field in input_dict:
    if field != "":
        print
        field
        zoneFieldList.append("z" + field)

## add each zone average field to projects and then calculate the zone average value per project using SUM_Area (the area of each zone calculated in the above section)

for each in zoneFieldList:
    arcpy.AddMessage("Adding " + each + " as new field")
    arcpy.AddField_management(mergedProjects, each,
                              "DOUBLE")  ## create fields in fieldList if not already in original project shapefile
    # multiply each field by the area and divide by the total area of the zone (SUM_Area) to get spatially averaged criteria values
    print
    "Calculate from field: " + each[1:]
    # calculate area weighted averages
    arcpy.CalculateField_management(mergedProjects, each, "(!" + each[1:] + "! * !area!) / !sum_area!", "PYTHON_9.3")

####################################################################################
## PERFORM SUMMARY STATS TO CALCULATE THE ZONE AVERAGES USING THE 'ZONE ID' FIELD ##
####################################################################################

# TO GET ZONES AVERAGES, sum across all projects in each zone ("zone_identification") using summary statistics
statsFields = []

for each in zoneFieldList:
    fieldStatement = [each, "SUM"]  ##
    statsFields.append(fieldStatement)
stats = arcpy.Statistics_analysis(mergedProjects, "in_memory/merged_table", statsFields, "zoneid")

# arcpy.CopyFeatures_management(mergedProjects, \
#    r"A:\IRENA\OUTPUTS\ScriptToolTesting\ScriptToolTesting.gdb\ke_wind_globalMapV2_windExclusionsAg_threshold250_projects_calculated_spatJoined_within")

#########################################################################
## JOIN SUMMARY STATS TABLE FROM MERGED PROJECTS TO ZONE FEATURE CLASS ##
#########################################################################

arcpy.JoinField_management(zones, "zoneid", stats, "zoneid")  ## add new "SUM_Area" to the merged feature class
arcpy.DeleteField_management(zones, "zoneid_1")

#############################################################################
## RECALCULATE ORIGINAL FIELDS, since ADDED fields are now SUM_zNEAR_Trans ##
#############################################################################

# Get the fields in the zones feature class
originalFields = []
fields = arcpy.ListFields(zones)
for field in fields:
    originalFields.append(str(field.name))  ## get the field names in the projects shapefile

recalculatedFields = {"d_trans": "SUM_zd_tra", "d_sub": "SUM_zd_sub", \
                      "d_road": "SUM_zd_roa", \
                      "d_pv": "SUM_zd_pv", "d_geo": "SUM_zd_geo", \
                      "d_anyre": "SUM_zd_any", "d_load": "SUM_zd_loa", \
                      "d_water": "SUM_zd_wat", newFieldName: "SUM_z" + newFieldName}

for origField in recalculatedFields:
    if (origField not in originalFields) and (origField != ""):  ## Only if a new feature class is provided
        arcpy.AddMessage("Adding " + origField + " as new field")
        arcpy.AddField_management(zones, origField,
                                  "DOUBLE")  ## create fields in fieldList if not already in original project shapefile
    if origField != "":
        ## recalculate the field, but make sure it is rounded to the nearest ones place after converting from m to km (just use integer)
        arcpy.CalculateField_management(zones, origField, "!" + recalculatedFields[origField] + "!/1000", "PYTHON_9.3")
        arcpy.DeleteField_management(zones, recalculatedFields[origField])

'''
###########################
## ADD FIELDS IF MISSING ##
###########################
'''

fieldList = ["egen", "incap", \
             "l_tra", "l_sub", \
             "l_road", \
             "l_gen", \
             "lt_tra", "lt_sub"]

# fieldList = costList + ["ScREloc", "ScREloc_geo", "ScREloc_all",\
#            "ScLoad", "ScRoad", "ScSub", "ScTrans", "ScWater"] ## list of all new fields to calculate below
## IF any of these fields are not in the original Zones feature class then add it
for each in fieldList:
    if each not in originalFields:
        print
        "Adding " + each + " as new field"
        arcpy.AddField_management(zones, each,
                                  "DOUBLE")  ## create fields in fieldList if not already in original project shapefile

## for debugging:
# arcpy.CopyFeatures_management(mergedProjects, r"A:\IRENA\PythonScripts\GIS_REzoningWorkshop\REzoningGIStools\Outputs\Outputs.gdb\projects_solarpv_za_update_postjoin")
# arcpy.AddMessage("copied projects file after spatial join")

'''
###################################
## CALCULATE COSTS FOR EACH ZONE ##
###################################
'''
## CRF calculation
CRF = (discountRate * (1 + discountRate) ** plantLifetime) / (
            ((1 + discountRate) ** plantLifetime) - 1)  # or the fixed charge factor
largestArea = 25

cursor = arcpy.UpdateCursor(zones)
for row in cursor:
    # get handle on values of RQ, area, road and transmission distances for calculations
    # RQ_row = row.getValue("RQ_Wm2")
    area = row.getValue("area_km2")
    arcpy.AddMessage("Zone area =" + str(area))
    areaRatio = area / largestArea

    RQ_row = row.getValue("m_rq_wm2")

    ## Get the capacity factor values
    ## CF = row.getValue("mean_capacityFactor")

    ###############################
    ## CALCULATE GENERATION LCOE ##
    ###############################

    ## Calculate CF:
    CF = effLoss_PV * outageRate * RQ_row / (maxInsol)  # derating factor*ResourceQuality/maxInsolation

    # ElectGen = CF * PD_PV(MW/km2) * Area(km2) * 8760 hours
    capacity = powerDensity * area * landUseDiscount  ## in MW
    ElectGen = capacity * CF * hours  # MWh

    # LCOE of generation: LCOEgen = (capital cost*CRF)/(8760 hours * 0.001 kW to MW * CF) + variable OM
    LCOEgen = (capCost * CRF + fixedGenOMcost) / (8760 * CF) + variableGenOMcost

    ## ROAD LCOE
    roadDist = row.getValue("d_road")
    arcpy.AddMessage("transmission dist = " + str(row.getValue("d_trans")))
    arcpy.AddMessage("substation dist = " + str(row.getValue("d_sub")))

    roadLCOE = (roadCost * CRF) * roadDist * areaRatio / (ElectGen)
    # roadLCOE = (roadCost*CRF)*roadDist/(50*CF*hours)

    # Add calculations to fields:
    row.setValue("m_cf", round(CF, 3))
    row.setValue("egen", round_to_n(ElectGen, 3))
    row.setValue("l_road", round(roadLCOE, 2))  ## display cost in rupees
    row.setValue("l_gen", round(LCOEgen, 2))
    row.setValue("incap", capacity)

    ###############################################################
    ## Calculate Transmission and/or Substation connection costs ##
    ###############################################################
    # Calculate Transmission and/or Substation connection costs: TransCost = [newTransCost + fixed OM ($/MW/km)] * transDist(km) * CRF/ (8760*CF) [=] $/MWh

    ## TRANSMISSION AND TOTAL TRANSMISSION COSTS
    transDist = row.getValue("d_trans")
    transLCOE = (transCost * transDist + subCost) * CRF / (CF * hours)
    row.setValue("l_tra", round(transLCOE, 2))
    ## calculate and set total LCOE
    LCOEtotTrans = LCOEgen + roadLCOE + transLCOE
    row.setValue("lt_tra", round(LCOEtotTrans, 2))

    # SUBSTATION LCOE AND TOTAL SUBSTATION COST
    subDist = row.getValue("d_sub")
    subLCOE = (transCost * subDist + subCost) * CRF / (CF * hours)
    row.setValue("l_sub", round(subLCOE, 2))
    ## Calculate and set total LCOE
    LCOEtotSub = LCOEgen + roadLCOE + subLCOE
    row.setValue("lt_sub", round(LCOEtotSub, 2))

    cursor.updateRow(row)
'''
############################################
## COPY CALCULATED ZONES FC TO HARD DRIVE ##
############################################
'''
arcpy.CopyFeatures_management(zones, zoneOutput)

if projectOutput != "":
    arcpy.CopyFeatures_management(projects, projectOutput)

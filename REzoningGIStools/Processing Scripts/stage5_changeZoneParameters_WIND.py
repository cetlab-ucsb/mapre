# -*- coding: utf-8 -*-
"""
Created on Friday May 08 11:51:15 2020

Recalculates wind zone parameters

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
## PVplant = GetParameterAsText()
## CSPplant = GetParameterAsText()
windPlant = arcpy.GetParameterAsText(8)
geothermalPlant = arcpy.GetParameterAsText(9)
anyRE = arcpy.GetParameterAsText(10)
loadCenter = arcpy.GetParameterAsText(11)
water = arcpy.GetParameterAsText(12)
newFC = arcpy.GetParameterAsText(13)
newFieldName = arcpy.GetParameterAsText(14)

## COSTS
capCost_classI = arcpy.GetParameter(15)
capCost_classII = arcpy.GetParameter(16)
capCost_classIII = arcpy.GetParameter(17)
variableGenOMcost = arcpy.GetParameter(18)
fixedGenOMcost = arcpy.GetParameter(19)
transCost = arcpy.GetParameter(20)
subCost = arcpy.GetParameter(21)
roadCost = arcpy.GetParameter(22)
discountRate = arcpy.GetParameter(23)
plantLifetime = arcpy.GetParameter(24)

## OTHERS
powerDensity = arcpy.GetParameter(25)
## correct for the wind losses (0.83) that were applied to the mean CFs in the original analysis
windLosses = arcpy.GetParameter(26) / 0.83
landUseDiscount = arcpy.GetParameter(27)

##########################
## SET FIXED PARAMETERS ##
##########################

## FIXED PARAMETERS
days = 365
hours = 8760


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
input_dict = {"d_tra": trans, "d_sub": sub, "d_roa": road, "d_win": windPlant, \
              "d_geo": geothermalPlant, "d_any": anyRE, "d_loa": loadCenter, "d_wat": water, \
              newFieldName: newFC}

## get all the fields in Project FC:
projectFields = arcpy.ListFields(projects)
projectFieldNames = []
for field in projectFields:
    projectFieldNames.append(field.name)

## set progressor (progress indicator bar in the geoprocessing windo)
arcpy.SetProgressor("step", "Calculating distances... ", 0, len(input_dict), 1)

for inputFC in input_dict:
    if input_dict[inputFC] != "":  ## if input is provided, then calculate the distance
        feature = input_dict[inputFC]
        fieldName = inputFC

        arcpy.SetProgressorLabel("Calculating distances for " + str(feature))
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
        arcpy.SetProgressorPosition()
arcpy.ResetProgressor()
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

#################################
## CALCULATE AREA OF NEW ZONES ##
#################################
## Calculate area of new zones (using zone_identification)
# arcpy.DeleteField_management(merged, "SUM_Area")  # delete old "SUM_Area" because it sums the area of the large zones before clustering
statsArea = arcpy.Statistics_analysis(mergedProjects, "in_memory/merged_areaTable", [["Area", "SUM"]],
                                      "zoneid")  ## calculate new areas of clustered zones using GroupVal(unique zone id)
arcpy.JoinField_management(mergedProjects, "zoneid", statsArea,
                           "zoneid")  ## add new "SUM_Area" to the merged feature class
arcpy.DeleteField_management(mergedProjects, "zoneid_1")

######################################################################
## CALCULATE AREA WEIGHTED VALUES OF EACH CRITERIA FOR EACH PROJECT ##
######################################################################

## List all the fields to average:

# mergedProject_fields = arcpy.ListFields(mergedProjects)
# mergedProject_fieldNames = []
# for field in mergedProject_fields:
#    mergedProject_fieldNames.append(field.name)
#
# regex_expression = re.compile("(\S+)NEAR(\S+)")
# fields_toSum = [string for string in mergedProject_fieldNames if re.search(regex_expression, string)]

# fields_toSum = ["d_tra", "d_sub", "d_roa", \
#                "d_win", "d_geo", "d_any", \
#                "d_loa", "d_wat", newFieldName]

## list to hold new zone averaged field names ("z*"")
zoneFieldList = []
for field in input_dict:
    if field != "":  ## If there is a new feature class
        print
        field
        zoneFieldList.append("z" + field)

## add each zone average field to projects and then calculate the zone average value per project using SUM_Area (the area of each zone calculated in the above section)

for each in zoneFieldList:
    print
    "Adding " + each + " as new field"
    arcpy.AddField_management(mergedProjects, each,
                              "DOUBLE")  ## create fields in fieldList if not already in original project shapefile
    # multiply each field by the area and divide by the total area of the zone (SUM_Area) to get spatially averaged criteria values
    print
    "Calculate from field: " + each[1:]
    # calculate area weighted averages
    arcpy.CalculateField_management(mergedProjects, each, "(!" + each[1:] + "! * !Area!) / !SUM_Area!", "PYTHON_9.3")

####################################################################################
## PERFORM SUMMARY STATS TO CALCULATE THE ZONE AVERAGES USING THE 'ZONE ID' FIELD ##
####################################################################################

# TO GET ZONES AVERAGES, sum across all projects in each zone ("zone_identification") using summary statistics
statsFields = []

for each in zoneFieldList:
    fieldStatement = [each, "SUM"]  ##
    statsFields.append(fieldStatement)
stats = arcpy.Statistics_analysis(mergedProjects, "in_memory/merged_table", statsFields, "zoneid")
# stats = arcpy.Statistics_analysis(mergedProjects, r"A:\IRENA\OUTPUTS\ScriptToolTesting\ScriptToolTesting.gdb\projects_zoneAvgTable_within", statsFields, "zone_identification")

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
                      "d_wind": "SUM_zd_win", "d_geo": "SUM_zd_geo", \
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
fieldList = ["egen_ch", "egen_cii", "incap", \
             "l_tra_ch", "l_sub_ch", "l_road_ch", \
             "l_gen_ch", "l_gen_cii", \
             "lt_tra_ch", "lt_tra_cii", \
             "lt_sub_ch", "lt_sub_cii"]

# fieldList = costList + ["ScREloc", "ScREloc_geo", "ScREloc_all",\
#            "ScLoad", "ScRoad", "ScSub", "ScTrans", "ScWater"] ## list of all new fields to calculate below
## IF any of these fields are not in the original Zones feature class then add it
for each in fieldList:
    if each not in originalFields:
        print
        "Adding " + each + " as new field"
        arcpy.AddField_management(zones, each,
                                  "DOUBLE")  ## create fields in fieldList if not already in original project shapefile

# arcpy.CopyFeatures_management(zones, r"A:\IRENA\OUTPUTS\ScriptToolTesting\ScriptToolTesting.gdb\ke_wind_globalMapV2_windExclusionsAg_threshold250_zonesforMap_capVal_forACEC_corr_test_intermed")
'''
###################################
## CALCULATE COSTS FOR EACH ZONE ##
###################################
'''
## CRF calculation
CRF = (discountRate * (1 + discountRate) ** plantLifetime) / (
            ((1 + discountRate) ** plantLifetime) - 1)  # or the fixed charge factor

cursor = arcpy.UpdateCursor(zones)
for row in cursor:
    # get handle on values of RQ, area, road and transmission distances for calculations
    # RQ_row = row.getValue("RQ_Wm2")
    area = row.getValue("area_km2")
    arcpy.AddMessage("Zone area =" + str(area))

    ## Get the capacity factor values
    CF_chosen = row.getValue("m_cf_ch")
    CF_ClsII = row.getValue("m_cf_cii")
    print
    str(CF_chosen) + " and " + str(CF_ClsII)

    ## If any value is missing set to zero:
    area_clsI = row.getValue("a_ch_ci")
    if area_clsI is None:
        area_clsI = 0

    area_clsII = row.getValue("a_ch_cii")
    if area_clsII is None:
        area_clsII = 0

    area_clsIII = row.getValue("a_ch_ciii")
    if area_clsIII is None:
        area_clsIII = 0

    CF_clsI = row.getValue("cf_ch_ci")
    if CF_clsI is None:
        CF_clsI = 0

    CF_clsII = row.getValue("cf_ch_cii")
    if CF_clsII is None:
        CF_clsII = 0

    CF_clsIII = row.getValue("cf_ch_ciii")
    if CF_clsIII is None:
        CF_clsIII = 0

    ###############################
    ## CALCULATE GENERATION LCOE ##
    ###############################

    ## Calculate total wind area:
    sum_windArea = area_clsI + area_clsII + area_clsIII

    ## Create dictionary linking each turbine class' area, capital cost and capacity factor
    turbineClasses = {area_clsI: [capCost_classI, CF_clsI], \
                      area_clsII: [capCost_classII, CF_clsII], \
                      area_clsIII: [capCost_classIII, CF_clsIII]}

    ## Create empty list to hold the generation LCOE value of each turbine class (we will later sum this list)
    turbineClasses_LCOE = []

    ## Calculate the generation LCOE for each turbine class and multiply by proportion of total area
    for turbineArea in turbineClasses:
        proportion = turbineArea / sum_windArea

        if proportion == 0:
            LCOEgen = 0
        else:
            ## Calculate the generation LCOE
            LCOEgen = (turbineClasses[turbineArea][0] * CRF + fixedGenOMcost) / (
                        hours * turbineClasses[turbineArea][1] * windLosses) + variableGenOMcost

        ## Calculate the area-weighted generationLCOE
        turbineClasses_LCOE.append(proportion * LCOEgen)

    ## Calculate the area-weighted generation LCOE of the zone
    LCOEgen_chosen = sum(turbineClasses_LCOE)

    ## Calculate the generation LCOE assuming that only Class II turbines are developed on the site, as opposed to the chosen turbine
    LCOEgen_clsII = (capCost_classII * CRF + fixedGenOMcost) / (hours * CF_ClsII * windLosses)

    ## Calculate the potential installed capacity
    capacity = powerDensity * area * landUseDiscount

    ## Calculate the potential electricity generation
    ElectGen_chosen = capacity * CF_chosen * hours * windLosses
    ElectGen_clsII = capacity * CF_ClsII * hours * windLosses

    ## Add calculations to fields:
    row.setValue("egen_ch", round_to_n(ElectGen_chosen, 3))
    row.setValue("egen_cii", round_to_n(ElectGen_clsII, 3))
    row.setValue("l_gen_ch", round(LCOEgen_chosen, 2))
    row.setValue("l_gen_cii", round(LCOEgen_clsII, 2))
    row.setValue("incap", round(capacity, 0))

    ###############################################################
    ## Calculate Transmission and/or Substation connection costs ##
    ###############################################################

    ## TransCost = [newTransCost + fixed OM ($/MW/km)] * transDist(km) * CRF/ (8760*CF) [=] $/MWh

    ## Get transmission distance
    transDist = row.getValue("d_trans")

    ## Get road distance
    roadDist = row.getValue("d_road")

    ## CALCULATE TRANSMISSION LCOE AND TOTAL LCOE FOR EACH SCENARIO (CHOSEN OR CLASS II)
    LCOEtotTrans_List = {"lt_tra_ch": [CF_chosen, LCOEgen_chosen, ElectGen_chosen], \
                         "lt_tra_cii": [CF_ClsII, LCOEgen_clsII, ElectGen_clsII]}

    for totalLCOEfield in LCOEtotTrans_List:
        transLCOE = (transCost * transDist + subCost) * CRF / (
                    LCOEtotTrans_List[totalLCOEfield][0] * hours * windLosses)

        ## RECALCULATE ROAD COSTS
        roadLCOE = (roadCost * CRF) * roadDist / (LCOEtotTrans_List[totalLCOEfield][0] * 50 * hours * windLosses)

        ## calculate TOTAL LCOE
        LCOEtotTrans = LCOEtotTrans_List[totalLCOEfield][1] + roadLCOE + transLCOE
        row.setValue(totalLCOEfield, round(LCOEtotTrans, 2))

    row.setValue("l_tra_ch", round((transCost * transDist + subCost) * CRF / (CF_chosen * hours * windLosses),
                                   2))  ## calculate the "TransCost" using the chosen turbine"
    # row.setValue("l_tra_cii", round((transCost*transDist + subCost)*CRF/(CF_ClsII*hours*windLosses),2)) ## calculate the "TransCost" using the CLASSII turbine"

    ## CALCULATE TRANSMISSION LCOE AND TOTAL LCOE FOR EACH SCENARIO (CHOSEN OR CLASS II)
    LCOEtotSub_List = {"lt_sub_ch": [CF_chosen, LCOEgen_chosen, ElectGen_chosen], \
                       "lt_sub_cii": [CF_ClsII, LCOEgen_clsII, ElectGen_clsII]}

    subDist = row.getValue("d_sub")

    for totalLCOEfield in LCOEtotSub_List:
        ## Calculate substation LCOE
        subLCOE = (transCost * subDist + subCost) * CRF / (LCOEtotSub_List[totalLCOEfield][0] * hours * windLosses)

        ## calculate road LCOE
        roadLCOE = (roadCost * CRF) * roadDist / (LCOEtotSub_List[totalLCOEfield][0] * 50 * hours * windLosses)

        ## calculate TOTAL LCOE
        LCOEtotSub = LCOEtotSub_List[totalLCOEfield][1] + roadLCOE + subLCOE
        row.setValue(totalLCOEfield, round(LCOEtotSub, 2))

    row.setValue("l_sub_ch", round((transCost * subDist + subCost) * CRF / (CF_chosen * hours * windLosses),
                                   2))  ## calculate the "SubCost" using the chosen turbine"
    # row.setValue("l_sub_cii", round((transCost*subDist + subCost)*CRF/(CF_ClsII*hours),2)) ## calculate the "SubCost" using the CLASSII turbine"

    ## calculate and set the road cost assuming a fixed capacity of 50 MW
    row.setValue("l_road_ch", round((roadCost * CRF) * roadDist / (CF_chosen * 50 * hours * windLosses), 2))
    # row.setValue("l_road_cii", round((roadCost*CRF)*roadDist/(CF_ClsII*50*hours),2))

    cursor.updateRow(row)

arcpy.DeleteField_management(zones, "FREQUENCY")

'''
############################################
## COPY CALCULATED ZONES FC TO HARD DRIVE ##
############################################
'''
arcpy.CopyFeatures_management(zones, zoneOutput)

if projectOutput != "":
    arcpy.CopyFeatures_management(projects, projectOutput)

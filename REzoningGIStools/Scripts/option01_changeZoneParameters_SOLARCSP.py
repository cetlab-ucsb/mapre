# -*- #################
"""
Created on Tue Sep 01 15:41:25 2015

Recalculates solar CSP zone parameters

@author: Grace
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
CSPplant = arcpy.GetParameterAsText(8)
## windPlant = arcpy.GetParameterAsText(8)
geothermalPlant = arcpy.GetParameterAsText(9)
anyRE = arcpy.GetParameterAsText(10)
loadCenter = arcpy.GetParameterAsText(11)
water = arcpy.GetParameterAsText(12)
newFC = arcpy.GetParameterAsText(13)
newFieldName = arcpy.GetParameterAsText(14)

## COSTS
capCost_6h = arcpy.GetParameter(15)
capCost_0h = arcpy.GetParameter(16)

variableGenOMcost = arcpy.GetParameter(17)
fixedGenOMcost = arcpy.GetParameter(18)
transCost = arcpy.GetParameter(19)
subCost =  arcpy.GetParameter(20)
roadCost = arcpy.GetParameter(21)
discountRate = arcpy.GetParameter(22)
plantLifetime = arcpy.GetParameter(23) 

## OTHERS
powerDensity_6h = arcpy.GetParameter(24)
powerDensity_0h = arcpy.GetParameter(25)
effLoss_CSP = arcpy.GetParameter(26)
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
	if not(x == 0):
		rounded = round(x, -int(math.floor(math.log10(abs(x))))+ (n-1))
		if rounded >100:
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
  
# Calculate CF from DNI for CSP using empirical function (from SAM simulations using African weather data and 3 US data points)
def CSPcfCalc_0h(DNI): ## for 0h storage
    DNIconverted_0h = DNI*(365*24/1000)
    CF_0h = (22.193*math.log(DNIconverted_0h) - 145.69)/100 # to make it a fraction
    return CF_0h

def CSPcfCalc_6h(DNI): ## for 6h storage
    DNIconverted_6h = DNI*(365*24/1000)
    CF_6h = (33.431*math.log(DNIconverted_6h) - 212.57)/100 # to make it a fraction
    return CF_6h
  
  
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
input_dict = {"d_tra": trans, "d_sub": sub, "d_roa": road, "d_csp": CSPplant, \
            "d_geo": geothermalPlant, "d_any": anyRE, "d_loa": loadCenter, "d_wat": water,\
            newFieldName : newFC}

## get all the fields in Project FC:
projectFields = arcpy.ListFields(projects)
projectFieldNames = []
for field in projectFields:
    projectFieldNames.append(field.name)

for inputFC in input_dict:
    if input_dict[inputFC] != "": ## if input is provided, then calculate the distance
        feature = input_dict[inputFC]
        fieldName = inputFC
        ## calculate distances 
        arcpy.Near_analysis(projects, feature, "", "NO_LOCATION", "NO_ANGLE")
        
        ## Add the new field
        if not(fieldName in projectFieldNames):
             arcpy.AddField_management(projects, fieldName, "DOUBLE")
        
        if (fieldName == "d_tra" or fieldName == "d_sub"):
            arcpy.CalculateField_management(projects, fieldName, "!NEAR_DIST! * " + str(transmissionDistMultiplier), "PYTHON_9.3")
        else: 
            arcpy.CalculateField_management(projects, fieldName, "!NEAR_DIST!", "PYTHON_9.3")

        arcpy.DeleteField_management(projects, "NEAR_DIST")
        arcpy.AddMessage("Distance calculations are complete for " + fieldName)

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
mergedProjects = arcpy.SpatialJoin_analysis(projects, zones, "in_memory/projectsSpatialJoinWithZones", "JOIN_ONE_TO_ONE", "KEEP_COMMON", fms, "WITHIN")

#################################
## CALCULATE AREA OF NEW ZONES ##
#################################

fields_mergedProjects = getFields(mergedProjects)
if "sum_area" in fields_mergedProjects:
    arcpy.DeleteField_management(mergedProjects, "sum_area")  # delete old "sum_area" if it exists
    ## Calculate area of new zones (using zone_identification)
    statsArea = arcpy.Statistics_analysis(mergedProjects, "in_memory/merged_areaTable", [["area","SUM"]], "zoneid") ## calculate new areas of clustered zones using GroupVal(unique zone id)


if "SUM_Area" in fields_mergedProjects:
    arcpy.DeleteField_management(mergedProjects, "SUM_Area")  # delete old "sum_area" if it exists    
    arcpy.AddMessage("Deleted the old SUM_Area field")
    ## Calculate area of new zones (using zone_identification)
    statsArea = arcpy.Statistics_analysis(mergedProjects, "in_memory/merged_areaTable", [["Area","SUM"]], "zoneid") ## calculate new areas of clustered zones using GroupVal(unique zone id)


## Calculate area of new zones (using zone_identification)
#arcpy.DeleteField_management(merged, "SUM_Area")  # delete old "SUM_Area" because it sums the area of the large zones before clustering
arcpy.JoinField_management(mergedProjects, "zoneid", statsArea, "zoneid") ## add new "SUM_Area" to the merged feature class
arcpy.DeleteField_management(mergedProjects, "zoneid_1")

## for debugging:
# arcpy.CopyFeatures_management(mergedProjects, r"A:\IRENA\PythonScripts\GIS_REzoningWorkshop\REzoningGIStools\Outputs\Outputs.gdb\projects_solarpv_za_update_afterAreaCalc")
# arcpy.AddMessage("copied projects file immediately after spatial join")

######################################################################
## CALCULATE AREA WEIGHTED VALUES OF EACH CRITERIA FOR EACH PROJECT ##
######################################################################
    
## list to hold new zone averaged field names ("z*"")
zoneFieldList = [] 
for field in input_dict:
    if field != "": ## If there is a new feature class
        print(field)
        zoneFieldList.append("z" + field)

## add each zone average field to projects and then calculate the zone average value per project using SUM_Area (the area of each zone calculated in the above section)

for each in zoneFieldList:
  print("Adding " + each + " as new field")
  arcpy.AddField_management(mergedProjects, each, "DOUBLE")  ## create fields in fieldList if not already in original project shapefile
  # multiply each field by the area and divide by the total area of the zone (SUM_Area) to get spatially averaged criteria values
  print("Calculate from field: " + each[1:])
  # calculate area weighted averages
  arcpy.CalculateField_management(mergedProjects, each, "(!" + each[1:] + "! * !area!) / !sum_area!", "PYTHON_9.3")

####################################################################################
## PERFORM SUMMARY STATS TO CALCULATE THE ZONE AVERAGES USING THE 'ZONE ID' FIELD ##
####################################################################################

# TO GET ZONES AVERAGES, sum across all projects in each zone ("zone_identification") using summary statistics 
statsFields = []

for each in zoneFieldList:
  fieldStatement = [each, "SUM"] ## 
  statsFields.append(fieldStatement)
stats = arcpy.Statistics_analysis(mergedProjects, "in_memory/merged_table", statsFields, "zoneid")
#stats = arcpy.Statistics_analysis(mergedProjects, r"A:\IRENA\OUTPUTS\ScriptToolTesting\ScriptToolTesting.gdb\projects_zoneAvgTable_within", statsFields, "zone_identification")

# arcpy.CopyFeatures_management(mergedProjects, \
#    r"A:\IRENA\OUTPUTS\ScriptToolTesting\ScriptToolTesting.gdb\ke_wind_globalMapV2_windExclusionsAg_threshold250_projects_calculated_spatJoined_within")

#########################################################################
## JOIN SUMMARY STATS TABLE FROM MERGED PROJECTS TO ZONE FEATURE CLASS ##
#########################################################################

arcpy.JoinField_management(zones, "zoneid", stats, "zoneid") ## add new "SUM_Area" to the merged feature class
arcpy.DeleteField_management(zones, "zoneid_1")

#############################################################################
## RECALCULATE ORIGINAL FIELDS, since ADDED fields are now SUM_zNEAR_Trans ##
#############################################################################

# Get the fields in the zones feature class
originalFields = []
fields = arcpy.ListFields(zones)
for field in fields:
        originalFields.append(str(field.name)) ## get the field names in the projects shapefile

recalculatedFields = {"d_trans": "SUM_zd_tra", "d_sub" : "SUM_zd_sub", \
                        "d_road" : "SUM_zd_roa", \
                        "d_csp" : "SUM_zd_csp", "d_geo" : "SUM_zd_geo",\
                        "d_anyre" : "SUM_zd_any", "d_load": "SUM_zd_loa", \
                        "d_water" : "SUM_zd_wat",  newFieldName : "SUM_z" + newFieldName}

for origField in recalculatedFields:
    if (origField not in originalFields) and (origField != ""): ## Only if a new feature class is provided
        arcpy.AddMessage("Adding " + origField + " as new field")
        arcpy.AddField_management(zones, origField, "DOUBLE")  ## create fields in fieldList if not already in original project shapefile
    if origField != "":
        ## recalculate the field, but make sure it is rounded to the nearest ones place after converting from m to km (just use integer)
        arcpy.CalculateField_management(zones, origField, "!" + recalculatedFields[origField] + "!/1000", "PYTHON_9.3")
        arcpy.DeleteField_management(zones, recalculatedFields[origField])

'''
###########################
## ADD FIELDS IF MISSING ##
###########################
'''

fieldList = ["egen_0h","egen_6h","incap_0h", \
            "incap_6h", "l_tra_6h", "l_tra_0h", "l_sub_6h", \
            "l_sub_0h", "l_road_6h", "l_road_0h",\
            "l_gen_6h", "l_gen_0h", "lt_tra_6h", \
            "lt_tra_0h", "lt_sub_6h", \
            "lt_sub_0h"]
            
#fieldList = costList + ["ScREloc", "ScREloc_geo", "ScREloc_all",\
#            "ScLoad", "ScRoad", "ScSub", "ScTrans", "ScWater"] ## list of all new fields to calculate below
## IF any of these fields are not in the original Zones feature class then add it
for each in fieldList:
        if each not in originalFields:
                print("Adding " + each + " as new field")
                arcpy.AddField_management(zones, each, "DOUBLE")  ## create fields in fieldList if not already in original project shapefile

# arcpy.CopyFeatures_management(zones, r"A:\IRENA\OUTPUTS\ScriptToolTesting\ScriptToolTesting.gdb\ke_wind_globalMapV2_windExclusionsAg_threshold250_zonesforMap_capVal_forACEC_corr_test_intermed")
'''
###################################
## CALCULATE COSTS FOR EACH ZONE ##
###################################
'''
## CRF calculation
CRF = (discountRate*(1 + discountRate)**plantLifetime) / (((1 + discountRate)**plantLifetime)-1) # or the fixed charge factor 

cursor = arcpy.UpdateCursor(zones) 
for row in cursor:        
    # get handle on values of RQ, area, road and transmission distances for calculations
    #RQ_row = row.getValue("RQ_Wm2")
    area = row.getValue("area_km2")
    arcpy.AddMessage("Zone area =" + str(area))
    
    RQ_row = row.getValue("m_rq_wm2")

    CF_0h = effLoss_CSP*CSPcfCalc_0h(RQ_row)
    CF_6h = effLoss_CSP*CSPcfCalc_6h(RQ_row)
    print(str(CF_0h) + " and " + str(CF_6h))

    # ElectGen = CF * PD_CSP(MW/km2) * Area(km2) * 8760 hours
    capacity_0h = powerDensity_0h*area*landUseDiscount ## in MW
    capacity_6h = powerDensity_6h*area*landUseDiscount ## in MW

    ElectGen_0h = capacity_0h*CF_0h*hours # MWh
    ElectGen_6h = capacity_6h*CF_6h*hours # MWh

    # LCOE of generation: LCOEgen = (capital cost*CRF)/(8760 hours * 0.001 kW to MW * CF) + variable OM
    LCOEgen_0h = (capCost_0h*CRF + fixedGenOMcost)/(hours*CF_0h) + variableGenOMcost
    LCOEgen_6h = (capCost_6h*CRF + fixedGenOMcost)/(hours*CF_6h) + variableGenOMcost

    ## ROAD LCOE    
    roadDist = row.getValue("d_road")

    roadLCOE_0hr = (roadCost*CRF)*roadDist/(CF_0h*50*hours)     
    roadLCOE_6hr = (roadCost*CRF)*roadDist/(CF_6h*50*hours) 
    
    # Add calculations to fields:
    row.setValue("m_cf_0h", round(CF_0h,3))
    row.setValue("m_cf_6h", round(CF_6h,3))
    row.setValue("egen_0h", round_to_n(ElectGen_0h,3))
    row.setValue("egen_6h", round_to_n(ElectGen_6h,3)) 
    row.setValue("l_road_0h", round(roadLCOE_0hr,2)) 
    row.setValue("l_road_6h", round(roadLCOE_6hr,2)) 
    row.setValue("l_gen_0h", round(LCOEgen_0h,2))
    row.setValue("l_gen_6h", round(LCOEgen_6h,2))
    row.setValue("incap_0h", round(capacity_0h,0))
    row.setValue("incap_6h", round(capacity_6h,0))

    ###############################################################
    ## Calculate Transmission and/or Substation connection costs ##
    ###############################################################
    # Calculate Transmission and/or Substation connection costs: TransCost = [newTransCost + fixed OM ($/MW/km)] * transDist(km) * CRF/ (8760*CF) [=] $/MWh
    
    LCOEtotTrans_List = {"lt_tra_0h": [CF_0h, LCOEgen_0h, roadLCOE_0hr, "l_tra_0h"], \
                        "lt_tra_6h": [CF_6h, LCOEgen_6h, roadLCOE_6hr, "l_tra_6h"]}

    transDist = row.getValue("d_trans")
    
    for each in LCOEtotTrans_List:                        
        transLCOE = (transCost*transDist + subCost)*CRF/(LCOEtotTrans_List[each][0]*hours)        
        row.setValue(LCOEtotTrans_List[each][3], round(transLCOE,2))
        
        LCOEtotTrans = LCOEtotTrans_List[each][1] + LCOEtotTrans_List[each][2]  + transLCOE        
        row.setValue(each, round(LCOEtotTrans,2))

    ## SUBSTATION CALCULATIONS
    LCOEtotSub_List = {"lt_sub_0h": [CF_0h, LCOEgen_0h, roadLCOE_0hr, "l_sub_0h"], \
                        "lt_sub_6h": [CF_6h, LCOEgen_6h, roadLCOE_6hr, "l_sub_6h"]}

    subDist = row.getValue("d_sub")
    
    for each in LCOEtotSub_List:
        subLCOE = (transCost*subDist + subCost)*CRF/(LCOEtotSub_List[each][0]*hours)
        row.setValue(LCOEtotSub_List[each][3], round(subLCOE,2))
        
        LCOEtotSub = LCOEtotSub_List[each][1] + LCOEtotSub_List[each][2] + subLCOE
        row.setValue(each, round(LCOEtotSub,2))

    cursor.updateRow(row)

## DELETE EXTRA FIELDS
arcpy.DeleteField_management(zones, "l_sub_0h")
arcpy.DeleteField_management(zones, "l_tra_0h")
arcpy.DeleteField_management(zones, "l_road_0h")
arcpy.DeleteField_management(zones, "FREQUENCY")

'''
############################################
## COPY CALCULATED ZONES FC TO HARD DRIVE ##
############################################
'''
arcpy.CopyFeatures_management(zones, zoneOutput)

if projectOutput != "":
    arcpy.CopyFeatures_management(projects, projectOutput)
    


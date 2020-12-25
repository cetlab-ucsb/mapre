## Author Grace Wu and Ranjit Deshmukh
## University of California Santa Barbara
## MapRE Initiative
###################################################################################################################
## This script calculates capacity factors for wind using weibull parameters ##
## Users can process the entire input data set (e.g. GWA or a region) or a subset by providing an extent ##
## Users can break up the processing using object id's of the feature class if running into memory issues ##
###################################################################################################################

##--------------------------------Preamble ----------------------------------
import arcpy
import numpy
import scipy.stats as stats
import math
import time
import pandas as pd
import operator
import os
import glob
# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")
from arcpy import env
from arcpy.sa import *
from arcpy import sa
import arcpy.cartography as CA
arcpy.env.overwriteOutput = True
start_time = time.time()
print(start_time)

##--------------------- Input Paths, Local Parameters and Workspace------------------------

defaultInputWorkspace_3Tier = "R:\\users\\anagha.uppal\\MapRE\\Eswatini.gdb\\" ##^^ enter the path to your DEFAULT INPUT path

# workspace for saving outputs. set for each technology
defaultWorkspace = defaultInputWorkspace_3Tier ##^^ enter the path to your DEFAULT GDB path
if not os.path.exists(defaultWorkspace):
    print("outputFolder does not exist. Ensure you have selected the right date's resource potential feature class")

env.scratchWorkspace = defaultWorkspace # sets scratchworkspace to your output workspace
env.workspace = defaultWorkspace # sets environment workspace to your output workspace

hubHeight = "100m" ## Set to the hub height of the turbine or wind speed data - 50, 80, 100, 120...
turbine_rating = 2000 # in kW. Depends on input values of power curve


windSpeed = defaultInputWorkspace_3Tier + "Eswatini_wind_windspeed_100m_Projected_Clipped"
weibullScale = defaultInputWorkspace_3Tier + "Eswatini_wind_weibullA_100m_Projected_Clipped" ## Scale = a
weibullShape = defaultInputWorkspace_3Tier + "Eswatini_wind_weibullk_100m_Projected_Clipped" ## Shape = k
# elevationRaster = E:\\Spatial_Research\\MapRE\\srtmdem500p"
# temperatureRaster = "E:\\Spatial_Research\\MapRE\\worldClim_tempMean_30s_esri\\tmean_annprjc"
airDensity = defaultInputWorkspace_3Tier + "Eswatini_wind_airdensity_100m_Projected_Clipped" ## Shape = k ## Air density

## Output files
all_parameters_fname = "Eswatini_250_all_parameters_100m_ls" ## Wind speed, weibull params, air density
wind_cf_fname = "Eswatini_gwa3_250_wind_capacity_factors_no_losses_100m_ls" ## Wind speed, weibull params, air density, AND CFs

# Extent or regional boundary for clipping [comment out if processing entire wind speed data extent or preclipped data
limitExtent = "no"
bounds = "R:\\users\\anagha.uppal\MapRE\\country_bounds.gdb\\Eswatini"
boundsSuffix = "_ls"

## power curve csvs:
classI_csv = "R:\\users\\anagha.uppal\\MapRE\\windPowerCurves\\windPowerCurves_V7_V80_2MW_IA.csv"
classII_csv = "R:\\users\\anagha.uppal\\MapRE\\windPowerCurves\\windPowerCurves_V7_V100_2MW_IIB.csv"
classIII_csv = "R:\\users\\anagha.uppal\\MapRE\\windPowerCurves\\windPowerCurves_V7_V110_2MW_IIIA.csv"

# ## constants for estimating air density [not used for GWA analysis]:
# Po = 101.325*1000 #Pa: sea level standard atmospheric pressure
# g = 9.81 # m/s2: gravitational acceleration
# # environmental lapse rate (not used) 6.5 degC per 1000m elevation increase
# R = 287.058	# J/kg-K: Specific gas constant

##------------------------- Extract the data sets by extent ----------------------------------------
if limitExtent == "yes":
    print("Extracting wind input data using provided bounds")
    # wind speed
    windSpeed_filename = windSpeed.split("\\")[-1].split(".")[0].replace("-", "_") + boundsSuffix
    windSpeed = ExtractByMask(windSpeed, bounds)
    windSpeed.save(defaultWorkspace + windSpeed_filename)
    # weibull scale
    weibullScale_filename = weibullScale.split("\\")[-1].split(".")[0].replace("-", "_") + boundsSuffix
    weibullScale = ExtractByMask(weibullScale, bounds)
    weibullScale.save(defaultWorkspace + weibullScale_filename)
    # weibull shape
    weibullShape_filename = weibullShape.split("\\")[-1].split(".")[0].replace("-", "_") + boundsSuffix
    weibullShape = ExtractByMask(weibullShape, bounds)
    weibullShape.save(defaultWorkspace + weibullShape_filename)
    # air density
    airDensity_filename = airDensity.split("\\")[-1].split(".")[0].replace("-", "_") + boundsSuffix
    airDensity = ExtractByMask(airDensity, bounds)
    airDensity.save(defaultWorkspace + airDensity_filename)

#------------------------- create all wind parameters feature -----------------------------------

## Add wind speed
windSpeed_pts = arcpy.RasterToPoint_conversion(windSpeed, "in_memory//windSpeed_pts")
arcpy.AlterField_management(windSpeed_pts, 'grid_code', 'wind_speed', 'wind_speed')
print("Wind speed raster converted to feature - completed")

# Add Weibull parameters and air density to all parameters
weibullScale_pts = ExtractValuesToPoints(windSpeed_pts, weibullScale, "in_memory//weibullScale_pts")
arcpy.AlterField_management(weibullScale_pts, 'RASTERVALU', 'weibull_scale_A', 'weibull_scale_A')
print("Weibull scale raster added to wind speed feature - completed")
weibullShape_pts = ExtractValuesToPoints(weibullScale_pts, weibullShape, "in_memory//weibullShape_pts")
arcpy.AlterField_management(weibullShape_pts, 'RASTERVALU', 'weibull_shape_K', 'weibull_shape_K')
print("Weibull shape raster added to wind speed and weibull scale feature - completed")

## Add Air Density
allParameters = ExtractValuesToPoints(weibullShape_pts, airDensity, defaultWorkspace + all_parameters_fname)
arcpy.AlterField_management(allParameters, 'RASTERVALU', 'air_density', 'air_density')
print("Air density added to all parameters - completed")

# # Code for estimating air density from temperature and elevation
# weibullParams = arcpy.CopyFeatures_management(weibullWindSpeed, defaultInputWorkspace_Resource + dataSource + "_" + hubHeight + "_all")
#
# ## Sample the average elevation for each point using elevation raster:
# elevationSample = ExtractValuesToPoints(defaultInputWorkspace_Resource + dataSource + "_" + hubHeight + "_all", elevationRaster, defaultInputWorkspace_Resource + dataSource + "_" + hubHeight + "_elevation","NONE")
# arcpy.AlterField_management(elevationSample, 'RASTERVALU', 'elevation', 'elevation')
# #arcpy.JoinField_management(weibullParams, "OBJECTID", elevationSample, "OBJECTID", ["SRTMDEM500P_3TIERCLIP"])
# print "elevation extracting is complete"
#
# ## Sample the average temperature for each point using temperature raster:
# temperatureSample = ExtractValuesToPoints(elevationSample, temperatureRaster, defaultInputWorkspace_Resource + dataSource + "_" + hubHeight + "_elevTemp", "NONE")
# arcpy.AlterField_management(temperatureSample, 'RASTERVALU', 'tmean_Cx10', 'tmean_Cx10')
# #arcpy.JoinField_management(weibullParams, "OBJECTID", temperatureSample, "OBJECTID", ["TMEAN_ANNPRJC"])
# print "temperature sampling is complete"
#
# # Sample the wind speed at each point using the wind speed data:
# windSpeedSample = Sample(windSpeedRaster, weibullParams, defaultInputWorkspace_3Tier + "annual_weibull_a_k_80m_windSpeed","BILINEAR")
# arcpy.JoinField_management(weibullParams, "FID", windSpeedSample, "WEIBULLPARAMS", ["annual_windspeed_80m"])


## Read all wind parameters data if data already processed
allParameters = arcpy.CopyFeatures_management(defaultWorkspace + all_parameters_fname, "in_memory\\params")

airDensityBins = numpy.linspace(0.75, 1.25, 11)
## average wind speed in each class 1: 10, class 2: 8.5, class 3: 7.5
windClassSpeeds = numpy.asarray([0, 7.5, 8.5]) ## using the average wind speeds as the maximum wind speed
#windClassSpeeds = numpy.asarray([0, 8, 9.25])  ## using upper wind speed limits for class I and II
windDict = {1: "CF_ClsIII", 2: "CF_ClsII", 3: "CF_ClsI"}
windSpeedIncrements = numpy.linspace(0.5, 29.5, num=30)
increment = 1.0  # m/s the size of each "bin"

##--------------------- Load power curves ------------------------------
classI = pd.DataFrame(numpy.genfromtxt(classI_csv, delimiter=","), \
                      index=windSpeedIncrements,columns=numpy.arange(1, 12, 1))
classII = pd.DataFrame(numpy.genfromtxt(classII_csv, delimiter=","), \
                       index=windSpeedIncrements, columns=numpy.arange(1, 12, 1))
classIII = pd.DataFrame(numpy.genfromtxt(classIII_csv, delimiter=","), \
                        index=windSpeedIncrements, columns=numpy.arange(1, 12, 1))

powerCurvesList = [classI, classII, classIII]
powerCurvesFieldList = ["CF_ClsI", "CF_ClsII", "CF_ClsIII"]

##---------------------Calculate capacity factor------------------------

originalFields = [f.name for f in arcpy.ListFields(allParameters)]
fieldTypeDict = {"air_density": "DOUBLE", "CF_ClsI": "DOUBLE", "CF_ClsII": "DOUBLE", "CF_ClsIII": "DOUBLE", \
                 "turbineCls": "Text", "CF_turbCls": "DOUBLE", "maxCls": "Text", "CF_maxCls": "DOUBLE"}
fieldList = ["air_density", "CF_ClsI", "CF_ClsII", "CF_ClsIII", "turbineCls", "CF_turbCls", "maxCls",
             "CF_maxCls"]  ## list of all new fields to calculate below
for each in fieldList:
    if each not in originalFields:
        print("Adding " + each + " as new field")
        arcpy.AddField_management(allParameters, each, fieldTypeDict[
            each])  ## create fields in fieldList if not already in original project shapefile

#### USER INPUT: If all parameters feature data is large, break up processing into multiple files ####
start_id = 1 # Change this id if processing a subset of ids and using a different starting point
length_id = 150000
# Determine max object id or specify an end_id
max_id = arcpy.Statistics_analysis(allParameters, "in_memory\\max_id", [["OBJECTID", "MAX"]])
arcpy.Statistics_analysis(allParameters, defaultWorkspace + "max_id", [["OBJECTID", "MAX"]])
cursor = arcpy.da.SearchCursor(max_id, "MAX_OBJECTID")
for row in cursor:
    end_id = int(row[0])
# end_id = 500000
#### END USER INPUT ####

fileCount_start = math.ceil(start_id/length_id)
fileCount_end = math.ceil(end_id/length_id)
fileCount = numpy.arange(fileCount_start, fileCount_end + 1)

for fc in fileCount:
    print("Processing all parameters subset " + str(fc) + " from object ID " + str(start_id) + " to " + str(
                                          start_id + length_id - 1))
    allParameters_subset = arcpy.MakeFeatureLayer_management(allParameters, "allParameters_" + str(fc),
                                      ' "OBJECTID" >= ' + str(start_id) + ' AND ' + '"OBJECTID" <= ' + str(
                                          start_id + length_id - 1))
    #allParameters_subset = arcpy.CopyFeatures_management("allParameters_" + str(fc), "in_memory\\params")

    c = 0
    cursor = arcpy.UpdateCursor(allParameters_subset)
    for row in cursor:
        # print("row =" + str(c))
        FID = row.getValue("OBJECTID")
        K = row.getValue("weibull_shape_K")
        A = row.getValue("weibull_scale_A")
        wind_speed = row.getValue("wind_speed")
        air_density = row.getValue("air_density")

        #### If calculating air density from elevation and temperature data ####
        # elev_m = row.getValue("demgadm_m")
        # temp_C = row.getValue("tmean_Cx10") / 10  # since worldClim data has units of deg C*10
        # temp_K = temp_C + 273.15  # deg Kelvin
        # airDensity = (Po / (R * temp_K)) * math.exp((-g * elev_m) / (R * temp_K))  ## kg/m3
        # air density = std atmsospheric pressure (at sea level) / (gas constant*Temp) *
        # exp(-gravitational acc * elevation (m)/ (gas constant*temp))
        # row.setValue("airDensity", airDensity)
        ####

        airDensityRange = numpy.digitize([air_density], airDensityBins)
        if airDensityRange < 1:
            airDensityRange = numpy.asarray([1]) # If air density is below 0.75, it's likely a data error.
        windProb = stats.exponweib.pdf(x=windSpeedIncrements, a=1, c=K,
                                       scale=A)  ## Evaluate weibull distribution at windSpeedIncrement values
        i = 0
        CFbyTurbine = {}  ## Create empty
        for each in powerCurvesList:
            powerCurveValues = each[airDensityRange[0]]
            powerCurveValues_t = powerCurveValues.transpose()
            meanWindPower = sum(
                windProb * powerCurveValues_t * increment)  # calculate power output at each wind speed and sum them across all speeds
            CF = meanWindPower / turbine_rating  ## calculate CF using rated turbine = 2000 kW or 2 MW
            row.setValue(powerCurvesFieldList[i], CF)
            CFbyTurbine[powerCurvesFieldList[i]] = CF
            i = i + 1

        windIndex = numpy.digitize([wind_speed], windClassSpeeds)
        row.setValue("turbineCls", windDict[windIndex[0]]) # Turbine class selected based on avg wind speed
        row.setValue("CF_turbCls", CFbyTurbine[windDict[windIndex[0]]]) # CF of turbine class selected on avg wind speed
        row.setValue("maxCls", max(CFbyTurbine)) # Turbine class with max CF
        row.setValue("CF_maxCls", max(CFbyTurbine.values())) # CF of turbine with max CF

        cursor.updateRow(row)
        c = c + 1

    print("finished calculating all CFs for subset " + str(fc))
    arcpy.CopyFeatures_management(allParameters_subset, defaultWorkspace + wind_cf_fname + str(fc))
    if int(FID) < start_id + length_id - 1: break
    start_id = start_id + length_id


## Merge all parameters subset features [use all files and not just the subset]
fileCount_toMerge = numpy.arange(1, fileCount_end + 1)
allParameters_subsets_to_merge = []
for fc in fileCount_toMerge:
    fname = defaultWorkspace + wind_cf_fname + str(fc)
    allParameters_subsets_to_merge.append(fname)

if len(fileCount_toMerge) == 1:
    arcpy.CopyFeatures_management(allParameters_subsets_to_merge[0], defaultWorkspace + wind_cf_fname)
else:
    arcpy.Merge_management(allParameters_subsets_to_merge, defaultWorkspace + wind_cf_fname)
print("Merged all subsets")

## Delete subset files [Uncomment this code if subset files need to be deleted after merging]
for f_to_delete in allParameters_subsets_to_merge:
    arcpy.Delete_management(f_to_delete)
print("Deleted all subsets")

elapsed_time = (time.time() - start_time)/(60)
print(str(elapsed_time) + " minutes")


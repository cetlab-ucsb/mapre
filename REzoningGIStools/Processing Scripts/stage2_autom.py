
import arcpy
# import stage2_HardcodeCollect
import pandas as pd
import stage2_function

arcpy.env.workspace = workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\allTiers_nolulc_wind.gdb"

countries = {
    'DRC': 'DRC',
    'Angola': 'AO',
    'Botswana': 'BW',
    'Eswatini': 'SZ',
    'Lesotho': 'LS',
    'Mozambique': 'MZ',
    'Malawi': 'MW',
    'Namibia': 'NA',
    'South_Africa': 'SA',
    'Tanzania': 'TZ',
    'Zambia': 'ZM',
    'Zimbabwe': 'ZI',

}

featureclasses = arcpy.ListFeatureClasses()
print(workspace)
print(featureclasses)


def run_it(countryName, countryAbbr):
    # from Scripts import

    stage2_function.my_function()

    '''
    ############################################################################################################
    ## --------------------------------------- GET ALL INPUTS ----------------------------------------------- ##
    ############################################################################################################
    '''


    #####################
    ## USER SET INPUTS ##
    #####################

    defaultInputWorkspace = "R:\\users\\anagha.uppal\\MapRE\\"

    ## SPATIAL INPUTS

    suitableSites = workspace + "\\" + countryName  ## required
    if countryName == "DRC":
        suitableSites = workspace + "\\" + "Democratic_Republic_of_the_Congo"
    if countryName == "Eswatini":
        suitableSites = workspace + "\\" + "Swaziland"
    projectsOut = suitableSites + "_areas"  ##

    scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\Scratch.gdb"  ## required scratch GDB

    templateRaster = defaultInputWorkspace + countryName + ".gdb\\" + countryName + "_elevation500_DEMGADM_Projected_Clipped"  ## required
    countryBounds = defaultInputWorkspace + "country_bounds.gdb\\" + countryName  ## optional
    geoUnits = ""  ## optional

    # csvInput = arcpy.GetParameterAsText(3) ## required

    ## PARAMETERS

    fishnetSize = 5  ## in km

    fishnetDirectory = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS" + "\\" + countryName + \
                       "\\" + countryAbbr+ "_Outputs.gdb"
    print(fishnetDirectory)
    # Parameter: area above which to intersect (b)
    whereClauseMax = str(100)  ## 25'

    # Parameter: area below which to aggregate (d)
    whereClauseMin = str(5)  ## 5'

    # Parameter: threshold for minimum contiguous project area (a)
    whereClauseMinContArea = str(2)  ## 2'

    analysis = stage2_function.ProjectCreation(suitableSites, projectsOut, scratch,
                                               templateRaster, countryBounds, geoUnits, fishnetSize,
                                               fishnetDirectory, whereClauseMax, whereClauseMin, whereClauseMinContArea)
    analysis.createProjectAreas()


for i in range(len(featureclasses)-1):
    previous_country = featureclasses[i]
    if previous_country == "Democratic_Republic_of_the_Congo":
        previous_country = "DRC"
    if previous_country == "Swaziland":
        previous_country = "Eswatini"
    new_country = featureclasses[i+1]
    print(previous_country, " ", new_country)
    if new_country == "Democratic_Republic_of_the_Congo":
        new_country = "DRC"
    if new_country == "Swaziland":
        new_country = "Eswatini"

    run_it(new_country, countries.get(new_country))
    print("Finished " + new_country)

previous_country = featureclasses[len(featureclasses)-1]
if previous_country == "Democratic_Republic_of_the_Congo":
    previous_country = "DRC"
if previous_country == "Swaziland":
    previous_country = "Eswatini"
new_country = featureclasses[0]
print(previous_country, " ", new_country)
if new_country == "Democratic_Republic_of_the_Congo":
    new_country = "DRC"
if new_country == "Swaziland":
    new_country = "Eswatini"


run_it(new_country, countries.get(new_country))
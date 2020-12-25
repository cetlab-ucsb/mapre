
import arcpy
# import stage2_HardcodeCollect
import pandas as pd
import import_functions.stage2_function as stage2

arcpy.env.workspace = workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\allTiers_wind.gdb"
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

featureclasses = [fc for fc in arcpy.ListFeatureClasses() if not ("areas" in fc)]
print(workspace)
print(featureclasses)


def run_it(countryName, countryAbbr):
    # from Scripts import

    stage2.my_function()

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

    templateRaster = defaultInputWorkspace + "SAPP.gdb\\" + "SAPP_elevation500_DEMGADM_Projected_Clipped"  ## required
    countryBounds = defaultInputWorkspace + "country_bounds.gdb\\" + countryName  ## optional
    geoUnits = ""  ## optional

    # csvInput = arcpy.GetParameterAsText(3) ## required

    ## PARAMETERS

    fishnetSize = 5  ## in km

    # fishnetDirectory = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\SAPP_Outputs.gdb"
    fishnetDirectory = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS" + "\\" + countryName + \
                       "\\" + countryAbbr+ "_Outputs.gdb"
    print(fishnetDirectory)
    # Parameter: area above which to intersect (b)
    whereClauseMax = str(60)  ## 25'

    # Parameter: area below which to aggregate (d)
    # whereClauseMin = str(5)  ## 5'

    # Parameter: threshold for minimum contiguous project area (a)
    whereClauseMinContArea = str(2)  ## 2'

    analysis = stage2.ProjectCreation(suitableSites, projectsOut, scratch,
                                               templateRaster, countryBounds, geoUnits, fishnetSize,
                                               fishnetDirectory, whereClauseMax, whereClauseMinContArea)
    analysis.createProjectAreas()


for i in range(len(featureclasses)):
    country = featureclasses[i]
    if country == "Democratic_Republic_of_the_Congo":
        country = "DRC"
    if country == "Swaziland":
        country = "Eswatini"
    print(country)

    run_it(country, countries.get(country))
    print("Finished " + country)
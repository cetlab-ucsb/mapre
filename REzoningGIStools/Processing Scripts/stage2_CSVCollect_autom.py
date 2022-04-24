
import arcpy
# import stage2_HardcodeCollect
import pandas as pd
import import_functions.stage2_function as stage2

#####################
## USER SET INPUTS ##
#####################

csv_file = pd.read_csv(r"D:\mmeng\mapre\RequiredCSVs\stage2_input_india_solar.csv", header=None)

# arcpy.env.workspace = workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\allTiers_wind.gdb"
arcpy.env.workspace = workspace = str(csv_file[1][0])
# countries = {
#     'DRC': 'DRC',
#     'Angola': 'AO',
#     'Botswana': 'BW',
#     'Eswatini': 'SZ',
#     'Lesotho': 'LS',
#     'Mozambique': 'MZ',
#     'Malawi': 'MW',
#     'Namibia': 'NA',
#     'South_Africa': 'SA',
#     'Tanzania': 'TZ',
#     'Zambia': 'ZM',
#     'Zimbabwe': 'ZI',
#
# }

featureclasses = [fc for fc in arcpy.ListFeatureClasses() if not ("suitability" in fc)]
print(workspace)
print(featureclasses)


def run_it(countryName):
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

    ## SPATIAL INPUTS

    suitableSites = workspace + "\\" + countryName  ## required

    projectsOut = suitableSites + "_areas"  ## required

    scratch = str(csv_file[1][2])  ## required scratch GDB

    templateRaster = str(csv_file[1][3])  ## required

    countryBounds = str(csv_file[1][4])  ## required

    geoUnits = str(csv_file[1][5])  ## optional

    # csvInput = arcpy.GetParameterAsText(3) ## required

    ## PARAMETERS

    fishnetSize = float(csv_file[1][6])  ## in km

    fishnetDirectory = str(csv_file[1][7])

    # Parameter: area above which to intersect (b)
    whereClauseMax = str(csv_file[1][8])  ## 25'

    # Parameter: area below which to aggregate (d)
    # whereClauseMin = str(csv_file[1][9]) ## 5'

    # Parameter: threshold for minimum contiguous project area (a)
    whereClauseMinContArea = str(csv_file[1][9])  ## 2'

    analysis = stage2.ProjectCreation(suitableSites, projectsOut, scratch,
                                               templateRaster, countryBounds, geoUnits, fishnetSize,
                                               fishnetDirectory, whereClauseMax, whereClauseMinContArea)
    analysis.createProjectAreas()


for i in range(len(featureclasses)):
    country = featureclasses[i]
    # if country == "Democratic_Republic_of_the_Congo":
    #     country = "DRC"
    # if country == "Swaziland":
    #     country = "Eswatini"
    print(country)

    run_it(country)
    print("Finished " + country)
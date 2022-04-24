
import arcpy
import pandas as pd
import import_functions.stage3_function as stage3

arcpy.env.overwriteOutput = True

csv_file = pd.read_csv(r"D:\mmeng\mapre\RequiredCSVs\stage3_input_india_solar.csv", header=None)
resource = str(csv_file[1][0])
arcpy.env.workspace = workspace = str(csv_file[1][1])

# arcpy.env.workspace = workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\human_wind.gdb"
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
# }

featureclasses = arcpy.ListFeatureClasses("*_areas")
print(workspace)
print(featureclasses)

def run_it(countryName):
    # from Scripts import
    import arcpy

    stage3.my_function()

    '''
    ############################################################################################################
    ## --------------------------------------- GET ALL INPUTS ----------------------------------------------- ##
    ############################################################################################################
    '''
    #####################
    ## USER SET INPUTS ##
    #####################

    # technology = arcpy.GetParameterAsText(0) ## required

    yourSpace = "R:\\users\\anagha.uppal\\MapRE\\"

    ## SPATIAL INPUTS
    projectsIn = workspace + "\\" + countryName  ##
    # if countryName == "DRC":
    #     projectsIn = workspace + "\\" "Democratic_Republic_of_the_Congo_areas"
    # if countryName == "Eswatini":
    #     projectsIn = workspace + "\\" "Swaziland_areas"  ## required

    projectsOut = str(csv_file[1][2]) + "\\" + countryName + "_attr"  ##
    resourceInput = str(csv_file[1][3])  ## MUST BE A RASTER
    csvInput = str(csv_file[1][4])  ## required
    templateRaster = str(csv_file[1][5])  ## required
    scratch = str(csv_file[1][6])

    ################
    ## PARAMETERS ##
    ################

    RQtype = csv_file[1][7]  ## capacityFactor" or "windPowerDensity"
    transmissionDistMultiplier = float(csv_file[1][8])
    cellSize = int(csv_file[1][9])  ## 500
    largestArea = int(csv_file[1][10])  ## 500

    ## COSTS
    capCost = int(csv_file[1][11])
    variableGenOMcost = int(csv_file[1][12])
    fixedGenOMcost = int(csv_file[1][13])
    omer = int(csv_file[1][14])  # Fixed O&M costs escalation rate

    effLoss = float(
        csv_file[1][15])  ## Assume wind losses (15%) without outage rate (2%). So default value should be 0.85;
    outageRate = float(csv_file[1][
                           16])  ## solar PV only # RD: for both wind and solar. Give option to user to set this to zero for the IRENA dataset.
    cfdr = float(csv_file[1][17])  # Capacity factor degradation rate

    transCost = int(csv_file[1][18])
    subCost = int(csv_file[1][19])
    roadCost = int(csv_file[1][20])
    discountRate = float(csv_file[1][21])
    plantLifetime = int(csv_file[1][22])

    ## OTHERS
    powerDensity = int(csv_file[1][23])
    landUseDiscount = float(csv_file[1][24])

    analysis = stage3.Attributes(resource, projectsIn, projectsOut, resourceInput, csvInput, templateRaster,
                                          scratch, RQtype, transmissionDistMultiplier, cellSize, largestArea, capCost,
                                          variableGenOMcost, fixedGenOMcost, omer, effLoss, outageRate, cfdr,
                                          transCost, subCost, roadCost, discountRate, plantLifetime, powerDensity,
                                          landUseDiscount)
    analysis.addAttributes()


# First, changing, country to process
for i in range(len(featureclasses)):
    country = featureclasses[i]
    # if country == "Democratic_Republic_of_the_Congo":
    #     country = "DRC"
    # if country == "Swaziland":
    #     country = "Eswatini"
    print(country)

    run_it(country)
    print("Finished " + country)

# for i in range(len(featureclasses)):
#     csv_path = "R:\\users\\anagha.uppal\\MapRE\\RequiredCSVs\\inputs_projectAreaAttributesw.csv"
#     previous_country = featureclasses[i][:-6]
#     if previous_country == "Democratic_Republic_of_the_Congo":
#         previous_country = "DRC"
#     if previous_country == "Swaziland":
#         previous_country = "Eswatini"
#     new_country = featureclasses[i+1][:-6]
#     print(previous_country, " ", new_country)
#     if new_country == "Democratic_Republic_of_the_Congo":
#         new_country = "DRC"
#     if new_country == "Swaziland":
#         new_country = "Eswatini"
#
#     suitfile = pd.read_csv(csv_path)
#     # First, changing, country to process
#     for i in suitfile:
#         if pd.notna(suitfile[i][2]):
#             if previous_country in suitfile[i][2]:
#                 suitfile[i][2] = suitfile[i][2].replace(previous_country, new_country)
#     suitfile.to_csv(csv_path, index=False)
#
#     run_it(new_country, countries.get(new_country))
#     print("Finished " + new_country)
#
# previous_country = featureclasses[len(featureclasses)-1][:-6]
# if previous_country == "Democratic_Republic_of_the_Congo":
#     previous_country = "DRC"
# if previous_country == "Swaziland":
#     previous_country = "Eswatini"
# new_country = featureclasses[0][:-6]
# print(previous_country, " ", new_country)
# if new_country == "Democratic_Republic_of_the_Congo":
#     new_country = "DRC"
# if new_country == "Swaziland":
#     new_country = "Eswatini"
#
# suitfile = pd.read_csv(csv_path)
#
# # First, changing, country to process
# for i in suitfile:
#     if pd.notna(suitfile[i][2]):
#         if previous_country in suitfile[i][2]:
#             suitfile[i][2] = suitfile[i][2].replace(previous_country, new_country)
# suitfile.to_csv(csv_path, index=False)
#
# run_it(new_country, countries.get(new_country))
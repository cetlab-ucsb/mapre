
import arcpy
import pandas as pd
import stage3_function

arcpy.env.overwriteOutput = True

arcpy.env.workspace = workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\human_wind.gdb"
resource = "wind"
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

featureclasses = arcpy.ListFeatureClasses("*_areas")
print(workspace)
print(featureclasses)

def run_it(countryName, countryAbbr):
    # from Scripts import
    import arcpy

    stage3_function.my_function()

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
    projectsIn = workspace + "\\" + countryName + "_areas"  ##
    if countryName == "DRC":
        projectsIn = workspace + "\\" "Democratic_Republic_of_the_Congo_areas"
    if countryName == "Eswatini":
        projectsIn = workspace + "\\" "Swaziland_areas"  ## required

    projectsOut = projectsIn + "_attr"  ##
    resourceInput = yourSpace + countryName + ".gdb\\" + countryName + "_wind_CF_calc_Projected_Clipped"  ## MUST BE A RASTER e.g. wind_CF_calc
    csvInput = yourSpace + "RequiredCSVs\\inputs_projectAreaAttributesw.csv"  ## required
    # templateRaster = yourSpace + countryName + ".gdb\\" + countryName + \
    #                  "_elevation500_DEMGADM_Projected_Clipped"  ## required
    templateRaster = yourSpace + "SAPP.gdb\\SAPP_elevation500_DEMGADM_Projected_Clipped"  ## required
    scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\Scratch.gdb"

    ################
    ## PARAMETERS ##
    ################

    RQtype = "Capacity Factor"  ## capacityFactor" or "kWh/m2-day" or "Wind speed (m/s)"
    transmissionDistMultiplier = 1.3
    cellSize = int(500)  ## 500
    largestArea = 25  ## 500
    transCost = 990
    subCost = 71000
    roadCost = 407000
    discountRate = 0.1
    if resource == "solar":
        ## COSTS
        capCost = 2000000 ## changes between wind and solar
        variableGenOMcost = 4 ## changes between wind and solar
        fixedGenOMcost = 50000 ## changes between wind and solar
        omer = 0  # Fixed O&M costs escalation rate

        effLoss = 0  ## Assume wind losses (15%) without outage rate (2%). So default value should be 0.85;
        outageRate = 0.0  ## changes between wind and solar
        cfdr = 0  # Capacity factor degradation rate

        plantLifetime = 25

        ## OTHERS
        powerDensity = 30  # Land use efficiency (MW/km2) ## changes between wind and solar
        landUseDiscount = 0.1 ## changes between wind and solar
    if resource == "wind":
        ## COSTS
        capCost = 1700000  ## changes between wind and solar
        variableGenOMcost = 0  ## changes between wind and solar
        fixedGenOMcost = 60000  ## changes between wind and solar
        omer = 0  # Fixed O&M costs escalation rate

        effLoss = 0.15  ## Assume wind losses (15%) without outage rate (2%).
        outageRate = 0.02  ## changes between wind and solar
        cfdr = 0  # Capacity factor degradation rate

        plantLifetime = 25

        ## OTHERS
        powerDensity = 9  # Land use efficiency (MW/km2) ## changes between wind and solar
        landUseDiscount = 0.25  ## changes between wind and solar

    analysis = stage3_function.Attributes(resource, projectsIn, projectsOut, resourceInput, csvInput, templateRaster,
                                          scratch, RQtype, transmissionDistMultiplier, cellSize, largestArea, capCost,
                                          variableGenOMcost, fixedGenOMcost, omer, effLoss, outageRate, cfdr,
                                          transCost, subCost, roadCost, discountRate, plantLifetime, powerDensity,
                                          landUseDiscount)
    analysis.addAttributes()


for i in range(len(countries)-1):
    csv_path = "R:\\users\\anagha.uppal\\MapRE\\RequiredCSVs\\inputs_projectAreaAttributesw.csv"
    previous_country = featureclasses[i][:-6]
    if previous_country == "Democratic_Republic_of_the_Congo":
        previous_country = "DRC"
    if previous_country == "Swaziland":
        previous_country = "Eswatini"
    new_country = featureclasses[i+1][:-6]
    print(previous_country, " ", new_country)
    if new_country == "Democratic_Republic_of_the_Congo":
        new_country = "DRC"
    if new_country == "Swaziland":
        new_country = "Eswatini"

    suitfile = pd.read_csv(csv_path)
    # First, changing, country to process
    for i in suitfile:
        if pd.notna(suitfile[i][2]):
            if previous_country in suitfile[i][2]:
                suitfile[i][2] = suitfile[i][2].replace(previous_country, new_country)
    suitfile.to_csv(csv_path, index=False)

    run_it(new_country, countries.get(new_country))
    print("Finished " + new_country)

previous_country = featureclasses[len(featureclasses)-1][:-6]
if previous_country == "Democratic_Republic_of_the_Congo":
    previous_country = "DRC"
if previous_country == "Swaziland":
    previous_country = "Eswatini"
new_country = featureclasses[0][:-6]
print(previous_country, " ", new_country)
if new_country == "Democratic_Republic_of_the_Congo":
    new_country = "DRC"
if new_country == "Swaziland":
    new_country = "Eswatini"

suitfile = pd.read_csv(csv_path)

# First, changing, country to process
for i in suitfile:
    if pd.notna(suitfile[i][2]):
        if previous_country in suitfile[i][2]:
            suitfile[i][2] = suitfile[i][2].replace(previous_country, new_country)
suitfile.to_csv(csv_path, index=False)

run_it(new_country, countries.get(new_country))
##--------------------------------Preamble ----------------------------------
import arcpy, numpy, math, time, os, csv
# import scipy.stats as stats
from collections import OrderedDict

start_time = time.time()
print(start_time)
# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")
from arcpy import env

arcpy.env.overwriteOutput = True


def my_function():
    print("Hello World")


# Defining a class
class Attributes:
    def __init__(self, technology, projectsIn, projectsOut, resourceInput, csvInput, templateRaster,
                 scratch, RQtype, transmissionDistMultiplier, cellSize, largestArea, capCost,
                 variableGenOMcost, fixedGenOMcost, omer, effLoss, outageRate, cfdr,
                 transCost, subCost, roadCost, discountRate, plantLifetime, powerDensity, landUseDiscount):
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
        self.technology = str(technology)  ##"Solar PV", "Wind"
        self.projectsIn = str(projectsIn)  ##
        self.projectsOut = str(projectsOut)  ##
        self.resourceInput = str(resourceInput)  ## MUST BE A RASTER
        self.csvInput = str(csvInput)  ## required
        self.templateRaster = str(templateRaster)  ## required
        self.scratch = str(scratch)

        ################
        ## PARAMETERS ##
        ################

        self.RQtype = str(RQtype)  ## capacityFactor" or "windPowerDensity" or "kWh/m2-day"
        self.transmissionDistMultiplier = transmissionDistMultiplier ## 1.3
        self.cellSize = int(cellSize)  ## 500
        self.largestArea = largestArea  ## 25

        ## COSTS
        self.capCost = capCost ## 1700000
        self.variableGenOMcost = variableGenOMcost ## 0
        self.fixedGenOMcost = fixedGenOMcost ## 50000
        self.omer = omer  # Fixed O&M costs escalation rate ## 0

        self.effLoss = 1 - effLoss  ## Assume wind losses (15%) without outage rate (2%). So default value should be 0.85; ## 0.17
        self.outageRate = 1 - outageRate  ## 0.02 ## solar PV only # RD: for both wind and solar. Give option to user to set this to zero for the IRENA dataset.
        self.cfdr = cfdr  ## 0 # Capacity factor degradation rate

        self.transCost = transCost ## 990
        self.subCost = subCost ## 71000
        self.roadCost = roadCost ## 407000
        self.discountRate = discountRate ## 0.01
        self.plantLifetime = plantLifetime ## 25

        ## OTHERS
        self.powerDensity = powerDensity  # Land use efficiency (MW/km2) ## 9
        self.landUseDiscount = landUseDiscount ## 0.01

    def addAttributes(self):

        hours = 8760
        maxInsol = 1000
        maxInsol_kWh = 24

        ## Calculate total losses
        losses = self.outageRate * self.effLoss  # RD 052019: Add outage rates. User can choose to set this as 1

        ### FUNCTIONS
        def CSPcfCalc_6h(DNI, units):  ## for 6h storage
            if units == "kWh/m2-day":
                DNI_kWhm2y_6h = DNI * 365  ## convert to kWh/m2/year
            if units == "W/m2":
                DNI_kWhm2y_6h = DNI * (365 * 24 / 1000)  ## convert to kWh/m2/year
            CF_6h = (33.431 * math.log(
                DNI_kWhm2y_6h) - 212.57) / 100  # to make it a fraction # RD; Does this include outage rate? losses?
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
        # arcpy.env.extent = countryBounds
        # arcpy.env.mask = countryBounds
        arcpy.env.snapRaster = self.templateRaster
        arcpy.env.cellSize = self.templateRaster

        env.scratchWorkspace = self.scratch
        #arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\SA_Outputs.gdb"

        ## COPY SUITABLE SITES FEATURE CLASS TO MEMORY
        projects = arcpy.CopyFeatures_management(self.projectsIn, "in_memory/projects")  ## in_memory/

        '''
        ##############
        ## Read CSV ##
        ##############
        '''
        with open(self.csvInput, "rt") as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            fields = next(reader)
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
                arcpy.CalculateField_management(projects, dist_fieldName, "!NEAR_DIST!/1000 * " + str(distMultiplier),
                                                "PYTHON_9.3")
                arcpy.DeleteField_management(projects, "NEAR_DIST")
                arcpy.AddMessage(dist_fieldName + " distance calculations are complete")
        '''
        #################
        ## ZONAL STATS ##
        #################
        '''
        ## Check whether projects file is a fc in fgdb or a shapefile and set the id field accordingly
        if self.projectsIn.find(
                ".shp") == -1:  ## .find is a Python method for finding a substring within a string (-1 indicates string not found)
            idField = "OBJECTID"
        else:
            idField = "FID"

        ## Convert projects file to raster
        projects_raster = arcpy.PolygonToRaster_conversion(projects, idField, "in_memory/raster", \
                                                           "MAXIMUM_AREA", "", self.cellSize)

        arcpy.CopyRaster_management(projects_raster, self.projectsOut + "_raster")

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
                                        self.resourceInput, "in_memory/RQ", "DATA", "MEAN")
        # Join zonal statistics table of "MEAN" values to target project polygon, projects
        arcpy.JoinField_management(projects, idField, \
                                   "in_memory/RQ", "Value", "MEAN")
        if self.RQtype == "Capacity Factor":
            arcpy.AddField_management(projects, "m_cf", "DOUBLE")
            ## Calculate the final CF field from mean by applying the wind losses value
            arcpy.CalculateField_management(projects, "m_cf", "!MEAN!", "PYTHON_9.3")

        if self.RQtype == "W/m2":
            arcpy.AddField_management(projects, "m_rq_wm2", "DOUBLE")
            ## Calculate the final CF field from mean by applying the wind losses value
            arcpy.CalculateField_management(projects, "m_rq_wm2", "!MEAN!", "PYTHON_9.3")

        if self.RQtype == "kWh/m2-day" and (self.technology == "Solar PV" or self.technology == "CSP"):
            arcpy.AddField_management(projects, "m_rq_kwh", "DOUBLE")
            ## Calculate the final CF field from mean by applying the wind losses value
            arcpy.CalculateField_management(projects, "m_rq_kWh", "!MEAN!", "PYTHON_9.3")

        if self.RQtype == "Wind speed (m/s)" and self.technology == "Wind":
            arcpy.AddField_management(projects, "m_rq_ms", "DOUBLE")
            ## Calculate the final CF field from mean by applying the wind losses value
            arcpy.CalculateField_management(projects, "m_rq_ms", "!MEAN!", "PYTHON_9.3")

        arcpy.DeleteField_management(projects, "MEAN")
        arcpy.AddMessage("Zonal stats for capacity factor is complete")

        # arcpy.CopyFeatures_management(projects, projectsOut)

        '''
        ################
        ## ADD FIELDS ##
        ################
        '''
        ## Add fields called "CF", "ElectGen", "TransCost", "RoadCost"
        # originalFields = []
        # for field in fields:
        #        originalFields.append(str(field.name)) ## get the field names in the projects shapefile

        fieldList = ["m_cf", "egen", "incap", "l_tra", "l_sub", "l_road", \
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
        CRF = (self.discountRate * (1 + self.discountRate) ** self.plantLifetime) / (
                ((1 + self.discountRate) ** self.plantLifetime) - 1)  # or the fixed charge factor

        #### RD modification 05272019 ####
        # Discount rate modified with CF degradation rate
        dr_mod_cf_degrad = (self.discountRate + self.cfdr) / (1 - self.cfdr)
        # CRF modified for CF degradation
        crf_mod_cf_degrad = (dr_mod_cf_degrad * (1 + dr_mod_cf_degrad) ** self.plantLifetime) / (
                ((1 + dr_mod_cf_degrad) ** self.plantLifetime) - 1)

        # Discount rate modified with OM escalation rate
        dr_mod_omer = (self.discountRate - self.omer) / (1 + self.omer)
        # CRF modified for O&M escalation
        crf_mod_omer = (dr_mod_omer * (1 + dr_mod_omer) ** self.plantLifetime) / (((1 + dr_mod_omer) ** self.plantLifetime) - 1)
        #### RD modification end ####

        cursor = arcpy.UpdateCursor(projects)
        # cursor = arcpy.da.UpdateCursor(projects, "*")
        for row in cursor:
            area = row.getValue("Area")
            areaRatio = area / self.largestArea
            if inputDataPath["d_road"][0] == "yes":  ## If road file exists
                roadDist = row.getValue("d_road")
            else:
                roadDist = 0

            ## If resource quality type is capacity factor then simply retrieve the CF from the attribute table
            if self.RQtype == "Capacity Factor":
                CF = row.getValue("m_cf") * losses

            else:
                ## Calculate Capacity factors
                if self.technology == "Solar PV":
                    if self.RQtype == "W/m2":
                        RQ_row = row.getValue("m_rq_wm2")
                        CF = (RQ_row / (maxInsol)) * losses  # derating factor*ResourceQuality/maxInsolation
                    if self.RQtype == "kWh/m2-day":
                        RQ_row = row.getValue("m_rq_kwh")
                        CF = (RQ_row / (maxInsol_kWh)) * losses  # derating factor*ResourceQuality/maxInsolation

                if self.technology == "CSP":
                    if self.RQtype == "W/m2":
                        RQ_row = row.getValue("m_rq_wm2")
                        CF = CSPcfCalc_6h(RQ_row, self.RQtype) * losses
                    if self.RQtype == "kWh/m2-day":
                        RQ_row = row.getValue("m_rq_kwh")
                        CF = CSPcfCalc_6h(RQ_row, self.RQtype) * losses

                if self.technology == "Wind":
                    if self.RQtype == "W/m2":
                        RQ_row = row.getValue("m_rq_wm2")
                        CF = self.sdfaf * losses

                    if self.RQtype == "Wind speed (m/s)":
                        RQ_row = row.getValue("m_rq_kwh")

                ## Set the calculate Capacity factor value
                row.setValue("m_cf", CF)

            LCOEgen = (self.capCost * CRF + self.fixedGenOMcost) / (8760 * CF) + self.variableGenOMcost

            #### RD modification 05272019 #####
            # NPV of electricity generation
            electGenPkWPyr = CF * hours
            electGenPkW_npv = electGenPkWPyr / (1 - self.cfdr) / crf_mod_cf_degrad

            # NPV of O&M fixed
            fixedGenOMcost_npv = self.fixedGenOMcost / (1 + self.omer) / crf_mod_omer

            # NPV of O&M variable
            variableGenOMcost_npv = self.variableGenOMcost * CF / (1 - self.cfdr) / crf_mod_cf_degrad

            # LCOE generation
            LCOEgenNew = (self.capCost + fixedGenOMcost_npv + variableGenOMcost_npv) / electGenPkW_npv

            #### RD modification end ####

            capacity = self.powerDensity * area * self.landUseDiscount

            #### GW modification 06242019 ####
            ## Calculate average annual electricity generation
            electGen_yr1 = capacity * CF * hours

            ## Create array of annual generation with degradation
            def calcElecGen(n, p, r):
                # return 1752000*(1-0.005)**n-1  # np.exp() is a built-in ufunc
                return p * (numpy.power((1 - r), n)) - 1

            electGen_new = numpy.mean(calcElecGen(range(0, int(self.plantLifetime), 1), electGen_yr1, self.cfdr))
            #### GW modification end ####

            electGen = capacity * CF * hours

            roadLCOE = (self.roadCost * CRF) * roadDist / (CF * 50 * hours)
            roadLCOEnew = (self.roadCost * roadDist) / 50 / electGenPkW_npv  # RD 05272019: Verify if roadLCOEnew is same as roadLCOE with 0 degradation. If same, change roadLCOEnew to roadLCOE.

            ## Add calculations to fields:

            row.setValue("egen", electGen_new)
            row.setValue("l_road", roadLCOEnew)
            row.setValue("l_gen", LCOEgenNew)
            row.setValue("incap", capacity)

            ## Calculate Transmission and/or Substation connection costs:
            ## TransCost = [newTransCost + fixed OM ($/MW/km)] * transDist(km) * CRF/ (8760*CF) [=] $/MWh

            if inputDataPath["d_trans"][0] == "yes":
                transDist = row.getValue("d_trans") * self.transmissionDistMultiplier
                transLCOE = (self.transCost * transDist + self.subCost) * CRF / (CF * hours)
                transLCOEnew = (self.transCost * transDist + self.subCost) / electGenPkW_npv  # RD 05272019: Verify if transLCOEnew is same as transLCOE with 0 degradation. If same, change transLCOEnew to transLCOE.
                LCOEtotTrans = LCOEgen + roadLCOE + transLCOE
                LCOEtotTransNew = LCOEgenNew + roadLCOEnew + transLCOEnew
                row.setValue("lt_tra", LCOEtotTransNew)
                row.setValue("l_tra", transLCOEnew)

            if inputDataPath["d_sub"][0] == "yes":
                subDist = row.getValue("d_sub") * self.transmissionDistMultiplier
                subLCOE = (self.transCost * subDist + self.subCost) * CRF / (CF * hours)
                subLCOEnew = (self.transCost * subDist + self.subCost) / electGenPkW_npv  # RD 05272019: Verify if subLCOEnew is same as subLCOE with 0 degradation. If same, change subLCOEnew to subLCOE.
                LCOEtotSub = LCOEgen + roadLCOE + subLCOE
                LCOEtotSubNew = LCOEgenNew + roadLCOEnew + subLCOEnew
                row.setValue("lt_sub", LCOEtotSubNew)
                row.setValue("l_sub", subLCOEnew)  ## calculate the "SubCost" using the chosen turbine"

            cursor.updateRow(row)

        ## COPY CALCULATED PROJECTS TO HARD DRIVE
        arcpy.CopyFeatures_management(projects, self.projectsOut)

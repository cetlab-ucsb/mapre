#-------------------------------------------------------------------------------
# Name:         GenerateReservoirs
# Purpose:      Develop dam reservoirs & calculate volume from DEM & dam points
#
# Author:      Erik Martin, emartin@tnc.org
#
# Created:     March 3, 2014
#-------------------------------------------------------------------------------

# Notes:
# preferably all files in a gdb
# workspace must be a gdb
# project all files to distance rather than degrees units - m
# cell size
# clip all input files (vector and raster) to same extent
# polygontoraster on line 79 causes problems for me. I did manually in software
# if dams not in gdb, i.e. .shp, must replace damsName variable without the .shp part
# script needs more checks overall like only create if not Exists
# need a scratch workspace
# uid can have spaces - replace wit underscore
# best to shorten uidfield to the first few letters at the beginning which cannot get messed up - no spaces, so punc

import arcpy
import sys
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

arcpy.env.overwriteOutput = True
workspace = r"R:\users\anagha.uppal\MapRE\hydropower\hydro.gdb" # must be a gdb
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace

def main():
    try:
        DEM = r"R:\users\anagha.uppal\MapRE\hydropower\hydro.gdb\DEM_Zambezi"
        dams = r"R:\users\anagha.uppal\MapRE\hydropower\hydro.gdb\dams_ZM"
        uIDField = "Plantname_short"
        heightField = "Head_m"
        moveDamDist = "200" # Check cell precision
        zFactor = ""
        cleanUp = False
        skip = False

        damsName = dams.split("\\")[-1].strip()

        arcpy.env.extent = DEM
        arcpy.env.mask = DEM

        arcpy.Compact_management(workspace)

        if not skip:
            # Create integer ID for dams
            # arcpy.AddField_management(dams, "emID", "SHORT")
            # emID = 1
            # with arcpy.da.UpdateCursor(dams, "emID") as rows:
            #     for row in rows:
            #         row[0] = emID
            #         rows.updateRow(row)
            #         emID += 1

            # create filled DEM
            # arcpy.AddMessage("Filling DEM sinks...")
            # print("Filling DEM sinks...")
            # outFill = Fill(DEM)
            # outFill.save("DEMFilled")
            # DEMFilled = "DEMFilled"
            # arcpy.CalculateStatistics_management(DEMFilled)
            DEMFilled = DEM # FIX
            # create FDR - used to create watershed mask
            arcpy.AddMessage("Creating flow direction raster...")
            print("Creating flow direction raster...")
            outFDR = FlowDirection(DEMFilled)
            outFDR.save("FDR")
            FDR = "FDR"

            # Create FAC grid for moving dam to highest volume location
            arcpy.AddMessage("Creating flow accumulation raster...")
            print("Creating flow accumulation raster...")
            outFAC = FlowAccumulation(FDR)
            outFAC.save("FAC")
            FAC = "FAC"

        else:
            DEMFilled = DEM
            FDR = "FDR"
            FAC = "FAC"
            # damsBuff_gr = "damsBuff_gr"
            # FACZoneStats = "FACZoneStats"
            # movedDams = "movedDams"
            # dams = "movedDams_pts"
            # dams = "dams_elev"


        arcpy.AddMessage("Moving dams to thalweg...")
        print("Moving dams to thalweg...")
        arcpy.Buffer_analysis(dams, "damsBuffer", moveDamDist)
        # cellsize_dem = arcpy.GetRasterProperties_management(DEM, "CELLSIZEX")
        # cellsize = cellsize_dem.getOutput(0)
        arcpy.PolygonToRaster_conversion(in_features="damsBuffer", value_field="emID",
                                         out_rasterdataset="damsBuff_gr", cell_assignment="CELL_CENTER",
                                         cellsize=DEM)
        damsBuff_gr = "damsBuff_gr"

        # Buffer dam points to get max FAC within buffer
        outZonalStats = ZonalStatistics(damsBuff_gr, "VALUE", FAC, "MAXIMUM", "DATA")
        outZonalStats.save("FACZoneStats")
        FACZoneStats = "FACZoneStats"

        newLocs = SetNull((Raster(FAC) != Raster(FACZoneStats)), Raster(damsBuff_gr))
        newLocs.save("movedDams")
        movedDams = "movedDams"

        arcpy.RasterToPoint_conversion(movedDams, "movedDams_pts", "VALUE")
        arcpy.AddField_management("movedDams_pts", uIDField, "TEXT")
        arcpy.AddField_management("movedDams_pts", heightField, "LONG")
        arcpy.MakeFeatureLayer_management("movedDams_pts", "movedDams_lyr")
        arcpy.AddJoin_management("movedDams_lyr", "grid_code", dams, "emID")
        arcpy.CalculateField_management("movedDams_lyr", "{}.{}".format("movedDams_pts", uIDField),
                                        "!{}.{}!".format(damsName, uIDField), "PYTHON")
        arcpy.CalculateField_management("movedDams_lyr", "{}.{}".format("movedDams_pts", heightField),
                                        "!{}.{}!".format(damsName, heightField), "PYTHON")

        # Get rid of multiple points that can occur if more than 1 cell in the buffer == max fac
        arcpy.DeleteIdentical_management("movedDams_pts",
                                         ["grid_code", "{}".format(uIDField), "{}".format(heightField)])
        dams = "movedDams_pts"

        # Get elevation at dams
        arcpy.AddMessage("Finding the elevation at each dam...")
        print("Finding the elevation at each dam...")
        ExtractValuesToPoints(dams, DEMFilled, "dams_elev")
        dams = "dams_elev"

        uIDList = []
        with arcpy.da.SearchCursor(dams, uIDField) as rows:
            for row in rows:
                uIDList.append(row[0])
        arcpy.AddMessage(uIDList)

        arcpy.Compact_management(workspace)

        for uID in uIDList:
            # if uID == "Songwe" or uID == "Songwe_1" or uID == "Songwe_2" or uID == "Kikonge" or \
            #         uID == "Masigira" or uID == "Mpanga" or uID == "Ruhudji" or uID == "Rumakali" or \
            #         uID == "Steiglers_Gorge_I" or uID == "Upper_Kihansi":

                #pull out the dam we're working on a separate layer
                arcpy.AddMessage("Generating reservoir for dam {}...".format(uID) )
                print("Generating reservoir for dam {}...".format(uID) )
                arcpy.MakeFeatureLayer_management(dams, "dam", """"{}" = '{}'""".format(uIDField, uID))


                #Create watershed mask & set mask
                outShed = Watershed(FDR, "dam")
                outShed.save("{}_watershed".format(uID))
                watershed = "{}_watershed".format(uID)
                arcpy.env.extent = watershed
                arcpy.env.mask = watershed

                #Calculate reservoir elevation from dam height & dam elevation
                fields = (heightField, "RASTERVALU")
                with arcpy.da.SearchCursor("dam", fields) as rows:
                    for row in rows:
                        print(row)
                        height = row[0]
                        damElev = row[1]
                        resElev = damElev + height

                #Create raster reservoir
                arcpy.AddMessage("...Beginning reclassification for {}...".format(uID))
                print("...Beginning reclassification for {}...".format(uID))
                outReclassify = Reclassify(DEMFilled, "Value", RemapRange([[-9999999, resElev, resElev], [resElev, 9999999999, "NODATA"]]))
                outReclassify.save("{}_reservoir".format(uID))
                resRaster = "{}_reservoir".format(uID)

                #Calculate volume / area
                arcpy.AddMessage("...Calculating area & volume for {}...".format(uID))
                print("...Calculating area & volume for {}...".format(uID))
                outVolRes = CutFill(DEMFilled, resRaster, zFactor)
                outVolRes.save("{}_reservoir_volume".format(uID))
                resVol = "{}_reservoir_volume".format(uID)

                arcpy.Statistics_analysis(resVol, "{}_VolStats".format(uID), [["VOLUME", "SUM"], ["AREA", "SUM"]])
                resVolStats = "{}_VolStats".format(uID)
                arcpy.AddField_management(resVolStats, uIDField, "TEXT")
                arcpy.CalculateField_management(resVolStats, uIDField, "'{}'".format(uID), "PYTHON")

                #Make vector version of reservoir & add volume & area calcs
                arcpy.AddMessage("...Creating polygon version of reservoir {}...".format(uID))
                print("...Creating polygon version of reservoir {}...".format(uID))
                arcpy.RasterToPolygon_conversion(resRaster, "{}_reservoir_poly".format(uID), "NO_SIMPLIFY")
                resPoly ="{}_reservoir_poly".format(uID)
                arcpy.AddField_management(resPoly, uIDField, "TEXT")
                arcpy.AddField_management(resPoly, "Volume", "DOUBLE")
                arcpy.AddField_management(resPoly, "Area", "DOUBLE")
                arcpy.CalculateField_management(resPoly, uIDField, "'{}'".format(uID), "PYTHON")
                arcpy.MakeFeatureLayer_management(resPoly, "resPoly_lyr")
                arcpy.AddJoin_management("resPoly_lyr", uIDField, resVolStats, uIDField)
                arcpy.CalculateField_management("resPoly_lyr", "{}.Volume".format(resPoly), "!{}.SUM_VOLUME!*-1".format(resVolStats), "PYTHON")
                arcpy.CalculateField_management("resPoly_lyr", "{}.Area".format(resPoly), "!{}.SUM_AREA!".format(resVolStats), "PYTHON")
                arcpy.RemoveJoin_management("resPoly_lyr")

                del resVol, resRaster

                #set mask back to full extent
                arcpy.env.extent = DEM
                arcpy.env.mask = DEM


        arcpy.AddMessage("Merging all reservoirs together...")
        print("Merging all reservoirs together...")
        reservoirs = arcpy.ListFeatureClasses("*_reservoir_poly")
        arcpy.Merge_management(reservoirs, "MergedReservoirs")
        arcpy.Dissolve_management("MergedReservoirs", "FinalReservoirs", [uIDField, "gridcode", "Volume", "Area"])
        arcpy.AddField_management("FinalReservoirs", "SurfElev", "DOUBLE")
        arcpy.CalculateField_management("FinalReservoirs", "SurfElev", "!gridcode!", "PYTHON")
        arcpy.DeleteField_management("FinalReservoirs", "gridcode")

        #Clean up intermediate files
        if cleanUp == True:
            try:
                arcpy.AddMessage("Cleaning up intermediate files...")
                print("Cleaning up intermediate files...")

                rasterList = arcpy.ListRasters("*_watershed*")
                for raster in rasterList:
                    arcpy.Delete_management(raster)

                rasterList = arcpy.ListRasters()
                for raster in rasterList:
                    if (raster == "damsBuff_gr") or (raster == "FACZoneStats") or (raster == "movedDams"):
                        arcpy.Delete_management(raster)

                fcList = arcpy.ListFeatureClasses()
                for fc in fcList:
                    if (fc == "damsBuffer") or (fc== "movedDams_pts") or (fc == "MergedReservoirs") or (fc == "movedDams_ptsNoDupe"):
                        arcpy.Delete_management(fc)

                tables = arcpy.ListTables("*_VolStats")
                for table in tables:
                    arcpy.Delete_management(table)

                rasterList = arcpy.ListRasters("*_reservoir*")
                for raster in rasterList:
                    arcpy.Delete_management(raster)

            except:
                arcpy.AddWarning("Reservoir generation was successful, but there was a problem deleting some of the intermediate data.")

        arcpy.CheckInExtension("Spatial")


        # mxd = arcpy.mp.ArcGISProject(r"C:\Users\anagha.uppal\Documents\ArcGIS\Projects\mapre\mapre.aprx")
        # df = mxd.listMaps()
        # print(df)
        # arcpy.MakeFeatureLayer_management("FinalReservoirs", "Final Reservoirs")
        # addReservoirs = df.addLayer("Final Reservoirs", "TOP")
        # arcpy.MakeFeatureLayer_management("dams_elev", "Dams - Moved to River")
        # addDams = df.addLayer("Dams - Moved to River", "TOP")
        # # arcpy.RefreshTOC()


    except Exception as e:
        tb = sys.exc_info()[2]
        arcpy.AddError ("Problem calculating dam reservoirs...")
        arcpy.AddError ("Line {}".format(tb.tb_lineno))
        arcpy.AddError (e.message)
        arcpy.CheckInExtension("Spatial")
        sys.exit()

if __name__ == '__main__':
    main()

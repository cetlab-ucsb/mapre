=====================================================
Using the site suitability tool (Script Tool Stage 1)
=====================================================

Script Tool Stage 1 allows the user to create a feature class of suitable sites for renewable energy development, which yields an estimate of resource potential given various assumptions. This tool may be used for any wind or solar technology, given the correct spatial resource data.

Inputs
======

You have the option of hardcoding the inputs directly into the ``stage1_HardcodeCollect.py`` script or to type the inputs into the ``stage1_input.csv`` file and placing that as an input into the ``stage1_CSVCollect.py`` script.

The inputs for this tool are:

* **Technology**: The renewable technology you are analyzing; input should be one of the following:
    * solar
    * wind
    * CSP
* **Template Raster**: Path to the (processed) elevation/DEM layer
* **Country Bounds**: Path to the (processed) boundary file of interest
* **CSV Input**: Path to CSV with exclusion criteria information (see Site Suitability Rasters CSV section below for more details)
* **Resource Input**: Raster dataset of resource quality for the region. For solar, this could be an irridiation layer; for wind, this could be the windspeed layer.
* **Threshold List**: Minimum threshold for resource quality for siting. Value should either be 1, 2, 3, or 4.
* **Output GDB**: Path to geodatabase to save output files. If you don't have one, you can create one in ArcGIS.
* **Filename Suffix**: A string to append to the results output file name.
* **CSV Area Output**: Path to where you want the output CSV to be saved. This should include the file name.
* **Scratch GDB**: Path to a geodatabase for some processes to run on. If you don't have one, create one in ArcGIS.
* **Raster Output**: TRUE or FALSE; if you want an additional raster output.
* **Land Use Efficiency**: Scalar value between 0-100
* **Land Use Discount**: Scalar value between 0-1
* **Average Capacity Factor**: Scalar value between 0-1
* **Min Area**: Scalar value
* **Geographic Units**: (optional)
* **GeoUnits Attribute Name**: (optional)
* **Workspace to save subunits**: (optional)

Site Suitability Rasters Input CSV
==================================

Use the template CSV, “inputs_siteSuitabilityRasters.csv,” provided in the RequiredCSVs folder accompanying the model to create an input CSV that contains the absolute filenames of the input rasters (Euclidean distance and threshold exclusion raster. Each column of the CSV indicates an individual input raster. You can create as many column inputs as you have rasters. That is, the tool will incorporate as many exclusions you provide in the CSV. As shown in Figure 2, the specifications for each row are as follows:

1. The first row should contain the name of the raster layer (e.g., water bodies).
2. The second row should contain either a "yes" or a "no" to indicate whether or not the raster should be used in the analysis.
3. The third row contains the absolute filename of the raster input (e.g., A:\INPUTS\\ke.gdb\ke_water_ed for the water body Euclidean distance raster).
4. The fourth and last row contains the conditional raster statement, which indicates the threshold or buffer to be applied, using values appropriate for the units of the raster layer (e.g., Value <= 20). All areas for which the conditional statement is true will be included in the analysis. For example, to exclude all areas with slope greater than 20%, the fourth row should contain the conditional statement, Value <= 20. To exclude all areas within 500 meters of a water body use, Value >= 500.

.. image:: img/site_suitability_raster_csv.png
    :width: 800
    :alt: Figure 1

Running the tool
================

To run the Stage 1 script using the CSVCollect or the HardcodeCollect method, you will use your command prompt/terminal window and once again use ArcGIS' Python installation to execute the script.

For example, if you're going to be running ``stage1_HardcodeCollect.py``, open up the command prompt and type the following:

.. code-block:: bash

    "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python" "path\to\stage1_HardCodeCollect.py"

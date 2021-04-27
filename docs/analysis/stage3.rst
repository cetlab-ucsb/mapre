===================================================================================
Using the Project Opportunity Area Attribute Calculation Tool (Script Tool Stage 3)
===================================================================================

This model calculates the attributes for the project opportunity areas feature class output of the ‘Stage 2: Create project areas’ model. These attributes include distances to different features (e.g. transmission lines, existing renewable energy plants) and levelized costs of energy generation, transmission expansion, and road extension.

Inputs
======

* **Resource**: The renewable technology you are analyzing; input should be one of the following: solar, wind, CSP.
* **Input project**: Path to output project feature class from Stage 2.
* **Output Project**: Path of where you want the output from this model to be saved
* **Input resource raster**: Raster layer of resource quality for the region. For solar, this could be an irridiation layer; for wind, this could be the windspeed layer.
* **Input attribute CSV**: Similar to the input CSV that was created for Script Tool B, Stage 1, the input CSV file for this final Script Tool B controls the inputs used to estimate the project attributes. Use the template CSV, “inputs_projectAreaAttributes.csv,” provided in the “mapre/REzoningGIStools/Processing Scripts/RequiredCSVs/For_CSV_based_Input” folder accompanying the model to create an input CSV that contains the absolute filenames of the input features and rasters. **NOTE: You MUST include the default columns provided in the “inputs_projectAreaAttributes.csv.” If you are missing any of the attribute data, such as transmission lines or load centers, simply indicate “no” in the second row of the attribute’s column.** However, you are able to add other attributes by adding additional columns to the csv (e.g., “d_protected” for distance to protected areas). The format and requirements of inputs_projectAreaAttributes.csv are specified below.
* **Template raster**: Path to the (elevation/DEM) template raster layer
* **Scratch GDB**: Path to scratch geodatabase
* **Renewable resource units**: Specify the units that the tool will use to calculate annual electricity generation and levelized cost of electricity. The options are: Capacity Factor, W/m2, kWh/m2-day, Wind speed (m/s). W/m :sup:`2` and kWh/m :sup:`2`-day are specific to Solar PV and CSP. Selecting these units for Wind generation will cause the model to fail or yield incorrect results.
* **Transmission distance multiplier**:
* **Cell size**:
* **Area of largest project**:
* **Capital cost**:
* **Variable O&M Cost generation**:
* **Fixed O&M cost of generation**:
* **Fixed O&M costs annual escalation rate**:
* **Efficiency losses**:
* **Outage rate**:
* **Annual output degradation rate**:
* **Transmission cost**:
* **Substation cost**:
* **Road cost**:
* **Economic discount rate**:
* **Power plant lifetime**:
* **Land use efficiency**:
* **Land use discount factor**:

Project Area Attributes Input CSV
=================================

Use the template CSV, “stage3_projectAreaAttributes.csv,” provided in the
mapre/REzoningGIStools/Processing Scripts/RequiredCSVs folder accompanying the model to create this input CSV. The specifications for each row are as follows:

1. The first row should contain the intended field name of the raster or feature class (e.g., ‘d_water’). Note that if you wish to save the output of this tool as a shapefile, the field name cannot be longer than 10 characters. Otherwise, no spaces or special characters are allowed.
2. The second row should contain either a "yes" or a "no" to indicate whether or not the raster or feature class should be used in the analysis. This allows you to turn the input "on" or "off".
3. The third row indicates the attribute calculation type you intend to apply to the input raster or feature. For example, you would specify ‘distance’ in this row for ‘d_trans,’ which is the transmission feature class for which you would apply the ‘Nearest’ distance tool (i.e., calculate the distance to the nearest transmission line for each project opportunity area). Rasters for which the area average will be calculated for each project opportunity area, such as ‘m_elev’ (mean elevation raster), need to have ‘mean’ in this row. The Script Tool only accepts ‘distance’ or ‘mean’ analyses.
4. The fourth and final row contains the absolute filename of the raster input (e.g., A:\INPUTS\\ke.gdb\ke_water for Kenya’s water body feature class).

.. image:: img/project_area_attributes.png
    :width: 600
    :alt: Project Area Attributes Example

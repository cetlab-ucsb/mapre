=====================================
Input approaches for analysis scripts
=====================================

Using CSV files as inputs
=========================

For this approach, the inputs required to run the analysis scripts will be pulled from CSV files. The templates for these CSV files can be found in the REzoningGIStools/Processing Scripts/RequiredCSVs/For_CSV_based_Input directory. You should edit all the required input cells in the CSVs accordingly, based on your own model.

The python script that you will run using the CSV input system will have ``_CSVCollect.py`` in their names. Before you can actually run these python scripts, you must go into the scripts themselves to make sure the input csv path at the top of the scripts are correctly pointing at your input CSV file.

Typing the inputs into the .py script directly
==============================================

Another method you could use is to directly type your inputs into the .py scripts themselves. All of the scripts that will be run using this approach have ``_HardcodeCollect.py`` in their names.

Using the ArcGIS Toolbox
========================

(note: add text on using ArcGIS toolbox)
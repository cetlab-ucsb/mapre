=======================================================================
Using the Project Opportunity Area Creation Tool (Script Tool Stage 2)
=======================================================================

Script Tool Stage 2 takes any resource area feature class output of the 'Script Tool B: Stage 1 Create site suitability’ model and divides the area into smaller geographic units called project opportunity areas, or simply, projects. The user can specify the range of the project sizes in km :sup:`2`.

Inputs
======

* **Suitable sites**: Path to feature class output from Stage 1
* **Projects output**: Path to what you want this Stage 2 output to be saved as
* **Scratch GDB**: Path to scratch geodatabase
* **Template raster**: Path to template (elevation) raster layer
* **Country Bounds**: Path to country bounds layer
* **Geographic unit of analysis**: (optional)
* **Fishnet size**: Size of fishnet in units of kilometers (km). Specifies the maximum size of the projects to be created (e.g., 5 km will generate projects that are at most 5 km x 5 km or 25 km :sup:`2`). A fishnet feature class will be created using this specified dimension in order to create projects. This function only works for countries within the African continent.
* **Fishnet Storage**: Path to where the fishnet feature class will be saved. It is recommended that this directory be a file geodatabase (fgdb). By saving the fishnet feature class to the computer’s hard drive, this tool can be run iteratively in less time. The fishnet filename will specify its dimensions so that multiple fishnet feature classes of different sizes can be created.
* **Max project area**: Maximum project area size in units of kilometers (km :sup:`2`). It is advised that the fishnet area be used (e.g., a fishnet size of 5 km would have a max project area of 25 km :sup:`2`). This parameter is used to identify the particular polygons that will be divided into smaller project areas. For example, if the user specifies 25 in this parameter field, all contiguous areas greater than 25 km :sup:`2` will be divided using the fishnet feature class.
* **Min contiguous project area**: Specifies the area below which polygons will be excluded from the project output feature class.
Renewable Energy Zoning GIS tools


ABOUT
The GIS tools enable users to (1) create solar and wind resource assessment maps using user-provided datasets, and (2) update existing spatial and non-spatial inputs of renewable energy zones in the Eastern and Southern Africa Power Pools identified for the Africa Clean Energy Corridor initiative. Download the original study's report on http://mapre.lbl.gov/searez or http://www.irena.org/. These GIS script tools have been programmed in Python 2.7 and is intended for use in ArcMap 10.2+
. Please see the user manual for a thorough description of its intended applications and requisite datasets.

USER MANUAL 
The user manual is in a publicly assessible Google Doc:
https://docs.google.com/document/d/1IdtfyILFuFycTf_9OBfM4HazkTTnDeDqKsjg3WF6-ss/edit?usp=sharing
If this link is broken, see mapre.lbl.gov for the latest user manual version.

DATA DOWNLOADS
http://mapre.lbl.gov

CONTACT INFO
Grace Wu (grace.cc.wu [a] gmail.com)
Ranjit Deshmukh (ranjit.deshmukh [a] lbl.gov)
Tijana Radjoicic (TRadojicic [a] irena.org)

COPYRIGHT
International Renewable Energy Agency (IRENA) and the Lawrence Berkeley National Laboratory (LBNL)



UPDATE LOG
2016-08-13 (v1.1): 
- Updated metadata for tutorial 1's included datasets. Replaced example Kenyan power plant csv and point file datasets with example Kenyan load datasets. Updated user manual accordingly. 
- Minor modifications to Option 1 scripts for all technologies to report distances calculations with more precision, reducing rounding differences compared to original zones and project files. 

2016-11-01 (v1.2):
- Updated Script Tool B-2 to create project areas for any region of the world, as specified by the template raster. Previously, projects could only be created for regions within the African continent.  

2017-01-26 (v1.3):
- Updated Script Tool B-2 to fix a bug having to do with the template raster. The tool should now run with any template raster provided. 

2017-08-25 (v1.4):
- Updated Script Tool B-3 to change the application of the transmission distance multiplier parameter. In previous versions, this user input was linearly applied to the calculated euclidean distance and reflected in the distance calculation column. Now, the multiplier is only applied for the calculation of the transmission or substation LCOE and total LCOE. The distance columns should show unmodified euclidean distances. 
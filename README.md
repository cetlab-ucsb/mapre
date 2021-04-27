# mapre
The MapRE set of scripts is associated with the MapRE toolset here: https://mapre.lbl.gov/gis-tools/. A detailed user manual is provided at [this link](https://docs.google.com/document/d/1IdtfyILFuFycTf_9OBfM4HazkTTnDeDqKsjg3WF6-ss/edit#heading=h.kug874sjmayh)

The scripts are located in the folder ReZoningGIStools and are divided into preprocessing and processing scripts. 
To use these scripts, first clone this git repository to your machine (directions on how to do this [here](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository)). 
 
Five stages (scripts in the Processing folder) take your input spatial files and deliver a result of potential project zones as well as the input file for Tableau to visualize your results. Prior to processing your input files, you must make certain that all files are in the same folder and aligned (sharing a common coordinate system and projection, rasters sharing a cell size). Use the Master_Function_v2 script in the Preprocessing Scripts folder to align all files first.

For direct support, please email the MapRE team () to be guided through the process and for questions. Issues can be raised through the Github repository.

## Building documentation

The documentation is stored in the ``docs`` directory. To build the documentation locally on your system (after cloning the repo), you need have Sphinx installed. You can install Sphinx (either in your virtual environment or globally on your computer) by running the following command in your terminal:
```bash
pip install sphinx
```

You will also need to have the [Read the Docs Sphinx theme](https://github.com/readthedocs/sphinx_rtd_theme) installed, which you can do by running the following command:
```bash
pip install sphinx-rtd-theme
```

Afterwards, navigate into the ``docs`` folder in your terminal and run the following command:
```bash
make html
```
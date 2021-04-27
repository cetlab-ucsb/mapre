================================
Running the preprocessing script
================================

The script needed to preprocess the GIS layers (where preprocess means to project the layers to the desired projection and clip to the desired boundary) is the ``run_preprocessing.py`` script, which is located under the **REzoningGIStools** > **Preprocessing Scripts** directory.

ArcGIS Pro installation of Python
=================================

The preprocessing script relies on ``arcpy``, which meanns it has to be run using ArcGIS Pro's installation of Python (instead of the traditional ``python`` argument). One way to do this is to navigate to the directory where ArcGIS Pro's Python installation is located (``C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3``) and run the preprocessing script from within this directory. Another option is to explicitly reference the ArcGIS Pro Python (``C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python``) from whatever directory in the terminal you are running the preprocessing script from.

Script input arguments
======================

To get the list of arguments the ``run_preprocessing.py`` takes, use the ``--help`` command:

.. code-block:: bash

    "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python" "D:\REzoningGIStools\Preprocessing Scripts\run_preprocessing.py" --help

The output when running the ``--help`` command should look something like:

.. code-block:: bash

    usage: run_processing.py [-h] -i INPUT [INPUT ...] -r
                                 [EXTRACT_REGION [EXTRACT_REGION ...]] -n
                                 [REGION_NAME [REGION_NAME ...]]
                                 [-pf PROCESS_FILE [PROCESS_FILE ...]]
                                 [-cs CELL_SIZE [CELL_SIZE ...]]

    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                            input directory
      -r [EXTRACT_REGION [EXTRACT_REGION ...]], --extract_region [EXTRACT_REGION [EX
    TRACT_REGION ...]]
                            the country or region (e.g. states) to extract as
                            condition (in quotes) e.g. “NAME" LIKE 'South Africa'
                            OR "NAME" LIKE 'Angola'
      -n [REGION_NAME [REGION_NAME ...]], --region_name [REGION_NAME [REGION_NAME ..
    .]]
                            name of region to give output folder gdb with
                            processed files for your region
      -pf PROCESS_FILE [PROCESS_FILE ...], --process_file PROCESS_FILE [PROCESS_FILE
     ...]
                            csv_file of 6 columns: 1 : in_features(feature class
                            or raster), 2 : name of output file or raster, 3 :
                            feature_class if feature class and raster if raster 4
                            : input coordinate system for arcpy.SpatialReference 5
                            : output coordinate system for arcpy.SpatialReference
                            6 : If raster, resampling method
                            (Nearest/Bilinear/Cubic/Majority
      -cs CELL_SIZE [CELL_SIZE ...], --cell_size CELL_SIZE [CELL_SIZE ...]
                            cell size in the form 'X Y' such as 500 500 in quotes


Example command
===============

Let's say my preprocessing script is ``D:\REzoningGIStools\Preprocessing Scripts\run_preprocessing.py``. Additionally, my inputs .gdb is ``D:\mapre\India2021_v2.gdb``, and my preprocessing inputs csv file is ``D:\mapre\inputs_preprocessing_india.csv``.

Within the country boundaries layer, I am using the column **NAME_0** to keep all shapes where ``NAME_0 == 'India'``. Finally, I'm going to name my outputs .gdb (with the clipped and projected layers) "India".

Therefore, the resulting command I type into terminal/command prompt is:

.. code-block:: bash

    "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python" "D:\REzoningGIStools\Preprocessing Scripts\run_preprocessing.py" -i "D:\mapre\India2021_v2.gdb" -pf "D:\mapre\inputs_preprocessing_india.csv" -n "India" -r "NAME_0 = 'India'"

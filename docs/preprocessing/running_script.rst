================================
Running the preprocessing script
================================

The script needed to preprocess the GIS layers (where preprocess means to project the layers to the desired projection and clip to the desired boundary) is the ``run_preprocessing.py`` script, which is located under the **REzoningGIStools** > **Preprocessing Scripts** directory.

ArcGIS Pro installation of Python
=================================

The preprocessing script relies on ``arcpy``, which meanns it has to be run using ArcGIS Pro's installation of Python (instead of the traditional ``python`` argument). One way to do this is to navigate to the directory where ArcGIS Pro's Python installation is located (``C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3``) and run the preprocessing script from within this directory. Another option is to explicitly reference the ArcGIS Pro Python (``C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python``) from whatever directory in the terminal you are running the preprocessing script from.

Script input arguments
======================

Example command
===============

Let's say my preprocessing script is ``D:\REzoningGIStools\Preprocessing Scripts\run_preprocessing.py``. Additionally, my inputs .gdb is ``D:\mapre\India2021_v2.gdb``, and my preprocessing inputs csv file is ``D:\mapre\inputs_preprocessing_india.csv``.

Within the country boundaries layer, I am using the column **NAME_0** to keep all shapes where ``NAME_0 == 'India'``. Finally, I'm going to name my outputs .gdb (with the clipped and projected layers) "India".

Therefore, the resulting command I type into terminal/command prompt is:

    .. code-block:: bash

        "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python" "D:\REzoningGIStools\Preprocessing Scripts\run_preprocessing.py" -i "D:\mapre\India2021_v2.gdb" -pf "D:\mapre\inputs_preprocessing_india.csv" -n "India" -r "NAME_0 = 'India'"

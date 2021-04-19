=================================
Creating preprocessing inputs csv
=================================

The preprocessing csv file is one of the inputs into the preprocessing script (along with the inputs .gdb). The inputs csv file can be completed after you're done adding all the needed GIS layers into the inputs .gdb (since the preprocessing inputs csv requires the names and projections of layers in the inputs .gdb file).

The preprocessing inputs csv has the following columns:

1. **Input File Name**: Name of layer in the inputs .gdb
2. **Output File Name**: Name you want to assign layer in outputs (preprocessed) .gdb
3. **File Type**: "Raster" or "Feature class"
4. **Input Projection**: The current projection of the layer in the inputs .gdb
5. **Output Projection**: The desired projection of the layer in the outputs (preprocessed) .gdb
6. **Resampling Type (for Raster):** For rasters, the desired resampling type. Choose between "NEAREST", "BILINEAR", or "CUBIC"
7. **Process?**: Do you want to preprocess this layer in this run (in some instances, you may just want to keep the layer in the input csv for reference but not actually want to preprocess it)? State either "Yes" or "No"
8. **Template Raster**: Is this the template raster? State "Yes" if so; otherwise, leave blank. Only one layer can be the template raster
9. **Euclidean Distance Raster**:
10. **Country Bound File**: Is this the layer with the boundaries for the preprocessing? If so, state "Yes"; otherwise, leave blank. Only one layer can be the country bound file.
11. **Extract Attributes**: This column is for listing any thresholds you have for the respective layer (filtering). If left blank, no thresholds/filtering will be applied and the whole layer will be preprocessed.

An example of the preprocessing input csv (csv_processing_file.csv) is provided under **REzoningGIStools** > **Preprocessing Scripts** > **RequiredCSVs**.
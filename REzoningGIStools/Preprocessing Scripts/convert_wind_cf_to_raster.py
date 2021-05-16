'''
script to convert the point layer output from preprocessing_calculateWindCFusingWeibull_v4.py
into a raster layer
'''

# import packages
import arcpy

# inputs and workspaces
arcpy.env.workspace = workspace = 'D:\\mmeng\\mapre\\India.gdb'
input_layer = 'gwa3_250_wind_capacity_factors_no_losses_100m_in'
val_field = 'CF_maxCls'
output_layer = input_layer + '_raster'
cell_assignment_type = 'MEAN'
priority_field = ''
cell_size = 0.0025

# convert input point layer to output raster layer
print('Converting point layer to raster layer...')
arcpy.PointToRaster_conversion(input_layer, val_field, output_layer, cell_assignment_type, priority_field, cell_size)

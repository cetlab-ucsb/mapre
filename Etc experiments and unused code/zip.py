## Takes in a gdb and outputs zip for each shp
import os
import shutil

directory_path = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\outputs_for_web\human_wind"
output_path = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\outputs_for_web\human_wind"
folder_list = os.listdir(directory_path)
#print(folder_list)
for folder_name in folder_list:
    folder_path = os.path.join(directory_path, folder_name)
    print(folder_path)
    if os.path.isdir(folder_path):
        out_folder_path = os.path.join(output_path, folder_name)
        shutil.make_archive(out_folder_path, 'zip', folder_path)


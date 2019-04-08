# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 15:33:18 2018

@author: Mayara E. Bonani
"""

import dropbox # Ref [3]
import os
import time 

# If delete is 0, it will just  download the files from Dropbox
# If delete is 1, it will download and delete the files from Dropbox
delete = 0

# The files will be saved in the folder which name is (year-month-day)
dir_name = time.strftime("%Y_%m_%d")
if (not os.path.exists(dir_name)): os.makedirs(dir_name) 

# Token 
dbx =dropbox.Dropbox('kjsoI3pk2aAAAAAAAAAAZ_IUaNc35nPZvgUkpPd6E_YrgPczKoxW2dLL-y7QBldY')

dropbox_path=''
ent = dbx.files_list_folder(dropbox_path, recursive=False).entries
for e in ent:
    folder = e.name
    print(folder)
    fil = dbx.files_list_folder(dropbox_path+'/'+folder, recursive=False).entries
    if (len(fil)!=0):
        for f in fil:
            file_name = f.name
            file_name_acceptable = file_name.replace(":","-") # Ref [2]
            file_folder = f.path_lower 
            print(file_folder+':'+file_name)
            dbx.files_download_to_file(dir_name+'/'+file_name_acceptable,file_folder) #Download a file from the Dropbox.
            if (delete == 1): dbx.files_delete(file_folder) # Ref [4]



# References:
#[1] - https://www.dropboxforum.com/t5/API-Support-Feedback/Is-it-possible-to-download-all-files-using-python-sdk/td-p/257159
#[2] - https://stackoverflow.com/questions/22620965/ioerror-errno-22-invalid-mode-wb-or-filename
#[3] - INSTALATION: https://anaconda.org/conda-forge/dropbox   
#[4] - https://dropbox-sdk-python.readthedocs.io/en/latest/moduledoc.html?highlight=delete
        


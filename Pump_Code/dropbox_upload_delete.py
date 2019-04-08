# -*- coding: utf-8 -*-
"""
Created on Sat Nov 9 08:10:32 2018

@author: Mayara E. Bonani
"""
#References:
# https://dropbox-sdk-python.readthedocs.io/en/latest/

import dropbox
from dropbox.exceptions import ApiError
import configuration as config
import os

# Create instance of a Dropbox class, which can make requests to API
# token = String with your access token
def dropbox_access(token):
    dbx=dropbox.Dropbox(str(token))
    try:
        dbx.users_get_current_account()
        print ("Valid Access Token")
        return(dbx)
    except:
        print("It was not possible to connect to Dropbox Account:")
        print("Without Internet Connection or Authentification Error,Invalid Access Token")
        return(0)

# Check if the folder exists in the Dropbox
# If folder does not exist, make a new folder
def check_folder(dbx,folder_name):
    try:
        dbx.files_get_metadata(folder_name)
        print('The folder:'+folder_name+' exists')
    except:
        print('The folder:'+folder_name+' does not exist')
        dbx.files_create_folder(folder_name,autorename=False)
        print ("The folder:"+folder_name+" was created!")

### Upload File(file_name) from local_path to Dropbox (dropbox_path)
# If the file was uploaded, so return  1
# If the file was not uploaded, so return 0
def upload_file(dbx,dropbox_path,local_path,file_name):

    with open(local_path, 'rb') as file:
        print("Uploading to Dropbox...")
        try:
            dbx.files_upload(file.read(), dropbox_path)
            print('Uploaded')
            return (1)
        except ApiError as err:
            # Check user has enough Dropbox space quota
            if (err.error.is_path() and err.error.get_path().error.is_insufficient_space()):
                print("ERROR: Cannot upload; insufficient space.")
            elif err.user_message_text:
                print(err.user_message_text)
            else:
                print(err)
            return(0)

# Delete file
def delete_local_file(local_path):
    os.system("rm " + local_path)
    print("Deleted")


# Return if the file can be saved in the Dropbox (0) or just locally (1)
def upload_toDropbox_delete(dbx,folder_mic_name,file_name,local_path,delete):
    dropbox_path = folder_mic_name+'/'+file_name
    local_path = local_path+'/'+file_name
    print('----',file_name)
    if ( not upload_file(dbx,dropbox_path,local_path,file_name)):
        local_storage = 1 # The file can be saved just locally
    else:
        if delete ==1: delete_local_file(local_path)
        local_storage = 0 # The file can be saved in the Dropbox and locally
    
    return(local_storage) 


    

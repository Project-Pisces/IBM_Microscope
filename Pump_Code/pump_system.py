# -*- coding: utf-8 -*-
"""
Created on Tue Nov 6 12:39:28 2018

@author: Mayara E. Bonani
"""
import os
import time
import subprocess
import RPi.GPIO as GPIO
import picamera
import microscope as mc
import dropbox_upload_delete as db
import configuration as config

### Global variables
# Pins 
green_led = 5
red_led = 6
blue_led = 18
sample_pump = 22
clean_water_pump = 16
shutdown = 17
toggle_clean = 27
# Pin Numbering - Using BCM
GPIO.setmode(GPIO.BCM)



### Change Directory to save Images: /home/pi/Pump_Microscope/Microscope(mic_id)
# Ex: If mic_id = 1, then the directory will be: /home/pi/Pump_Microscope/Microscope1 and all the images will be saved in this folder
def change_dir(mic_id):
    # Create a directory to save all videos to be recorded
    if (not os.path.exists("/home/pi/Pump_Microscope")):
        os.makedirs("/home/pi/Pump_Microscope")
    os.chdir("/home/pi/Pump_Microscope")

    # Create a directory to save videos to be recorded on a specific date
    if (not os.path.exists('Microscope'+mic_id)):
        os.makedirs('Microscope'+mic_id)
    os.chdir('Microscope'+mic_id)
    
    local_path = "/home/pi/Pump_Microscope/Microscope"+ mic_id
    return(local_path)


### Check is shutdown button is pressed for more than 2 seconds
def check_shutdown(shutdown_pin):
    # Shutdown Button was pressed 
    if(GPIO.input(shutdown_pin)==False): 
        time.sleep(2) # Wait for 2 seconds
        if(GPIO.input(shutdown_pin)==False): # Shutdown Button still pressed for 2 seconds -> Shutdown the Raspberry Pi
            GPIO.cleanup()
            os.system("sudo shutdown -h now")


### Check the size of the folder where the images are saved. 
# If the memory size of the folder located in "path" is bigger than "max_storage_file" in GB, then delete all the files of this folder
def check_folder_size(path,max_storage_size):
    # Flag to inform if the files were deleted (1) or not (0)
    erased=0
    # Size in Kbytes of the folder with located in "path"
    str_size = subprocess.check_output(['du','-sk', path]).split()[0].decode('utf-8')
    # Size in gigabytes
    gbyte_size = int(str_size)/1048576
    if gbyte_size > max_storage_size:
        all_files = path+'/*'
        subprocess.call(['rm -rf '+ all_files],shell= True)
        erased =1
    return(erased)



def main():
    
    # Configurations are saved in a dictionary structure
    # The configuration.py allows to get all relevant informations
    #To check USB:
    #if (config.check_usb_configfile()): print('Copied File')
    #else: print('Using the old file')
    config_dic = config.config_dictionary()
    
    # Microscope_id
    mic_id = str(config_dic["MIC_ID"])
    
    # Change directory to save all the images in this local_path: "/home/pi/Pump_Microscope/Microscope(mic_name)
    # Ex: "/home/pi/Pump_Microscope/Microscope1"
    local_path = change_dir(mic_id)
    
    # Continue running the code but not uploading to Dropbox the files
    # local_storage = 1 - Files are saved just locally - This option happens when there is a problem with the Dropbox Account, for instance, there is no space free to upload more images
    # local_storage = 0 - Files are saved locally and in the Dropbox
    local_storage = 0    
  
    # DROPBOX
    # Create instance of a Dropbox class, which can make requests to API
    # dbx = instance of Dropbox Class 
    # if dbx =0, there is a problem with the token or there is a problem with the internet connection
    dbx = db.dropbox_access(config_dic["TOKEN"]) 
    # If was not possible to access Dropbox (dbx=0), so the Code will run just saving locally the images (local_storage = 1)
    if (dbx == 0):
        local_storage = 1
    else:
        local_storage = 0 # It was possible to access Dropbox, the images will be upload and save locally.
        # Dropbox Folder Name to save the images
        folder_mic_name ="/Microscope"+mic_id
        db.check_folder(dbx,folder_mic_name)
    
    # Delete Flag
    # If delete = 1, then delete the files after upload
    # If delete = 0, then keep saved locally the files after upload
    delete = 1
    
    # List of Images to Upload: List related to the images didn't upload after its capture.
    images_not_uploaded = []
    
    # Set up Camera Parameters and instance
    camera,rawCapture = mc.camera_parameters()

    # 3 LEDs - Using Common Anode RGB LED + 2 Pumps
    GPIO.setup(green_led, GPIO.OUT,initial=GPIO.HIGH)  # Green LED to GPIO5
    GPIO.setup(red_led, GPIO.OUT,initial=GPIO.HIGH)  # Red LED to GPIO6
    GPIO.setup(blue_led, GPIO.OUT,initial=GPIO.HIGH) # Blue LED to GPIO24
    GPIO.setup(sample_pump, GPIO.OUT,initial=GPIO.LOW) # Sample Pump to GPIO22
    GPIO.setup(clean_water_pump, GPIO.OUT,initial=GPIO.LOW) # Clean_Water_Pump to GPIO16
    # Push-Button to shutdown the Raspberry Pi
    GPIO.setup(shutdown, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Button to GPIO17- To Shutdown
    # Toggle to select if there will be a clen routine or not 
    # If toggle_clean = 1, so do the clean routine
    # If toggle_clean = 0, skip the clean routine
    GPIO.setup(toggle_clean, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Button to GPIO27

    while(1):
        
        # 1-  Sample Pummp - Green LED ON
        print('Pump is on. Green LED ON')
        check_shutdown(shutdown)
        GPIO.output(green_led, 0) # Turn on the Green LED
        GPIO.output(sample_pump, 1) # Turn on the Sample Pump
        time.sleep(config_dic["PUMP_ON_TIME"])
        GPIO.output(sample_pump, 0) # Turn off the Sample Pump
        check_shutdown(shutdown)
        time.sleep(config_dic["PUMP_SETTLE_TIME"])
        GPIO.output(green_led, 1) # Turn off the Green LED 



        # 2- Capture an Image - Red LED ON
        print ('Capturing an Image. Red LED ON')
        check_shutdown(shutdown)
        GPIO.output(red_led, 0) # Turn on the Red LED
        # The images saved locally can not occupy a memory space larger than the allowed space = config_dic["MAX_STORAGE"].
        # If the size is larger than the size allowed, then all these images will be deleted.
        # In order to achieve it, is necessary to check the memory space of the actual folder.
        # Call function check_folder_size : if 1, all the images were deteled and the list of images_not_uploaded is emptied 
        if (check_folder_size(local_path,config_dic["MAX_STORAGE"])): images_not_uploaded = []      
        image_name = 'Mic'+mic_id+'_'+time.strftime("%Y_%m_%d-%H:%M:%S.png")
        #image = mc.capture_image(camera,rawCapture,image_name)
        image = mc.capture_frame(camera,rawCapture,image_name)
        # Uploading Images to Dropbox
        if(not local_storage):
            try:
                dropbox_flag = 0 # Flag to inform if the upload of the last picture captured was upload(1) or not(0)
                local_storage = db.upload_toDropbox_delete(dbx,folder_mic_name,image_name,local_path,delete)
                dropbox_flag =1 # If the image was uploaded, the code will run this line. On the other hand, if a exception ocurred, the flag is still 0
                while(len(images_not_uploaded)!=0): # Try to upload the Images in the list "images_not_uploaded" until the list is empty
                    print('Uploading old images:')
                    local_storage = db.upload_toDropbox_delete(dbx,folder_mic_name,images_not_uploaded[0],local_path,delete)
                    del images_not_uploaded[0] # Delete this image from the list "images_not_uploaded" 
            except:
                if dropbox_flag==0: images_not_uploaded.append(image_name)
                print('Upload later:',images_not_uploaded)                
        GPIO.output(red_led, 1) # Turn off the Red LED



        # 3- Post Photo Wait - Blue LED ON
        GPIO.output(blue_led, 0) # Turn on the Blue LED
        start = time.time()
        delta = time.time()- start
        print('Waiting Time - Blue LED ON')
        while(delta < config_dic["POST_PHOTO_WAIT"]):
            check_shutdown(shutdown)
            delta = time.time()- start
            #print (delta)
        GPIO.output(blue_led, 1) # Turn off the Blue LED

        

if __name__ == "__main__":
	main()






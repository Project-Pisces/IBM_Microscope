import subprocess
import os


# Check if there is a config.txt file in the USB Flash Drive.
# If there is, copy the config.txt to the directory '/home/pi/Pump_field'
def check_usb_configfile():
    copy = 0 # Flag to inform if the file was copied (copy =1) or not(copy = 0)
    rpistr = "ls /media/pi"
    proc = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid,stdout=subprocess.PIPE)
    line = proc.stdout.readline()
    if (len(line)): # If there is an USB Flash Drive
       location = '/media/pi/'+line.rstrip()+'/config.txt'
       #  If the config.txt is in there
       if (os.path.isfile(location)): 
            subprocess.call('cp '+location+' /home/pi/Pump_field',shell=True)
            copy=1 
    return(copy)

def config_dictionary():
    config_dic = {"MAX_STORAGE":0,"TOKEN":0,"POST_PHOTO_WAIT": 0,"MIC_ID":0,"MAXAREA":0,"MINAREA":0,"PUMP_ON_TIME"   : 0, "PUMP_SETTLE_TIME"   : 0,"VIDEO_CAPTURE_DURATION"  : 0,"NUMBER_OF_TIMES_KEEP_WET"  :0,"CLEAN_PUMP_ON_TIME"  :0,"CLEAN_SETTLE_TIME"  :0,"HOST":0,"CLIENTID":0,"USERNAME":0,"PASSWORD":0}
    with open('config.txt','r') as config_file:
        for line in config_file:
            #lie = config_file.readline() 
            line = line.split('=') # Return a list with the strings before and after '='
            key = line[0].strip() # Remove whitespace from the beginning and end
            value = (line[1].strip()).split('"') # Extract String between quotes
            if (len(value[1])>6):
                config_dic[key] = str(value[1])
            else:
                config_dic[key] = int(value[1]) # Fill the configuration dictionary with the information in the "config.txt" file

    config_file.close()
    return(config_dic)

def check_dictionary():
    config_dic = config_dictionary()
    print('Filled Dictionary:')
    print (config_dic)



#check_dictionary()
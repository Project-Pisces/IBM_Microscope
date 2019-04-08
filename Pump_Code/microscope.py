import cv2
import time
import numpy as np
from picamera.array import PiRGBArray  # 'rawcapture' to gain performance
from picamera import PiCamera # Rasp Pi Camera
import json  # To convert a list to a json file
import base64 # To convert a image to a json format
import time
import os



### Image Pre processing
def pre_process(image): 
    blur_kernel=9 # kernel size
    THRESH = 100 # Threshold 
    gray_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) #Convert to Grayscale
    blur=cv2.medianBlur(gray_image,blur_kernel)    # Bluring
    ret,binary_image = cv2.threshold(blur,THRESH,255,cv2.THRESH_BINARY_INV) # Binary image applying threshold value
    return(gray_image, binary_image)




### PiCamera Parameters Declaration 
def camera_parameters():
    #Initialize the camera and grab a reference to raw camera capture
    camera = PiCamera()
    #camera.resolution =(1920,1088)
    camera.resolution = (2592,1944)
    camera.framerate = 30
    #camera.shuter_speed = 0 It is necessary to set up to the best value acording lighter(LED ilumination)
    #camera.iso = 800 It is necessary to set up to the best value acording lighter(LED ilumination)
    
    #rawCapture = PiRGBArray(camera,size=(1920,1088))
    rawCapture = PiRGBArray(camera,size=(2592,1944))
    # Allow the camera to warmup
    time.sleep(0.1)
    
    return(camera,rawCapture)



### Creation of numpy array related to the histogram
def create_bin_edges():
    # HISTOGRAM INFORMATION  RELATED TO THE BINS VALUES
    # minarea = minimum area value for the relevant values
    # maxarea = maximun area value for the relevant values
    # firstxvalue = minimum area value acceptable for the histogram
    # nbins = number of bins in the histogram
    # PS: Do not forget: the X-axis scale is not linear-> first and last bin has different sizes
    # bin_edges = numpy array with the values of each bin
    minarea = 9
    maxarea = 999999
    nbins = 25
    firstxvalue = 1
    interval = maxarea-minarea/(nbins-2)
    bin_edges = np.array((firstxvalue))
    interval= (maxarea-minarea)/(nbins-2)# Interval for relevant values   
    for t in range (nbins-1):
        bin_edges = np.append(bin_edges,minarea+interval*t)
    # Add the last value for the bin
    # Be carefull - the max possible value must be declared!
    # The maximum value for area = number of pixels of the image whole itself = 1944*2592 (resolution) = 5038848
    bin_edges = np.append(bin_edges,5038848) 
    #print('bin_edgeslen:',len(bin_edges),bin_edges)
    return(bin_edges)




### Crop Image with a specific contour from a whole image
def crop_image(image,contour,area,bin_id):
    # Image size (here is the same size as resolution) 
    y_max= 1944-1
    x_max = 2592-1
     
    x,y,w,h=cv2.boundingRect(contour)
    
    x_add = int(0.5*w)
    y_add = int(0.5*h)
    
    x_,y_,w_,h_ =x-x_add,y-y_add,w+x_add+x_add,h+y_add+y_add
    
    # Check if this values are in the range of the actual image size
    if(x_<0): x_=0
    if(y_<0): y_=0
    w_ = x_+w_
    h_= y_+h_
    if(w_ > x_max): w_= x_max
    if(h_ > y_max): h_ = y_max
    
    # Crop Image whose contours have the specific area value -> (bin[non_zero[m]] <= area <= bin[non_zero[m]+1])
    image_file = str(bin_id+1)+'bin_'+str(int(area))+'area_crop.png'
    crop_img = image[y_:h_,x_:w_]
    cv2.imwrite(image_file,crop_img)

    return(crop_img,image_file)




### Convert a monocromatic image to a json file and save the file in the current directory
def image_to_json(crop_img,image_file,area):# Crop Image is a Monocromatic Image (One Channel or Grayscale image)
    # Image byte size threshold 
    # I can not send a image which size is greater than 97762
    img_thresh=97762

    # Check if image byte size is not greater than the threshold value acceptable to iot_sender
    resize=0
    img_size = os.stat(image_file).st_size
    while (img_size> img_thresh):
        resize=resize+1
        (y,x)=crop_img.shape
        (y_new,x_new)=(int(y/2),int(x/2))
        crop_img= cv2.resize(crop_img,(x_new,y_new))
        cv2.imwrite(image_file,crop_img)
        img_size = os.stat(image_file).st_size

    
    # Convert to dictionary file
    retval,buffer = cv2.imencode('.png',crop_img)
    jpg_as_text=base64.b64encode(buffer)      
    data ={}
    data["image"]=jpg_as_text.decode('ascii')
    data["area"]=int(area)
    data["resize"]=2**resize
    
    # Sending images
    with open(image_file+'__image.json','w')as out_file:
       
        img_json = json.dumps(data)
        out_file.write(img_json)

    return(img_json)


def capture_frame(camera,rawCapture,imagename):
    frame_id =-1
    for frame in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
        image= frame.array
        rawCapture.truncate(0)
        frame_id = frame_id+1
        if frame_id ==10:
            cv2.imwrite(imagename,image)
            print(camera.exposure_speed)
            break
    return(image)


def capture_image(camera,rawCapture,imagename):
    # capture(output, format=None, use_video_port=False, resize=None, splitter_port=0, bayer=False, **options)
    camera.capture(rawCapture, format="bgr",use_video_port=True)

    image = rawCapture.array
    rawCapture.truncate(0)

    cv2.imwrite(imagename,image)
    return(image)


### Capture and process an image
def capture_process_image(camera,rawCapture):
    # capture(output, format=None, use_video_port=False, resize=None, splitter_port=0, bayer=False, **options)
    camera.capture(rawCapture, format="bgr",use_video_port=False)

    image = rawCapture.array
    rawCapture.truncate(0)

    cv2.imwrite('image.png',image)
    
    # Pre processing the image
    gray_image,binary_image = pre_process(image)
    #cv2.imwrite('gray.png',gray_image)
    #cv2.imwrite('binary.png',binary_image)
    
    # Find Contours 
    binary_image,all_contours,hierarchy = cv2.findContours(binary_image,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE) 
    
    return(image,gray_image,binary_image,all_contours)




### Convert an histogram to a json file
def hist_to_json(bin_edges,frequency):
    
    # Label bins - 0 is the key related to the first bin, 1 is to the second bin, 2 is to the third bin, ... 
    labelbins = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
       '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23','24']
    frequency_to_list = frequency.tolist()
    hist_to_dictionary = dict(zip(labelbins,frequency_to_list)) 

    # Convert Data Dictionary to an json file -> Array to json file   
    json_file ="data.json"
    with open(json_file,'w')as outfile:
        hist_json = json.dumps(hist_to_dictionary)
        outfile.write(hist_json)
    
    return(hist_json)




### Build the histogram related to the area of each contour in a image and crop one image per bin
def hist_and_images_json(gray_image,all_contours):
    # Histogram informations
    bin_edges = create_bin_edges()
    print('bin_edgeslen:',len(bin_edges),bin_edges)
    frequency = np.zeros((len(bin_edges-1)))
    
    # Image Sample Informations
    # image_sampled = numpy array which lenght is the same of the number of bins in the histogram
    # Each element is related to the area range in the bin
    # Ex: image_sampled[3] is related to the 3rd bin in the histogram
    # If image_sampled = 1 -> I sent a crop image for the specific area value
    # If image_sampled = 0 -> I still need a crop image sample for this specific area value
    image_sampled = np.zeros((len(bin_edges)))
    # List of all json files
    list_imgs_json=[]
    
    # Area of each contour found 
    #area = np.array((),dtype =int)
    for contour in all_contours:
        area=cv2.contourArea(contour)
        print('area:',area)
        
        for bin_id in range(25): # Bin_id value is from 0 to (nbins-1) -1 
           print('bin_id',bin_id,bin_edges[bin_id],bin_edges[bin_id+1])
       
           if (area > bin_edges[bin_id]) and (area <= bin_edges[bin_id+1]): # The firstxvalue for the area is not select for a image sample
              frequency[bin_id] = frequency[bin_id]+1
              if image_sampled[bin_id]==0:
                 crop_img,image_file = crop_image(gray_image,contour,area,bin_id)
                 img_json = image_to_json(crop_img,image_file,area)
                 list_imgs_json.append(img_json)               
                 image_sampled[bin_id]=1
      
    hist_json = hist_to_json(bin_edges,frequency)

    
    return(list_imgs_json,hist_json)


def hist_and_imgs_to_cloud(client,list_imgs_json,hist_json):
    sender.send_histogram(client, hist_json,"area_histogram")
    for img_json in list_imgs_json:
        sender.send_image(client, img_data)
        print('img:',img_json)



#def hist_to_png()


### histogram_and_images
def hist_and_images_png(image,all_contours):
     # Histogram informations
    bin_edges = create_bin_edges()
    print('bin_edgeslen:',len(bin_edges),bin_edges)
    frequency = np.zeros((len(bin_edges-1)))
    
    # Image Sample Informations
    # image_sampled = numpy array which lenght is the same of the number of bins in the histogram
    # Each element is related to the area range in the bin
    # Ex: image_sampled[3] is related to the 3rd bin in the histogram
    # If image_sampled = 1 -> I sent a crop image for the specific area value
    # If image_sampled = 0 -> I still need a crop image sample for this specific area value
    image_sampled = np.zeros((len(bin_edges)))
    # List of all json files
    list_imgs=[]
    
    # Area of each contour found 
    #area = np.array((),dtype =int)
    for contour in all_contours:
        area=cv2.contourArea(contour)
        print('area:',area)
        
        for bin_id in range(25): # Bin_id value is from 0 to (nbins-1) -1 
           print('bin_id',bin_id,bin_edges[bin_id],bin_edges[bin_id+1])
       
           if (area > bin_edges[bin_id]) and (area <= bin_edges[bin_id+1]): # The firstxvalue for the area is not select for a image sample
              frequency[bin_id] = frequency[bin_id]+1
              if image_sampled[bin_id]==0:
                 crop_img,image_file = crop_image(image,contour,area,bin_id)
                 list_imgs.append(image_file)
                 image_sampled[bin_id]=1
                 
    print(list_imgs) 
    #hist_png = hist_to_png(bin_edges,frequency)

    


#camera, rawCapture = camera_parameters()
#image = capture_image(camera,rawCapture,'test.png')
#image,gray_image,binary_image,all_contours = capture_process_image(camera,rawCapture)
#list_imgs_json, hist_json = hist_and_images_json(gray_image,all_contours)
#hist_and_imgs_to_cloud(client,list_imgs_json,hist_json)

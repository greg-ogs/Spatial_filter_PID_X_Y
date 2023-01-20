# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 20:10:05 2022

@author: grego
"""

import os
import PySpin
import matplotlib.pyplot as plt
import sys
import keyboard
import time
import numpy as np
#from simple_pid import PID

import mysql.connector

from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float
from skimage import io

global continue_recording
continue_recording = True

    
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="PASSWD",
  database = "AIRY"
)

mycursor = mydb.cursor()

def handle_close(evt):
    """
    This function will close the GUI when close event happens.

    :param evt: Event that occurs when the figure closes.
    :type evt: Event
    """

    global continue_recording
    continue_recording = False
    


def acquire_and_display_images(cam, nodemap, nodemap_tldevice):
    """
    This function continuously acquires images from a device and display them in a GUI.

    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :param nodemap_tldevice: Transport layer device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :type nodemap_tldevice: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    global continue_recording

    sNodemap = cam.GetTLStreamNodeMap()
    
    Xkp = 2.6001
    float(Xkp)
    Xki = 11.5880
    float(Xki)
    Xkd = 2.8970
    float(Xkd)
    XSetpoint = 640
    float(XSetpoint)
    
    Ykp = 7.0501
    float(Ykp)
    Yki = 6.3064
    float(Yki)
    Ykd = 1.5766
    float(Ykd)
    YSetpoint = 512
    float(YSetpoint)
    
    XlastTime = time.time()
    XlastTime = int(XlastTime)
    YlastTime = time.time()
    YlastTime = int(YlastTime)
    XInput = 0
    YInput = 0
    XOutput = 0
    YOutput = 0
    XerrSum = 0
    YerrSum = 0
    XlastErr = 0
    YlastErr = 0
    Xstack = [0, 0]
    Ystack = [0, 0]
    XS = 0
    YS = 0
    maP = 0
    step = 1
    
    sql = "UPDATE DATA SET SW = %s WHERE ID = %s"
    values = (0, 1)
    mycursor.execute(sql, values)
    mydb.commit()
    #pid = PID((kp,ki,kd), setpoint)
    #pid.output_limits(0,255)

    # Change bufferhandling mode to NewestOnly
    node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))
    if not PySpin.IsAvailable(node_bufferhandling_mode) or not PySpin.IsWritable(node_bufferhandling_mode):
        print('Unable to set stream buffer handling mode.. Aborting...')
        return False

    # Retrieve entry node from enumeration node
    node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')
    if not PySpin.IsAvailable(node_newestonly) or not PySpin.IsReadable(node_newestonly):
        print('Unable to set stream buffer handling mode.. Aborting...')
        return False

    # Retrieve integer value from entry node
    node_newestonly_mode = node_newestonly.GetValue()

    # Set integer value from entry node as new value of enumeration node
    node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

    print('*** IMAGE ACQUISITION ***\n')
    try:
        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
            return False

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
            return False

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        print('Acquisition mode set to continuous...')

        #  Begin acquiring images
        #
        #  *** NOTES ***
        #  What happens when the camera begins acquiring images depends on the
        #  acquisition mode. Single frame captures only a single image, multi
        #  frame catures a set number of images, and continuous captures a
        #  continuous stream of images.
        #
        #  *** LATER ***
        #  Image acquisition must be ended when no more images are needed.
        cam.BeginAcquisition()

        print('Acquiring images...')

        #  Retrieve device serial number for filename
        #
        #  *** NOTES ***
        #  The device serial number is retrieved in order to keep cameras from
        #  overwriting one another. Grabbing image IDs could also accomplish
        #  this.
        device_serial_number = ''
        node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
        if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
            device_serial_number = node_device_serial_number.GetValue()
            print('Device serial number retrieved as %s...' % device_serial_number)

        # Close program
        print('Press enter to close the program..')

        # Figure(1) is default so you can omit this line. Figure(0) will create a new window every time program hits this line
        #fig = plt.figure(1)
        

        # Close the GUI when close event happens
        #fig.canvas.mpl_connect('close_event', handle_close)

        # Retrieve and display images
        while(continue_recording):
            try:

                #  Retrieve next received image
                #
                #  *** NOTES ***
                #  Capturing an image houses images on the camera buffer. Trying
                #  to capture an image that does not exist will hang the camera.
                #
                #  *** LATER ***
                #  Once an image from the buffer is saved and/or no longer
                #  needed, the image must be released in order to keep the
                #  buffer from filling up.
                #time.sleep(2)
                image_result = cam.GetNextImage(100)

                #  Ensure image completion
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                else:                    

                    # Getting the image data as a numpy array
                    image_data = image_result.GetNDArray()
                    image_data = np.uint8(image_data)
                    
                    I = np.mean(image_data)
                    if I > 20 and maP == 0:
                        maP == 1
                        #UPDATE VAR  SWITCH
                        sql = "UPDATE DATA SET SW = %s WHERE ID = %s"
                        values = (1, 1)
                        mycursor.execute(sql, values)
                        mydb.commit()
                        
                    if maP == 0:
                        #map
                        mycursor.execute("SELECT * FROM DATA")
                        myresult = mycursor.fetchall()
                        
                        listOne = myresult[0]
                        Hx = listOne[1]
                        Hy = listOne[2]
                        signal = listOne[3]
                        
                        if signal == 0:
                            if Hx < 25 and Hx >= 0:
                                Hx = Hx + step
                                sql = "UPDATE DATA SET X = %s WHERE ID = %s"
                                values = (Hx, 1)
                                mycursor.execute(sql, values)
                                mydb.commit()
                            else:
                                if Hy < 25 and Hy > 0:
                                    Hy = Hy + step
                                    sql = "UPDATE DATA SET X = %s, Y = %s WHERE ID = %s"
                                    values = (0, Hy, 1)
                                    mycursor.execute(sql, values)
                                    mydb.commit()
                                else:
                                    print('error, no se encontro el laser')
                                    
                            sql = "UPDATE DATA SET HANDLER = %s WHERE ID = %s"
                            values = (1, 1)
                            mycursor.execute(sql, values)
                            mydb.commit()
                        
                    if maP == 1:
                        A = image_data
                        B = image_data
                        C = np.dstack((A, B))
                        image = np.dstack((C, B))
                        
                        #for numSegments in (100, 200, 300):
                        numSegments = 500
                        # apply SLIC and extract (approximately) the supplied number
                        # of segments
                        segments = slic(image, n_segments = numSegments, sigma = 5)
                        # show the output of SLIC
                        fig = plt.figure("Superpixels -- %d segments" % (numSegments))
                        ax = fig.add_subplot(1, 1, 1)
                        ax.imshow(mark_boundaries(image, segments))
                        plt.axis("off")
                        plt.show()
                       
                        #select mnax value
                        #mean segments
                        #lower/ more pre
                        nlabels = np.amax(segments)
                        nlabels = nlabels + 1
                        nlabels = int(nlabels)
                        values = []
                        for i in range(1,nlabels):
                            coor = np.where(segments == i)#coordenada de cada segmento
                            #co = [coor[0][0],coor[1][0]]# toma la primera coordenada de cada segmento
                            #segmentVal = image[co[0]][co[1]][2]#usa la coordenada anterior para buscar el valor en la imagen
                            arraysize = coor[0].shape# canntidad de coordenadas de el segmento actual
                            arrsiz = arraysize[0]
                            meansum = []
                            for j in range(arrsiz):
                                #individualCoor = [coor[0][j],coor[1][j]]#coordenada individual de cda pixel del segemento
                                coorVal = image[coor[0][j]][coor[1][j]][0] #valaor de cada pixel del segmento
                                meansum.append(coorVal)#se agrega el valor a un vector
                            segmentVal = np.mean(meansum)#media
                            values.append(segmentVal) #agrega ese valor a una variable (la media de cada segmento)
                        maxsegment = np.where(values == np.amax(values))#elige segmento con valor maximo
                        maxS = maxsegment[0] + 1# compensacion del 0 en el indice del array
                        maxseg = maxS[0]
                        #print(maxseg)
                        maxVC = np.where(segments == maxseg) #selecciona todas las coordenadas del segmento con valor maximo
                        #calcular la distancia desde el segmento hasta el centro
                        arraysz = maxVC[0].shape #dimencion del conjunto de coordenadas del segmento
                        arsz = int(arraysz[0]/2)    #la mitad de ese conjunto
                        XselectCoor = maxVC[1][arsz] #coordenada intermedia en x
                        X = XselectCoor
                        YselectCoor = maxVC[0][arsz] #coordenada intermedia en y
                        Y = YselectCoor
                        
                        #mid coor
                        #2-3 s faster/ less pre
    # =============================================================================
    #                     nlabels = np.amax(segments)
    #                     nlabels = nlabels + 1
    #                     nlabels = int(nlabels)
    #                     values = []
    #                     for i in range(1,nlabels):
    #                         coor = np.where(segments == i)#coordenada de cada segmento
    #                         arraysize = coor[0].shape# canntidad de coordenadas de el segmento actual
    #                         arrsiz = arraysize[0]
    #                         arsz = int(arrsiz/2)
    #                         co = [coor[0][arsz],coor[1][arsz]]# toma la primera coordenada de cada segmento
    #                         segmentVal = image[co[0]][co[1]][0]#usa la coordenada anterior para buscar el valor en la imagen
    #                         values.append(segmentVal) #agrega ese valor a una variable 
    #                     maxsegment = np.where(values == np.amax(values))#elige segmento con valor maximo
    #                     maxS = maxsegment[0] + 1# compensacion del 0 en el indice del array
    #                     maxseg = maxS[0]
    #                     #print(maxseg)
    #                     maxVC = np.where(segments == maxseg) #selecciona todas las coordenadas del segmento con valor maximo
    #                     #calcular la distancia desde el segmento hasta el centro
    #                     arraysz = maxVC[0].shape #dimencion del conjunto de coordenadas del segmento
    #                     arsz = int(arraysz[0]/2)    #la mitad de ese conjunto
    #                     selectCoor = maxVC[1][arsz] #coordenada intermedia en x
    #                     X =  selectCoor
    #                     selectCoor = maxVC[0][arsz] #coordenada intermedia en x
    #                     Y = selectCoor
    # =============================================================================
                        
                        #PID x
                        XInput = X
                        Xnow = time.time()
                        XtimeChange = (Xnow - XlastTime)
                        Xerror = (XInput - XSetpoint)*(-1)
                        XerrStack = (Xerror * XtimeChange)
                        Xstack.append(XerrStack)
                        Xstack.pop(0)
                        XerrSum = sum(Xstack)  
                        #3.57745-4.37742
                        #0.7999700000000001
                        XdErr = (Xerror - XlastErr) / XtimeChange
                        XOutput = Xkp * Xerror + Xki * XerrSum + Xkd * XdErr
                        XlastErr = Xerror
                        XlastTime = Xnow
                        
                        XOutput = XOutput / 1000
                        Xdist =  XOutput * 0.00004
                        print(str(Xerror) + " salida = " + str(XOutput) + " dista = " + str(Xdist))
                       
                        #Upgrade values mariadb
                        if Xerror < 45 and Xerror > -45:
                            XS = 1
                            sql = "UPDATE DATA SET X = %s WHERE ID = %s"
                            values = (0, 1)
                            mycursor.execute(sql, values)
                            mydb.commit()
                        else:
                            sql = "UPDATE DATA SET X = %s WHERE ID = %s"
                            values = (Xdist, 1)
                            mycursor.execute(sql, values)
                            mydb.commit()
                        
                        #PID y
                        YInput = Y
                        Ynow = time.time()
                        YtimeChange = (Ynow - YlastTime)
                        Yerror = (YInput - YSetpoint)*(-1)
                        YerrStack = (Yerror * YtimeChange)
                        Ystack.append(YerrStack)
                        Ystack.pop(0)
                        YerrSum = sum(Ystack)  
                        #3.57745-4.37742
                        #0.7999700000000001
                        YdErr = (Yerror - YlastErr) / YtimeChange
                        YOutput = Ykp * Yerror + Yki * YerrSum + Ykd * YdErr
                        YlastErr = Yerror
                        YlastTime = Ynow
                        
                        YOutput = YOutput / 1000
                        Ydist =  YOutput * 0.00004
                        print(str(Yerror) + " salida = " + str(YOutput) + " dista = " + str(Ydist))
                       
                        #Upgrade values mariadb
                        if Yerror < 45 and Yerror > -45:
                            YS = 1
                            sql = "UPDATE DATA SET Y = %s WHERE ID = %s"
                            values = (0, 1)
                            mycursor.execute(sql, values)
                            mydb.commit()
                        else:
                            sql = "UPDATE DATA SET Y = %s WHERE ID = %s"
                            values = (Ydist, 1)
                            mycursor.execute(sql, values)
                            mydb.commit()
                            
                        if XS == 1 and YS == 1:
                            continue_recording=False
                            sql = "UPDATE DATA SET X = %s, Y = %s WHERE ID = %s"
                            values = (0, 0, 1)
                            mycursor.execute(sql, values)
                            mydb.commit()

                    # Draws an image on the current figure
                    #plt.imshow(image_data, cmap='gray')
#Data               #image_data is a image in array data
                    #print('Ploting images')
                    # Interval in plt.pause(interval) determines how fast the images are displayed in a GUI
                    # Interval is in seconds.
                    #plt.pause(0.001)
                    # Clear current reference of a figure. This will improve display speed significantly
                    #plt.clf()
                    
                    # If user presses enter, close the program
                    if keyboard.is_pressed('ENTER'):
                    #    print('Program is closing...')
                        
                        # Close figure
                    #    plt.close('all')             
                    #    input('Done! Press Enter to exit...')
                        continue_recording=False   
                        sql = "UPDATE DATA SET X = %s, Y = %s WHERE ID = %s"
                        values = (0, 0, 1)
                        mycursor.execute(sql, values)
                        mydb.commit()

                #  Release image
                #
                #  *** NOTES ***
                #  Images retrieved directly from the camera (i.e. non-converted
                #  images) need to be released in order to keep from filling the
                #  buffer.
                image_result.Release()

            except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False

        #  End acquisition
        #
        #  *** NOTES ***
        #  Ending acquisition appropriately helps ensure that devices clean up
        #  properly and do not need to be power-cycled to maintain integrity.
        cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return True;#retornar image_data


def run_single_camera(cam):
    
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.

    :param cam: Camera to run on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Acquire images
        #result =bool , image_data
        result = acquire_and_display_images(cam, nodemap, nodemap_tldevice)
        result&=result
        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result;


def main():
    sql = "UPDATE DATA SET X = %s, Y = %s WHERE ID = %s"
    values = (0, 0, 1)
    mycursor.execute(sql, values)
    mydb.commit()
    
    """
    Example entry point; notice the volume of data that the logging event handler
    prints out on debug despite the fact that very little really happens in this
    example. Because of this, it may be better to have the logger set to lower
    level in order to provide a more concise, focused log.

    :return: True if successful, False otherwise.
    :rtype: bool
    """
    result = True

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Get current library version
    version = system.GetLibraryVersion()
    print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    print('Number of cameras detected: %d' % num_cameras)

    # Finish if there are no cameras
    if num_cameras == 0:

        # Clear camera list before releasing system
        cam_list.Clear()
        image_data=[10,10]

        # Release system instance
        system.ReleaseInstance()

        print('Not enough cameras!')
        #input('Done! Press Enter to exit...')
        return False, image_data

    # Run example on each camera
    for i, cam in enumerate(cam_list):

        print('Running example for camera %d...' % i)
        #time.sleep(2)
        result = run_single_camera(cam)
        result&=result
        print('Camera %d example complete... \n' % i)

    # Release reference to camera
    # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
    # cleaned up when going out of scope.
    # The usage of del is preferred to assigning the variable to None.
    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()
    
    #input('Done! Press Enter to exit...')
    #return only bool # return result


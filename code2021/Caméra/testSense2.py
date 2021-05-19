##opencv example

import pyrealsense2 as rs
import numpy as np
import cv2

def trackChaned(x):
  pass
# Configure depth and color streams

pipeline = rs.pipeline()
config = rs.config()
#config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

kernel = np.ones((5,5),np.int8)
'''
cv2.namedWindow("H Value")
cv2.createTrackbar("Max", "H Value",0,255,trackChaned)
cv2.createTrackbar("Min", "H Value",0,255,trackChaned)
cv2.namedWindow("S Value")
cv2.createTrackbar("Max", "S Value",0,255,trackChaned)
cv2.createTrackbar("Min", "S Value",0,255,trackChaned)
cv2.namedWindow("V Value")
cv2.createTrackbar("Max", "V Value",0,255,trackChaned)
cv2.createTrackbar("Min", "V Value",0,255,trackChaned)
'''
'''
cv2.namedWindow("Binary")
cv2.createTrackbar("Max","Binary",0,255,trackChaned)
cv2.createTrackbar("Min","Binary",0,255,trackChaned)
'''

# Start streaming
pipeline.start(config)

try:
    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        #depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue
        '''
        h_h=cv2.getTrackbarPos("Max", "H Value")
        h_l=cv2.getTrackbarPos("Min", "H Value")
        v_h=cv2.getTrackbarPos("Max", "V Value")
        v_l=cv2.getTrackbarPos("Min", "V Value")
        s_h=cv2.getTrackbarPos("Max", "S Value")
        s_l=cv2.getTrackbarPos("Min", "S Value")
        '''
        '''
        huh=cv2.getTrackbarPos("Max", "Binary")
        hul=cv2.getTrackbarPos("Min", "Binary")
        '''
        # Convert images to numpy arrays
        #depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        hsv_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
        l_orange = np.array([0,110,114])
        h_orange = np.array([12,255,255])
        mask = cv2.inRange(hsv_image,l_orange,h_orange)
        result = cv2.bitwise_and(color_image,color_image,mask=mask)
        res_gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        ret,res_binary = cv2.threshold(res_gray,0,255,cv2.THRESH_BINARY)
        res_erode = cv2.erode(res_binary,kernel,iterations=3)

        cnts, hierarchy = cv2.findContours(res_erode,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        for i in cnts:
            #Moment = cv2.moments(cnts)
            Moment = cv2.moments(res_erode)
            cX = int(Moment["m10"] / Moment["m00"])
            cY = int(Moment["m01"] / Moment["m00"])
            cv2.circle(color_image,(cX,cY),7,(255,255,255),-1)
            cv2.putText(color_image, "center", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            print(cX,cY)
        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        #depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        
        # Stack both images horizontally
        #images = np.hstack((color_image, output))

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', color_image)
        key = cv2.waitKey(1)
        if(key == 27):
            break

finally:

    # Stop streaming
    pipeline.stop()

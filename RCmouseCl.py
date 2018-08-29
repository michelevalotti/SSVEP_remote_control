import numpy as np
from socket import *
import cv2


'''client for remote control of the robot using mouse input. This script receives and displays the camera feed from the robot.
Use a double click to select a target on the displayed feed, the robot will turn towards it and drive forward'''


s = socket(AF_INET,SOCK_STREAM)
host = '10.245.31.75'
port = 12391
s.connect((host, port))

x = 0


def doubleclick_pos(event,x,y,flags,param):
	global mouseX,mouseY
	if event == cv2.EVENT_LBUTTONDBLCLK:
		mouseX, mouseY = x, y



frame_extra = ''

mouseX, mouseY = 320, 240


while(True):
	

	frame = frame_extra
	frame_extra = ''

	while(True):

		# receive and display frame

		rec = s.recv(2048)
		frame += rec
		
		RGBIMGpos = frame.find('RGBIMG')
		if RGBIMGpos != -1:
			startRGB = 6 + RGBIMGpos
		GRAYIMGpos = frame.find('GRAIMG')
		if GRAYIMGpos != -1:
			startDEPTH = 6 + GRAYIMGpos
		ENDIMGpos = frame.find('ENDIMG')
		if ENDIMGpos != -1:
			endDEPTH = ENDIMGpos
			break

	frame_extra += frame[(endDEPTH+6):]
	frameRGB = frame[startRGB:(startDEPTH-6)]
	frameDEPTH = frame[startDEPTH:endDEPTH]


	# if len(frame) == 307200:
	frameRGB = np.fromstring(frameRGB, dtype=np.uint8)
	frameRGB = cv2.imdecode(frameRGB,1) # rgb frame is jpg encoded
	frameRGB = frameRGB.reshape(480,640,3)
	
	frameDEPTH = np.fromstring(frameDEPTH, dtype=np.uint16) # depth frame is 10 bit
	frameDEPTH = frameDEPTH.reshape(480,640)
	depth_eight = np.uint8(frameDEPTH)


	cv2.imshow('depth', depth_eight)
	cv2.imshow('RGB', frameRGB)
	cv2.setMouseCallback('RGB', doubleclick_pos)
	s.send(str(mouseX)+','+str(mouseY))



	k = cv2.waitKey(50) & 0xFF
	if k == ord('x'): # x key closes display window and shuts down robot
		s.send('x')
		s.close()
		break


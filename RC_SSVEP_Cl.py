import numpy as np
from socket import *
import cv2
import sys, os

from stimuli import *


'''remote control of robot using EEG headset. Streams feed from camera on the robot, when the robot stops iot grabs a frame from the camera,
segments it and flickers 1 to 3 targets, the final target is selected using the EEG kit to measure SSVEPs, and its coordinates are sent 
to the robot.
The targets are shown and flickerd by stimuli.py and the data gathered by the EEG kit is anakysed by the CNN in order to decode the frequency,
each frequency corresponds to a target.'''



s = socket(AF_INET,SOCK_STREAM)
host = '129.234.103.140'
port = 12391
s.connect((host, port))



frame_extra = '' # anything that is left of the frame string after 'ENDIMG'

# default target coords, center of the frame
targetX = 320
targetY = 240


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



	frameRGB = np.fromstring(frameRGB, dtype=np.uint8)
	frameRGB = cv2.imdecode(frameRGB,1) # rgb frame is jpg encoded
	frameRGB = frameRGB.reshape(480,640,3)
	
	frameDEPTH = np.fromstring(frameDEPTH, dtype=np.uint16) # depth frame is 10 bit
	frameDEPTH = frameDEPTH.reshape(480,640)


	cv2.imshow('image', frameRGB)

	target = np.array([targetX,targetY])
	s.send(target.tostring())
	

	rec_str = s.recv(4) # refceive robot status (turn, forw or stop)
	
	if rec_str == 'stop':

		while(True):
			# when robot stops, run stimuli and get new target coordinates

			cv2.imwrite('rgb.jpg', frame) # save for stimuli.py script
			np.save('depth.npy', depth) # save as numpy array because it is 10 bit

			print 'RUN LSL SCRIPT ON WINDOWS MACHINE'

			center_coords = getCoordinates() # calls stimuli.py and gets new target coordinates based on EEG CNN results
			targetX = center_coords[0]
			targetY = center_coords[1]

			if (targetX != 1000 and targetY != 1000): # targetX and targetY are 1000 when getCoordinates() doesn't find any objects to flicker
				break



	k = cv2.waitKey(50) & 0xFF
	if k == ord('x'): # x key closes display window and shuts down robot
		s.send('x')
		s.close()
		break

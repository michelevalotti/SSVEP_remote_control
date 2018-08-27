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

	while len(frame) < 307200:
		
		rec = s.recv(307203)

		frame += rec

		# if len(frame) >= 307200:
		# 	break

	startim = 3+frame.find('XXX')
	frame_extra += frame[(startim+307200):]
	frame = frame[startim:(startim+307200)]


	if len(frame) == 307200:
		frame = np.fromstring(frame, dtype=np.uint8).reshape(480,640)
		cv2.imshow('image', frame)
		cv2.setMouseCallback('image', doubleclick_pos)
		s.send(str(mouseX)+','+str(mouseY))


	else:
		x += 1
		#print 'frame skipped', x



	k = cv2.waitKey(50) & 0xFF
	if k == ord('x'): # x key closes display window and shuts down robot
		s.send('x')
		s.close()
		break


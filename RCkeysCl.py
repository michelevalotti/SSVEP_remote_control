import numpy as np
from socket import *
import cv2
from cStringIO import StringIO
import cPickle


'''client for remote control of the robot using WASD keys, this script remotely controls the movement of the robot,
and receievs and displays the camera feed from it. Run it with RCkeysServ.py'''



s = socket(AF_INET,SOCK_STREAM)
host = '10.245.31.75'
port = 12365
s.connect((host, port))

x = 0

frame_extra = ''


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
	else:
		x += 1
		print 'frame skipped', x



	k = cv2.waitKey(50) & 0xFF
	if k == ord('x'): #esc key closes display window and shuts down robot
		s.send('x')
		break
		s.close()

	elif k == ord('w'):
		print 'sending w'
		s.send('w')

	elif k == ord('a'):
		s.send('a')
		print 'sending a'

	elif k == ord('s'):
		print 'sending s'
		s.send('s')

	elif k == ord('d'):
		print 'sending d'
		s.send('d')
	else:
		s.send('.')

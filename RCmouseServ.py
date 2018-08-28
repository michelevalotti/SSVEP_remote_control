from __future__ import division 
import socket
import freenect
import cv2
import numpy as np
import sys
from AriaPy import *
import os
import sys
import time
import stat


'''remote control of the robot with mouse double click. Run this on the robot. Streams camera feed to client and waits fror target coordinates
from the server (pixel position of double click)'''



def getDepthMap():	
	depth, timestamp = freenect.sync_get_depth()
 
	np.clip(depth, 0, 2**10 - 1, depth)
	depth >>= 2
	depth = depth.astype(np.uint8)

	return depth
	
mouseX, mouseY = 320, 240

def doubleclick_pos(event,x,y,flags,param):
	global mouseX,mouseY
	if event == cv2.EVENT_LBUTTONDBLCLK:
		#cv2.circle(blur,(x,y),100,(255,0,0),-1)
		mouseX, mouseY = x, y


# Action that allows the robot to navigate towards a target once its in the frame of the camera

class ActionTrack(ArAction):

	# Set the turn threshold, the amount to turn by and the direction to turn
	def __init__(self, turnThreshold, turnAmount):
		ArAction.__init__(self, "Turn")
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		host = '10.245.31.75'
		port = 12391
		server.bind((host, port))
		print 'socket bind created'
		server.listen(5)


		self.conn, self.addr = server.accept()
		print 'got connection from', self.addr

		self.myDesired = ArActionDesired()
		self.myTurnThreshold = turnThreshold
		self.myTurnAmount = turnAmount
		self.myTurning = 0 # 1 == left, -1 == right, 0 == none

		# initilise at random values
		self.clickX = 1000
		self.clickY = 1000
		self.centre_target_x = 0
		self.centre_target_y = 0
		self.target_depth = 10
		self.avg_target_x = 10
		self.target_dist = 10
	
	
	def setRobot(self, robot):
		# Sets myRobot in the parent ArAction class (must be done):
		print("ActionTurn: calling ArAction.setActionRobot...")
		self.setActionRobot(robot)


	# Function that defines the real work of the action
	def fire(self, currentDesired):
	
		# reset the actionDesired (must be done)
		self.myDesired.reset()
				
		depth = getDepthMap() #get depth info from kinect
		blur = cv2.GaussianBlur(depth, (9, 9), 0) #apply gaussian blur to avoid false positives and deal with random noise
		(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(blur) #find values for brightest (furthest) and darkest (closest) point in image
		cv2.circle(blur, minLoc, 30, (0, 0, 255), 2) #plot circle around closest point

		send_blur = blur.tostring()
		
		self.conn.send('XXX'+send_blur)

		blur = np.fromstring(send_blur, dtype=np.uint8).reshape(480,640)

		rec = self.conn.recv(10) # receive mouse double click coordinate
		

		if rec == 'x':
			print('Exiting...')
			Aria_exit(1)
			server.close()
		
		comma = rec.find(',') # find delimiter for two coordinates		

		mouseX = int(rec[:comma])
		mouseY = int(rec[comma+1:])

		if ((self.clickX != mouseX) or (self.clickY != mouseY)):
			self.clickX = mouseX
			self.clickY = mouseY
			self.centre_target_x = self.clickX
			self.centre_target_y = self.clickY
			self.target_depth = blur[int(mouseY), int(mouseX)]
			print mouseX, mouseY



		else:

			if (self.centre_target_x == 320 and self.centre_target_y == 240):

				self.myDesired.setVel(0) # Tell the robot to do nothing


			elif self.centre_target_x < 640/2: # Check to see if the robot needs to rotate left or right
				print('Turn Left')

				degree_left_rotation = (640/2 - self.centre_target_x)*(62/640) # 62/640 is FOV/horizontal res

				if abs(degree_left_rotation) < 1: # Check to see if the robot is aligned with target
					print('TARGET ALIGNED')
					self.myDesired.setVel(10) # Tell the robot to move forward
				else:
					print('Turning: ',degree_left_rotation)
					self.myTurning = 1
					self.myDesired.setDeltaHeading(1 * self.myTurning) # Tell the robot to rotate left by 1 degree
					self.centre_target_x += 640/62 # update position of target (move it 1 degree to the right)

			else:
				print('Turn Right')

				degree_right_rotation = (640/2 - self.centre_target_x)*(62/640)

				if abs(degree_right_rotation) < 1:
					print('TARGET ALIGNED')
					self.myDesired.setVel(10)
				else:
					print('Turning: ',degree_right_rotation)
					self.myTurning = -1
					self.myDesired.setDeltaHeading(1 * self.myTurning)

					self.centre_target_x -= 640/62

		return self.myDesired # Return the desired action for the robot 


# Initialise robot components including device, serial connection and sonar sensor

Aria_init()
parser = ArArgumentParser(sys.argv)
parser.loadDefaultArguments()
robot = ArRobot()
conn = ArRobotConnector(parser, robot)

# Create instances of the action defined above, plus ArActionStallRecover, a predefined action from Aria_
track = ActionTrack(400, 90)  # Turn threshold and turn amount
recover = ArActionStallRecover() 

  
# Check for successfull connection to the robot
if not conn.connectRobot():
	ArLog.log(ArLog.Terse, "actionExample: Could not connect to robot, Exiting.")
	Aria_exit(1)

  
# Parse all command-line arguments
if not Aria_parseArgs():
	Aria_logOptions()
	Aria_exit(1)


# Add our actions in order. The second argument is the priority, with higher priority actions going first.
robot.addAction(recover, 4)
robot.addAction(track, 2)


# Enable the robot motors
robot.enableMotors()

# Run the robot processing cycle. 'true' means to return if it loses connection, after which we exit the program.
robot.run(True)

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


'''remote control of the robot through WASD keys. Run this script on the robot. Streams camera feed to the client and
waits for keybord inputs from it'''



def getDepthMap():	
	depth, timestamp = freenect.sync_get_depth()
 
	np.clip(depth, 0, 2**10 - 1, depth)
	depth >>= 2
	depth = depth.astype(np.uint8)

	return depth



class ActionTrack(ArAction):

	# Set the turn threshold, the amount to turn by and the direction to turn
	def __init__(self, turnThreshold, turnAmount):
		ArAction.__init__(self, "Turn")
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		host = '10.245.31.75'
		port = 12365
		server.bind((host, port))
		print 'socket bind created'
		server.listen(5)


		self.conn, self.addr = server.accept()
		print 'got connection from', self.addr

		self.myDesired = ArActionDesired()
		self.myTurnThreshold = turnThreshold
		self.myTurnAmount = turnAmount
		self.myTurning = 0 # 1 == left, -1 == right, 0 == none
	
	
	def setRobot(self, robot):
		# Sets myRobot in the parent ArAction class (must be done):
		print("ActionTurn: calling ArAction.setActionRobot...")
		self.setActionRobot(robot)


	# Function that defines the real work of the action
	def fire(self, currentDesired):
	
		self.myDesired.reset()
				
		depth = getDepthMap() #get depth info from kinect
		blur = cv2.GaussianBlur(depth, (9, 9), 0) #apply gaussian blur to avoid false positives and deal with random noise
		(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(blur) #find values for brightest (furthest) and darkest (closest) point in image
		cv2.circle(blur, minLoc, 30, (0, 0, 255), 2) #plot circle around closest point

		blur = blur.tostring()
		
		self.conn.send('XXX'+blur)

		key = self.conn.recv(1)

		if key == 'a':
			print('Turn Left')
			self.myTurning = 1
			self.myDesired.setDeltaHeading(5 * self.myTurning) # Tell the robot to rotate left by 10 degrees
		elif key == 'd':
			print('Turn Right')
			self.myTurning = -1
			self.myDesired.setDeltaHeading(5 * self.myTurning) # Tell the robot to rotate right by 10 degrees
		elif key == 'w':
			print('Go Forward')
			self.myTurning = 0
			self.myDesired.setVel(50)
		elif key == 's':
			print('Go Backward')
			self.myTurning = 0
			self.myDesired.setVel(-50)
		elif key == 'x':
			print('Exiting...')
			Aria_exit(1)
			server.close()
		else:
			self.myTurning = 0
			self.myDesired.setVel(0)
		return self.myDesired # Return the desired action for the robot 



Aria_init()

parser = ArArgumentParser(sys.argv)
parser.loadDefaultArguments()
robot = ArRobot()
connect = ArRobotConnector(parser, robot)


# Create instances of the action defined above, plus ArActionStallRecover, a predefined action from Aria_
track = ActionTrack(400, 90)  # Turn threshold and turn amount
recover = ArActionStallRecover() 

  
# Check for successfull connection to the robot
if not connect.connectRobot():
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

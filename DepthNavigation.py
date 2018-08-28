from __future__ import division 
import sys
from AriaPy import *
import pickle
import os
import sys
import time
import stat

import cv2
import freenect
import matplotlib
import numpy as np


'''robot follows the closest point to the camera, i.e. finger pointed towards it. Press esc to close
camera feed and robot.'''


 

# Grabs a depth map from the Kinect sensor and creates an image from it (grayscale).

def getDepthMap():	
	depth, timestamp = freenect.sync_get_depth()
 
	np.clip(depth, 0, 2**10 - 1, depth)
	depth >>= 2
	depth = depth.astype(np.uint8)

	return depth



# Action that allows the robot to navigate towards a target once its in the frame of the camera

class ActionTrack(ArAction):

	# Set the turn threshold, the amount to turn by and the direction to turn
	def __init__(self, turnThreshold, turnAmount):
		ArAction.__init__(self, "Turn")
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
	
		# reset the actionDesired (must be done)
		self.myDesired.reset()

		while(True): #loop to get depth info, find closest point and drive robot towards it
			depth = getDepthMap() #get depth info from kinect
			blur = cv2.GaussianBlur(depth, (9, 9), 0) #apply gaussian blur to avoid false positives and deal with random noise
			

			'''edge detection'''
			# canny = cv2.Canny(blur, 5, 170);
			# _, contours, hierarchy = cv2.findContours(canny,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
			# max_contour_area = -1;
			# for cnt in contours:
			# 	area = cv2.contourArea(cnt);
			# 	if (area >  max_contour_area):
			# 		max_contour_area = area;
			# 		largest_contour = cnt;
			# cv2.drawContours(blur, contours, -1, (0,255,0), 3);

			(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(blur) #find values for brightest (furthest) and darkest (closest) point in image
			cv2.circle(blur, minLoc, 30, (0, 0, 255), 2) #plot circle around closest point

			cv2.imshow('image', blur) #show image
			k = cv2.waitKey(50) & 0xFF #set refresh rotate
			
			if k == 27: #esc key closes display window and shuts down robot
				Aria.exit(0)
				break


			target_position = minLoc
			centre_target_x = target_position[0]
			centre_target_y = target_position[1]
			
			if centre_target_x < 640/2: # Check to see if the robot needs to rotate left or right
				print('Turn Left')
				degree_left_rotation = (640/2 - centre_target_x)*(62/640) # 62/640 is FOV/horizontal res
				if abs(degree_left_rotation) < 5: # Check to see if the robot is aligned with target
					print('TARGET ALIGNED')
					self.myDesired.setVel(100) # Tell the robot to move forward
				else:
					print('Turning: ',degree_left_rotation)
					self.myTurning = 1
					self.myDesired.setDeltaHeading(10 * self.myTurning) # Tell the robot to rotate left by 2 degrees
			else:
				print('Turn Right')
				degree_right_rotation = (640/2 - centre_target_x)*(62/640)
				if abs(degree_right_rotation) < 5:
					print('TARGET ALIGNED')
					self.myDesired.setVel(100)
				else:
					print('Turning: ',degree_right_rotation)
					self.myTurning = -1
					self.myDesired.setDeltaHeading(10 * self.myTurning)
			return self.myDesired # Return the desired action for the robot 
		cv2.destroyAllWindows()


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
# robot.stopRunning(False)





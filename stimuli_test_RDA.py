from __future__ import division
import numpy as np
import cv2
from psychopy import *
import random

import rdaclient as rc

'''show 3 boxes flickering at 10, 12 and 15 hz, gather data from the EEG headset using RDA server, and save the data (with the 
corresponding labels) in numpy files to be used to train the CNN.'''

# RDA
address = ('129.234.103.236', 51244)     # server address
window = 3000              # plotting window (samples)
print 'here'
# creating a client
client = rc.Client(buffer_size=300000, buffer_window=window)
print 'client created'
client.connect(address)
print 'connected'
client.start_streaming()
print 'started streaming'


# create a window

mywin= visual.Window([800, 600],fullscr=True, monitor='testMonitor',units='deg', waitBlanking = False)

trialdur = 3 # duration of flickering in seconds
numtrials = 9 # number of times the three stimuli are shown
waitdur = 2 # duration of fixation (point shown before flickering stimuli) in seconds


# pattern1 is white frame, pattern2 is black frame. f0,1,2 are the three squares

pattern1_f0 = visual.GratingStim(win=mywin, name='pattern1',units='cm', 
				tex=None, mask=None,
				ori=0, pos=[-30, 0], size=5, sf=1, phase=0.0,
				color=[1,1,1], colorSpace='rgb', opacity=1, 
				texRes=256, interpolate=True, depth=-1.0)
pattern2_f0 = visual.GratingStim(win=mywin, name='pattern2',units='cm', 
				tex=None, mask=None,
				ori=0, pos=[-30, 0], size=5, sf=1, phase=0,
				color=[-1,-1,-1], colorSpace='rgb', opacity=1,
				texRes=256, interpolate=True, depth=-2.0)
pattern1_f1 = visual.GratingStim(win=mywin, name='pattern1',units='cm', 
				tex=None, mask=None,
				ori=0, pos=[0, 0], size=5, sf=1, phase=0.0,
				color=[1,1,1], colorSpace='rgb', opacity=1, 
				texRes=256, interpolate=True, depth=-1.0)
pattern2_f1 = visual.GratingStim(win=mywin, name='pattern2',units='cm', 
				tex=None, mask=None,
				ori=0, pos=[0, 0], size=5, sf=1, phase=0,
				color=[-1,-1,-1], colorSpace='rgb', opacity=1,
				texRes=256, interpolate=True, depth=-2.0)
pattern1_f2 = visual.GratingStim(win=mywin, name='pattern1',units='cm',			
				tex=None, mask=None,
				ori=0, pos=[30, 0], size=5, sf=1, phase=0.0,
				color=[1,1,1], colorSpace='rgb', opacity=1, 
				texRes=256, interpolate=True, depth=-1.0)
pattern2_f2 = visual.GratingStim(win=mywin, name='pattern2',units='cm', 
				tex=None, mask=None,
				ori=0, pos=[30, 0], size=5, sf=1, phase=0,
				color=[-1,-1,-1], colorSpace='rgb', opacity=1,
				texRes=256, interpolate=True, depth=-2.0)


# points to show before the flickering stimuli to tell the user where to focus

fixation0 = visual.GratingStim(win=mywin, size = 0.3, pos=[-30,0], sf=0, rgb=-1)
fixation1 = visual.GratingStim(win=mywin, size = 0.3, pos=[0,0], sf=0, rgb=-1)
fixation2 = visual.GratingStim(win=mywin, size = 0.3, pos=[30,0], sf=0, rgb=-1)
fixations = [fixation0,fixation1,fixation2]


# frequencies of the stimuli

frame_f0 = [1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1,1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1]
frame_f1 = [1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1]
frame_f2 = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]

count = 0 # initialise count of number of trials
labels = [] # list of labels to be saved
patt_list = [[pattern1_f0, pattern2_f0, frame_f0],[pattern1_f1, pattern2_f1, frame_f1],[pattern1_f2, pattern2_f2, frame_f2]]


#draw the stimuli and update the window

sample_tot = [] # array for all the samples from eeg kit



while count < numtrials:
		
	mywin.flip() # syncronises loop with refresh rate of screen

	fix_index = random.randint(0,2) # pick a random square that the user will focus on, and save its label
	labels.append(fix_index)

	for seconds in range(int(waitdur*60)): # show fixation for 2 seconds
		fixations[fix_index].draw()
		mywin.flip()

	start_sample = client.last_sample # obtain number of letest sample written to buffer (start of meaningful data in our case)

	# Loop through the required trial duration, show stimuli for 3 seconds
	for seconds in range(int(trialdur)):

		#draws square and fixation on screen.

		for frameN in range(len(frame_f0)):
			for obj in patt_list:
				frame_f0 = obj[2] # 10, 12 or 15 hz
				if frame_f0[frameN] == 1 : # show white frame
					obj[0].draw()      
				if frame_f0[frameN] == -1 : # show black frame
					obj[1].draw()
			event.clearEvents()
			mywin.flip()

	
	mywin.flip(clearBuffer=True)   

	end_sample = client.last_sample # obtain number of latest sample written to buffer (end of meaningful data in our case)

	sig = client.get_data(start_sample, end_sample) # get data from buffer
	sig = sig[:1500,:8] # slice array to get the right shape for CNN (1500 arrays of 8 elements - for 8 EEG sensors)

	sample_tot.append(sig)
	#count number of trials
	count+=1


#cleanup
mywin.close()

# save data from EEG kit and respective labels in numpy files - will be read by CNN trainer
np.save('Object_VideoStimuli_09_RDA.npy',sample_tot)
np.save('Object_VideoStimuli_09_labels_RDA.npy',labels)

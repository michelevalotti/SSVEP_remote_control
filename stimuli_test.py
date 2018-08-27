from __future__ import division
import numpy as np
import random
from psychopy import *
from socket import *

'''show 3 boxes flickering at 10, 12 and 15 hz, gather data from the EEG headset using LSL server, and save the data (with the 
corresponding labels) in numpy files to be used to train the CNN.'''


mywin= visual.Window([800, 600],fullscr=True, monitor='testMonitor',units='deg', waitBlanking = False)

trialdur = 3 # duration of trial in seconds
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

# connect to script on windows machine that sends EEG data

s = socket(AF_INET,SOCK_STREAM)
host = '10.245.233.148'
port = 12396
s.connect((host, port))


rec = s.recv(12) # windows machine connected to Data Acquisition Software

if rec == 'startstimuli':
	
	print rec
	
	# Loop through all trials
	while count < numtrials:
		
		mywin.flip() # syncronises loop with refresh rate of screen

		fix_index = random.randint(0,2) # pick a random square that the user will focus on, and save its label
		labels.append(fix_index)

		for seconds in range(int(waitdur*60)): # show fixation for 2 seconds
			fixations[fix_index].draw()
			mywin.flip()

		stream = s.recv(10) # windows machine starts to record data from Data Acquisition Software
		print stream

		# Loop through the required trial duration
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
		#count number of trials
		count+=1

	#cleanup
	mywin.close()


# receive EEG data from windows machine

x = 0
sample_tot = [] # initialise list to hold EEG data

while(True):

	sample = s.recv(104) # receive one array at a time, containing the veltages of the 8 sensors, plus 5 metadata
	
	# check sample is the rigth length (13 elements)
	
	if len(sample) < 104:
		x += 1
		print len(sample)

	if len(sample) == 104:
		sample = np.fromstring(sample) # turn sample from string to array
		sample = sample[:-5] # only keep useful data
		sample_tot.append(sample)

	if len(sample) == 0: # windows machine stopped streaming
		break



print 'skipped arrays: ', x

# sample_tot contains all the data from EEG kit, split this in 9 arrays (for 9 trials), each containing 1500 arrays of 8 elements (microvoltages from the headset)

sample1 = np.asarray(sample_tot[:1500])
sample2 = np.asarray(sample_tot[1500:3000])
sample3 = np.asarray(sample_tot[3000:4500])
sample4 = np.asarray(sample_tot[4500:6000])
sample5 = np.asarray(sample_tot[6000:7500])
sample6 = np.asarray(sample_tot[7500:9000])
sample7 = np.asarray(sample_tot[9000:10500])
sample8 = np.asarray(sample_tot[10500:12000])
sample9 = np.asarray(sample_tot[12000:13500])


sample_tot = np.asarray([sample1,sample2,sample3,sample4,sample5,sample6,sample7,sample8,sample9]).reshape(9,1500,len(sample_tot[0]))

# save daat as numpy array for CNN trainer

np.save('Object_VideoStimuli_019.npy',sample_tot)
np.save('Object_VideoStimuli_019_labels.npy',labels)

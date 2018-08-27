from __future__ import division
import numpy as np
import random
from psychopy import *
from socket import *

'''test different frequencies'''


mywin= visual.Window([800, 600],fullscr=True, monitor='testMonitor',units='deg', waitBlanking = False)

trialdur = 3 # duration of trial in seconds
numtrials = 1
waitdur = 2

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


fixation0 = visual.GratingStim(win=mywin, size = 0.3, pos=[-30,0], sf=0, rgb=-1)
fixation1 = visual.GratingStim(win=mywin, size = 0.3, pos=[0,0], sf=0, rgb=-1)
fixation2 = visual.GratingStim(win=mywin, size = 0.3, pos=[30,0], sf=0, rgb=-1)
fixations = [fixation0,fixation1,fixation2]

nBox = 3
xPos = [0, 20, 0, -20]
yPos = [10, 0, -10, 0]


frame_f0 = [1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1,1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1]
frame_f1 = [1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1]
frame_f2 = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]

count = 0
labels = []
patt_list = [[pattern1_f0, pattern2_f0, frame_f0],[pattern1_f1, pattern2_f1, frame_f1],[pattern1_f2, pattern2_f2, frame_f2]]

s = socket(AF_INET,SOCK_STREAM)
host = '10.245.233.148'
port = 12396
s.connect((host, port))


rec = s.recv(12)
# rec = 'startstimuli'


# if rec == 'startstimuli':

# 	print rec
# 	# Loop through all trials
# 	while count < numtrials:
		
# 		mywin.flip()

# 		fix_index = random.randint(0,2)
# 		labels.append(fix_index)

# 		for seconds in range(int(waitdur*60)):
# 			fixations[fix_index].draw()
# 			mywin.flip()

# 		# stream = s.recv(10)
# 		# print stream

# 		# Loop through the required trial duration
# 		for seconds in range(int(trialdur)):

# 			#draws square and fixation on screen.

# 			for frameN in range(len(frame_f0)):
# 				if frame_f0[frameN] == 1 :
# 					pattern1_f0.draw()      
# 				if frame_f0[frameN] == -1 :
# 					pattern2_f0.draw()
# 				if frame_f1[frameN] == 1 :
# 					pattern1_f1.draw()      
# 				if frame_f1[frameN] == -1 :
# 					pattern2_f1.draw()
# 				if frame_f2[frameN] == 1 :
# 					pattern1_f2.draw()      
# 				if frame_f2[frameN] == -1 :
# 					pattern2_f2.draw()

# 				mywin.flip()

		
# 		mywin.flip(clearBuffer=True)   
# 		#count number of trials
# 		count+=1

# 	#cleanup
# 	# mywin.close()



if rec == 'startstimuli':

	print rec
	# Loop through all trials
	while count < numtrials:
		
		mywin.flip()

		fix_index = random.randint(0,2)
		labels.append(fix_index)

		for seconds in range(int(waitdur*60)):
			fixations[fix_index].draw()
			mywin.flip()

		stream = s.recv(10)
		print stream

		# Loop through the required trial duration
		for seconds in range(int(trialdur)):

			#draws square and fixation on screen.

			for frameN in range(len(frame_f0)):
				for obj in patt_list:
					frame_f0 = obj[2] # 10, 12 or 15 hz
					if frame_f0[frameN] == 1 :
						obj[0].draw()      
					if frame_f0[frameN] == -1 :
						obj[1].draw()
				event.clearEvents()
				mywin.flip()

		
		mywin.flip(clearBuffer=True)   
		#count number of trials
		count+=1

	#cleanup
	mywin.close()



x = 0
sample_tot = []

while(True):

	sample = s.recv(104)
	
	if len(sample) < 104:
		x += 1
		print len(sample)

	if len(sample) == 104:
		sample = np.fromstring(sample)
		sample = sample[:-5]
		sample_tot.append(sample)

	if len(sample) == 0:
		break



print 'skipped arrays: ', x

print len(sample_tot)

sample1 = np.asarray(sample_tot[:1500])
sample2 = np.asarray(sample_tot[1500:3000])
sample3 = np.asarray(sample_tot[3000:4500])
sample4 = np.asarray(sample_tot[4500:6000])
sample5 = np.asarray(sample_tot[6000:7500])
sample6 = np.asarray(sample_tot[7500:9000])
sample7 = np.asarray(sample_tot[9000:10500])
sample8 = np.asarray(sample_tot[10500:12000])
sample9 = np.asarray(sample_tot[12000:13500])


print sample_tot[0]
sample_tot = np.asarray([sample1,sample2,sample3,sample4,sample5,sample6,sample7,sample8,sample9]).reshape(9,1500,len(sample_tot[0]))

# while(True):

# 	sample = s.recv(104)
	
# 	if len(sample) == 104:
# 		sample = np.fromstring(sample) # recieve array of 14 elements (last 5 are metadata)
# 		sample = sample[:-5]
# 		sample_tot.append(sample)
# 	if len(sample) == 0:
# 		break

# sample_tot = np.asarray(sample_tot[:1500]).reshape(1500,len(sample_tot[0]))



np.save('Object_VideoStimuli_019.npy',sample_tot)
np.save('Object_VideoStimuli_019_labels.npy',labels)
# np.save('stim3.npy',sample_tot)
# np.save('lab3.npy',labels)

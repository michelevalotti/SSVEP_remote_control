from pylsl import StreamInlet, resolve_stream
from socket import *
import numpy as np
import time


'''For this example we use a Cognionics Quick-20 EEG headset that takes data from 8 sensors (positioned on the occipital 
and parietal lobe), the rest of the data sent by the Data Acquisition Software is, respectively, x, y and z accellerometer, 
packet counter, and trigger. This script is used to gather data to train the CNN, therefore the subject is shown, in our case,
9 consecutive flickering stimuli that we alternate with fixation points (point on the screen that tell the user where to focus).
Each fixation is shown for 2 seconds, each stimulus is shown for 3 seconds.''' 


# create socket to send data to linux machine
server = socket(AF_INET, SOCK_STREAM)
host = '10.245.233.148' # ethernet: 129.234.103.169 # wifi: 10.245.233.148
port = 12399
server.bind((host,port))
print 'socket bind created'
server.listen(5)

conn,addr = server.accept()
print 'got connection from', addr


# first resolve an EEG stream on the lab network (same machine as the data aquisition software)
print "looking for an EEG stream..."
streams = resolve_stream('type', 'EEG')
print "EEG stream found"

sample_tot = [] # array to hold data from EEG kit

conn.send('startstimuli') # tell linux machine to start displaying the fixation points

for i in range(9): # 9 trials of different flickering stimuli
	inlet = StreamInlet(streams[0]) #set up stream from EEG kit

	time.sleep(2.0) #wait while fixation points are shown
	conn.send('openstream') # tell linux machine to start flickering stimuli
	inlet.open_stream() # start gathering data from Data Acquisition Software

	# pull chunk of data from buffer
	sample, timestamp = inlet.pull_chunk(max_samples=1510,timeout=3.1) # timeout in seconds, retreive data for this long (1500 arrays - max at 1510 to account for lost ones when sent)

	inlet.close_stream()

	sample_tot.append(sample)


# send array with all the data one element at a time (voltages of sensors on EEG kit)

for i in range(len(sample_tot)): # sample_tot is made of 9 arrays, each made of 1500 arrays of 13 elements (8 voltages and 5 metadata)
	for j in range(len(sample_tot[i])):
		sample_i = np.asarray(sample_tot[i][j])
		sample_i = sample_i.tostring() # turn array to string to send it over the network
		conn.send(sample_i) # send one 13 element array at a time

conn.close()
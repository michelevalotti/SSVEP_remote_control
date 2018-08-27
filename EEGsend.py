from pylsl import StreamInlet, resolve_stream
from socket import *
import numpy as np
import time


'''script to be run when the flickering stimulus is shown on the linux machine. This script gathers
the data from the Data Acquisition Software (only available on Windows) and sends it to the linux machine
to be used in the trained CNN in order to get a predicted label (target for the mobile robot)'''



# create socket to send data to linux machine
server = socket(AF_INET, SOCK_STREAM)
host = '10.245.233.148' # ethernet: 129.234.103.169 # wifi: 10.245.233.148
port = 12396
server.bind((host,port))
print 'socket bind created'
server.listen(5)

conn,addr = server.accept()
print 'got connection from', addr


# first resolve an EEG stream on the lab network
print "looking for an EEG stream..."
streams = resolve_stream('type', 'EEG')
print "EEG stream found"


conn.send('startstimuli') # tell linux machine to start displaying the fixation points

# create a new inlet to read from the stream
inlet = StreamInlet(streams[0])

time.sleep(2.0) #wait while fixation points are shown

conn.send('openstream') # tell linux machine to start flickering stimuli
inlet.open_stream() # start gathering data from Data Acquisition Software

sample, timestamp = inlet.pull_chunk(max_samples=1510,timeout=3.1) # timeout in seconds, retreive data for 3s (1500 arrays)
print len(sample), len(sample[0])
inlet.close_stream()


# send array with all the data one element at a time (voltages of sensors on EEG kit)

for i in range(len(sample)): # the array is composed of 1500 arrays, each one an array of 13 elements
	
	sample_i = np.asarray(sample[i])
	sample_i = sample_i.tostring() # turn each 13-element array into a string to send it over the network

	conn.send(sample_i)


conn.close()
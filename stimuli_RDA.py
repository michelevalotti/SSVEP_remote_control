from __future__ import division
import cv2
import numpy as np
import freenect
from psychopy import *
import sys, os
from socket import *
from eeg_cnn import *



'''take image segmented by model, pick the right contours (not too small or too big) and calculate theur distance from the camera,
these contours are the targets that are flickered at different frequencies. RDA server is used to stream the data from the EEG 
headset. This data is then fed into the CNN which gives the predicted target.'''


'''call shell script to take image and segment it'''

os.system('./demo_test.sh')


'''contours and depth'''

screenX = 3840 # resolution of monitor being used, use to rescale and display image for psychopy
screenY = 2160

# file names
rgb_and_segm_img = 'rgb_and_segm.png' # file with rgb image and object segmentation image
depth_img = 'depth.jpg' # file with depth image

# edge detections variables
lower_threshold = 112
upper_threshold = 170
sobel_size = 3
area_min = 2000
area_max = 40000
midcont = [] # contours with areas between are_min and area_max
obj_masks = [] # masks for grating shape
center_coords = []


# object segmentation (filter out floor and walls)

pred_color = cv2.imread(rgb_and_segm_img, 1)
im_rgb = pred_color[:, :640] # crop to get rgb image alone
im_seg = pred_color[:, 640:] # crop to get object segmentation image alone
hsv = cv2.cvtColor(im_seg, cv2.COLOR_BGR2HSV) # turn image in hsv color space
hsv_mask = cv2.inRange(hsv, np.array([0,100,150]), np.array([255,255,255])) # threshold on hsv image (use as mask on hsv image) - less saturated objs are background
res = cv2.bitwise_and(im_seg,im_seg,mask=hsv_mask) # result of mask on im_seg




# # get depth image to calculate depth value (use for debugging when camera is connected to client and not to robot)
# number_of_frames = 10 # number of frames to average on

# depth = np.zeros((480, 640))

# for i in range(number_of_frames):
# 	frame,_ = freenect.sync_get_depth() # 11 bits
# 	depth += frame

# depth = depth/number_of_frames
# np.clip(depth, 0, 2**10 - 1, depth) # get rid of background noise

# depth = cv2.imread(depth_img, 0) # use for debugging, gives wrong depth (since it reads 8 bit image - need 10 bit)


# load depth image sent by robot (server) and saved by client

depth = np.load('depth.npy') # read numpy array (10 bit grayscale image)


# edge detection
contour_list = []
canny = cv2.Canny(res, lower_threshold, upper_threshold, apertureSize=sobel_size) # finds edges, but not always closed contours (needed for cv2.findContours)
dilated = cv2.dilate(canny, np.ones((3, 3))) # makes sure canny edges are closed for findContours
_, contours, hierarchy = cv2.findContours(dilated,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) # finds contours around inner and outer canny edges, use hierarchy to select only inner ones
# cv2.drawContours(res, contours, -1, (255,255,0), 1) # draw all contours - debugging

# in hierarchy, if first element is -1 then contour has no other contour on same hierarchy level (is inner one), choose only inner contours (insde of canny edge line)
ind = 0 # initialise index for hierarchy
for c in contours:
	if hierarchy[0][ind][0] == -1:
		contour_list.append(c)
	ind += 1



# select valid contours from inner most one

for cont in contour_list:

	area = int(cv2.contourArea(cont))

	if (area > area_min) and (area < area_max): # only pick contours between specified values (to avoid contours aruond objects too big or too small)

		# compute center of contour
		M = cv2.moments(cont)
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])

		# calculate min depth of all valid contours for if statement
		center_neighbourhood = depth[cY-10:cY+10,cX-10:cX+10]
		center_depth = center_neighbourhood.mean()


		if center_depth < 1020: # don't calculate center of contours in background (most probably noise)

			center_coords.append([cX,cY]) # add to list of coordinates of centers of contours

			# calculate avg depth value of valid contours excluding white pixels

			each_obj = np.zeros((480,640)) # blank image
			cv2.drawContours(each_obj, [cont], -1, 255, -1) # fill valid contours on blank image
			obj_masks.append(each_obj) # use for mask in flickering image
			pts = np.where(each_obj == 255) # find coordinates of pixels in filled contours
			obj_depths = depth[pts] # get grayscale value of pixels in filled contours
			center_depth = obj_depths[np.where(obj_depths<1023)].mean() # take mean of non-white pixels (grayscale value < 1023)


			cv2.circle(im_rgb, (cX, cY), 3, (255, 255, 255), -1)
			depth_cm = int(100/((-0.00307*(center_depth))+3.33)) # convert pixel value to depth in cm, measurement not that accurate so only keep int value
			cv2.putText(im_rgb, str(depth_cm)+' '+'cm', (cX - 20, cY - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)


			print 'pixel value of depth: ', center_depth, 'depth in cm: ', depth_cm, 'at coordinates ', 'X: ', cX,'Y: ', cY
			midcont.append(cont) # 3d list of contours


cv2.drawContours(im_rgb, midcont, -1, (255,0,0), 3) # draw valid contours
im_rgb_scaled = cv2.resize(im_rgb,None,fx=screenX/640,fy=screenY/480,interpolation = cv2.INTER_CUBIC) # 640,480 are original dimensions of image
cv2.imwrite('segmented.jpg', im_rgb_scaled)


# cv2.imshow('depth', res) # openCV conflicts with psychopy, if imshow() is called, the stimuli cannot be shown
# k = cv2.waitKey(0) & 0xFF


if len(center_coords) != 0: # show flickering stimuli if we have a target

	'''stimuli'''


	#initialise variables

	waitdur = 2 # wait time before showing stimuli, in seconds
	trialdur = 3 # duration of stimuli, in seconds

	# frequescies of flickering stimuli
	tenHz = [1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1,1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1]
	twelveHz = [1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1]
	fifteenHz = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
	freqs = [tenHz, twelveHz, fifteenHz]



	# format contours for mask attribute in grating (to give grating the shape of the target)
	for mask in obj_masks:
		mask[mask==0] = -1
		mask[mask==255] = 1 # 1 is black

	obj_masks = obj_masks[:3] # have a maximum of 3 stimuli in image (frequency decoder trained on 3 frequencies)
	center_coords = center_coords[:3]



	# display image and flicker contours

	# create a window
	mywin = visual.Window((screenX,screenY),monitor="testMonitor",fullscr=True,units="deg")
	grating_list = []
	i = 0 # initialise index to assign frequencies to stimuli

	# create some stimuli
	img = visual.ImageStim(mywin, 'segmented.jpg') # show gratigs on top of this image
	for mask in obj_masks:
		grating = visual.GratingStim(win=mywin, mask=mask, units='pix', size=(screenX, -screenY), pos=[0,0], sf=3, tex='sqr') # mask is image of dim(640, 480) centered in the middle of the frame
		grating_list.append([grating, freqs[i]])
		i += 1


	fixation = visual.GratingStim(mywin, tex=None, mask='gauss', sf=0, size=0,name='fixation', autoLog=False) # empty frame to alternate with grating for flickering stimulus



	'''receive data from eeg kit to use for CNN'''

	# RDA
	address = ('129.234.103.236', 51244) # server address
	window = 3000 # plotting window (samples)
	print 'here'
	# creating a client
	client = rc.Client(buffer_size=300000, buffer_window=window)
	print 'client created'
	client.connect(address)
	print 'connected'
	client.start_streaming()
	print 'started streaming'



	# show targets for 2 second without flickering, to allow user to choose

	mywin.flip()
	for seconds in range(int(waitdur*60)): # draw just image with targets
		img.draw()
		mywin.flip()

	start_sample = client.last_sample # obtain number of letest sample written to buffer (start of meaningful data in our case)

	for seconds in range(int(trialdur)): # flicker targets
		for frameN in range(len(freqs[0])): # 60 frames (1 sec)
			img.draw()
			for obj in grating_list:
				frame_f0 = obj[1] # 10, 12 or 15 hz
				if frame_f0[frameN] == 1 :
					obj[0].draw()      
				if frame_f0[frameN] == -1 :
					fixation.draw()
			event.clearEvents()
			mywin.flip()

	mywin.flip(clearBuffer=True)

	end_sample = client.last_sample # obtain number of latest sample written to buffer (end of meaningful data in our case)
	sig = client.get_data(start_sample, end_sample) # get data from buffer
	sig = sig[:1500,:8] # slice array to get the right shape for CNN (1500 arrays of 8 elements - for 8 EEG sensors)

	# cleanup
	mywin.close()


	chosen_target = classification(sig, 0) # runs CNN on sample_tot, returns 0, 1 or 2, second parameter is not used by function

	target_coords = center_coords[chosen_target] # pick cooordinates corresponding to chosen target


else:
	target_coords = [1000,1000] # if segmentation doesn't find target to flicker tell client to repeat process


np.save('target.npy', np.array(target_coords)) # psychopy interferes with cv2, so can't call script as a function, need to save coords and read them from SSVEP client

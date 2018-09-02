# Brain computer interface (BCI) to remotely control a mobile robot with the use of a EEG kit to decode SSVEP signals

## Contents
- Introduction
- Requirements
  - Hardware
  - Software
- Description of the project
  - Controlling the robot
    - Example scripts
    - BCI navigation
  - Selecting the targets and creating the stimuli
  - Gathering and decoding the brain signal


## Introduction
The aim of this project is to create a brain-computer interface (BCI) to allow the remote control of a robot with a Cognionics Quick-20 EEG kit.

The mobile robot is programmed to find at most three targets and ask the user to confirm which one it should move towards. This process is repeated every few meters to allow a user to control the path of the robot.

The robot selects the targets by segmenting the image it acquires from its camera and selecting the biggest objects in the scene. It then flickers these targets at different frequencies (10, 12 anf 15 hz), allowing the user to focus on one.

The EEG headset reads the brain signals in the Occipital and Partietal lobe, the regions responsible for vision, when the user looks at the flickering stimulus on a screen. The raw data is fed (using either Lab Streaming Layer, or LSL, or RDA server) to a Convolutional Neural Network (CNN) which attemps to decode it to recover the frequency of the stimulus.

Once the target is acquired, the robot turns and moves towards it before repeating the process again to find a new target.


## Requirements
### Hardware
The robot used in this project was a Pioneer 3-AT, on which we attached an Xbox 360 Kinect. The two were connected to a laptop, running linux, that rested on the robot.

It is important to note that the kinect has a depth range of ~1-5 meters, so objects to close to it will saturate the sensor and appear as far, while all objects beyond a certain distance will generate random noise.

The headset used to read the brain signals was a Cognionics Quick-20, which was particularly convinient as it functions using dry sensors. The data from 8 sensors was recorded (7 on the Occipital and Parietal lobes and one for reference).

The software to acquire the data from the EEG kit was run on a windows machine (see next section), and the rest of the scripts were run from a separate linux machine.

### Software
Python2.x and Python3.x -- unfortunately some libraries run only on either one or the other verion.
The requirements are:
- Numpy
- Socket
- OpenCV
- freenect
- AriaPy
- [PsychoPy](http://psychopy.org/installation.html)
- [rdaclient](https://github.com/belevtsoff/rdaclient.py)
- pylsl

Instructions to install freenect, and its python wrapper can be found [here](https://github.com/OpenKinect/libfreenect) and [here](https://github.com/OpenKinect/libfreenect#fetch-build), respectively -- this module only seems to work with the Xbox360 version of the Kinect, not the later released Windows version.

AriaPy can be installed from [here](http://robots.mobilerobots.com/wiki/ARIA) -- connecting the robot to a laptop can be tricky:
- it might be necessary to run ```sudo chmod -R 666 /dev/ttyUSB0 ``` to give access to the usb port
- If it does not exist already, create a file named Aria.args in /etc and add the text ```-robotPort /dev/ttyUSB0```

The Cognionics Data Acquisition software can be daownloaded [here](http://cognionics.com/wiki/pmwiki.php/Main/DataAcquisitionSoftware). This software only runs on windows, but can be connected to other operating systems through a network.


## Descriptiom of the project
### Controlling the robot

_Example Scripts_

DepthNavigation.py and PointnClick.py run on the laptop connected to the robot. The first selects the target as the closest point to the kinect sensor and guides to robot towards it. The way this script was used was to make the robot follow the user's finger when this was pointed towards the camera sensor. The second script is a useful demo to understand how to operate the robot: on the laptop a feed of the camera is shown and a double click on it selects the target for the robot, this can be repeated to select new targets.

**A note on how AriaPy works:**
A class is defined where the variables are initialised, as well as a function called fire(): this is where we tell the robot what to do. To conrtol the robot we then add actions and call run(): this function repeatedly calls fire() in an infinite loop.

Other example scripts include Remote Control (RC) scripts, each having a Server (Serv) script, running on the robot, and a Client (Cl) script, running on another machine. Examples include controlling the robot with WASD keys and  mouse clicks.

_BCI Navigation_

The scripts to run to control the robot with the EEG headset are RC_SSVEP_Serv.py and RC_SSVEP_Cl.py for the server (running on the robot) and client respectively. The robot broadcasts its status to the client and when it stops, the client calls a script to segment the Kinect image and select possible targets, flicker them and connect to the EEG data stream to select the final target.

### Selecting the targets and creating the stimuli

When the robot stops, the script Stimuli_RDA.py receives the RGB and Depth images from the Kinect camera, and uses a [neural network](https://github.com/CSAILVision/semantic-segmentation-pytorch) to segment the RGB image. The background and floor planes are then discarded using a HSV filter, as they have low saturation. Of the ramaining contours, the ones with reasonably sized areas are selected and their depth calculated from the Kinect data. If they are not too far they are then flickered at 10, 12 and 15 hz. A maximum of three targets is selelcted, as the CNN to decode the signal is trained on three classes.

### Gathering and decoding the brain signal

As was mentioned before, the Data Acquisition Software (DAS) from Cognionics only runs on Windows, so it is necessary to stream its data to our linux machine. To do this we can use either Lab Streaming Layer (LSL) or RDA server. The best results were achieved with RDA, but this repository includes the code for LSL too.

We were able to connect RDA directly from the DAS to our linux machine, but LSL needed an intermidiate script to be run on the Windows machine and then send the data with socket.

_RDA_

Stimuli_RDA.py is called by the robot navigation script, automatically connects to the DAS and pulls the required data from it.
Stimuli_test_RDA.py is used to get training data for the CNN: it runs an arbitrary number of stimuli and records the labels of the frequency the user is looking at. It is advisable to train and test the CNN on the same day, as the EEG data is subject to daily variations.

_LSL_

The LSL scripts run in a much similar way to the RDA ones, but require two additional ones to gather the data from the DAS and send it to the linux machine. These are EEGsendLSL.py and EEGtestSendLSL.py, they run on the Window machine where the DAS runs. EEGtestSendLSL.py is used to acquire training data for the CNN, whereas EEGsendLSL.py must be run when Stimuli_LSL.py starts showing the stimulus.

_Neural Network_

The CNN used to interpret the raw signal from the EEG kit was kindly provided by Ms Nik Khadijah Nik Aznan. It is a one layer deep network trained on band-pass filtered and referenced data, that achieves accuracies of 95-100 %. More information about the network and the Cognionics headset can be found in [this paper](https://arxiv.org/pdf/1805.04157.pdf).

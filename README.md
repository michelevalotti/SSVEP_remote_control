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

The EEG headset reads the brain signals in the Occipital and Partietal lobe, the regions responsible for vision, when the user looks at the flickering stimulus on a screen. The raw data is fed to a Convolutional Neural Network (CNN) which attemps to decode it to recover the frequency of the stimulus.

Once the target is acquired, the robot turns and moves towards it before repeating the process again to find a new target.


## Requirements
### Hardware
The robot used in this project was a Pioneer 3-AT, on which we we attached an Xbox 360 Kinect. The two were connected to a laptop, running linux, that rested on the robot.
The headset used to read the brain signals was a Cognionics Quick-20, which was particularly convinient as it functions using dry sensors.
The software to acquire the data from the EEG kit was run on a windows machine (see next section), and the rest of the scripts were run from a separate linux machine

### Software
Python2.x and Python3.x -- unfortunately some libraries run only on either one or the other verion.
The requirements are:
- Numpy
- Socket
- OpenCV
- freenect
- AriaPy

Instructions to install freenect, and its python wrapper can be found [here](https://github.com/OpenKinect/libfreenect) -- this module only seems to work with the Xbox360 version of the kinect, not the later released Windows version.

AriaPy can be installed from [here](http://robots.mobilerobots.com/wiki/ARIA) -- connecting the robot to a laptop can be tricky:
- it might be necessary to run ```sudo chmod -R 666 /dev/ttyUSB0 ``` to give access to the usb port
- If it does not exist already, create a file named Aria.args in /etc and add the text ```-robotPort /dev/ttyUSB0```

The Cognionics Data Acquisition software can be daownloaded [here](http://cognionics.com/wiki/pmwiki.php/Main/DataAcquisitionSoftware). This software only runs on windows, but can be connected to other operating systems through a network.


## Descriptiom of the project
### Controlling the robot

_Example Scripts_

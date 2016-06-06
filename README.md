#Description
This project provides an easy to use GUI for creating data visualizations from HOBO Energy sensors. 
There are four types of HOBO Energy sensors: light, power, temperature/humidity, and state sensors.
The Green Labs Team at Case Western Reserve University has been installing these sensors in labs around campus.
However, the wealth of data they were collecting was not being well utilized.
This software tool attempts to bridge the gap between data collection and deep insights into ways to change behavior and increase sustainability on campus.

#Requirements
* pyInstaller==3.2
* pandas==0.18.0
* matplotlib==1.5.1
* numpy==1.11.0
* pyQt5
* Qt5.6
* QtCreator5 (Only neccesary for easily editing the UI file)

Other versions of these packages might work, however they have not been tested.
To convert the source code into an easy-to-use .exe file, use the following command:

`pyinstaller main.py -F -w -n green_labs_visualization`

#Data Description


#Usage


#Demos

The GUI is shown below:
<img align="center" src="https://cloud.githubusercontent.com/assets/6250320/15837941/9efefafe-2c09-11e6-9d98-e7ac68c50df7.PNG">


Here are some of the visualizations the GUI allows the user to easily create:
<img align="center" src="https://cloud.githubusercontent.com/assets/6250320/15837951/a7f1655c-2c09-11e6-9575-e2f61eaa6a22.png">
<img align="center" src="https://cloud.githubusercontent.com/assets/6250320/15837954/adce343c-2c09-11e6-93b7-01c48aee99be.png">
<img align="center" src="https://cloud.githubusercontent.com/assets/6250320/15837946/a405183a-2c09-11e6-841f-1f3d6e58629b.png">

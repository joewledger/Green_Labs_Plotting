#Description
The Green Labs Team at Case Western Reserve University has been installing Hoboware Energy sensors in labs around campus.
However, the wealth of data they were collecting was not being well utilized.
This project provides an easy to use GUI for creating data visualizations from HOBO Energy sensors.
These visualizations are fully customizable, and allow non-technical team members to make edits to visualizations through the GUI, **without writing any additional code**.

#Goal

This software tool attempts to bridge the gap between **data collection** and **deep insights** into ways to change behavior and increase sustainability on campus.

#Requirements
* Python 3.5
* pyInstaller==3.2
* pandas==0.18.0
* matplotlib==1.5.1
* numpy==1.11.0
* pyQt5
* Qt5.6
* QtCreator5 (Only neccesary for easily editing the UI file)

Other versions of these packages might work, however they have not been tested. PyQt5 and Qt5.6 are definately required.

To propagate changes to the Qt Creator UI file to the application source code, use the following command:

    `pyuic5 mainwindow.ui > mainwindow.py`

To run the python version of the program, use the following command:

    `py -3.5 main.py`

To convert the source code into an easy-to-use .exe file, use the following command:

    `pyinstaller main.py -F -w -n green_labs_visualization`


#Data Description

There are four types of HOBO Energy sensors: light, power, temperature/humidity, and state sensors. The properties of each of the data sources are listed in the table below.

| Sensor Type | Data Type | Missing Values | Even Time Increments | Number of Columns |
| --- | --- | --- | --- | --- |
| State | Boolean | Yes | No | 1 |
| Power | Float | No | Yes | 21 |
| Lighting | Boolean | Yes | No | 6 |
| Temperature | Float | No | Yes | 3 |

#Usage

Full instructions for software usage are posted on the CWRU Green Labs Google Drive. On request, a link to the tutorial will be granted. However, the software should be mostly intuitive to use.

#Licensing



#Demos

The GUI is shown below:
<img align="center" src="https://cloud.githubusercontent.com/assets/6250320/15837941/9efefafe-2c09-11e6-9d98-e7ac68c50df7.PNG">


Here are some of the visualizations the GUI allows the user to easily create:
<img align="center" src="https://cloud.githubusercontent.com/assets/6250320/15837951/a7f1655c-2c09-11e6-9575-e2f61eaa6a22.png">
<img align="center" src="https://cloud.githubusercontent.com/assets/6250320/15837954/adce343c-2c09-11e6-93b7-01c48aee99be.png">
<img align="center" src="https://cloud.githubusercontent.com/assets/6250320/15837946/a405183a-2c09-11e6-841f-1f3d6e58629b.png">

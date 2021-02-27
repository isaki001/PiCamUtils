# Measure Water Level using Raspberry PI
This project is about measuring water level using Raspberry PI.

## Program Options

```
$ ./watertank.py --help
usage: pi [-h] {capture,test,train} ...

Raspberry Pi Water Tank Demo

positional arguments:
  {capture,test,train}
    capture             Capture Images
    test                Test images
    train               Train Images

optional arguments:
  -h, --help            show this help message and exit

```
1. Train the model: ./watertank.py train (add --debug flag for debug options)
3. Test the model: ./watertank.py test <image name> (add --debug flag for debug options) : ./watertank.py test testImage1.jpg

## Project Code Description 

```
.
├── images                 # Module for aggregating and reporting data from multiple data sources 
├── watertank.py           # Code for measuring water tank level and turning the respective LED ligts 
```

## Image Description

```
images
├── testing              # Testing Images
├── training             # Training Images 
```

**Testing Images**

Image Name| Water Level | LED Lights
---------|------------|--------------- 
 testImage1.jpg           |  low-mid      |  green
 testImage2.jpg           |  low          |  green
 testImage3.jpg           |  empty        |  green
 testImage4.jpg           |  empty        |  green
 testImage5.jpg           |  low          |  green
 testImage6.jpg           |  mid          |  yellow
 testImage7.jpg           |  mid          |  yellow 
 testImage8.jpg           |  mid          |  yellow
 testImage9.jpg           |  mid-high     |  yellow
 testImage10.jpg          |  mid-high     |  yellow
 testImage11.jpg          |  mid-high     |  yellow
 testImage12.jpg          |  mid-high     |  yellow
 testImage13.jpg          |  high         |  red
 testImage14.jpg          |  high         |  red
 testImage17.jpg          |  > high       |  red
 testImage18.jpg          |  > high       |  red
 testImage19.jpg          |  > high       |  red
 testImage20.jpg          |  > high       |  red
 testImage21.jpg          |  > high       |  red

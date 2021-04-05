# Flooding Alarm System using Raspberry PI
This project measures the flooding levels using Raspberry PI by comparing images and turns on the respective LED to alert the user.

## DEPENDENCIES
* Python3 
* picamera
* OpenCV
* gpiozero

## Project Assumptions
1. The code requires 256*256 pixel images.
2. This project was simulated on a fish tank.
3. All the training and testing images must capture the entire fishtank.
4. More than 90% of the image must be the fish tank to reduce the surrounding noise for better results. 

## LED Color Codes

LED Color| Water Level | 
---------|------------| 
RED      | High Water Level
YELLOW   | Moderate Water Level
GREEN    | Low Water Level

## Program Options
```
$ ./watertank.py 
1: Capture Image 
2: Training the Model 
3: Testing the Model
0: Exit

```

## Project Code Description 

```
.
├── images                 # Module for aggregating and reporting data from multiple data sources 
│  ├── testing             # Testing Images
│  ├── training            # Training Images
│  ├── intrermediate       # Intermediate Images
├── watertank.py           # Code for measuring water tank level and turning the respective LED ligts
├── configmanagement.py    # Read and writing configuration files
├── configuration
│  ├── config.ini          # Configuration file
│  ├── config              # Serialized Config object
```

## Truth Set of Testing Images

Image Name| Water Level | Expected LED Light | Predicted LED Light | Pass/Fail
---------|------------|---------------|---------------|---------------|--------------- 
 testImage1.jpg           |  low-mid      |  green     |  green       |  Pass
 testImage2.jpg           |  low          |  green     |  green       |  Pass
 testImage3.jpg           |  empty        |  green     |  green       |  Pass
 testImage4.jpg           |  empty        |  green     |  green       |  Pass
 testImage5.jpg           |  low          |  green     |  green       |  Pass
 testImage6.jpg           |  mid          |  yellow    |  yellow      |  Pass
 testImage7.jpg           |  mid          |  yellow    |  yellow      |  Pass
 testImage8.jpg           |  mid          |  yellow    |  yellow      |  Pass
 testImage9.jpg           |  mid-high     |  yellow    |  yellow      |  Pass     
 testImage10.jpg          |  mid-high     |  yellow    |  yellow      |  Pass  
 testImage11.jpg          |  mid-high     |  yellow    |  yellow      |  Pass  
 testImage12.jpg          |  mid-high     |  yellow    |  red         |  Fail  
 testImage13.jpg          |  high         |  red       |  red         |  Pass  
 testImage14.jpg          |  high         |  red       |  red         |  Pass  
 testImage17.jpg          |  > high       |  red       |  red         |  Pass  
 testImage18.jpg          |  > high       |  red       |  red         |  Pass  
 testImage19.jpg          |  > high       |  red       |  red         |  Pass  
 testImage20.jpg          |  > high       |  red       |  red         |  Pass  
 testImage21.jpg          |  > high       |  red       |  red         |  Pass  
 testImage22.jpg          |  > high       |  red       |  red         |  Pass  
 testImage23.jpg          |  > high       |  red       |  red         |  Pass 

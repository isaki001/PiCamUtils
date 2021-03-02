import configparser
import pickle
import os

def setup_config_file(configDict):
    configObj = configparser.ConfigParser()
    conf_path = os.path.join(os.path.dirname(__file__), "configuration")
    configObj.read(os.path.join(conf_path, "config.ini"))
    conf_record = dict(waterHeightLow=configDict.get("lowWater", float(configObj['LOW']['WATER'])),
                        waterHeightMid=configDict.get("midWater" , float(configObj['MID']['WATER'])),
                        waterHeightHigh=configDict.get("highWater" , float(configObj['HIGH']['WATER'])),
                        heightDifferenceLow=configDict.get("lowLand", float(configObj['LOW']['DIFFERENCE'])),
                        heightDifferenceMid=configDict.get("midLand", float(configObj['MID']['DIFFERENCE'])),
                        heightDifferenceHigh=configDict.get("highLand", float(configObj['HIGH']['DIFFERENCE'])),
                        waterLandRatioLow=configDict.get("ratioLow", float(configObj['LOW']['RATIO'])),
                        waterLandRatioMid=configDict.get("ratioMid", float(configObj['MID']['RATIO'])),
                        waterLandRatioHigh=configDict.get("ratioHigh", float(configObj['HIGH']['RATIO'])),
                        debug=configDict.get("debug", False),
                        training=configDict.get("training", False),
                        redled=configDict.get("red", int(configObj["LED"]["RED"])),
                        yellowled=configDict.get("red", int(configObj["LED"]["YELLOW"])),
                        greenled=configDict.get("red", int(configObj["LED"]["GREEN"])),
                        )
    with open(os.path.join(conf_path, "config"), "wb") as ofile:
        pickle.dump(conf_record, ofile)

def read_config_file():
    with open(os.path.join(os.path.dirname(__file__), "configuration", "config"), "rb") as ofile:
        conf_record = pickle.load(ofile)
    return conf_record

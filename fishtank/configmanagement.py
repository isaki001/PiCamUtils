import configparser
import pickle
import os

def setup_config_file(**kwargs):
    configObj = configparser.ConfigParser()
    conf_path = os.path.join(os.path.dirname(__file__), "configuration")
    configObj.read(os.path.join(conf_path, "config.ini"))
    conf_record = dict(waterHeightLow=kwargs.get("lowWater", float(configObj['LOW']['WATER'])),
                        waterHeightMid=kwargs.get("midWater" , float(configObj['MID']['WATER'])),
                        waterHeightHigh=kwargs.get("highWater" , float(configObj['HIGH']['WATER'])),
                        heightDifferenceLow=kwargs.get("lowLand", float(configObj['LOW']['DIFFERENCE'])),
                        heightDifferenceMid=kwargs.get("midLand", float(configObj['MID']['DIFFERENCE'])),
                        heightDifferenceHigh=kwargs.get("highLand", float(configObj['HIGH']['DIFFERENCE'])),
                        waterLandRatioLow=kwargs.get("ratioLow", float(configObj['LOW']['RATIO'])),
                        waterLandRatioMid=kwargs.get("ratioMid", float(configObj['MID']['RATIO'])),
                        waterLandRatioHigh=kwargs.get("ratioHigh", float(configObj['HIGH']['RATIO'])),
                        debug=kwargs.get("debug", False),
                        training=kwargs.get("training", False))
    with open(os.path.join(conf_path, "config"), "wb") as ofile:
        pickle.dump(conf_record, ofile)

def read_config_file():
    with open(os.path.join(os.path.dirname(__file__), "configuration", "config"), "rb") as ofile:
        conf_record = pickle.load(ofile)
    return conf_record

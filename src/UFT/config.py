#!/usr/bin/env python
# encoding: utf-8
"""Description: Configuration for UFT program.
"""

__version__ = "0.1"
__author__ = "@dqli"

import os
import configparser
import ast

# station settings
STATION_CONFIG = "./xml/station.cfg"
if not os.path.exists(STATION_CONFIG):
    raise Exception("Station config does not exist!")

config = ConfigParser.RawConfigParser()
config.read(STATION_CONFIG)

ALLOWED_PN = ast.literal_eval(config.get('StationConfig', 'ALLOWED_PN'))
VPD_FILE = ast.literal_eval(config.get('StationConfig', 'VPD_FILE'))

FCT_NO1 = config.get('StationConfig', 'FCT_NO1')
FCT_NO2 = config.get('StationConfig', 'FCT_NO2')
FCT_NO3 = config.get('StationConfig', 'FCT_NO3')
FCT_NO4 = config.get('StationConfig', 'FCT_NO4')
FCT_DEBUG_INFOR = config.getboolean('StationConfig', 'FCT_DEBUG_INFOR')


# Result Database
RESULT_DB = "./db/pgem.db"

# Location to save xml log
RESULT_LOG = "./logs/"

# Resource Folder, include images, icons
RESOURCE = "./res/"
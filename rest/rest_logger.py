import json
import sys
import codecs
import os
import argparse
import logging
import time

loggerInstance = False
def getLogger():
    global  loggerInstance

    if loggerInstance is not False:
        return  loggerInstance

    stdout = sys.stdout
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    sys.path.append(os.path.join(sys.path[0], '../'))
    fileName = "rest_application.log"
    logging.basicConfig(format='%(asctime)s %(message)s', filename='/home/instapy-log/' + fileName, level=logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger = logging.getLogger('[schedule]')
    logger.setLevel(logging.INFO)
    logger.addHandler(ch)
    loggerInstance = logger

    return logger

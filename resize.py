import argparse
import codecs
import json
import logging
import os
import sys
import time

BASE_DIR = "/Users/cbardas/instapy-log/"
# BASE_DIR = "/home/instapy-log/"

stdout = sys.stdout
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.path.append(os.path.join(sys.path[0], '../'))
fileName = "resize" + time.strftime("%d.%m.%Y") + ".log"
logging.basicConfig(format='%(asctime)s %(message)s', filename=BASE_DIR + fileName, level=logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger = logging.getLogger('[schedule]')
logger.setLevel(logging.DEBUG)
logger.addHandler(ch)
import requests

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-id_droplet', type=str, help="id_droplet")
args = parser.parse_args()

apiUrl = 'https://rest.angie.one/doapi/'
authKey = 'b5a42bd29ebc5697adcec0adf446c26e'
#EIGHT_GB_SIZE = "s-4vcpu-8gb"
#TWO_GB_SIZE = "s-1vcpu-2gb"

#args.id_droplet = "144926024"
#args.size = EIGHT_GB_SIZE

if args.id_droplet is None:
    exit("dispatcher: Error: id_droplet is not specified !")

if args.size is None:
    exit("dispatcher: Error: id_droplet is not specified !")


def getDropletStatus(id_droplet):
    url = apiUrl + "droplet?id_droplet=" + id_droplet
    logger.info("Requesting: %s", url)
    r = requests.get(url, headers={'Authorization': authKey})
    result = r.content
    result = json.loads(result)

    print(result['droplet']['status'])


def shutdownDroplet(id_droplet):
    url = apiUrl + "shutdown"
    data = json.dumps({"id_droplet": id_droplet})
    logger.info("Shutdown: requesting: %s, with data: %s" % (url, data))
    r = requests.post(url, headers={'Authorization': authKey}, data=data)
    result = r.content
    result = json.loads(result)

    logger.info("Shutdown: Action Status: %s, id: %s" % (result['action']['status'], result['action']['id']))

    return result['action']['id']


def checkStatus(id_action):
    url = apiUrl + "status?id_action=" + str(id_action)
    logger.info("Requesting: %s", url)
    r = requests.get(url, headers={'Authorization': authKey})
    result = r.content
    result = json.loads(result)

    logger.info("checkStatus: response: %s", result)
    return result['action']['status']


def powerOn(id_droplet):
    url = apiUrl + "power"
    data = json.dumps({"id_droplet": id_droplet})
    logger.info("Requesting: %s, with data: %s" % (url, data))
    r = requests.post(url, headers={'Authorization': authKey}, data=data)
    result = r.content
    result = json.loads(result)

    logger.info("Action Status: %s, id: %s" % (result['action']['status'], result['action']['id']))

    return result['action']['id']


def powerOff(id_droplet):
    url = apiUrl + "powerOff"
    data = json.dumps({"id_droplet": id_droplet})
    logger.info("Requesting: %s, with data: %s" % (url, data))
    r = requests.post(url, headers={'Authorization': authKey}, data=data)
    result = r.content
    result = json.loads(result)

    logger.info("Action Status: %s, id: %s" % (result['action']['status'], result['action']['id']))

    return result['action']['id']


def resize(id_droplet, size):
    url = apiUrl + "resize"
    data = json.dumps({"id_droplet": id_droplet, "size": size})
    logger.info("Requesting: %s, with data: %s" % (url, data))
    r = requests.post(url, headers={'Authorization': authKey}, data=data)
    result = r.content
    result = json.loads(result)

    logger.info("Resize response: %s", result)
    logger.info("Action Status: %s, id: %s" % (result['action']['status'], result['action']['id']))

    return result['action']['id']


logger.info("STARTING RESIZE PROCESS FOR DROPLET: %s, SIZE: %s" % (args.id_droplet, args.size))
#
# waitForShutdownMin = 1
#
# # SHUTDOWN THE DROPLET
# shutdownId = shutdownDroplet(args.id_droplet)
# logger.info("Going to wait %s minutes for shutdown", waitForShutdownMin)
# time.sleep(waitForShutdownMin * 60)
# logger.info("Done waiting, going to check the status.")
# status = checkStatus(shutdownId)
#
# if status != "completed":
#     logger.info("Shutdown failed, status: %s. Going to powerOff", status)
#     powerOffId = powerOff(args.id_droplet)
#     logger.info("Going to wait %s minute for powerOff", waitForShutdownMin)
#     time.sleep(waitForShutdownMin * 60)
#     powerOffStatus = checkStatus(powerOffId)
#
#     if powerOffStatus != 'completed':
#         logger.info("PowerOff failed, status: %s", powerOffStatus)
#         raise Exception('Could not powerOff the droplet.')
#
# logger.info("Done shutting down, going to resize the droplet...")
#
# resizeWaitMin = 5
# resizeId = resize(args.id_droplet, args.size)
# logger.info("Going to wait %s minutes for resize", resizeWaitMin)
# time.sleep(resizeWaitMin * 60)
# logger.info("done waiting, going to check the resize status")
#
# resizeStatus = checkStatus(resizeId)
# if resizeStatus != 'completed':
#     logger.info('Resize failed, status: %s', resizeStatus)
#     raise Exception('Resize failed, status: %s', resizeStatus)
#
# logger.info("Done resizing, going to startup the machine")
# startupId = powerOn(args.id_droplet)
# startUpWait = 2
# logger.info("Going to wait %s minutes for powerOn" % (startUpWait))
#
# time.sleep(resizeWaitMin * 60)
# logger.info("Done waiting... going to check the startup status")
# startupStatus = checkStatus(startupId)
#
# if startupStatus != 'completed':
#     logger.info("Startup failed, status: %s", startupStatus)
#     raise Exception("Startup failed...")
#
# logger.info("Done resizing the machine, going to exit !")

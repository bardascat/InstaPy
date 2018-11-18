import subprocess
import os
from rest_logger import getLogger
import json
python_path = "python"
base_path = "/home/ubuntu/projects/InstaPy"
DEVNULL = open(os.devnull, 'wb')

def readAll():
    #todo ->
    x = 1


def start(body):
    logger = getLogger()
    bodyObject = json.loads(body)
    logger.info(body)
    id_campaign = bodyObject["id_campaign"]
    logger.info("engagement-bot.start: Going to start bot for campaign id: %s", id_campaign)

    processName = 'angie_instapy_idc'+str(id_campaign)
    subprocess.Popen("bash -c \"exec -a " + processName + " python "+base_path+"/start.py  -angie_campaign=" + str(id_campaign) + " \"", stdin=None, stdout=DEVNULL, stderr=DEVNULL, close_fds=True, shell=True)

def getBot(id_campaign):
    #todo ->
    x = 1



def scheduler(id_campaigns):
    processName = 'angie_schedule_instapy_bot_to_start'
    subprocess.Popen("bash -c \"exec -a " + processName + " python " + base_path + "/start.py  -angie_campaign=" + str(id_campaigns) + " \"", stdin=None, stdout=DEVNULL, stderr=DEVNULL, close_fds=True, shell=True)

def stopAll():
    x=1
    DEVNULL = open(os.devnull, 'wb')
    processName = 'angie_stop_bots'
    subprocess.Popen("bash -c \"exec -a " + processName + " python " + base_path + "/stop_bot.py " + " \"", stdin=None, stdout=DEVNULL, stderr=DEVNULL, close_fds=True, shell=True)

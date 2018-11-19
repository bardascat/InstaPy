import os
import subprocess
import json
from flask import abort
from rest_logger import getLogger
import os.path

python_path = "python"
base_path = "/home/ubuntu/projects/InstaPy"
DEVNULL = open(os.devnull, 'wb')


def readAll():
    # todo ->
    x = 1


def start(campaign):
    logger = getLogger()
    logger.info("engagement-bot.start: Going to start bot for campaign id: %s", campaign['id_campaign'])
    id_campaign = campaign["id_campaign"]

    processName = 'angie_instapy_idc' + str(id_campaign)
    command = "bash -c \"exec -a " + processName + " python " + base_path + "/start.py  -angie_campaign=" + str(
        id_campaign) + " \""

    logger.info("executing command: %s", command)
    subprocess.Popen(command, close_fds=True, shell=True, stdin=None, stdout=DEVNULL, stderr=DEVNULL)


def getBot(id_campaign):
    logger = getLogger()
    logger.info("engagement-bot.getBot: Getting bot for campaign id: %s", id_campaign)

    processname = 'angie_instapy_idc' + str(id_campaign)
    tmp = os.popen("ps -Af").read()
    proccount = tmp.count(processname)

    logger.info("engagement-bot.getBot: Found %s processes that contain name: %s" % (proccount, processname))
    if proccount > 0:
        return True
    return abort(404)

def getBotLog(id_campaign,date):
    #logger = getLogger()
    logsPath = "/Users/cbardas/instapy-log/campaign/logs/"+id_campaign+"/"+date+".log"
    #logger.info("engagement-bot.getBotLog: Searching logs in path: %s", logsPath)

    if os.path.isfile(logsPath):
        with open(logsPath, 'r') as myfile:
            data = myfile.read()
        return data
    else:
        #logger.info("log not found.")
        abort(404)



def scheduler(campaigns):
    logger = getLogger()
    logger.info("engagement-bot.scheduler: Going to schedule the following campaigns: %s", campaigns)

    processName = 'angie_schedule_instapy_bot_to_start'

    campaignsList = []
    for campaign in campaigns:
        campaignsList.append(campaign['id_campaign'])

    command = "bash -c \"exec -a " + processName + " python " + base_path + "/schedule.py  -angie_campaigns='" + json.dumps(
        campaignsList) + "' \""

    logger.info("executing command: %s", command)
    subprocess.Popen(command, close_fds=True, shell=True, stdin=None, stdout=DEVNULL, stderr=DEVNULL)


def stopAll():
    logger = getLogger()
    logger.info("engagement-bot.stopAll")
    processName = 'angie_stop_bots'

    command = "bash -c \"exec -a " + processName + " python " + base_path + "/stop_bot.py" + " \""
    logger.info("executing command: %s", command)
    subprocess.Popen(command, close_fds=True, shell=True, stdin=None, stdout=DEVNULL, stderr=DEVNULL)

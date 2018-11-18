import os
import subprocess

from rest_logger import getLogger

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
    # todo ->
    x = 1


def scheduler(id_campaigns):
    processName = 'angie_schedule_instapy_bot_to_start'
    subprocess.Popen("bash -c \"exec -a " + processName + " python " + base_path + "/start.py  -angie_campaign=" + str(
        id_campaigns) + " \"", stdin=None, stdout=DEVNULL, stderr=DEVNULL, close_fds=True, shell=True)


def stopAll():
    logger = getLogger()
    logger.info("engagement-bot.stopAll")
    processName = 'angie_stop_bots'

    command = "bash -c \"exec -a " + processName + " python " + base_path + "/stop_bot.py" + " \""
    logger.info("executing command: %s", command)
    subprocess.Popen(command, close_fds=True, shell=True, stdin=None, stdout=DEVNULL, stderr=DEVNULL)

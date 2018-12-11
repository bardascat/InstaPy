import os
import subprocess
import json
from flask import abort
from rest_logger import getLogger
import os.path

python_path = "python"
base_path = "/home/ubuntu/projects/instabot/run"
DEVNULL = open(os.devnull, 'wb')


def scanFeed(campaign):
    id_campaign = campaign['id_campaign']
    logger = getLogger()
    logger.info("crawler.scanFeed: Going to start feed crawler, id_campaign: %s", id_campaign)

    processName = 'angie_scan_user_feed_' + str(id_campaign)
    command = "bash -c \"exec -a " + processName + " sudo /usr/bin/python2.7 " + base_path + "/scan_user_feed.py  -angie_campaign=" + str(
        id_campaign) + " \""

    logger.info("executing command: %s", command)
    subprocess.Popen(command, close_fds=True, shell=True, stdin=None, stdout=DEVNULL, stderr=DEVNULL)


def scanUserProfile(campaign):
    id_campaign = campaign['id_campaign']
    logger = getLogger()
    logger.info("crawler.scanUserProfile: Going to start profile crawler, id_campaign: %s", id_campaign)

    processName = 'angie_scan_users_profile_' + str(id_campaign)
    command = "bash -c \"exec -a " + processName + " sudo /usr/bin/python2.7 " + base_path + "/scan_user_profile.py  -angie_campaign=" + str(id_campaign) + " \""

    logger.info("executing command: %s", command)
    subprocess.Popen(command, close_fds=True, shell=True, stdin=None, stdout=DEVNULL, stderr=DEVNULL)
t
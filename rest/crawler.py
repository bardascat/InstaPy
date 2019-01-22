import os
import subprocess
import json
from flask import abort
import datetime
from rest_logger import getLogger
import os.path
from pymongo import MongoClient

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
    command = "bash -c \"exec -a " + processName + " sudo /usr/bin/python2.7 " + base_path + "/scan_user_profile.py  -angie_campaign=" + str(
        id_campaign) + " \""

    logger.info("executing command: %s", command)
    subprocess.Popen(command, close_fds=True, shell=True, stdin=None, stdout=DEVNULL, stderr=DEVNULL)


def scanUserFollowers(campaign):
    id_campaign = campaign['id_campaign']
    logger = getLogger()
    logger.info("crawler.scanUserFollowers: Going to start followers crawler, id_campaign: %s", id_campaign)

    processName = 'angie_scan_user_followers_' + str(id_campaign)
    command = "bash -c \"exec -a " + processName + " sudo /usr/bin/python2.7 " + base_path + "/scan_user_followers.py  -angie_campaign=" + str(
        id_campaign) + " \""

    logger.info("executing command: %s", command)
    subprocess.Popen(command, close_fds=True, shell=True, stdin=None, stdout=DEVNULL, stderr=DEVNULL)


def processUserFollowers():
    logger = getLogger()
    logger.info("crawler.processUserFollowers: Going to start process followers crawler")

    processName = 'angie_process_user_followers'
    command = "bash -c \"exec -a " + processName + " sudo /usr/bin/python2.7 " + base_path + "/process_user_followers.py  \""

    logger.info("executing command: %s", command)
    subprocess.Popen(command, close_fds=True, shell=True, stdin=None, stdout=DEVNULL, stderr=DEVNULL)


def getUserFollowersBreakdown(instagram_username, since, until):
    logger = getLogger()
    logger.info("crawler.getUserFollowersBreakdown: instagram_username: %s, since: %s, until: %s" % (
        instagram_username, since, until))

    format_str = '%Y-%m-%d'  # The format

    gte = datetime.datetime.strptime(since, format_str)
    lte = datetime.datetime.strptime(until, format_str)

    gte = gte.replace(minute=0, hour=0, second=0, microsecond=0)
    lte = lte.replace(minute=59, hour=23, second=59, microsecond=999)

    logger.info("crawler.getUserFollowersBreakdown: start: %s, end: %s" % (gte, lte))

    client = MongoClient(host='localhost', port=27017)
    db = client.angie_app

    result = db.processed_user_followers.find({"owner_instagram_username": instagram_username, "start_date": {'$gt': gte, '$lt': lte}}, sort=[("start_date", -1)])
    result = list(result)

    logger.info("getUserFollowersBreakdown: Retrieved %s lines", len(result))

    client.close()

    return result

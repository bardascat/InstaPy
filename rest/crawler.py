import datetime
import os.path
import subprocess

from pymongo import MongoClient

from rest_logger import getLogger

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


def scanUserActions(campaign):
    id_campaign = campaign['id_campaign']
    logger = getLogger()
    logger.info("crawler.scanUserActions: Going to start user action crawler, id_campaign: %s", id_campaign)

    processName = 'angie_scan_user_actions_' + str(id_campaign)
    command = "bash -c \"exec -a " + processName + " sudo /usr/bin/python2.7 " + base_path + "/scan_user_actions.py  -id_campaign=" + str(
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


def userActionsQueueStatus(campaigns):
    logger = getLogger()
    client = MongoClient(host='localhost', port=27017)
    db = client.angie_app

    logger.info("crawler.userActionsCrawlerStatus: Getting user actions status for %s campaigns", len(campaigns))

    status = []
    for id_campaign in campaigns:
        pipeline = [{"$match": {'processed': 0, "id_campaign": id_campaign}},
                    {"$group": {"_id": "$id_campaign", "count": {"$sum": 1}}}]

        result = list(db.user_actions_queue.aggregate(pipeline=pipeline))

        count = 0
        if len(result) > 0:
            count = result[0]['count']

        status.append({"id_campaign": id_campaign, "queue": count})

    return status


def userFollowersCralwerStatus(body):
    campaigns = body['campaigns']
    date = body['date']

    logger = getLogger()

    client = MongoClient(host='localhost', port=27017)
    db = client.angie_app
    format_str = '%Y-%m-%d'  # The format
    gte = datetime.datetime.strptime(date, format_str)
    lte = datetime.datetime.strptime(date, format_str)

    gte = gte.replace(minute=0, hour=0, second=0, microsecond=0)
    lte = lte.replace(minute=59, hour=23, second=59, microsecond=999)

    logger.info("crawler.userFollowersStatus: Going to return crawler status between: %s - %s, users: %s" % (
        gte, lte, campaigns))

    output = []
    for campaign in campaigns:
        user = campaign['instagram_username']

        result = db.user_followers.find({"owner_instagram_username": user, "crawled_at": {'$gt': gte, '$lt': lte}},
                                        {"followers": 0})

        result = list(result)

        if len(result) > 0:
            output.append({"instagram_username": user, "scanned": True})
        else:
            output.append({"instagram_username": user, "scanned": False})

    logger.info("Result is : %s", output)
    return output

import subprocess
import os
from rest_logger import getLogger
import json
from flask import abort
import re

python_path = "python"
base_path = "/home/ubuntu/projects/InstaPy"
DEVNULL = open(os.devnull, 'wb')


def verify(username, password, id_campaign, twoFactorRecoveryCode=None, unusualLoginToken=None):
    twoFactorRecoveryCode = None if (not twoFactorRecoveryCode) else twoFactorRecoveryCode
    unusualLoginToken = None if (not unusualLoginToken) else unusualLoginToken

    logger = getLogger()
    logger.info(
        "bot.verify: Going to verify instagram account of id_campaign: %s. u:%s, twoFactorRecoveryCode: %s, unusualLoginToken: %s" % (
            id_campaign, username, twoFactorRecoveryCode, unusualLoginToken))
    settings = {"u": username, "p": password, "id_campaign": id_campaign,
                "twoFactorRecoveryCode": twoFactorRecoveryCode, "unusualLoginToken": unusualLoginToken}

    process = subprocess.Popen(
        "sudo /usr/bin/python2.7 " + base_path + "/verify_account.py -settings='" + json.dumps(settings) + "'",
        shell=True, stdout=subprocess.PIPE)
    result = process.communicate()[0]
    process.wait()

    logger.info("bot.verify: Result is: %s", result)
    return result


def user(username):
    base_path = "/home/ubuntu/projects/instabot/run"

    JOHN_CRYAN_BOT = '273'

    logger = getLogger()
    logger.info("bot.user: Getting details for user %s" % (username))

    command = "sudo /usr/bin/python2.7 " + base_path + "/get_user_info.py -instagramUsername='" + username + "' -id_campaign=" + JOHN_CRYAN_BOT
    logger.info("executing command:" + command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    result = process.communicate()[0]
    process.wait()

    logger.info("bot.user: Result is: %s", result)
    return result


def getProcess(query):
    processName = query
    logger = getLogger()
    logger.info("bot.process: Going to search for process with name: %s" % processName)

    query = re.compile(processName + r"\b")
    contents = os.popen("ps -Af").read()
    count = sum(1 for match in re.finditer(query, contents))

    logger.info("engagement-bot.getBot: Found %s processes that contain name: %s" % (count, processName))
    if count > 0:
        return True
    return abort(404)

def getUserFollowers(username):
    # todo: implement this
    logger = getLogger()
    logger.info("crawler.isFollower: Going to return user %s followers, order by follow back" % (username))
    #todo: retrieve user follower order by follow back


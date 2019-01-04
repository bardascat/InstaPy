import subprocess
import os
from rest_logger import getLogger
import json

python_path = "python"
base_path = "/home/ubuntu/projects/InstaPy"
DEVNULL = open(os.devnull, 'wb')


def verify(username, password, id_campaign, twoFactorRecoveryCode):
    logger = getLogger()
    logger.info("bot.verify: Going to verify instagram account of id_campaign: %s. u:%s, twoFactorRecoveryCode: %s" % (id_campaign, username, twoFactorRecoveryCode))
    settings = {"u": username, "p": password, "id_campaign": id_campaign, "twoFactorRecoveryCode": twoFactorRecoveryCode}

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

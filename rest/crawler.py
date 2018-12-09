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

def getPostsByHashtag(hashtag, amount, id_campaign, removeLikedPosts, removeFollowedUsers):
    id_campaign_bot = 401 #florin_geambasu

    logger = getLogger()
    logger.info("crawler.getPostsByHashtag: Going to search posts by hashtag with options: hashtag: %s, amount: %s, id_campaign: %s" % (hashtag, amount, id_campaign))

    processName = 'angie_scan_posts_by_hashtag_' + str(id_campaign)
    command = "bash -c \"exec -a " + processName + " sudo /usr/bin/python2.7 " + base_path + "/get_posts_by_hashtag.py  -id_campaign=" + str(id_campaign) + "  -id_bot=" + str(id_campaign_bot) + " -amount=" + str(amount) + " -hashtag=" + hashtag+ " -removeLikedPosts=" + removeLikedPosts + " -removeFollowedUsers=" + removeFollowedUsers + "\""

    logger.info("executing command: %s", command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    result = process.communicate()[0]
    process.wait()

    logger.info("crawler.getPostsByHashtag: Result is: %s", result)
    return result

def getPostsByLocation(location, amount, id_campaign, removeLikedPosts, removeFollowedUsers):
    id_campaign_bot = 401 #florin_geambasu

    logger = getLogger()
    logger.info("crawler.getPostsByHashtag: Going to search posts by location with options: location: %s, amount: %s, id_campaign: %s" % (location, amount, id_campaign))

    processName = 'angie_scan_posts_by_location_' + str(id_campaign)
    command = "bash -c \"exec -a " + processName + " sudo /usr/bin/python2.7 " + base_path + "/get_posts_by_location.py  -id_campaign=" + str(id_campaign) + "  -id_bot=" + str(id_campaign_bot) + " -amount=" + str(amount) + " -location=" + location+ " -removeLikedPosts=" + removeLikedPosts + " -removeFollowedUsers=" + removeFollowedUsers + "\""

    logger.info("executing command: %s", command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    result = process.communicate()[0]
    process.wait()

    logger.info("crawler.getPostsByLocation: Result is: %s", result)
    return result
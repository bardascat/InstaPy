from random import randint

from selenium.common.exceptions import NoSuchElementException

import bot_util
from .api_db import *
from .bot_util import getIfUserWantsToUnfollow
from .like_util import get_links_for_tag, check_link, get_links_for_location
from .like_util import like_image
from .unfollow_util import custom_unfollow, follow_user
import time
import bot_action_handler
from datetime import datetime
import urllib2
import urllib
import requests
import json
import traceback
from bot_util import *
class InstabotRestClient:
    def __init__(self,
                 campaign,
                 instapy
                 ):
        self.campaign = campaign
        self.instapy = instapy
        self.browser = instapy.browser
        self.logger = instapy.logger

    def getPostsByHashtag(self, hashtag, amount):

        # todo: if not enough posts are retrieve from instabot try to move the difference to other tags

        removeFollowedUsers = bot_util.isFollowEnabled(self.campaign['id_campaign'], self.logger)
        removeLikedPosts = True

        url = "http://35.166.100.155:5002/api/posts/hashtag"
        parameters = {}
        parameters['id_campaign'] = self.campaign['id_campaign']
        parameters['amount'] = amount
        parameters['hashtag'] = hashtag
        parameters['removeLikedPosts'] = str(removeLikedPosts).lower()
        parameters['removeFollowedUsers'] = str(removeFollowedUsers).lower()

        urlValues = urllib.urlencode(parameters)
        url = url + "?" + urlValues

        self.logger.info("getPostsByHashtag: API URL: %s:", url)

        req = urllib2.Request(url)
        response = urllib2.urlopen(req)

        body = response.read()
        try:
            result = json.loads(body)
        except Exception as exc:
            exceptionDetail = traceback.format_exc()
            self.logger.info("There was an error parsing the json: json: %s, error: %s" % (body, exceptionDetail))
            raise Exception("Cannot parse json: error:" + exceptionDetail)


        if "error" in result:
            # maybe send an email with the error
            # self.browser.get('https://rest.angie.one/email/sendError?id=' + str(campaign['id_user']))
            self.instapy.logger.error(
                "get_links: Error while getting links for tag: %s, error: %s" % (hashtag, result['error']))
            return []

        if len(result) < amount:
            self.instapy.logger.error(
                "instabot_rest_client.getPostsByHashtag: Not enough links received for tag: %s. Expected: %s, received: %s" % (
                    hashtag, amount, len(result)))

        return result

    def getPostsByLocation(self, location, amount):
        removeFollowedUsers = True  # todo set the right value for this
        removeLikedPosts = True  # todo set the right value for this

        url = "http://35.166.100.155:5002/api/posts/location"

        parameters = {}
        parameters['id_campaign'] = self.campaign['id_campaign']
        parameters['amount'] = amount
        parameters['location'] = location
        parameters['removeLikedPosts'] = str(removeLikedPosts).lower()
        parameters['removeFollowedUsers'] = str(removeFollowedUsers).lower()

        urlValues = urllib.urlencode(parameters)
        url = url + "?" + urlValues

        self.logger.info("getPostsByLocation: API URL: %s:", url)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)

        body = response.read()
        try:
            result = json.loads(body)
        except Exception as exc:
            exceptionDetail = traceback.format_exc()
            self.logger.info("There was an error parsing the json: json: %s, error: %s" % (body, exceptionDetail))
            raise Exception("Cannot parse json: error:" + exceptionDetail)

        if "error" in result:
            # maybe send an email with the error
            # self.browser.get('https://rest.angie.one/email/sendError?id=' + str(campaign['id_user']))
            self.instapy.logger.error(
                "get_links: Error while getting links for location: %s, error: %s" % (location, result['error']))
            return []

        if len(result) < amount:
            self.instapy.logger.error(
                "instabot_rest_client.getPostsByHashtag: Not enough links received for tag: %s. Expected: %s, received: %s" % (len(result), amount, len(result)))

        return result

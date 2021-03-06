from random import randint

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, InvalidElementStateException

import bot_util
from .api_db import *
from .bot_util import getIfUserWantsToUnfollow
from .like_util import get_links_for_tag, check_link, get_links_for_location
from .like_util import like_image
from .unfollow_util import custom_unfollow, follow_user
import time
import bot_action_handler
from datetime import datetime


class Engagements:
    def __init__(self,
                 campaign,
                 instapy
                 ):

        self.totalLikeExpected = 0
        self.totalFollowExpected = 0
        self.totalUnfollowExpected = 0

        self.username = campaign['username']
        self.campaign = campaign
        self.instapy = instapy
        self.browser = instapy.browser
        self.logger = instapy.logger

        self.totalLikePerformed = bot_action_handler.getActionsPerformed(self.campaign, datetime.now(), "like",
                                                                         self.logger)
        self.totalFollowPerformed = bot_action_handler.getActionsPerformed(self.campaign, datetime.now(), "follow",
                                                                           self.logger)
        self.totalUnfollowPerformed = bot_action_handler.getActionsPerformed(self.campaign, datetime.now(), "unfollow",
                                                                             self.logger)

    def perform_engagement(self, operation, likeAmount, followAmount, unfollowAmount):
        self.logger.info(
            "start perform engagement: ----------------- STARTED operation: %s, Going to perform %s likes, %s follow, %s Unfollow. -------------------" % (
                operation['configName'], likeAmount, followAmount, unfollowAmount))

        iteration = 0
        likePerformed = 0
        followPerformed = 0
        unfollowPerformed = 0

        likeAmountForEachTag = self.splitTotalAmount(likeAmount, len(operation['list']), divideAmountTo=4)
        followAmountForEachTag = self.splitTotalAmount(followAmount, len(operation['list']), divideAmountTo=4)
        unfollowAmountForEachTag = self.splitTotalAmount(unfollowAmount, len(operation['list']), divideAmountTo=4)

        # run while we have hashtags and the amount of likes,follow,unfollow is not exceeded
        while self.shouldContinueLooping(likePerformed, followPerformed, unfollowPerformed, likeAmount, followAmount,
                                         unfollowAmount, iteration) is True:

            likeAmountForeachRandomized = randint(likeAmountForEachTag,
                                                  bot_util.randomizeValue(likeAmountForEachTag, 10, "up"))
            followAmountForeachRandomized = randint(followAmountForEachTag,
                                                    bot_util.randomizeValue(followAmountForEachTag, 10, "up"))
            unfollowAmountForEachRandomized = randint(unfollowAmountForEachTag,
                                                      bot_util.randomizeValue(unfollowAmountForEachTag, 10, "up"))

            engagementValue = self.getItemToProcess(operation, operation['configName'])

            self.logger.info(
                "------------ perform_engagement start iteration: %s, TAG: %s. Going to perform likes: %s, follow: %s, unfollow: %s for tag: %s --------------" % (
                    iteration + 1, engagementValue,
                    likeAmountForeachRandomized, followAmountForeachRandomized, unfollowAmountForEachRandomized,
                    engagementValue))

            numberOfPostsToExtract = max(likeAmountForeachRandomized, followAmountForeachRandomized,
                                         unfollowAmountForEachRandomized)

            links = self.get_links(numberOfPostsToExtract=numberOfPostsToExtract, engagementBy=operation['configName'],
                                   engagementByValue=engagementValue)

            if len(links) == 0:
                self.logger.info('perform_engagement: Too few images, skipping this tag:  %s', engagementValue)
                continue

            result = self.engage(links, engagementValue=engagementValue,
                                 likeAmountToPerform=likeAmountForeachRandomized,
                                 followAmountToPerform=followAmountForeachRandomized,
                                 unfollowAmountToPerform=unfollowAmountForEachRandomized,
                                 numberOfPostsToExtract=numberOfPostsToExtract,
                                 operation=operation)

            # update overall stats
            self.totalLikePerformed += result['likePerformed']
            self.totalFollowPerformed += result['followPerformed']
            self.totalUnfollowPerformed += result['unfollowPerformed']

            # update local stats
            likePerformed += result['likePerformed']
            followPerformed += result['followPerformed']
            unfollowPerformed += result['unfollowPerformed']

            self.logger.info(
                "-------------- perform_engagement end iteration: %s, TAG: %s. LIKE PERFORMED/EXPECTED %s/%s, FOLLOW PERFORMED/EXPECTED: %s/%s, UNFOLLOW PERFORMED/EXPECTED: %s/%s ------------------" % (
                    iteration + 1, engagementValue, result['likePerformed'], likeAmountForeachRandomized,
                    result['followPerformed'], followAmountForeachRandomized, result['unfollowPerformed'],
                    unfollowAmountForEachRandomized))

            iteration = iteration + 1

        self.logger.info(
            "-------------- END PERFORM_ENGAGEMENT: END operation: %s. LIKE PERFORMED/EXPECTED %s/%s, FOLLOW PERFORMED/EXPECTED: %s/%s, UNFOLLOW PERFORMED/EXPECTED: %s/%s ------------------" % (
                operation['configName'], likePerformed, likeAmount, followPerformed, followAmount, unfollowPerformed,
                unfollowAmount))

        return {"totalLikePerformed": likePerformed, "totalFollowPerformed": followPerformed,
                "totalUnfollowPerformed": unfollowPerformed}

    def shouldContinueLooping(self, likePerformed, followPerformed, unfollowPerformed, likeAmountExpected,
                              followAmountExpected, unfollowAmountExpected, iteration):
        securityBreak = 10

        if iteration > securityBreak:
            self.logger.info("shouldContinueLooping: Loop should stop: Security break, iteration: %s", iteration)
            return False

        if likePerformed >= likeAmountExpected and followPerformed >= followAmountExpected and unfollowPerformed >= unfollowAmountExpected:
            self.logger.info(
                "shouldContinueLooping: Loop should stop: LP: %s, FP: %s, UP: %s,  LE: %s, FE: %s, UE: %s" % (
                    likePerformed, followPerformed, unfollowPerformed, likeAmountExpected, followAmountExpected,
                    unfollowAmountExpected))
            return False

        if self.totalLikePerformed >= self.totalLikeExpected and self.totalFollowPerformed >= self.totalFollowExpected and self.totalUnfollowPerformed >= self.totalUnfollowExpected:
            self.logger.info(
                "shouldContinueLooping: Loop should stop. Total actions reached: LP: %s, FP: %s, UP: %s,  LE: %s, FE: %s, UE: %s" % (
                    self.totalLikePerformed, self.totalFollowPerformed, self.totalUnfollowPerformed,
                    self.totalLikeExpected,
                    self.totalFollowExpected, self.totalUnfollowExpected))
            return False

        return True

    def engage(self, links, engagementValue, likeAmountToPerform, followAmountToPerform, unfollowAmountToPerform,
               numberOfPostsToExtract, operation):
        result = {"likePerformed": 0, "followPerformed": 0, "unfollowPerformed": 0}

        self.logger.info("engage: Received %s link, going to iterate through them", len(links))

        for i, post in enumerate(links):
            self.logger.info(
                'engage: **************** START PROCESSING LINK: {}, TAG {}, [{}/{}] ********************'.format(
                    post['link'], engagementValue, i + 1, len(links)))

            try:

                self.logger.info("engage: Navigating to link: %s", post['link'])
                linkValidationDetails = self.canInteractWithLink(post['link'])

                if linkValidationDetails is not False:

                    self.logger.info("engage: Going to like the link: %s", post['link'])
                    if self.performLike(user_name=linkValidationDetails['user_name'],
                                        operation=operation,
                                        link=post['link'],
                                        engagementValue=engagementValue) is True:
                        result['likePerformed'] += 1

                    self.logger.info("engage: Trying to follow user: %s", linkValidationDetails['user_name'])
                    if self.performFollow(numberOfPostsToInteract=numberOfPostsToExtract,
                                          followAmount=followAmountToPerform,
                                          operation=operation, link=post['link'],
                                          user_name=linkValidationDetails['user_name'],
                                          tag=engagementValue) is True:
                        result['followPerformed'] += 1

                    self.logger.info("engage: Trying to unfollow an user from database...")

                    if self.performUnfollow(numberOfPostsToInteract=numberOfPostsToExtract,
                                            unfollowAmount=unfollowAmountToPerform,
                                            operation=operation) is True:
                        result['unfollowPerformed'] += 1



            except (NoSuchElementException, StaleElementReferenceException, InvalidElementStateException) as err:
                self.logger.error('engage: Something went wrong: {}'.format(err))
                continue

            self.logger.info(
                'engage: **************** DONE PROCESSING LINK: {}, TAG {}, [{}/{}] ********************'.format(
                    post['link'], engagementValue, i + 1, len(links)))

        return result

    def performLike(self, user_name, link, operation, engagementValue):

        if self.totalLikePerformed >= self.totalLikeExpected:
            self.logger.error("performLike: ERROR - The like amount is reached. Expected %s, performed %s " % (
                self.totalLikeExpected, self.totalLikePerformed))
            return False

        liked, msg = like_image(self.browser,
                                user_name,
                                self.instapy.blacklist,
                                self.logger,
                                self.instapy.logfolder,
                                self.instapy)
        if liked:
            self.logger.info("performLike: Link %s was liked. User %s" % (link, user_name))

        if msg == "already_liked":
            self.logger.info("performLike: Link %s was already liked, going to store it in db.", link)

        if liked is True or msg == "already_liked":
            insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                            None, None, user_name,
                            None, None, None,
                            link, 'like_' + operation['configName'], engagementValue, self.instapy.id_log)
            self.logger.info("performLike: Going to sleep 3 seconds after jumping to other page...")
            time.sleep(3)
            return True

        return False

    def performFollow(self, followAmount, numberOfPostsToInteract, operation, link, user_name, tag):

        if user_name is None:
            self.logger.error("performFollow: Cannot follow user: %s ", user_name)
            return False

        if self.totalFollowPerformed >= self.totalFollowExpected:
            self.logger.error("performFollow: ERROR - The follow amount is reached. Expected %s, performed %s " % (
                self.totalFollowExpected, self.totalFollowPerformed))
            return False

        if operation['follow_user'] == 0:
            self.logger.info("performFollow: User doesn't want to follow... going to return..")
            return False

        if operation['follow_user'] == 1:

            probabilityPercentage = followAmount * 100 // numberOfPostsToInteract

            randomProbability = randint(0, 100)

            self.logger.info(
                "performFollow: Number of posts to interact: %s, followAmount: %s, probability: %s. Random Probability: %s" % (
                    numberOfPostsToInteract, followAmount, probabilityPercentage, randomProbability))

            if randomProbability <= probabilityPercentage:
                # try to folllow
                self.logger.info("performFollow: Trying to follow user %s", user_name)

                # this is not necessary since the posts are prefiltered
                # # check if user was followed in the past
                # if userWasFollowedInThePast(user_name, self.campaign['id_user']):
                #     self.logger.error("performFollow: Warning: User %s was followed in the past, going to skip it !",
                #                       user_name)
                #     return False

                # todo: follow_user method is overengineered , try to simplify it

                followed, msg = follow_user(self.browser,
                                                "post",
                                                self.campaign['username'],
                                                user_name,
                                                None,
                                                self.instapy.blacklist,
                                                self.logger,
                                                self.instapy.logfolder,
                                                self.instapy)

                if msg == "already_followed":
                    self.logger.info("performFollow: User %s was already followed, going to store it in DB", user_name)

                if followed is True or msg == "already_followed":
                    insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                                    None, None, user_name,
                                    None, None, None,
                                    link, 'follow_' + operation['configName'], tag, self.instapy.id_log)

                    self.logger.info("performFollow: Going to sleep 3 seconds after jumping to other page...")
                    time.sleep(3)

                    return True
                else:
                    self.logger.error(
                        "peformFollow: Error could not perform follow for user %s, reason: %s" % (user_name, msg))
                    return False
            else:
                self.logger.info(
                    "performFollow: Going to skip follow. Actual Probability: %s, random probability: %s" % (
                        probabilityPercentage, randomProbability))

            return False

    def performUnfollow(self, unfollowAmount, numberOfPostsToInteract, operation):
        # todo check if there is user to unfollow
        if self.totalUnfollowPerformed >= self.totalUnfollowExpected:
            self.logger.error("performLike: ERROR - The unfollow amount is reached. Expected %s, performed %s " % (
                self.totalUnfollowExpected, self.totalUnfollowPerformed))
            return False

        # check if user wants to unfollow
        userWantsToUnfollow = getIfUserWantsToUnfollow(self.campaign['id_campaign'])
        if userWantsToUnfollow == False:
            self.logger.info("performUnfollow: User does not want to unfollow, going to continue !")
            return False

        probabilityPercentage = unfollowAmount * 100 // numberOfPostsToInteract
        randomProbability = randint(0, 100)

        self.logger.info(
            "performUnfollow: Number of posts to interact: %s, Unfollow Amount: %s, probability: %s. Random Probability: %s" % (
                numberOfPostsToInteract, unfollowAmount, probabilityPercentage, randomProbability))

        if randomProbability <= probabilityPercentage:
            self.logger.info("performUnfollow: User wants to unfollow after %s hours" % userWantsToUnfollow['value'])

            # get users to unfollow older than x days. People who did not follow back are the first to be unfollowed.
            recordToUnfollow = getUserToUnfollow(self.campaign['id_user'], userWantsToUnfollow['value'])

            if recordToUnfollow:
                status = custom_unfollow(self.browser, recordToUnfollow['username'], self.logger, self.instapy)
                if status is True:
                    lastBotAction = insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                                                    None, None, recordToUnfollow['username'],
                                                    None, None, None, None, 'unfollow_' + operation['configName'],
                                                    None,
                                                    self.instapy.id_log)

                    self.logger.info("performUnfollow: Succesfully unfollowed user: %s", recordToUnfollow['username'])

                    revertBotFollow(recordToUnfollow['_id'], lastBotAction)
                    self.logger.info("peformUnfolow: Update bot_operation_reverted with value %s for id: %s" % (
                        lastBotAction, recordToUnfollow['_id']))
                    self.logger.info("performFollow: Going to sleep 3 seconds after jumping to other page...")
                    time.sleep(3)
                    return True
                else:
                    self.logger.info("performFollow: Could not unfollow user...")
                    return False

            else:
                self.logger.info("performUnfollow: No user found in database to unfollow...")

        else:
            self.logger.info(
                "performUnfollow: Going go skip UNFOLLOW. Actual Probability: %s, random probability: %s" % (
                    probabilityPercentage, randomProbability))

        return False

    def canInteractWithLink(self, link):
        try:
            # this is going to open the post link
            inappropriate, user_name, is_video, reason, scope = (
                check_link(self.browser,
                           link,
                           [],
                           [],
                           [],
                           self.logger)
            )

            return {'status': True, 'user_name': user_name}

        except NoSuchElementException as err:
            self.logger.error('canInteractWithLink: Invalid Page: {}'.format(err))
            return False

        return False

    def splitTotalAmount(self, amount, noOfHashtags, divideAmountTo=4):
        if amount == 0:
            return 0

        if noOfHashtags < divideAmountTo:
            divideAmountTo = noOfHashtags

        self.logger.info("splitTotalAmount: Going to divide amount to %s hashtags.", divideAmountTo)
        return amount // divideAmountTo

    def get_links(self, numberOfPostsToExtract, engagementBy, engagementByValue):

        # todo: test this

        if engagementBy == "engagement_by_hashtag":
            self.logger.info(
                "get_links: Getting %s links for hashtag: %s" % (numberOfPostsToExtract, engagementByValue))
            return self.instapy.instabotRestClient.getPostsByHashtag(hashtag=engagementByValue,
                                                                     amount=numberOfPostsToExtract)

        elif engagementBy == "engagement_by_location":
            self.logger.info(
                "get_links: Getting %s links for location: %s" % (numberOfPostsToExtract, engagementByValue))
            return self.instapy.instabotRestClient.getPostsByLocation(location=engagementByValue,
                                                                      amount=numberOfPostsToExtract)

    def getItemToProcess(self, operation, engagement_by):

        # we need to refresh the operation list
        if len(operation['list']) < 1:
            self.logger.info(
                "getItemToProcess: We used all the hashtags/locations, going to refresh the list with all the values from db.")
            if engagement_by == "engagement_by_location":
                operation['list'] = select("SELECT * FROM `instagram_locations` WHERE `id_config` = %s",
                                           operation['id_config'])
            if engagement_by == "engagement_by_hashtag":
                operation['list'] = select("SELECT * FROM `instagram_hashtags` WHERE `id_config` = %s",
                                           operation['id_config'])

        # extract a random hashtag from the list
        itemIndex = randint(0, len(operation['list']) - 1)
        itemObject = operation['list'][itemIndex]

        if engagement_by == "engagement_by_location":
            itemValue = itemObject['id_location']

        if engagement_by == "engagement_by_hashtag":
            itemValue = itemObject['hashtag']

        # itemValue="atp"

        del operation['list'][itemIndex]
        return itemValue

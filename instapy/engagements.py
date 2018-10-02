import time
import bot_util
from random import randint

from selenium.common.exceptions import NoSuchElementException

from .api_db import *
from .bot_util import getOperationByName, isOperationEnabled, getIfUserWantsToUnfollow
from .like_util import get_links_for_tag, check_link, get_links_for_location
from .like_util import like_image
from .unfollow_util import custom_unfollow, follow_user
from .util import validate_username
from .util import web_address_navigator
import traceback


class Engagements:
    def __init__(self,
                 totalLikes,
                 totalFollow,
                 totalUnfollow,
                 campaign,
                 instapy
                 ):

        self.totalLikeExpected = totalLikes
        self.totalFollowExpected = totalFollow
        self.totalUnfollowExpected = totalUnfollow

        self.username = campaign['username']
        self.campaign = campaign
        self.instapy = instapy
        self.browser = instapy.browser
        self.logger = instapy.logger

        # TODO: these values should be extracted from db ???
        self.totalLikePerformed = 0
        self.totalFollowPerformed = 0
        self.totalUnfollowPerformed = 0

    def perform_engagement(self, operation, likeAmount, followAmount, unfollowAmount):
        self.logger.info(
            "perform_engagement: *********************** STARTED operation: %s, Going to perform %s likes, %s follow, %s Unfollow. ******************************" % (
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

            self.logger.info("perform_engagement: ************** TAG %s, ITERATION NUMBER %s*****************" % (
                engagementValue, iteration + 1))

            self.logger.info("perform_engagement: Going to perform likes: %s, follow: %s, unfollow: %s for tag: %s" % (
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

            iteration = iteration + 1

        self.logger.info("perform_engagement: **************** END operation: %s **********************",
                         operation['configName'])

        return likePerformed

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

        return True

    def engage(self, links, engagementValue, likeAmountToPerform, followAmountToPerform, unfollowAmountToPerform,
               numberOfPostsToExtract, operation):
        result = {"likePerformed": 0, "followPerformed": 0, "unfollowPerformed": 0}

        self.logger.info("engage: Received %s link, going to iterate through them", len(links))

        for i, link in enumerate(links):
            self.logger.info('engage: TAG {}, [{}/{}], link: {}'.format(engagementValue, i + 1, len(links), link))

            try:
                # todo: check if this function is needed
                self.logger.info("engage: Going to interact with the link...")
                linkValidationDetails = self.canInteractWithLink(link)

                self.logger.info("engage: Navigating to link: %s", link)

                if linkValidationDetails is not False:

                    # navigate to url ! (previously it was on user profile page)
                    try:
                        web_address_navigator(self.browser, link)
                    except:
                        exceptionDetail = traceback.format_exc()
                        self.logger.critical("engage: EXCEPTION on http connection: %s", exceptionDetail)
                        continue

                    self.logger.info("engage: Going to like the link: %s", link)
                    if self.performLike(user_name=linkValidationDetails['user_name'],
                                        operation=operation,
                                        link=link,
                                        engagementValue=engagementValue) is True:
                        result['likePerformed'] += 1

                    self.logger.info("engage: Going to follow user: %s", linkValidationDetails['user_name'])
                    if self.performFollow(numberOfPostsToInteract=numberOfPostsToExtract,
                                          followAmount=followAmountToPerform,
                                          operation=operation, link=link,
                                          user_name=linkValidationDetails['user_name'],
                                          tag=engagementValue) is True:
                        result['followPerformed'] += 1

                    self.logger.info("engage: Going to unfollow an user from database...")

                    if self.performUnfollow(numberOfPostsToInteract=numberOfPostsToExtract,
                                            unfollowAmount=unfollowAmountToPerform,
                                            operation=operation) is True:
                        result['unfollowPerformed'] += 1



            except NoSuchElementException as err:
                self.logger.error('engage: Invalid Page: {}'.format(err))
                continue

        return result

    def performLike(self, user_name, link, operation, engagementValue):

        if self.totalLikePerformed >= self.totalLikeExpected:
            self.logger.error("performLike: ERROR - The like amount is reached. Expected %s, performed %s " % (
                self.totalLikeExpected, self.totalLikePerformed))
            return False

        try:
            linkCode = link.split("https://www.instagram.com/p/")[1].split("/")[0]
        except:
            linkCode = link

        result = fetchOne(
            "select count(*) as wasPostLiked  from bot_action where post_link like %s and id_user=%s and bot_operation like %s",
            '%' + linkCode + '%', self.campaign['id_user'], "like_engagement_" + '%')

        if result['wasPostLiked'] > 0:
            self.logger.info("performLike: Post %s was liked in the past, skipping...", link)
            return False

        liked, msg = like_image(self.browser,
                           user_name,
                           self.instapy.blacklist,
                           self.logger,
                           self.instapy.logfolder,
                           self.instapy)
        if liked:
            self.logger.info("engage: Link %s was liked. User %s" % (link, user_name))

            insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                            None, None, user_name,
                            None, None, None,
                            link, 'like_' + operation['configName'], engagementValue, self.instapy.id_log)
            return True

        return False

    def performFollow(self, followAmount, numberOfPostsToInteract, operation, link, user_name, tag):

        if self.totalFollowPerformed >= self.totalFollowExpected:
            self.logger.error("performLike: ERROR - The follow amount is reached. Expected %s, performed %s " % (
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

                # check if user was followed in the past
                if userWasFollowedInThePast(user_name, self.campaign['id_user']):
                    self.logger.error("performFollow: Warning: User %s was followed in the past, going to skip it !",
                                      user_name)
                    return False

                # todo: follow_user method is overengineered , try to simplify it
                followed, msg = follow_user(self.browser,
                                            ['profile', 'post'],
                                            None,
                                            user_name,
                                            None,
                                            self.instapy.blacklist,
                                            self.logger,
                                            self.instapy.logfolder,
                                            self.instapy)

                if followed:
                    insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                                    None, None, user_name,
                                    None, None, None,
                                    link, 'follow_' + operation['configName'], tag, self.instapy.id_log)
                    return True
                else:
                    self.logger.error(
                        "peformFollow: Error could not perform follow for user %s, reason: %s" % (user_name, msg))
                    return False
            else:
                self.logger.info(
                    "performFollow: Going go skip follow. Actual Probability: %s, random probability: %s" % (
                        probabilityPercentage, randomProbability))

            return False

    def performUnfollow(self, unfollowAmount, numberOfPostsToInteract, operation):
        #todo check if there is user to unfollow
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

            selectFollowings = "select * from bot_action where  bot_operation like %s and timestamp< (NOW() - INTERVAL %s HOUR) and id_user= %s and bot_operation_reverted is null order by timestamp asc limit %s"
            recordToUnfollow = fetchOne(selectFollowings, 'follow' + '%', userWantsToUnfollow['value'],
                                        self.campaign['id_user'], 1)

            if recordToUnfollow:
                status = custom_unfollow(self.browser, recordToUnfollow['username'], self.logger, self.instapy)
                lastBotAction = insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                                                None, None, recordToUnfollow['username'],
                                                None, None, None, None, 'unfollow_' + operation['configName'],
                                                None,
                                                self.instapy.id_log)

                self.logger.info("performUnfollow: Succesfully unfollowed user: %s", recordToUnfollow['username'])
                insert("update bot_action set bot_operation_reverted=%s where id=%s", lastBotAction,
                       recordToUnfollow['id'])
                self.logger.info("peformUnfolow: Update bot_operation_reverted with value %s for id: %s" % (lastBotAction, recordToUnfollow['id']))
                return True
            else:
                self.logger.info("performUnfollow: No user found in database to unfollow...")

        else:
            self.logger.info(
                "performUnfollow: Going go skip UNFOLLOW. Actual Probability: %s, random probability: %s" % (
                    probabilityPercentage, randomProbability))

        return False

    def canInteractWithLink(self, link):
        try:
            # TODO: i don't think this is required
            inappropriate, user_name, is_video, reason, scope = (
                check_link(self.browser,
                           link,
                           [],
                           [],
                           [],
                           self.logger)
            )
            time.sleep(2)
            if not inappropriate:
                # validate user
                validation, details = validate_username(self.browser,
                                                        user_name,
                                                        self.username,
                                                        self.instapy.ignore_users,
                                                        self.instapy.blacklist,
                                                        self.instapy.potency_ratio,
                                                        self.instapy.delimit_by_numbers,
                                                        self.instapy.max_followers,
                                                        self.instapy.max_following,
                                                        self.instapy.min_followers,
                                                        self.instapy.min_following,
                                                        self.logger)
                if validation is True:
                    return {'status': True, 'user_name': user_name}
                else:
                    self.logger.info("canInteractWithLink: Error, link is not good %s", details)

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
        if engagementBy == "engagement_by_hashtag":
            try:
                links = get_links_for_tag(browser=self.browser, amount=numberOfPostsToExtract, tag=engagementByValue,
                                          skip_top_posts=True, media=None, logger=self.logger, randomize=True)
            except NoSuchElementException:
                self.logger.info('get_links: Too few images, skipping this tag: %s', engagementByValue)
                return []

        elif engagementBy == "engagement_by_location":
            try:
                links = get_links_for_location(self.browser,
                                               amount=numberOfPostsToExtract,
                                               location=engagementByValue,
                                               logger=self.logger)

            except NoSuchElementException:
                self.logger.warning('get_links: Too few images, skipping this location: %s' % (engagementByValue))
                return []

        return links

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

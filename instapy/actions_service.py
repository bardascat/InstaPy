import time
from random import randint
import pymongo
from selenium.common.exceptions import NoSuchElementException

from .api_db import *
from .bot_util import getIfUserWantsToUnfollow, isFollowEnabled
from .like_util import like_image
from .unfollow_util import custom_unfollow, follow_user
from random import randint


class ActionsService:
    def __init__(self,
                 campaign,
                 instapy
                 ):
        self.campaign = campaign
        self.instapy = instapy
        self.browser = instapy.browser
        self.logger = instapy.logger
        self.isFollowEnabled = isFollowEnabled(campaign['id_campaign'], self.logger)
        self.isUnfollowEnabled = getIfUserWantsToUnfollow(campaign['id_campaign'])

    def perform_engagement(self, likeAmount, followAmount, unfollowAmount):

        result = {"like": 0, "follow": 0, "unfollow": 0}

        self.logger.info("perform_engagement: Going to perform %s likes, %s follow, %s Unfollow." % (
            likeAmount, followAmount, unfollowAmount))

        numberOfPostsToInteractWith = max(likeAmount, followAmount, unfollowAmount)

        if numberOfPostsToInteractWith < 0:
            self.logger.info("perform_engagement: No actions to performed, likeAmount: %s, followAmount: %s, unfollowAmount: %s " % (likeAmount, followAmount, unfollowAmount))
            return False

        self.followProbabilityPercentage = followAmount * 100 // numberOfPostsToInteractWith
        self.likeProbabilityPercentage = likeAmount * 100 // numberOfPostsToInteractWith
        self.unfollowProbabilityPercentage = unfollowAmount * 100 // numberOfPostsToInteractWith

        posts = self.getPosts(numberOfPostsToInteractWith)
        it = 0
        for post in posts:

            if 'link' not in post:
                continue

            self.logger.info("perform_engagement: [%s][%s] link: %s" % (it, len(posts), post['link']))
            try:
                actionStatus = self.engage(post)

                if actionStatus['like']:
                    result['like'] += 1
                if actionStatus['follow']:
                    result['follow'] += 1
                if actionStatus['unfollow']:
                    result['unfollow'] += 1
                self.disablePost(post)

            except NoSuchElementException as err:
                self.logger.error('engage: Invalid Page: {}'.format(err))
                self.disablePost(post)
                continue
            it += 1

            # pause once at 100 posts
            if it % 100 == 0:
                wait = randint(7, 15)
                time.sleep(wait * 60)
                self.logger.info("perform_engagement: Iteration: %s Going to wait for %s minutes" % (it, wait))

            self.logger.info("perform_engagement: Done waiting...")

        return result

    def disablePost(self, post):
        client = getMongoConnection()
        db = client.angie_app
        db.user_actions_queue.update({"_id": post["_id"]}, {"$set": {"processed": 1}})
        client.close()

    def getPosts(self, noPosts):


        increasedNumberOfPosts = noPosts * 12 // 100 + noPosts

        client = getMongoConnection()
        db = client.angie_app
        # sort them desc, interact with latest post
        result = db.user_actions_queue.find({"id_campaign": self.campaign['id_campaign'], "processed": 0},
                                            sort=[("timestamp", pymongo.DESCENDING)]).limit(increasedNumberOfPosts)
        client.close()

        if result is None:
            self.logger.error("getPosts: Could not find any posts to engage with, going to return")
            return False

        result = list(result)
        self.logger.info("getPosts: Found %s posts for this user, expected: %s posts, expected with safety: %s" % (len(result), noPosts, increasedNumberOfPosts))

        return result

    def engage(self, post):

        self.browser.get(post['link'])

        operation = self.getOperationName(post)

        self.logger.info("engage: Trying to like post %s", post['link'])
        likeStatus = self.performLike(user_name=post['instagram_username'],
                                      operation=operation,
                                      link=post['link'],
                                      engagementValue=post['tag'])

        self.logger.info("engage: Trying to follow user: %s", post['instagram_username'])

        followStatus = self.performFollow(followAmountProbabilityPercentage=self.followProbabilityPercentage,
                                          link=post['link'],
                                          operation=operation,
                                          user_name=post['instagram_username'],
                                          tag=post['tag'])

        self.logger.info("engage: Trying to unfollow an user from database...")

        unfollowStatus = self.performUnfollow(unFollowAmountProbabilityPercentage=self.unfollowProbabilityPercentage, operation=operation)

        return {"like": likeStatus, "follow": followStatus, "unfollow": unfollowStatus}

    def getOperationName(self, post):
        if post['targetType'] == "hashtag":
            operation = "engagement_by_hashtag"
        elif post['targetType'] == "location":
            operation = "engagement_by_location"
        return operation

    def performLike(self, user_name, link, operation, engagementValue):
        # if self.totalLikePerformed >= self.totalLikeExpected:
        #     self.logger.error("performLike: ERROR - The like amount is reached. Expected %s, performed %s " % (
        #         self.totalLikeExpected, self.totalLikePerformed))
        #     return False
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
                            link, 'like_' + operation, engagementValue, self.instapy.id_log)
            self.logger.info("performLike: Going to sleep 3 seconds after jumping to other page...")
            time.sleep(3)
            return True

        return False

    def performFollow(self, followAmountProbabilityPercentage, link, user_name, tag, operation):

        if user_name is None:
            self.logger.error("performFollow: Cannot follow user: %s ", user_name)
            return False

        # if self.totalFollowPerformed >= self.totalFollowExpected:
        #     self.logger.error("performFollow: ERROR - The follow amount is reached. Expected %s, performed %s " % (
        #         self.totalFollowExpected, self.totalFollowPerformed))
        #     return False

        if self.isFollowEnabled:
            randomProbability = randint(0, 100)

            self.logger.info("performFollow: Probability to follow: %s. Random Probability: %s" % (
                followAmountProbabilityPercentage, randomProbability))
            if randomProbability <= followAmountProbabilityPercentage:
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
                                    link, 'follow_' + operation, tag, self.instapy.id_log)

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
                        followAmountProbabilityPercentage, randomProbability))

            return False

    def performUnfollow(self, unFollowAmountProbabilityPercentage, operation):
        # todo check if there is user to unfollow
        # if self.totalUnfollowPerformed >= self.totalUnfollowExpected:
        #     self.logger.error("performLike: ERROR - The unfollow amount is reached. Expected %s, performed %s " % (
        #         self.totalUnfollowExpected, self.totalUnfollowPerformed))
        #     return False

        # check if user wants to unfollow
        userWantsToUnfollow = getIfUserWantsToUnfollow(self.campaign['id_campaign'])
        if userWantsToUnfollow == False:
            self.logger.info("performUnfollow: User does not want to unfollow, going to continue !")
            return False

        randomProbability = randint(0, 100)

        self.logger.info("performUnfollow: Probability to unfollow: %s. Random Probability: %s" % (
            unFollowAmountProbabilityPercentage, randomProbability))

        if randomProbability <= unFollowAmountProbabilityPercentage:
            self.logger.info("performUnfollow: User wants to unfollow after %s hours" % userWantsToUnfollow['value'])

            # get users to unfollow older than x days. People who did not follow back are the first to be unfollowed.
            recordToUnfollow = getUserToUnfollow(self.campaign['id_user'], userWantsToUnfollow['value'])

            if recordToUnfollow:
                status = custom_unfollow(self.browser, recordToUnfollow['username'], self.logger, self.instapy)
                if status is True:
                    lastBotAction = insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                                                    None, None, recordToUnfollow['username'],
                                                    None, None, None, None, 'unfollow_' + operation,
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
                    unFollowAmountProbabilityPercentage, randomProbability))

        return False

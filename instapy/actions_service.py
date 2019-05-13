import time
from random import randint
import pymongo
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidElementStateException

from .api_db import *
from .bot_util import getIfUserWantsToUnfollow, isFollowEnabled, isLikeEnabled, getBotOperations, isLikeEngagementWithPostsEnabled
from .like_util import like_image
from .unfollow_util import custom_unfollow, follow_user
from random import randint
import action_delay_util
from feed_service import FeedService
from bot_action_handler import getActionsPerformed
from datetime import datetime
class ActionsService:
    def __init__(self,
                 campaign,
                 instapy
                 ):
        self.campaign = campaign
        self.instapy = instapy
        self.browser = instapy.browser
        self.logger = instapy.logger
        operations = getBotOperations(campaign['id_campaign'], self.logger)
        self.isFollowEnabled = isFollowEnabled(operations)
        self.isLikeEnabled = isLikeEnabled(operations)
        self.isLikeEngagementWithPostsEnabled = isLikeEngagementWithPostsEnabled(operations)
        self.isUnfollowEnabled = getIfUserWantsToUnfollow(campaign['id_campaign'])
        self.feedService = FeedService(campaign=self.campaign, instapy=instapy, operations=operations, actionService=self)


    def perform_engagement(self, likeAmount, followAmount, unfollowAmount):

        result = {"like": 0, "follow": 0, "unfollow": 0}

        self.logger.info("perform_engagement: Going to perform %s likes, %s follow, %s Unfollow." % (likeAmount, followAmount, unfollowAmount))

        numberOfPostsToInteractWith = max(likeAmount['tags'], followAmount, unfollowAmount)

        if max(likeAmount['tags'] + likeAmount['feed'], followAmount, unfollowAmount) is 0:
            self.logger.info("perform_engagement: No actions to performed, likeAmount: %s, followAmount: %s, unfollowAmount: %s " % (likeAmount, followAmount, unfollowAmount))
            return False

        self.followProbabilityPercentage = followAmount * 100 // numberOfPostsToInteractWith
        self.likeProbabilityPercentage = likeAmount['tags'] * 100 // numberOfPostsToInteractWith
        self.unfollowProbabilityPercentage = unfollowAmount * 100 // numberOfPostsToInteractWith


        posts = self.getPosts(numberOfPostsToInteractWith)
        it = 0
        while self.continueLooping(likeAmount, followAmount, unfollowAmount, result) is True:

            #engage with post
            engagePostResult = self.engageWithPost(posts, it)

            #if all posts are completed set a pause to avoid fast looping
            self.pause(posts, it)

            #engage with feed
            engageFeedResult = self.feedService.engageWithFeed(postsNumber=2)

            result['like'] += engagePostResult['like'] + engageFeedResult['like']
            result['follow'] += engagePostResult['follow']
            result['unfollow'] += engagePostResult['unfollow']

            it+=1


        return result

    def continueLooping(self, likeAmount, followAmount, unfollowAmount, result):

        if likeAmount['feed'] + likeAmount['tags']<=result['like'] and followAmount<=result['follow'] and unfollowAmount<=result['unfollow']:
            self.logger.info("continueLooping: Stopping engagement bot, reached target. result: %s", result)
            return False

        return True


    def disablePost(self, post):
        client = getMongoConnection()
        db = client.angie_app
        db.user_actions_queue.update({"_id": post["_id"]}, {"$set": {"processed": 1}})
        client.close()

    def getPosts(self, noPosts):

        if self.isLikeEngagementWithPostsEnabled is False:
            self.logger.info("getPosts: isLikeEngagementWithPostsEnabled: is Fale, going to return [] posts.")
            return []
        increasedNumberOfPosts = noPosts * 10 // 100 + noPosts

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

        self.logger.info("engage: accessing link: %s", post['link'])
        self.browser.get(post['link'])
        self.logger.info("engage: done loading link: %s", post['link'])

        operation = self.getOperationName(post)

        if self.isLikeEngagementWithPostsEnabled == False:
            likeStatus = False
        else:
            likeStatus = self.performLike(user_name=post['instagram_username'],
                                          operation=operation,
                                          link=post['link'],
                                          engagementValue=post['tag'])

        followStatus = self.performFollow(followAmountProbabilityPercentage=self.followProbabilityPercentage,
                                          link=post['link'],
                                          operation=operation,
                                          user_name=post['instagram_username'],
                                          tag=post['tag'])

        unfollowStatus = self.performUnfollow(unFollowAmountProbabilityPercentage=self.unfollowProbabilityPercentage, operation=operation)

        return {"like": likeStatus, "follow": followStatus, "unfollow": unfollowStatus}

    def getOperationName(self, post):
        if post['targetType'] == "hashtag":
            operation = "engagement_by_hashtag"
        elif post['targetType'] == "location":
            operation = "engagement_by_location"
        return operation

    def performLike(self, user_name, link, operation, engagementValue):

        if self.isLikeEnabled:
            self.logger.info("performLike: Going to like: %s", link)
            liked, msg = like_image(self.browser,
                                    user_name,
                                    self.instapy.blacklist,
                                    self.logger,
                                    self.instapy.logfolder,
                                    self.instapy)
            if liked:
                self.logger.info("performLike: Link was liked.")

            action_delay_util.set_last_like_timestamp(self.instapy, action_delay_util.get_current_timestamp())

            status = True
            if liked is not True:
                status = msg

            insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                            None, None, user_name,
                            None, None, None,
                            link, 'like_' + operation, engagementValue, self.instapy.id_log, status)

            return liked

        return False

    def performFollow(self, followAmountProbabilityPercentage, link, user_name, tag, operation):

        if user_name is None:
            self.logger.error("performFollow: Cannot follow user: %s ", user_name)
            return False

        if self.isFollowEnabled:
            self.logger.info("performFollow: Going to follow: %s", user_name)

            randomProbability = randint(0, 100)

            if randomProbability <= followAmountProbabilityPercentage:

                followed, msg = follow_user(self.browser,
                                            "post",
                                            self.campaign['username'],
                                            user_name,
                                            None,
                                            self.instapy.blacklist,
                                            self.logger,
                                            self.instapy.logfolder,
                                            self.instapy)

                action_delay_util.set_last_follow_timestamp(self.instapy, action_delay_util.get_current_timestamp())
                if followed is True:
                    self.logger.info("performFollow: User: %s followed.", user_name)

                status = True
                if followed is not True:
                    status = msg
                    if msg == 'instagram_following_limit_reached':
                        self.logger.error("performFollow: Going ot disable Follow since the maximum number is reached !")
                        self.isFollowEnabled = False

                insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                                None, None, user_name,
                                None, None, None,
                                link, 'follow_' + operation, tag, self.instapy.id_log, status)

                return followed
            else:
                self.logger.info("performFollow: Skipping follow. Actual Probability: %s, random probability: %s" % (followAmountProbabilityPercentage, randomProbability))

            return False

        return False

    def performUnfollow(self, unFollowAmountProbabilityPercentage, operation):

        if self.isUnfollowEnabled is not False:
            self.logger.info("performUnfollow: Going to unfollow.")

            randomProbability = randint(0, 100)

            # self.logger.info("performUnfollow: Probability to unfollow: %s. Random Probability: %s" % (
            #     unFollowAmountProbabilityPercentage, randomProbability))

            if randomProbability <= unFollowAmountProbabilityPercentage:
                #self.logger.info("performUnfollow: User wants to unfollow after %s hours" % self.isUnfollowEnabled['value'])

                # get users to unfollow older than x days. People who did not follow back are the first to be unfollowed.
                recordToUnfollow = getUserToUnfollow(self.campaign['id_campaign'], self.isUnfollowEnabled['value'])

                if recordToUnfollow:
                    unfollowed, msg = custom_unfollow(self.browser, recordToUnfollow['username'], self.logger, self.instapy)

                    if unfollowed is True:
                        self.logger.info("performUnfollow: Succesfully unfollowed user: %s.",recordToUnfollow['username'])

                    action_delay_util.set_last_unfollow_timestamp(self.instapy, action_delay_util.get_current_timestamp())

                    status = True
                    if unfollowed is not True:
                        status = msg

                    lastBotAction = insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                                                    None, None, recordToUnfollow['username'],
                                                    None, None, None, None, 'unfollow_' + operation,
                                                    None,
                                                    self.instapy.id_log, status)

                    revertBotFollow(recordToUnfollow['_id'], lastBotAction)


                    return unfollowed
                else:
                    self.logger.info("performUnfollow: No available user found in database to unfollow, going to close the unfollow cycle, and disable unfollow to false for this session.")
                    insert("update bot_unfollow_cycle set completed=1 where id_campaign=%s", self.campaign['id_campaign'])
                    self.isUnfollowEnabled = False

            else:
                self.logger.info("performUnfollow: Skipping unfollow, actual probability: %s, random probability: %s" % (unFollowAmountProbabilityPercentage, randomProbability))

            return False
        return False

    def engageWithPost(self, posts, it):
        result={'like':0, 'follow':0, 'unfollow':0}

        if len(posts)<=it:
            self.logger.info("engageWithPosts: No more posts to process. Iteration: %s, posts number: %s" % (it, len(posts)))
            return result

        post = posts[it]

        if 'link' not in post:
            return result

        self.logger.info("********************* START PROCESSING: [%s][%s] link: %s ***********************" % (it, len(posts), post['link']))
        try:
            actionStatus = self.engage(post)

            if actionStatus['like']:
                result['like'] = 1
            if actionStatus['follow']:
                result['follow'] = 1
            if actionStatus['unfollow']:
                result['unfollow'] = 1
            self.disablePost(post)

        except (NoSuchElementException, StaleElementReferenceException, InvalidElementStateException) as err:
            self.logger.error('perform_engagement: Error: {}'.format(err))
            self.disablePost(post)
        finally:
            self.logger.info("Done processing link.")

        # pause once at 100 posts
        if it % 100 == 0 and it > 0:
            wait = randint(7, 15)
            self.logger.info("perform_engagement: DAILY PAUSE every 100 posts. Iteration: %s. Going to wait for %s minutes" % (it, wait))
            time.sleep(wait * 60)
            self.logger.info("perform_engagement: Done waiting...")

        return result

    def pause(self, posts, it):

        if len(posts) <= it and it!=0:
            wait = 10
            self.logger.info("engageWithPosts: No more posts to process. Iteration: %s, number of posts: %s. Going to sleep for %s minutes between actions." % (it, len(posts), wait))
            time.sleep(wait * 60)









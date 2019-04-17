import urllib2

from unfollow_util import get_following_status
from .api_db import *
from .unfollow_util import custom_unfollow
import time
from .like_util import like_image
from .unfollow_util import custom_unfollow, follow_user
from datetime import datetime

class VerifyActionService:
    def __init__(self,
                 campaign,
                 instapy
                 ):
        self.campaign = campaign
        self.instapy = instapy
        self.browser = instapy.browser
        self.logger = instapy.logger


    def checkUnfollowSpamTreshhold(self):
        TRESH_HOLD = 15
        dateParam = datetime.today()
        gte = dateParam.replace(minute=0, hour=0, second=0, microsecond=0)
        lte = dateParam.replace(minute=59, hour=23, second=59, microsecond=59)

        client = getMongoConnection()
        db = client.angie_app
        result = db.bot_action.find({"id_campaign": self.campaign['id_campaign'], "bot_operation": {"$regex": "^unfollow"},"status": {"$regex": "^unfollow_spam"}, "timestamp": {"$gte": gte, "$lte": lte}})
        client.close()

        if result == None:
            return 0

        noSpams = result.count()
        if noSpams >= TRESH_HOLD:
            # raise exception, set pause
            exceptionDetail = "The follow was reverted after refresh, going to assume that like is blocked by instagram"
            likeException = "UNFOLLOW_SPAM_BLOCK"
            insert("INSERT INTO campaign_log (`id_campaign`, event, `details`, `timestamp`) VALUES (%s, %s, %s, now())",self.campaign['id_campaign'], 'unfollow_spam_block', exceptionDetail)
            urllib2.urlopen("https://rest.angie.one/email/sendBotException?type=" + likeException + "&id_campaign=" + str(self.campaign['id_campaign'])).read()
            self.addPause()
            raise Exception(likeException)

        return True

    def checkFollowSpamTreshhold(self):
        TRESH_HOLD = 15
        dateParam = datetime.today()
        gte = dateParam.replace(minute=0, hour=0, second=0, microsecond=0)
        lte = dateParam.replace(minute=59, hour=23, second=59, microsecond=59)

        client = getMongoConnection()
        db = client.angie_app
        result = db.bot_action.find({"id_campaign": self.campaign['id_campaign'], "bot_operation": {"$regex": "^follow"}, "status": {"$regex": "^follow_spam"},"timestamp": {"$gte": gte, "$lte": lte}})
        client.close()

        if result == None:
            return 0

        noSpams = result.count()
        if noSpams >= TRESH_HOLD:
            #raise exception, set pause
            exceptionDetail = "The follow was reverted after refresh, going to assume that like is blocked by instagram"
            followException = "FOLLOW_SPAM_BLOCK"
            insert("INSERT INTO campaign_log (`id_campaign`, event, `details`, `timestamp`) VALUES (%s, %s, %s, now())",self.campaign['id_campaign'], 'follow_spam_block', exceptionDetail)
            urllib2.urlopen("https://rest.angie.one/email/sendBotException?type=" + followException + "&id_campaign=" + str(self.campaign['id_campaign'])).read()
            self.addPause()
            raise Exception(followException)

        return True

    def checkLikeSpamTreshhold(self):
        TRESH_HOLD = 15
        dateParam = datetime.today()
        gte = dateParam.replace(minute=0, hour=0, second=0, microsecond=0)
        lte = dateParam.replace(minute=59, hour=23, second=59, microsecond=59)

        client = getMongoConnection()
        db = client.angie_app

        result = db.bot_action.find(
            {"id_campaign": self.campaign['id_campaign'], "bot_operation": {"$regex": "^like"}, "status": {"$regex": "^like_spam"},"timestamp": {"$gte": gte, "$lte": lte}})
        client.close()

        if result == None:
            return 0

        noSpams = result.count()
        if noSpams >= TRESH_HOLD:
            #raise exception, set pause
            exceptionDetail = "The like was reverted after refresh, going to assume that like is blocked by instagram"
            likeException = "LIKE_SPAM_BLOCK"
            insert("INSERT INTO campaign_log (`id_campaign`, event, `details`, `timestamp`) VALUES (%s, %s, %s, now())",self.campaign['id_campaign'], 'like_spam_block', exceptionDetail)
            urllib2.urlopen("https://rest.angie.one/email/sendBotException?type=" + likeException + "&id_campaign=" + str(self.campaign['id_campaign'])).read()
            self.addPause()
            raise Exception(likeException)

        return True


    def verifyActions(self):

        self.logger.info("verifyActions: Going to verify if instagram blocked like/follow actions.")

        post = self.getPostToVerify()

        if post is None:
            self.logger.info("verifyActions: Post is none, could not verify operations.")
            return False

        self.logger.info("verifyActions: Going to verify 'like' action by liking post %s", post['link'])

        isLikeBlocked = self.verifyLiking(post)
        isFollowBlocked = self.verifyFollow(post)
        isUnfollowBlocked = self.verifyUnfollow()

        likeException = ""
        followException = ""
        unfollowException = ""
        if isLikeBlocked:
            exceptionDetail = "The like was reverted after refresh, going to assume that like is blocked by instagram"
            likeException = "LIKE_SPAM_BLOCK"
            insert("INSERT INTO campaign_log (`id_campaign`, event, `details`, `timestamp`) VALUES (%s, %s, %s, now())",
                   self.instapy.campaign['id_campaign'], likeException, exceptionDetail)

        if isFollowBlocked is True:
            followException = "FOLLOW_SPAM_BLOCK"
            exceptionDetail = "Could not follow an user, going to assume that follow is blocked by instagram"
            insert("INSERT INTO campaign_log (`id_campaign`, event, `details`, `timestamp`) VALUES (%s, %s, %s, now())",
                   self.instapy.campaign['id_campaign'], followException, exceptionDetail)

        if isUnfollowBlocked is True:
            unfollowException = "UNFOLLOW_SPAM_BLOCK"
            exceptionDetail = "Could not unfollow an user, going to assume that unfollow is blocked by instagram"
            insert("INSERT INTO campaign_log (`id_campaign`, event, `details`, `timestamp`) VALUES (%s, %s, %s, now())",
                   self.instapy.campaign['id_campaign'], unfollowException, exceptionDetail)

        if isLikeBlocked is True or isFollowBlocked is True or isUnfollowBlocked is True:
            exception = likeException + "|" + followException + "|" + unfollowException
            urllib2.urlopen("https://rest.angie.one/email/sendBotException?type=" + exception + "&id_campaign=" + str(
                self.instapy.campaign['id_campaign'])).read()
            #self.addPause()
            raise Exception(
                "verifyAction: SPAM BLOCK: likeBlocked: %s, followBlocked: %s, unfollowBlocked: %s, going to stop the bot" % (
                isLikeBlocked, isFollowBlocked, isUnfollowBlocked))

    def verifyLiking(self, post):

        # ------------------- verify liking -----------------
        self.browser.get(post['link'])

        liked, msg = like_image(self.browser,
                                post['instagram_username'],
                                self.instapy.blacklist,
                                self.logger,
                                self.instapy.logfolder,
                                self.instapy)


        if msg=="like_spam_block":
            self.logger.info("like_spam_block: %s", True)
            return True

        self.logger.info("like_spam_block: %s, status: %s" % (False, msg))

        status = True
        if liked is not True:
            status = msg

        insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                        None, None, post['instagram_username'],
                        None, None, None, post['link'],
                        'like_engagement_by_hashtag', post['tag'], self.instapy.id_log, status)

        return False

    def verifyFollow(self, post):

        followed, msg = follow_user(self.browser,
                                    "post",
                                    self.campaign['username'],
                                    post['instagram_username'],
                                    None,
                                    self.instapy.blacklist,
                                    self.logger,
                                    self.instapy.logfolder,
                                    self.instapy)

        if msg == "follow_spam_block":
            path = "/home/instapy-log/campaign/logs/" + str(self.campaign['id_campaign']) + "/" + time.strftime("%d.%m.%Y.%H.%M.%S") + ".png"
            self.browser.get_screenshot_as_file(path)
            self.logger.info("verify_follow: follow_spam_block: True, image path: %s" % (msg, path))
            isFollowBlocked=True
        else:
            self.logger.info("verify_follow: Follow operation status: %s. follow_spam_block: False", msg)
            isFollowBlocked = False

        status = True
        if followed is not True:
            status = msg

        insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                        None, None, post['instagram_username'],
                        None, None, None,
                        post['link'], 'follow_engagement_by_hashtag', post['tag'], self.instapy.id_log, status)



        return isFollowBlocked

    def verifyUnfollow(self):
        isUnfollowBlocked = False

        self.logger.info("verifyUnfollow: Going to check if unfollow is blocked by IG.")
        recordToUnfollow = getUserToUnfollow(self.campaign['id_campaign'], 72)

        if recordToUnfollow:
            unfollowed, message = custom_unfollow(self.browser, recordToUnfollow['username'], self.logger, self.instapy)

            status = True
            if unfollowed is not True:
                status = message

            lastBotAction = insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                                            None, None, recordToUnfollow['username'],
                                            None, None, None, None, 'unfollow_engagement_by_hashtag',
                                            None,
                                            self.instapy.id_log, status)
            revertBotFollow(recordToUnfollow['_id'], lastBotAction)

            if message=="unfollow_spam_block":

                path = "/home/instapy-log/campaign/logs/" + str(self.campaign['id_campaign']) + "/" + time.strftime("%d.%m.%Y.%H.%M.%S") + ".png"
                self.browser.get_screenshot_as_file(path)

                self.logger.info("verifyUnfollow: Unfollowing status after refresh: %s, unfollow_spam_block:True path: %s" % (message, path))
                isUnfollowBlocked = True
            else:
                self.logger.info("verifyUnfollow: Unfollowing status after refresh: %s. unfollow_spam_block: False" % (message))

        else:
            self.logger.info("verifyUnfollow: No available user found in database could not check if unfollow is blocked.")

        return isUnfollowBlocked

    def addPause(self):
        pauseDays = 2
        self.logger.info("addPause: Going to pause the bot until: current_date + %s days", pauseDays)
        insert(
            "insert into bot_pause (id_campaign, pause_from, pause_until) VALUES (%s, CURDATE(), CURDATE() + INTERVAL %s DAY)",
            self.campaign['id_campaign'], pauseDays)

    def getPostToVerify(self):
        posts = self.instapy.actionService.getPosts(10)

        post = None
        for item in posts:
            if 'link' not in item:
                continue
            post = item
            break

        if post is None:
            return None

        self.instapy.actionService.disablePost(post)
        return post

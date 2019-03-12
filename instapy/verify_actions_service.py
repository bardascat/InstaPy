import urllib2

from unfollow_util import get_following_status
from .api_db import *
from .unfollow_util import custom_unfollow


class VerifyActionService:
    def __init__(self,
                 campaign,
                 instapy
                 ):
        self.campaign = campaign
        self.instapy = instapy
        self.browser = instapy.browser
        self.logger = instapy.logger

    def verifyActions(self):

        self.logger.info("verifyActions: Going to verify if instagram blocked like/follow actions.")

        post = self.getPostToVerify()

        if post is None:
            self.logger.info("verifyActions: Post is none, could not verify operations.")
            return False

        self.logger.info("verifyActions: Going to verify 'like' action by liking post %s", post['link'])

        isLikeBlocked = self.verifyLiking(post)
        isFollowBlocked = self.verifyFollow(post)
        isUnfollowBlocked = self.verifyUnfollow(post)

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
            self.addPause()
            raise Exception(
                "verifyAction: SPAM BLOCK: likeBlocked: %s, followBlocked: %s, unfollowBlocked: %s, going to stop the bot" % (
                isLikeBlocked, isFollowBlocked, isUnfollowBlocked))

    def verifyLiking(self, post):

        isLikeBlocked = False

        # ------------------- verify liking -----------------
        self.browser.get(post['link'])
        likeStatus = self.instapy.actionService.performLike(user_name=post['instagram_username'],
                                                            operation='engagement_by_hashtag',
                                                            link=post['link'],
                                                            engagementValue=post['tag'])
        if likeStatus is True:
            # reload the page
            self.browser.get(post['link'])

            unlike_xpath = "//section/span/button/span[@aria-label='Unlike']"
            liked_elem = self.browser.find_elements_by_xpath(unlike_xpath)
            if len(liked_elem) == 1:
                self.logger.info(
                    "verifyActions: Post was verify after refresh and it was successfully liked, like action is not blocked.")
            else:
                self.logger.info(
                    "verifyActions: Post was verified after refresh, and was not Liked, like action is blocked.")
                isLikeBlocked = True
        else:
            self.logger.info("verifyActions: Could not like the post, so we are going to skip the verifying for like.")

        return isLikeBlocked

    def verifyFollow(self, post):
        isFollowBlocked = False

        followStatus = self.instapy.actionService.performFollow(followAmountProbabilityPercentage=100,
                                                                link=post['link'],
                                                                operation='engagement_by_hashtag',
                                                                user_name=post['instagram_username'],
                                                                tag=post['tag'])
        if followStatus is True:
            # reload the page
            self.browser.get("https://www.instagram.com/{}/".format(post['instagram_username']))

            following_status, follow_button = get_following_status(self.browser,
                                                                   'post',
                                                                   self.instapy.campaign['username'],
                                                                   post['instagram_username'],
                                                                   None,
                                                                   self.logger,
                                                                   self.instapy.logfolder)
            if following_status in ["Following", "Requested"]:
                self.logger.info(
                    "verifyActions: User %s was verified after refresh and it was successfully followed, follow action is not blocked." % (
                        post['instagram_username']))
            else:
                self.logger.info(
                    "verifyActions: User %s, was verified after refresh and it was not followed, follow is blocked." % (
                        post['instagram_username']))
                isFollowBlocked = True
        else:
            self.logger.info("verifyActions: Could not FOLLOW user: %s, so we are going to skip verifying follow.",
                             post['instagram_username'])
            isFollowBlocked = False

        return isFollowBlocked

    def verifyUnfollow(self, post):
        isUnfollowBlocked = False

        self.logger.info("verifyUnfollow: Going to check if unfollow is blocked by IG.")
        recordToUnfollow = getUserToUnfollow(self.campaign['id_campaign'], 72)

        if recordToUnfollow:
            status = custom_unfollow(self.browser, recordToUnfollow['username'], self.logger, self.instapy)
            if status is True:

                self.browser.get("https://www.instagram.com/{}/".format(recordToUnfollow['username']))

                following_status, follow_button = get_following_status(self.browser,
                                                                       'post',
                                                                       self.instapy.campaign['username'],
                                                                       recordToUnfollow['username'],
                                                                       None,
                                                                       self.logger,
                                                                       self.instapy.logfolder)
                if following_status in ["Follow"]:
                    self.logger.info(
                        "verifyActions: User %s, was verified after refresh and it was  successfully UNFOLLOWED, unfollow action is not blocked." % (
                            post['instagram_username']))
                    lastBotAction = insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                                                    None, None, recordToUnfollow['username'],
                                                    None, None, None, None, 'unfollow_engagement_by_hashtag',
                                                    None,
                                                    self.instapy.id_log)
                    revertBotFollow(recordToUnfollow['_id'], lastBotAction)
                else:
                    self.logger.info(
                        "verifyActions: User %s was verified after refresh and it was not followed, follow is blocked." % (
                        post['instagram_username']))
                    isUnfollowBlocked = True
            else:
                self.logger.info(
                    "performFollow: Could not unfollow user: %s. Could not verify if unfollow is blocked by IG.",
                    recordToUnfollow['username'])
                return False
        else:
            self.logger.info(
                "verifyUnfollow: No available user found in database could not check if unfollow is blocked.")

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

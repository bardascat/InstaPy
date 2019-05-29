from .bot_util import isEngagementWithOwnFeedEnabled
from api_db import getMongoConnection
import pymongo
from datetime import datetime, timedelta
from .like_util import get_links_from_feed

class FeedService:
    def __init__(self,
                 campaign,
                 operations,
                 instapy,
                 actionService
                 ):
        self.campaign = campaign
        self.instapy = instapy
        self.browser = instapy.browser
        self.logger = instapy.logger
        self.actionService = actionService
        self.engageWithOwnFeedEnabled = isEngagementWithOwnFeedEnabled(operations, self.logger)
        self.lastPostLikedTimestamp = self.getLastPostLikeTimestamp()

    def engageWithFeed(self, postsNumber):
        result = {'like': 0}
        oneHourAgo = datetime.now() - timedelta(hours=int(1))

        if self.engageWithOwnFeedEnabled is False:
            return result

        if self.lastPostLikedTimestamp is not None and self.lastPostLikedTimestamp>=oneHourAgo:
            return result

        self.logger.info("engageWithFeed: **************** FEED ENGAGEMENT WITH: %s POSTS ***********************", postsNumber)


        posts = get_links_from_feed(self.instapy.browser, 3, postsNumber, self.logger, self.campaign)
        self.logger.info("engageWithFeed: Received %s posts from feed / expected %s" % (len(posts), postsNumber))
        it=1
        for post in posts:

            self.logger.info("[%s][%s] - %s" % (it, len(posts), post['link']))
            self.browser.get(post['link'])
            if self.actionService.performLike(user_name=post['instagram_username'],
                                          operation='engagement_with_own_feed',
                                          link=post['link'],
                                          engagementValue=None) is True:

                result['like']+=1
            it+=1
        self.lastPostLikedTimestamp = datetime.now()
        self.logger.info("********************* FEED ENGAGEMENT done liking %s posts from user feed. *****************************", len(posts))
        return result



    def getLastPostLikeTimestamp(self):
        client = getMongoConnection()
        db = client.angie_app

        row = db.bot_action.find_one({"id_user": self.campaign['id_user'], "bot_operation": 'like_engagement_with_own_feed'}, sort=[("timestamp", pymongo.DESCENDING)])
        client.close()

        if row == None:
            return None

        return row['timestamp']

import api_db
import time
from random import randint
from .like_util import like_image


class LikeForLike:
    def __init__(self,
                 campaign,
                 instapy):

        self.campaign = campaign
        self.username = campaign['username']
        self.instapy = instapy
        self.browser = instapy.browser
        self.logger = instapy.logger

    def start(self):
        self.logger.info("LikeForLike:performLikes: Going to perform l4l for user with ID: %s.",
                         self.campaign['id_user'])

        # Select all user_posts and exclude the ones already liked by the current user
        sqlTotal = " select count(*) as total from user_post  join user_subscription us on (user_post.id_user=us.id_user) " \
                   " join plan plan on (us.id_plan=plan.id_plan) " \
                   " join plan_type on (plan.id_plan_type=plan_type.id_plan_type) " \
                   " where id_post not in  (select id_post from user_post_log where id_user=%s)  " \
                   " and user_post.id_user!=%s " \
                   " and user_post.timestamp>=(select start_date from user_subscription where id_user=%s and (user_subscription.end_date>=NOW() " \
                   " or user_subscription.end_date is null)) " \
                   " and user_post.timestamp>=DATE(NOW() - INTERVAL 1 DAY) " \
                   " and user_post.code is not null"

            # if logged user doesn't have a trial startup plan then like only posts from users without startup plans
            # else if user have a startup plan like everything
            # " and case when  "
            # " ( (select pt.name from user_subscription us  join plan p on (us.id_plan=p.id_plan) "
            # " join plan_type pt on (p.id_plan_type=pt.id_plan_type) where id_user=%s)!='TRIAL_STARTUP') "
            # " then "
            # " plan_type.name!='TRIAL_STARTUP' "
            # " else TRUE end",
        self.logger.info("LikeForLike: Query for total amount of work/posts: %s", sqlTotal)

        totalToLikeResult = api_db.fetchOne(sqlTotal,
            self.campaign['id_user'], self.campaign['id_user'], self.campaign['id_user'])

        self.logger.info("LikeForLike:performLikes:: User has %s posts to like", totalToLikeResult['total'])

        totalLiked = 0
        havePendingWork = True
        securityBreak = 100
        iteration = 0

        while havePendingWork is True and securityBreak > iteration:
            self.logger.info("LikeForLike:performLikes: Iteration %s started...", iteration)

            sqlForGettingOnePost = "select user_post.* from user_post join user_subscription us on (user_post.id_user=us.id_user) join plan plan on (us.id_plan=plan.id_plan) join plan_type on (plan.id_plan_type=plan_type.id_plan_type) where id_post not in  (select id_post from user_post_log where id_user=%s)  and user_post.id_user!=%s and user_post.timestamp>=(select start_date from user_subscription where id_user=%s and (user_subscription.end_date>=NOW() or user_subscription.end_date is null))   and user_post.timestamp>=DATE(NOW() - INTERVAL 1 DAY) and user_post.code is not null order by id_post asc limit 1"
            self.logger.info("LikeForLike:performLikes: sqlForGettingOnePost: %s", sqlForGettingOnePost)

            post = api_db.fetchOne(sqlForGettingOnePost,self.campaign['id_user'], self.campaign['id_user'], self.campaign['id_user'])
            if post is None:
                self.logger.info("LikeForLike:performLikes:: There are no more posts to like, going to return !")
                havePendingWork = False
            else:
                self.logger.info("LikeForLike:performLikes:: Going to like id_post: %s", post['id_post'])
                wasPostLiked = self.performLike(post)

                if wasPostLiked:
                    totalLiked = totalLiked + 1
                    self.logger.info("LikeForLike:performLikes:: Success: Post %s was liked !", post['id_post'])

                    # update the log
                    api_db.insert("INSERT INTO `user_post_log` (`id_post`, `id_user`, `like_timestamp`,`liked`) VALUES (%s, %s, CURRENT_TIMESTAMP, %s)",post['id_post'], self.campaign['id_user'], wasPostLiked)
                    self.logger.info("LikeForLike:performLikes:: user_post_log was updated")

                else:
                    self.logger.info("LikeForLike:performLikes:: Error: Post %s was NOT liked", post['id_post'])

                    # update the log
                    api_db.insert(
                        "INSERT INTO `user_post_log` (`id_post`, `id_user`, `like_timestamp`,`liked`) VALUES (%s, %s, CURRENT_TIMESTAMP, %s)",
                        post['id_post'], self.campaign['id_user'], wasPostLiked)
                    self.logger.info("LikeForLike:performLikes:: user_post_log was updated")

            iteration = iteration + 1

            if havePendingWork is True:
                pause = randint(1, 1)
                self.logger.info("LikeForLike:performLikes:: Going to sleep %s seconds until proceeding to next post",pause)
                time.sleep(pause)

        self.logger.info("LikeForLike:performLikes:: DONE, total liked posts %s from a total of %s " % (
        totalLiked, totalToLikeResult['total']))
        return totalLiked

    def performLike(self, post):

        url = "https://instagram.com/p/" + str(post['code'])

        self.logger.info("likeForLike: performLike: Accessing url for user post %s", url)

        self.browser.get(url)

        liked = like_image(self.browser,
                           self.username,
                           self.instapy.blacklist,
                           self.logger,
                           self.instapy.logfolder)

        if liked is True:
            self.logger.info("likeForLike: performLike: SUCCESSFUL liked post id %s", post['id_post'])
        else:
            self.logger.info("likeForLike: performLike: UNSUCCESSFUL liking post id %s", post['id_post'])

        return liked

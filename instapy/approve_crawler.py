import traceback

from api_db import *


class ApproveCrawler:
    def __init__(self, instapy):
        self.instapy = instapy
        self.logger = instapy.logger

    def approve(self):

        crawlers = self.getCrawlers()

        self.logger.info("ApproveCrawler: approve: Going to approve %s crawlers for user: %s" % (
            len(crawlers), self.instapy.campaign['username']))

        if len(crawlers) == 0:
            self.logger.info("ApproveCrawler: No new crawlers to approve. Going to return...")
            return False

        for crawler in crawlers:
            self.approveCrawler(crawler)

        self.logger.info("ApproveCrawler: approve: Done approving crawler follow requests, returning...")

    def approveCrawler(self, crawler):
        self.logger.info("approveCrawler: Trying to approve crawler: %s", crawler['instagram_username'])

        self.clickNotificationsButton()

        followRequestsButton = self.instapy.browser.find_elements_by_xpath(
            "//span[contains(text(), 'Follow Requests')]")

        if len(followRequestsButton) == 0:
            self.logger.info("ApproveCrawler: approve: No (more) pending follow requests for user %s. Returning...",
                             self.instapy.campaign['username'])
            return False

        followRequestsButton[0].click()

        userRequestElements = self.instapy.browser.find_elements_by_xpath("//a[contains(text(), 'Follow Requests')]")[0] \
            .find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_xpath('..') \
            .find_elements_by_xpath("//a[contains(text(), '" + crawler['instagram_username'] + "')]")

        if len(userRequestElements):
            try:
                userRequestElement = userRequestElements[0]

                parentDiv = userRequestElement \
                    .find_element_by_xpath('..') \
                    .find_element_by_xpath('..') \
                    .find_element_by_xpath('..')

                approveButton = parentDiv.find_element_by_xpath(".//button[contains(text(), 'Approve')]")
                approveButton.click()
                self.logger.info("ApproveCrawler: approve: Done accepting follower %s", crawler['instagram_username'])
                self.saveFollow(crawler)

            except:
                exceptionDetail = traceback.format_exc()
                self.logger.info("ApproveCrawler:approveCrawler: There was an error: %s", exceptionDetail)

        else:
            self.logger.info("ApproveCrawler: No request from user %s", "florinbabusca")

        # close the popup
        self.clickNotificationsButton()

    def getCrawlers(self):
        self.logger.info("ApproveCrawler:getCrawlers: getting list of crawlers")
        crawlers = select("select * from campaign where bot_type='crawler'")

        self.logger.info("ApproveCrawler:getCrawlers: Found %s crawlers", len(crawlers))

        return crawlers

    def clickNotificationsButton(self):
        activityFeedButton = self.instapy.browser.find_element_by_xpath(
            "//*[contains(text(), 'Activity Feed')]").find_element_by_xpath('..').find_element_by_xpath('..');

        if activityFeedButton is None:
            raise Exception("ApproveCrawler: could not find Activity Feed Button")
        activityFeedButton.click()

    def saveFollow(self, crawler):
        query = "insert into bot_action (`id_campaign`,`id_user`,`bot_operation`,`bot_operation_value`,username, timestamp) values (%s, %s, %s, %s, %s, now())";

        insert(query,
               self.instapy.campaign['id_campaign'],
               self.instapy.campaign['id_user'],
               "follow_engagement_by_hashtag",
               crawler['instagram_username'],
               crawler['instagram_username'])

        self.logger.info("saveFollow: Dong saving follow action")

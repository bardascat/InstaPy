import time, datetime
import api_db
import random


def get_like_delay(instapy):
    delaySeconds = random.randint(instapy.like_delay - 3, instapy.like_delay + 5)
    timeSpentFromLastAction = get_current_timestamp() - instapy.last_action_timestamp

    remainedDelay = delaySeconds - timeSpentFromLastAction.seconds
    if remainedDelay < 0:
        remainedDelay = 0

    instapy.logger.info("get_like_delay: Time spent from last action: %s seconds, calculatedDelay: %s seconds, remained delay: %s seconds" % (timeSpentFromLastAction.seconds, delaySeconds, remainedDelay))

    return remainedDelay


def get_follow_delay(instapy):
    delaySeconds = random.randint(instapy.follow_delay - 5, instapy.follow_delay + 5)
    timeSpentFromLastAction = get_current_timestamp() - instapy.last_action_timestamp

    remainedDelay = delaySeconds - timeSpentFromLastAction.seconds
    if remainedDelay < 0:
        remainedDelay = 0

    instapy.logger.info("get_follow_delay: Time spent from last action: %s seconds, calculatedDelay: %s seconds, remained delay: %s seconds" % (timeSpentFromLastAction.seconds, delaySeconds, remainedDelay))

    return remainedDelay


def get_unfollow_delay(instapy):
    return get_follow_delay(instapy)


def get_current_timestamp():
    return datetime.datetime.now()


def set_last_action_timestamp(instapy, last_action_timestamp):
    instapy.logger.info("set_last_action_timestamp: setting last action timestamp to: %s", last_action_timestamp)
    instapy.last_action_timestamp = last_action_timestamp


def get_last_action_timestamp(campaign, logger):
    logger.info("get_last_action_timestamp: Getting last action timestamp for campaign: %s", campaign['id_campaign'])
    record = api_db.fetchOne("select timestamp from bot_action where id_campaign=%s order by timestamp desc limit 1",
                             campaign['id_campaign'])

    if record is not None:
        if record['timestamp'] is not None:
            return record['timestamp']

    return 0

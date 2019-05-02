import time, datetime
import api_db
import random


def get_like_delay(instapy):
    delaySeconds = random.randint(instapy.like_delay - 3, instapy.like_delay + 3)
    timeSpentFromLastAction = get_current_timestamp() - instapy.last_like_timestamp

    remainedDelay = delaySeconds - timeSpentFromLastAction.seconds
    if remainedDelay < 0:
        remainedDelay = 0

    instapy.logger.info("get_like_delay: Time spent from last like: %s seconds, calculatedDelay: %s seconds, remained delay: %s seconds" % (timeSpentFromLastAction.seconds, delaySeconds, remainedDelay))

    return remainedDelay


def get_follow_delay(instapy):
    delaySeconds = random.randint(instapy.follow_delay - 3, instapy.follow_delay + 3)
    timeSpentFromLastAction = get_current_timestamp() - instapy.last_follow_timestamp

    remainedDelay = delaySeconds - timeSpentFromLastAction.seconds
    if remainedDelay < 0:
        remainedDelay = 0

    instapy.logger.info("get_follow_delay: Time spent from last follow: %s seconds, calculatedDelay: %s seconds, remained delay: %s seconds" % (timeSpentFromLastAction.seconds, delaySeconds, remainedDelay))

    return remainedDelay


def get_unfollow_delay(instapy):
    delaySeconds = random.randint(instapy.unfollow_delay - 3, instapy.unfollow_delay + 3)
    timeSpentFromLastAction = get_current_timestamp() - instapy.last_unfollow_timestamp

    remainedDelay = delaySeconds - timeSpentFromLastAction.seconds
    if remainedDelay < 0:
        remainedDelay = 0

    instapy.logger.info("get_unfollow_delay: Time spent from last unfollow: %s seconds, calculatedDelay: %s seconds, remained delay: %s seconds" % (timeSpentFromLastAction.seconds, delaySeconds, remainedDelay))

    return remainedDelay


def get_current_timestamp():
    return datetime.datetime.now()

def set_last_like_timestamp(instapy, last_like_timestamp):
    instapy.last_like_timestamp = last_like_timestamp

def set_last_follow_timestamp(instapy, last_follow_timestamp):
    instapy.last_follow_timestamp = last_follow_timestamp

def set_last_unfollow_timestamp(instapy, last_unfollow_timestamp):
    instapy.last_unfollow_timestamp = last_unfollow_timestamp
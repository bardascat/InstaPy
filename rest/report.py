from pymongo import MongoClient
import datetime
from rest_logger import getLogger


def getMongoConnection():
    client = MongoClient(host='localhost', port=27017)
    return client


def summary(id_campaign, start, end, groupBy):
    logger = getLogger()
    format_str = '%Y-%m-%d'  # The format

    gte = datetime.datetime.strptime(start, format_str)
    lte = datetime.datetime.strptime(end, format_str)

    gte = gte.replace(minute=0, hour=0, second=0, microsecond=0)
    lte = lte.replace(minute=59, hour=23, second=59, microsecond=999)

    logger.info(
        "report.search: Bot Action report by operation: campaign: %s, start: %s, end: %s" % (id_campaign, gte, lte))

    client = getMongoConnection()
    db = client.angie_app

    if groupBy == "operation":
        pipeline = [
            {"$match": {"id_campaign": int(id_campaign), "timestamp": {"$gte": gte, "$lte": lte}}},
            {"$group": {"_id": {"bot_operation": "$bot_operation"},"total_action": {"$sum": 1}}},
            {"$project": {"_id": 0, "grouping": "$_id", "total_action": 1}}
        ]
    elif groupBy == "operationAndValue":
        pipeline = [
            {"$match": {"id_campaign": int(id_campaign), "timestamp": {"$gte": gte, "$lte": lte}}},
            {"$group": {"_id": {"bot_operation": "$bot_operation", "bot_operation_value": "$bot_operation_value"},"total_action": {"$sum": 1}}},
            {"$project": {"_id": 0, "grouping": "$_id", "total_action": 1}}
        ]

    result = db.bot_action.aggregate(pipeline=pipeline)
    result = list(result)

    logger.info("report: Retrieved %s rows", len(result))
    #client.close()

    return result


def getUserFollowersBreakdown(instagram_username, since, until):
    logger = getLogger()
    logger.info("crawler.getUserFollowersBreakdown: instagram_username: %s, since: %s, until: %s" % (
        instagram_username, since, until))

    format_str = '%Y-%m-%d'  # The format

    gte = datetime.datetime.strptime(since, format_str)
    lte = datetime.datetime.strptime(until, format_str)

    gte = gte.replace(minute=0, hour=0, second=0, microsecond=0)
    lte = lte.replace(minute=59, hour=23, second=59, microsecond=999)

    logger.info("crawler.getUserFollowersBreakdown: start: %s, end: %s" % (gte, lte))

    client = MongoClient(host='localhost', port=27017)
    db = client.angie_app

    result = db.processed_user_followers.find(
        {"owner_instagram_username": instagram_username, "start_date": {'$gt': gte, '$lt': lte}}, {"_id": 0},
        sort=[("start_date", -1)])
    result = list(result)

    logger.info("getUserFollowersBreakdown: Retrieved %s lines", len(result))

    #client.close()

    return result
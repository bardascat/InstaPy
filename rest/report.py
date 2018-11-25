from pymongo import MongoClient
import datetime
from rest_logger import getLogger


def getMongoConnection():
    client = MongoClient(host='localhost', port=27017)
    return client


def getActionsGroupByOperation(id_campaign, start, end):
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
    pipeline = [
        {"$match": {"id_campaign": int(id_campaign), "timestamp": {"$gte": gte, "$lte": lte}}},
        {"$group": {"_id": "$bot_operation", "total_action": {"$sum": 1}}},
        {"$project": {"_id": 0, "bot_operation": "$_id", "total_action": 1}}
    ]

    result = db.bot_action.aggregate(pipeline=pipeline)
    result = list(result)

    logger.info("report: Retrieved %s rows", len(result))
    client.close()

    return result

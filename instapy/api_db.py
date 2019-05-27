import MySQLdb
from pymongo import MongoClient
import datetime
import pymongo

client = None


def getMongoConnection():
    client = MongoClient('mongodb://127.0.0.1/angie_app')
    return client


def getMysqlConnection():
    db = MySQLdb.connect(host="104.248.128.65",  # your host, usually localhost
                         user="angie_app",  # your username
                         passwd="angiePasswordDB",  # your password
                         db="angie_app")

    db.set_character_set('utf8mb4')
    dbc = db.cursor()
    dbc.execute('SET NAMES utf8mb4;')
    dbc.execute('SET CHARACTER SET utf8mb4;')
    dbc.execute('SET character_set_connection=utf8mb4;')

    return db


def getCampaign(campaignId):
    if campaignId != False:
        row = fetchOne(
            "select username,id_user,id_campaign,timestamp,id_account_type from campaign where id_campaign=%s",
            campaignId)
        return row
    else:
        return None


def postWasLikedInThePast(linkCode, id_user):
    client = getMongoConnection()
    db = client.angie_app

    row = db.bot_action.find_one(
        {"post_link": linkCode, "id_user": id_user, "bot_operation": {"$regex": "^like_engagement_"}})
    client.close()

    if row == None:
        return False

    return True


def userWasFollowedInThePast(user_name, id_user):
    client = getMongoConnection()
    db = client.angie_app

    row = db.bot_action.find_one({"username": user_name, "id_user": id_user, "bot_operation": {"$regex": "^follow"}})
    client.close()

    if row == None:
        return False

    return True


def getWebApplicationUser(id_user):
    if id_user != False:
        row = fetchOne("select * from users where id_user=%s", id_user)
        return row
    else:
        return False


def fetchOne(query, *args):
    db = getMysqlConnection()
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(query, args)
    db.close()
    return cur.fetchone()


def select(query, *args):
    db = getMysqlConnection()
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(query, args)
    rows = cur.fetchall()
    db.close()
    return list(rows)


def insert(query, *args):
    db = getMysqlConnection()
    cur = db.cursor()
    cur.execute(query, args)
    db.commit()
    id = cur.lastrowid
    db.close()
    return id


def updateCampaignChekpoint(key, value, id_campaign):
    query = 'INSERT INTO campaign_checkpoint (id_campaign, _key, value, timestamp) VALUES(%s, %s, %s, CURDATE()) ON DUPLICATE KEY UPDATE  value=%s'

    id = insert(query, id_campaign, key, value, value)

    return id


def getCampaignWorkingDays(id_campaign):
    client = getMongoConnection()

    db = client.angie_app
    pipeline = [{"$match": {"id_campaign": id_campaign}},
                {"$group": {"_id": {"year": {"$year": "$timestamp"}, "month": {"$month": "$timestamp"},
                                    "day": {"$dayOfMonth": "$timestamp"}}, "count": {"$sum": 1}}}]

    client.close()
    return len(list(db.bot_action.aggregate(pipeline=pipeline)))


def revertBotFollow(recordToUnfollow, lastBotAction):
    client = getMongoConnection()
    db = client.angie_app
    db.bot_action.update({"_id": recordToUnfollow}, {"$set": {"bot_operation_reverted": lastBotAction}})
    client.close()


def createUnfollowCycle(id_campaign, activeFollowings):

    cycle = fetchOne("select * from bot_unfollow_cycle where completed=0 and id_campaign=%s", id_campaign)
    if cycle is None:
        insert("INSERT INTO bot_unfollow_cycle (id_campaign, angie_followings, completed ) VALUES(%s, %s, 0)", id_campaign, activeFollowings)
        return True
    return False


def getActiveFollowings(id_campaign, queryDate):
    client = getMongoConnection()
    db = client.angie_app
    result = db.bot_action.find({"id_campaign": int(id_campaign), "bot_operation_reverted": None, "status": True,
                                 "bot_operation": {"$regex": "^follow"}, "timestamp": {"$lte": queryDate}})
    if result is None:
        return 0

    activeFollowings = result.count()
    client.close()

    return activeFollowings

def getAmountOperations(campaign, dateParam, operation):
    gte = dateParam.replace(minute=0, hour=0, second=0, microsecond=0)
    lte = dateParam.replace(minute=59, hour=23, second=59, microsecond=59)

    client = getMongoConnection()
    db = client.angie_app

    result = db.bot_action.find({"id_campaign": campaign['id_campaign'], "status":True, "bot_operation": {"$regex": "^" + operation},
                                 "timestamp": {"$gte": gte, "$lte": lte}})
    client.close()

    if result == None:
        return 0

    return result.count()


def getUserToUnfollow(id_campaign, olderThan):
    #return True
    # TODO: unfollow only users who did not follow back
    # selectFollowings = "select * from bot_action where  bot_operation like %s and timestamp< (NOW() - INTERVAL %s HOUR) and id_user= %s and bot_operation_reverted is null ORDER BY - follow_back desc, timestamp asc limit %s"
    # recordToUnfollow = fetchOne(selectFollowings, 'follow' + '%', userWantsToUnfollow['value'],
    #                            self.campaign['id_user'], 1)

    currentDate = datetime.datetime.now()
    queryDate = currentDate - datetime.timedelta(hours=int(olderThan))
    lte = queryDate.replace(minute=59, hour=23, second=59, microsecond=59)

    client = getMongoConnection()
    db = client.angie_app

    result = db.bot_action.find_one(
        {"id_campaign": id_campaign, "bot_operation_reverted": None, "status":True, "bot_operation": {"$regex": "^follow"},
         "timestamp": {"$lte": lte}}, sort=[("timestamp", pymongo.ASCENDING)])
    client.close()

    return result


def insertBotAction(*args):
    client = getMongoConnection()
    db = client.angie_app

    _id = db.bot_action.insert({
        "id_campaign": args[0],
        "id_user": args[1],
        "instagram_id_user": args[2],
        "full_name": args[3],
        "username": args[4],
        "user_image": args[5],
        "post_id": args[6],
        "post_image": args[7],
        "post_link": args[8],
        "bot_operation": args[9],
        "bot_operation_value": args[10],
        "bot_operation_reverted": None,
        "id_log": args[11],
        "status":args[12],
        "timestamp": datetime.datetime.now(),
    })

    client.close()
    return _id


def insertOwnFollower(*args):
    query = "insert into own_followers (id_user,instagram_id_user,full_name,username,user_image,is_verified,timestamp) " \
            " VALUES (%s,%s,%s,%s,%s,%s,now()) ON DUPLICATE KEY UPDATE instagram_id_user=instagram_id_user"

    id = insert(query, *args)
    return id


def insertUserFollower(*args):
    query = "insert into instagram_user_followers (fk,instagram_id_user,full_name,username,user_image,is_verified,timestamp) " \
            " VALUES (%s,%s,%s,%s,%s,%s,now()) ON DUPLICATE KEY UPDATE instagram_id_user=instagram_id_user"

    id = insert(query, *args)
    return id


def getBotIp(bot, id_user, id_campaign, is_bot_account):
    query = "select ip,type from  campaign left join ip_bot on campaign.id_ip_bot=ip_bot.id_ip_bot where id_campaign=%s"

    result = fetchOne(query, id_campaign)

    if result is None or result['ip'] is None:
        bot.logger.warning("getBotIp: Could not find an ip for user %s", id_user)
        raise Exception("getBotIp: Could not find an ip for user" + str(id_user))

    bot.logger.info("User %s, has ip: %s" % (id_user, result['ip']))
    return result

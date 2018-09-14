import argparse
import codecs
import os
import sys
import traceback
from time import sleep
from instapy import InstaPy
from instapy.bot_action_handler import getAmountDistribution, getLikeAmount, getFollowAmount, getUnfollowAmount, getActionAmountForEachLoop
from instapy.bot_util import *
from instapy.account_privacy_service import AccountPrivacyService

stdout = sys.stdout
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.path.append(os.path.join(sys.path[0], '../'))

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-angie_campaign', type=str, help="angie_campaign")
args = parser.parse_args()

args.angie_campaign='1'

if args.angie_campaign is None:
    exit("dispatcher: Error: Campaign id it is not specified !")

try:

    campaign = fetchOne("select ip,username,password,campaign.timestamp,id_campaign,id_user  from campaign left join ip_bot using (id_ip_bot) where id_campaign=%s",args.angie_campaign)

    if campaign['ip'] is None:
        exit("Invalid proxy")

    session = InstaPy(username=campaign['username'],
                      password=campaign['password'],
                      headless_browser=False,
                      bypass_suspicious_attempt=False,
                      proxy_address=campaign['ip'].replace("http://cata:lin@", ""),
                      campaign=campaign,
                      proxy_port="80",
                      multi_logs=True,
                      force_login=False)

    status = session.login()
    if status == False:
        exit("Could not  login")

    calculatedAmount = getAmountDistribution(session, args.angie_campaign)
    totalExpectedLikesAmount = int(getLikeAmount(calculatedAmount))
    totalExpectedFollowAmount = int(getFollowAmount(calculatedAmount))
    totalExpectedUnfollowAmount = int(getUnfollowAmount(calculatedAmount))

    operations = getBotOperations(campaign['id_campaign'], session.logger)

    session.set_max_actions(totalExpectedLikesAmount, totalExpectedFollowAmount, totalExpectedUnfollowAmount)
    session.set_relationship_bounds(enabled=True, potency_ratio=0.01, max_followers=999999, max_following=99999, min_followers=100, min_following=50)

    session.logger.info("start: PID: %s, Instapy Started for account %s using proxy: %s" % (os.getpid(), campaign['username'], campaign['ip']))
    session.canBotStart(args.angie_campaign, "angie_instapy_idc")



    noOfLoops = randint(6,8)

    session.logger.info("start: Bot started going to perform %s likes, %s follow, %s unfollow during %s loops" % (totalExpectedLikesAmount, totalExpectedFollowAmount, totalExpectedUnfollowAmount, noOfLoops))
    insert("INSERT INTO campaign_log (`id_campaign`, event, `details`, `timestamp`) VALUES (%s, %s, %s, now())", campaign['id_campaign'], "ENGAGEMENT_BOT_STARTED", None)

    for loopNumber in range(0, noOfLoops):

        #TODO: IMPORTANT -> this is an issue with small values ! tested with like 45 follow 30
        likeAmountForEachLoop = getActionAmountForEachLoop(totalExpectedLikesAmount, noOfLoops)
        followAmountForEachLoop = getActionAmountForEachLoop(totalExpectedFollowAmount, noOfLoops)
        unFollowAmountForEachLoop = getActionAmountForEachLoop(totalExpectedUnfollowAmount, noOfLoops)

        session.logger.info("start: Starting loop number %s, going to perform: likeAmount: %s, followAmount:%s, unfollowAmount %s" % (loopNumber, likeAmountForEachLoop, followAmountForEachLoop, unFollowAmountForEachLoop))

        session.executeAngieActions(operations, likeAmount=likeAmountForEachLoop, followAmount=followAmountForEachLoop, unfollowAmount=unFollowAmountForEachLoop)

        sleepMinutes = randint(30,60)
        session.logger.info("start: GOING TO SLEEP FOR %s MINUTES, LOOP NO %s" % (sleepMinutes, loopNumber))

        sleep(sleepMinutes*60)
        session.logger.info("start: Done sleeping going to continue looping...")

    session.logger.info("start: Angie loop completed , going to exit...")

    session.logger.info("start: Setting privacy to public for this account...")
    accountPrivacyService = AccountPrivacyService(session)
    accountPrivacyService.switchToPublic()

    session.logger.info("start: ALL DONE, CLOSING APP")
except:
    exceptionDetail = traceback.format_exc()
    print(exceptionDetail)
    session.logger.critical("start: FATAL ERROR: %s", exceptionDetail)
finally:
    session.logger.info("start: Instapy ended for user: %s", campaign['username'])

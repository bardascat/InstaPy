import argparse
import codecs
import os
import sys
from time import sleep
from instapy import InstaPy
from instapy.bot_action_handler import getAmountDistribution, getLikeAmount, getFollowAmount, getUnfollowAmount, \
    getActionAmountForEachLoop
from instapy.bot_util import *
from instapy.account_privacy_service import AccountPrivacyService
from instapy.exception_handler import ExceptionHandler
import traceback

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

    campaign = fetchOne("select ip,username,password,campaign.timestamp,id_campaign,id_user  from campaign left join ip_bot using (id_ip_bot) where id_campaign=%s", args.angie_campaign)
    insert("INSERT INTO campaign_log (`id_campaign`, event, `details`, `timestamp`) VALUES (%s, %s, %s, now())", campaign['id_campaign'], "ENGAGEMENT_BOT_STARTED", None)

    if campaign['ip'] is None:
        exit("Invalid proxy")

    session = InstaPy(username=campaign['username'],
                      password=campaign['password'],
                      headless_browser=False,
                      bypass_suspicious_attempt=False,
                      proxy_address=campaign['ip'].replace("http://cata:lin@", ""),
                      disable_image_load=True,
                      campaign=campaign,
                      proxy_port="80",
                      multi_logs=True,
                      bot_type="engagement_bot",
                      force_login=False)

    session.set_quota_supervisor(enabled=True)


    session.logger.info("start: ENGAGEMENT BOT STARTED for campaign: %s, with ip: %s. Going to try login..." % (campaign['id_campaign'], campaign['ip']))
    status = session.login()
    if status == False:
        exit("Could not  login")

    calculatedAmount = getAmountDistribution(session, args.angie_campaign)
    if calculatedAmount['like_amount'] == 0 and calculatedAmount['follow_amount'] == 0:
        session.logger.info("start: No actions set, going to exit. like_amount:%s, follow_amount:%s" % (calculatedAmount['like_amount'], calculatedAmount['follow_amount']))
    else:
        totalExpectedLikeAmount = int(getLikeAmount(calculatedAmount))
        totalExpectedFollowAmount = int(getFollowAmount(calculatedAmount))
        totalExpectedUnfollowAmount = int(getUnfollowAmount(calculatedAmount))

        operations = getBotOperations(campaign['id_campaign'], session.logger)

        session.set_max_actions(totalExpectedLikeAmount, totalExpectedFollowAmount, totalExpectedUnfollowAmount)
        session.set_relationship_bounds(enabled=True, potency_ratio=0.01, max_followers=999999, max_following=99999,
                                        min_followers=100, min_following=50)

        session.logger.info("start: PID: %s, Instapy Started for account %s using proxy: %s" % (
        os.getpid(), campaign['username'], campaign['ip']))
        session.canBotStart(args.angie_campaign, "angie_instapy_idc")

        noOfLoops = randint(6, 8)

        session.logger.info("start: Bot started performing actions: %s likes, %s follow, %s unfollow during %s loops" % (
        totalExpectedLikeAmount, totalExpectedFollowAmount, totalExpectedUnfollowAmount, noOfLoops))
        insert("INSERT INTO campaign_log (`id_campaign`, event, `details`, `timestamp`) VALUES (%s, %s, %s, now())",
               campaign['id_campaign'], "ENGAGEMENT_BOT_STARTED_PERFORMING_ACTIONS", None)


        angieResults={"totalLikePerformed": 0, "totalFollowPerformed": 0, "totalUnfollowPerformed": 0}
        for loopNumber in range(0, noOfLoops):
            likeAmountForEachLoop = getActionAmountForEachLoop(totalExpectedLikeAmount, noOfLoops)
            followAmountForEachLoop = getActionAmountForEachLoop(totalExpectedFollowAmount, noOfLoops)
            unFollowAmountForEachLoop = getActionAmountForEachLoop(totalExpectedUnfollowAmount, noOfLoops)

            session.logger.info(
                "START ITERATION %s, going to perform: likeAmount: %s, followAmount:%s, unfollowAmount %s" % (
                loopNumber, likeAmountForEachLoop, followAmountForEachLoop, unFollowAmountForEachLoop))

            iterationResults = session.executeAngieActions(operations, likeAmount=likeAmountForEachLoop,
                                        followAmount=followAmountForEachLoop, unfollowAmount=unFollowAmountForEachLoop)

            session.logger.info("-------------- END ITERATION %s : LIKE PERFORMED/EXPECTED %s/%s, FOLLOW PERFORMED/EXPECTED: %s/%s, UNFOLLOW PERFORMED/EXPECTED: %s/%s ------------------" % (iterationResults['totalLikePerformed'], likeAmountForEachLoop, iterationResults['totalFollowPerformed'], followAmountForEachLoop, iterationResults['totalUnfollowPerformed'], unFollowAmountForEachLoop ))


            if session.engagementService.totalLikePerformed>=totalExpectedLikeAmount and session.engagementService.totalFollowPerformed>=totalExpectedFollowAmount and session.engagementService.totalUnfollowPerformed>=totalExpectedUnfollowAmount:
                session.logger.info("start: going to break the loop. Number of actions reached for all ops !")
                break

            #sleepMinutes = randint(30, 60)
            #session.logger.info("start: GOING TO SLEEP FOR %s MINUTES, LOOP NO %s" % (sleepMinutes, loopNumber))
            #sleep(sleepMinutes * 60)
            #session.logger.info("start: Done sleeping going to continue looping...")

        session.logger.info("start: Angie loop completed , going to exit...")
        session.logger.info("--------------ENGAGEMENT BOT RESULT : LIKE PERFORMED/EXPECTED %s/%s FOLLOW PERFORMED/EXPECTED: %s/%s UNFOLLOW PERFORMED/EXPECTED: %s/%s ------------------"
                            % (session.engagementService.totalLikePerformed, totalExpectedLikeAmount, session.engagementService.totalFollowPerformed, totalExpectedFollowAmount, session.engagementService.totalUnfollowPerformed, totalExpectedUnfollowAmount))

        session.logger.info("start: Setting privacy to public for this account...")
        accountPrivacyService = AccountPrivacyService(session)
        accountPrivacyService.switchToPublic()

        session.logger.info("start: ALL DONE, CLOSING ENGAGEMENT BOT")
except Exception as exc:
    exceptionDetail = traceback.format_exc()
    print(exceptionDetail)
    exceptionHandler = ExceptionHandler(session,'engagement_bot')
    exceptionHandler.handle(exc)

import argparse
import codecs
import os
import sys
import traceback

from instapy import InstaPy
from instapy.account_privacy_service import AccountPrivacyService
from instapy.bot_action_handler import getAmountDistribution
from instapy.bot_util import *
from instapy.exception_handler import ExceptionHandler

stdout = sys.stdout
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.path.append(os.path.join(sys.path[0], '../'))

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-angie_campaign', type=str, help="angie_campaign")
args = parser.parse_args()

#args.angie_campaign='1'

if args.angie_campaign is None:
    exit("dispatcher: Error: Campaign id it is not specified !")


def start(session):
    session.logger.info("start: ENGAGEMENT BOT STARTED for campaign: %s, with ip: %s. Going to try login..." % (
        campaign['id_campaign'], campaign['ip']))
    status = session.login()
    if status == False:
        exit("Could not  login")

    # if no actions are set by the user
    calculatedAmount = getAmountDistribution(session, args.angie_campaign)
    if calculatedAmount['like_amount'] == 0 and calculatedAmount['follow_amount'] == 0:
        session.logger.info("start: No actions set, going to exit. like_amount:%s, follow_amount:%s" % (
        calculatedAmount['like_amount'], calculatedAmount['follow_amount']))
        return False

    totalExpectedLikeAmount = int(calculatedAmount["like_amount"])
    totalExpectedFollowAmount = int(calculatedAmount["follow_amount"])
    totalExpectedUnfollowAmount = int(calculatedAmount["unfollow_amount"])

    operations = getBotOperations(campaign['id_campaign'], session.logger)
    if getOperationsNumber(operations)==0:
        session.logger.info("No operations of type engagement by hashtag/location enabled for this user.")
        return False


    session.logger.info("start: PID: %s, Instapy Started for account %s using proxy: %s" % (
    os.getpid(), campaign['username'], campaign['ip']))


    session.logger.info("start.py: Bot started performing actions: %s likes, %s follow, %s unfollow." % (totalExpectedLikeAmount, totalExpectedFollowAmount, totalExpectedUnfollowAmount))
    insert("INSERT INTO campaign_log (`id_campaign`, event, `details`, `timestamp`) VALUES (%s, %s, %s, now())",
           campaign['id_campaign'], "ENGAGEMENT_BOT_STARTED_PERFORMING_ACTIONS", None)


    iterationResults = session.actionService.perform_engagement(likeAmount=totalExpectedLikeAmount,
                                                                followAmount=totalExpectedFollowAmount,
                                                                unfollowAmount=totalExpectedUnfollowAmount)

    session.logger.info("start: Done processing %s posts: result: %s" % (max(totalExpectedLikeAmount, totalExpectedFollowAmount, totalExpectedUnfollowAmount), iterationResults))
    session.logger.info("start: Setting privacy to public for this account...")
    accountPrivacyService = AccountPrivacyService(session)
    accountPrivacyService.switchToPublic()

    session.logger.info("start: ALL DONE, CLOSING ENGAGEMENT BOT")


try:
    campaign = fetchOne(
        "select ip,username,password,instagram_username,campaign.timestamp,id_campaign,id_user  from campaign left join ip_bot using (id_ip_bot) where id_campaign=%s",
        args.angie_campaign)
    insert("INSERT INTO campaign_log (`id_campaign`, event, `details`, `timestamp`) VALUES (%s, %s, %s, now())",
           campaign['id_campaign'], "ENGAGEMENT_BOT_STARTED", None)

    if campaign['ip'] is None:
        exit("Invalid proxy")

    session = InstaPy(username=campaign['username'],
                      password=campaign['password'],
                      headless_browser=True,
                      bypass_suspicious_attempt=False,
                      proxy_address=campaign['ip'].replace("http://cata:lin@", ""),
                      disable_image_load=False,
                      campaign=campaign,
                      proxy_port=80,
                      multi_logs=True,
                      bot_type="engagement_bot",
                      force_login=False)

    canBotStart = session.canBotStart(args.angie_campaign, "angie_instapy_idc")

    if canBotStart:
        session.set_quota_supervisor(enabled=True)
        session.set_relationship_bounds(enabled=True, potency_ratio=0.01, max_followers=999999, max_following=99999,min_followers=100, min_following=50)
        start(session)


except Exception as exc:
    exceptionDetail = traceback.format_exc()
    print(exceptionDetail)
    exceptionHandler = ExceptionHandler(session, 'engagement_bot')
    exceptionHandler.handle(exc)

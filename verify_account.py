import argparse
import codecs
import json
import os
import sys
import traceback



stdout = sys.stdout
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.path.append(os.path.join(sys.path[0], '../'))

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-settings', type=str, help="settings")
args = parser.parse_args()

if args.settings is None:
    exit("verify_account: settings are not specified !")

result = {}
result['status'] = False

try:
    from instapy import InstaPy
    from instapy.bot_util import *
    from instapy.account_privacy_service import AccountPrivacyService

    settings = json.loads(args.settings)
    campaign = fetchOne(
        "select ip,username,password,campaign.timestamp,id_campaign,id_user  from campaign left join ip_bot using (id_ip_bot) where id_campaign=%s",
        settings['id_campaign'])

    insert("INSERT INTO campaign_log (`id_campaign`, event, `details`, `timestamp`) VALUES (%s, %s, %s, now())", campaign['id_campaign'], "USER_TRYING_TO_VERIFY_INSTAGRAM_CREDENTIALS", None)

    session = InstaPy(username=settings['u'],
                      password=settings['p'],
                      headless_browser=True,
                      bypass_suspicious_attempt=False,
                      proxy_address=campaign['ip'].replace("http://cata:lin@", ""),
                      campaign=campaign,
                      proxy_port="80",
                      multi_logs=True,
                      show_logs=False,
                      force_login=True)

    status = session.login()
    if status is True:
        result['status'] = True


        accountPrivacyService = AccountPrivacyService(session)
        accountPrivacyService.switchToPublic()
        accountPrivacyService.extractInstagramUsername()

    session.logger.info("start: ALL DONE, CLOSING APP")
except:
    exceptionDetail = traceback.format_exc()
    # print(exceptionDetail)
    session.logger.critical("start: FATAL ERROR: %s", exceptionDetail)
    result['exception'] = exceptionDetail
finally:
    print(json.dumps(result))
    # session.logger.info("start:finally: Closing process...")

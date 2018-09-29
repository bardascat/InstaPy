import argparse
import codecs
import os
import sys

from instapy import InstaPy
from instapy.bot_util import *

stdout = sys.stdout
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.path.append(os.path.join(sys.path[0], '../'))

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-angie_campaign', type=str, help="angie_campaign")
args = parser.parse_args()
from instapy.exception_handler import ExceptionHandler

#args.angie_campaign='1'

if args.angie_campaign is None:
    exit("dispatcher: Error: Campaign id it is not specified !")

try:

    print("Started like_for_like")
    campaign = fetchOne("select ip,username,password,campaign.timestamp,id_campaign,id_user  from campaign left join ip_bot using (id_ip_bot) where id_campaign=%s",args.angie_campaign)
    
    print(campaign)
    
    if campaign['ip'] is None:
        exit("Invalid proxy")

    session = InstaPy(username=campaign['username'],
                      password=campaign['password'],
                      headless_browser=True,
                      bypass_suspicious_attempt=False,
                      proxy_address=campaign['ip'].replace("http://cata:lin@", ""),
                      campaign=campaign,
                      proxy_port="80",
                      multi_logs=True)

    session.logger.info("likeforlike: START PID: %s, account %s, using proxy: %s" % (os.getpid(), campaign['username'], campaign['ip']))
    session.canBotStart(id_campaign=args.angie_campaign, prefix="angie_instapy_like_for_like_idc")

    status = session.login()

    if status == False:
        exit("Could not  login")

    session.startLikeForLike()

except Exception as exc:
    exceptionHandler = ExceptionHandler(session,'like_for_like')
    exceptionHandler.handle(exc)
finally:
    session.logger.info("start: LIke For Like ended for user: %s", campaign['username'])

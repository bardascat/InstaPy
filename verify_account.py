import argparse
import codecs
import json
import os
import sys
import traceback

from instapy import InstaPy
from instapy.bot_util import *

stdout = sys.stdout
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.path.append(os.path.join(sys.path[0], '../'))

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-settings', type=str, help="settings")
args = parser.parse_args()

if args.settings is None:
    exit("verify_account: settings are not specified !")

result = {}
result['status']=False

try:
    settings = json.loads(args.settings)
    campaign = fetchOne(
        "select ip,username,password,campaign.timestamp,id_campaign,id_user  from campaign left join ip_bot using (id_ip_bot) where id_campaign=%s", settings['id_campaign'])

    session = InstaPy(username=settings['u'],
                      password=settings['p'],
                      headless_browser=True,
                      bypass_suspicious_attempt=False,
                      proxy_address=campaign['ip'].replace("http://cata:lin@", ""),
                      campaign=campaign,
                      proxy_port="80",
                      multi_logs=True,
                      show_logs=True,
                      force_login=True)

    status = session.login()
    if status is True:
        result['status']=True

    session.logger.info("start: ALL DONE, CLOSING APP")
except:
    exceptionDetail = traceback.format_exc()
    #print(exceptionDetail)
    session.logger.critical("start: FATAL ERROR: %s", exceptionDetail)
    result['exception']=exceptionDetail
finally:
    print(json.dumps(result))
    session.logger.info("start:finally: Closing process...")

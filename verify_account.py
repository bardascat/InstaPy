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

try:
    from pymongo import MongoClient
    result["mongo"]="fine"
    from instapy import InstaPy
    from instapy.bot_util import *
    from instapy.account_privacy_service import AccountPrivacyService


except:
    exceptionDetail = traceback.format_exc()
    # print(exceptionDetail)
    result['exception'] = exceptionDetail
finally:
    print(json.dumps(result))
    # session.logger.info("start:finally: Closing process...")

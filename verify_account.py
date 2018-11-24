import argparse
import codecs
import json
import os
import sys
import traceback

try:
    from instapy import InstaPy
    from instapy import InstaPy
    from instapy.bot_action_handler import getAmountDistribution, getActionAmountForEachLoop
    from instapy.bot_util import *
    from instapy.account_privacy_service import AccountPrivacyService
    result = {}
    result['status'] = False
except:
    exceptionDetail = traceback.format_exc()
    # print(exceptionDetail)
    #session.logger.critical("start: FATAL ERROR: %s", exceptionDetail)
    result['exception'] = exceptionDetail
finally:
    print(json.dumps(result))
    # session.logger.info("start:finally: Closing process...")

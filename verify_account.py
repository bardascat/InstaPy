import argparse
import codecs
import json
import os
import sys
import traceback

try:
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

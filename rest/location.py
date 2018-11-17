import os
import subprocess

from rest_logger import getLogger

python_path = "python"
base_path = "/home/ubuntu/projects/instabot/run"
DEVNULL = open(os.devnull, 'wb')


def search(location):

    SEARCH_LOCATION_ACCOUNT_OP_ART = '3'

    logger = getLogger()
    logger.info("location.search: Going to search for locations using: %s wildcard" % (location))

    process = subprocess.Popen("python "+base_path + "/search_location.py -location="+location+" -id_campaign="+SEARCH_LOCATION_ACCOUNT_OP_ART, shell=True, stdout=subprocess.PIPE)
    result = process.communicate()[0]
    process.wait()

    logger.info("location.search: Result is: %s", result)
    return result

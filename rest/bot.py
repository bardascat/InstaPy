import subprocess
import os
from rest_logger import getLogger
import json

python_path = "python"
base_path = "/home/ubuntu/projects/InstaPy"
DEVNULL = open(os.devnull, 'wb')


def verify(username, password, id_campaign):
    logger = getLogger()
    logger.info("bot.verify: Going to verify instagram account of id_campaign: %s. u:%s" % (id_campaign, username))
    settings = {"u": username, "p": password, "id_campaign": id_campaign}

    process = subprocess.Popen("python "+base_path + "/verify_account.py -settings='"+json.dumps(settings)+"'", shell=True, stdout=subprocess.PIPE)
    result = process.communicate()[0]
    process.wait()

    logger.info("bot.verify: Result is: %s", result)
    return result

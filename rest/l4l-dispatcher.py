import os
import subprocess

from rest_logger import getLogger

python_path = "python"
base_path = "/home/projects/InstaPy"
DEVNULL = open(os.devnull, 'wb')

logger = getLogger()
logger.info("l4l-dispatcher.start: Starting like for like dispatcher")

processName = 'angie_like_for_like_dispatcher'

command = "bash -c \"exec -a " + processName + " sudo /usr/bin/python2.7 " + base_path + "/l4l_dispatcher.py \""

logger.info("executing command: %s", command)
subprocess.Popen(command, close_fds=True, shell=True, stdin=None, stdout=DEVNULL, stderr=DEVNULL)

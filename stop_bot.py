import time
import psutil
import logging
import os
import signal
from random import randint


# logging.basicConfig(format='%(asctime)s %(message)s', filename='/home/instabot-log/stop_bot.log', level=logging.DEBUG)
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# ch.setFormatter(formatter)
# logger = logging.getLogger('[l4l]')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(ch)


def killProcess(pid):
    print("killProcess: killing process: %s", pid)
    os.kill(pid, signal.SIGKILL)


def stopProcesses():
    # logger.info("stopProcesses:Searching process...")

    print("final cleanup, going to kill hanging procesess")
    os.system(" ps aux  |  grep -i angie_idc  |  awk '{print $2}'  |  xargs  kill -9")
    os.system("ps aux  |  grep -i angie_instapy |  awk '{print $2}'  |  xargs  kill -9")
    os.system("ps aux  |  grep -i angie_scan_user |  awk '{print $2}'  |  xargs  kill -9")
    os.system("ps aux  |  grep -i angie_ |  awk '{print $2}'  |  xargs  kill -9")
    os.system("ps aux  |  grep -i chrome |  awk '{print $2}'  |  xargs  kill -9")
    os.system("ps aux  |  grep -i instabot |  awk '{print $2}'  |  xargs  kill -9")
    os.system("ps aux  |  grep -i instapy |  awk '{print $2}'  |  xargs  kill -9")
    print("final cleanup done...")

    print("stopProcesses: DONE")


stopProcesses()

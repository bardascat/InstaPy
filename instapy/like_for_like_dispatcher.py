import time
import psutil
import logging
import os
import api_db
import subprocess
from random import randint
import signal
import settings

class LikeForLikeDispatcher:
    def __init__(self):
        fileName = time.strftime("%d.%m.%Y") + ".log"
        loggingPath = settings.BASE_DIR+'campaign/logs/l4l/' + fileName

        logging.basicConfig(format='%(asctime)s %(message)s', filename=loggingPath,level=logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger = logging.getLogger('[l4l]')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(ch)

        self.DEVNULL = open(os.devnull, 'wb')

    #this method is going to select all users that have an active subscription (account is enabled) and have posts to like
    #and each user will have to perform likeForLike for posts that are not liked yet and are not older than 1 day
    def bootstrap(self):
        self.logger.info("bootstrap: ************* Like for like dispatcher STARTED ! *****************")
        self.logger.info("bootstrap: Checking if process is already started...")
        processName = "angie_like_for_like_dispatcher"
        pid = self.canDispatcherProcessStart(processName)

        if pid is False:
            self.logger.error("bootstrap: Error:There is already a l4l dispatcher process with name %s started", processName)
            return False
        else:
            self.logger.info("bootstrap: All good ! There is no other l4l dispatcher process running !")

        # select users that have an active subscription, and have pending posts to like.
        result = api_db.select("select users.id_user, email, username, campaign.password, campaign.id_campaign from users join campaign on (users.id_user=campaign.id_user) join user_subscription on (users.id_user = user_subscription.id_user) join plan on (user_subscription.id_plan=plan.id_plan) join plan_type on (plan.id_plan_type=plan_type.id_plan_type) where (user_subscription.end_date>now() or user_subscription.end_date is null) and (select count(*) as total from user_post join user_subscription us2 on (user_post.id_user=us2.id_user) join plan plan2 on (us2.id_plan=plan2.id_plan) join plan_type plan_type2 on (plan2.id_plan_type=plan_type2.id_plan_type) where id_post not in (select id_post from user_post_log where id_user=users.id_user) and user_post.id_user!=users.id_user and user_post.timestamp>=user_subscription.start_date and user_post.timestamp>=DATE(NOW() - INTERVAL 1 DAY))>0 and campaign.active=1 order by rand()")

        # self.logger.info(result)
        self.logger.info("bootstrap: Found %s users with pending work", len(result))
        for user in result:
            self.logger.info("bootstrap: Going to process user %s", user['email'])

            self.startLikeForLikeProcess(user)

            pause = randint(1, 1)
            self.logger.info("bootstrap: Going to wait %s seconds before processing another user !", pause)
            time.sleep(pause)
            self.logger.info("bootstrap: Done waiting, going to process next user...")

        self.logger.info("bootstrap: Done executing the script.. exiting")

    def startLikeForLikeProcess(self, user):
        self.logger.info("startLikeForLikeProcess: Trigering l4l functionality for user: %s", user['email'])

        defaultBotProcessName = 'angie_instapy_idc' + str(user['id_campaign'])
        pid = self.findProcessPid(defaultBotProcessName)

        if pid == False:
            self.logger.info("startLikeForLikeProcess: Default bot campaign process(%s) is NOT running for campaign %s. Going to start the l4l process." % (defaultBotProcessName, user['id_campaign']))
            self.startLikeForLikeProcessProcess(user['id_campaign'])
        else:
            self.logger.info("startLikeForLikeProcess: Default bot campaign process(%s) is running for campaign %s. Going to send the SIGUSR1 signal..." % (defaultBotProcessName, defaultBotProcessName))
            self.sendL4lSignal(pid, str(user['id_campaign']))


    def sendL4lSignal(self, pid, id_campaign):
        self.logger.info("sendL4lSignal: Going to send SIGUSR1 signal to process: %s, campaign: %s", pid, id_campaign)
        p = psutil.Process(pid)
        p.send_signal(sig=signal.SIGUSR1)
        self.logger.info("sendL4lSignal: Done sending the signal.")
        return True

    #TODO: IMPORTANT::::::::: what happens if this process starts first and then the default one start over ???

    def startLikeForLikeProcessProcess(self, id_campaign):

        self.logger.info("startLikeForLikeProcessProcess: Starting like for like process for campaign %s", id_campaign)
        processName = "angie_instapy_like_for_like_idc" + str(id_campaign)

        self.logger.info("startLikeForLikeProcessProcess: checking if there is already a process started with name %s", processName)
        pid = self.findProcessPid(processName)
        if pid != False:
            self.logger.info("startLikeForLikeProcessProcess: Error - there is already an active like for like process for campaign %s, GOING TO SKIP THIS USER",id_campaign)
            return False
        else:
            self.logger.info("startLikeForLikeProcessProcess: All good, the like for like process with name %s is not active, going to start it now !",processName)

        #TODO the location for the python script needs to be changed when deploying to linux server
        subprocess.Popen(
            "bash -c \"exec -a " + processName + " /usr/bin/python /home/InstaPy/like_for_like.py  -angie_campaign=" + str(id_campaign) + " \"", stdin=None, stdout=self.DEVNULL, stderr=self.DEVNULL, close_fds=True, shell=True)
        
            
        self.logger.info("startLikeForLikeProcessProcess: Successfully started process for campaign %s", id_campaign)


    def findProcessPid(self, processName):
        self.logger.info("findProcessPid:Searching process with name :%s ", processName)
        for p in psutil.process_iter():
            cmdline = p.cmdline()
            if len(cmdline) > 0:
                if processName==cmdline[0]:
                    self.logger.info("findProcessPid:Found %s, pid %s" % (cmdline[0], p.pid))
                    return p.pid

        self.logger.info("findProcessPid: Did not find any process for name  %s", processName)
        return False

    #TODO: this can be rewritten using the findProcessPid Function
    def canDispatcherProcessStart(self, processName):
        timesStarted=0

        for p in psutil.process_iter():
            cmdline = p.cmdline()
            if len(cmdline) > 1:
                if processName==cmdline[0]:
                    timesStarted=timesStarted+1

        if timesStarted>1:
            return False
        else:
            return True


from api_db import *
from selenium.common.exceptions import NoSuchElementException
import urllib2
import traceback


class ExceptionHandler:
    def __init__(self, instapy, bot_type):
        self.instapy = instapy
        self.logger = instapy.logger
        self.bot_type = bot_type

    def handle(self, exc):
        exceptionDetail = traceback.format_exc()
        #print(exceptionDetail)

        if isinstance(exc, NoSuchElementException):
            self.logger.info("ExceptionHandler: IMPORTANT ERROR: NoSuchElementException -> maybe instagram changed their DOM again.")

            insert("INSERT INTO campaign_log (`id_campaign`, event, `details`, `timestamp`) VALUES (%s, %s, %s, now())", self.instapy.campaign['id_campaign'], "NO_SUCH_ELEMENT_EXCEPTION", exceptionDetail)
            urllib2.urlopen("https://rest.angie.one/email/sendBotException?type=NoSuchElementException&id_campaign=" + str(self.instapy.campaign['id_campaign'])).read()

        else:
            # TODO: I think this log catches our own exception, find a way to not log them in database as they are already logged. Or log them only once here ?
            insert("INSERT INTO campaign_log (`id_campaign`, event, `details`, `timestamp`) VALUES (%s, %s, %s, now())", self.instapy.campaign['id_campaign'], "RUNTIME_ERROR", exceptionDetail)

        self.logger.critical("start: FATAL ERROR for bot type: %s, stacktrace: %s" % (self.bot_type, exceptionDetail))
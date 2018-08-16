"""Module only used for the login part of the script"""
from .time_util import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from .util import update_activity
import pickle
import time
import api_db


def bypass_suspicious_login(browser):
    """Bypass suspicious loggin attempt verification. This should be only enabled
    when there isn't available cookie for the username, otherwise it will and
    shows "Unable to locate email or phone button" message, folollowed by
    CRITICAL - Wrong login data!"""
    # close sign up Instagram modal if available
    try:
        close_button = browser.find_element_by_xpath("[text()='Close']")
        ActionChains(
            browser).move_to_element(close_button).click().perform()
    except NoSuchElementException:
        pass

    try:
        # click on "This was me" button if challenge page was called
        this_was_me_button = browser.find_element_by_xpath(
            "//button[@name='choice'][text()='This Was Me']")
        ActionChains(
            browser).move_to_element(this_was_me_button).click().perform()
    except NoSuchElementException:
        # no verification needed
        pass

    try:
        user_email = browser.find_element_by_xpath(
            "//label[@for='choice_1']").text
    except NoSuchElementException:
        try:
            user_email = browser.find_element_by_xpath(
                "//label[@class='_q0nt5']").text
        except:
            try:
                user_email = browser.find_element_by_xpath(
                    "//label[@class='_q0nt5 _a7z3k']").text
            except:
                print("Unable to locate email or phone button, maybe "
                      "bypass_suspicious_login=True isn't needed anymore.")
                return False

    send_security_code_button = browser.find_element_by_xpath(
        ("//button[text()='Send Security Code']"))
    (ActionChains(browser)
     .move_to_element(send_security_code_button)
     .click()
     .perform())

    print('Instagram detected an unusual login attempt')
    print('A security code wast sent to your {}'.format(user_email))
    security_code = input('Type the security code here: ')

    security_code_field = browser.find_element_by_xpath((
        "//input[@id='security_code']"))
    (ActionChains(browser)
     .move_to_element(security_code_field)
     .click().send_keys(security_code).perform())

    submit_security_code_button = browser.find_element_by_xpath((
        "//button[text()='Submit']"))

    (ActionChains(browser)
     .move_to_element(submit_security_code_button)
     .click().perform())

    try:
        sleep(5)
        # locate wrong security code message
        wrong_login = browser.find_element_by_xpath((
            "//p[text()='Please check the code we sent you and try "
            "again.']"))
        if wrong_login is not None:
            print(('Wrong security code! Please check the code Instagram'
                   'sent you and try again.'))
    except NoSuchElementException:
        # correct security code
        pass


def login_user(browser,
               username,
               password,
               logfolder,
               switch_language=True,
               bypass_suspicious_attempt=False, logger=None):
    """Logins the user with the given username and password"""
    assert username, 'Username not provided'
    assert password, 'Password not provided'

    browser.get('https://www.instagram.com')
    # update server calls
    update_activity()
    cookie_loaded = False

    # try to load cookie from username
    try:
        browser.get('https://www.google.com')
        for cookie in pickle.load(open('{0}{1}_cookie.pkl'
                                       .format(logfolder,username), 'rb')):
            browser.add_cookie(cookie)
            cookie_loaded = True
    except (WebDriverException, OSError, IOError):
        logger.info("login_user: Cookie file not found, creating cookie...")

    # include time.sleep(1) to prevent getting stuck on google.com
    time.sleep(1)

    browser.get('https://www.instagram.com')
    # Cookie has been loaded, user should be logged in. Ensurue this is true
    login_elem = browser.find_elements_by_xpath(
        "//*[contains(text(), 'Log in')]")
    # Login text is not found, user logged in
    # If not, issue with cookie, create new cookie
    logger.info("login_user: Done searching for login_elem")
    if len(login_elem) == 0:
        logger.info("login_user: User logged in !")
        return True

    # If not, issue with cookie, create new cookie
    if cookie_loaded:
        logger.info("Issue with cookie for user " + username+ ". Creating new cookie...")

    # Changes instagram language to english, to ensure no errors ensue from
    # having the site on a different language
    # Might cause problems if the OS language is english
    if switch_language:
        browser.find_element_by_xpath(
          "//select[@class='hztqj']/option[text()='English']").click()

    # Check if the first div is 'Create an Account' or 'Log In'
    login_elem = browser.find_element_by_xpath(
        "//article/div/div/p/a[text()='Log in']")
    if login_elem is not None:
        ActionChains(browser).move_to_element(login_elem).click().perform()

    # Enter username and password and logs the user in
    # Sometimes the element name isn't 'Username' and 'Password'
    # (valid for placeholder too)
    sleep(1)
    input_username = browser.find_elements_by_xpath(
        "//input[@name='username']")

    ActionChains(browser).move_to_element(input_username[0]). \
        click().send_keys(username).perform()
    sleep(1)
    input_password = browser.find_elements_by_xpath(
        "//input[@name='password']")
    if not isinstance(password, str):
        password = str(password)
    ActionChains(browser).move_to_element(input_password[0]). \
        click().send_keys(password).perform()

    login_button = browser.find_element_by_xpath(
        "//form/span/button[text()='Log in']")
    ActionChains(browser).move_to_element(login_button).click().perform()
    # update server calls
    update_activity()

    if bypass_suspicious_attempt is True:
        bypass_suspicious_login(browser)
    print("login_user: Sleeping 5 seconds")
    sleep(5)

    # Check if user is logged-in (If there's two 'nav' elements)
    nav = browser.find_elements_by_xpath('//nav')
    if len(nav) == 2:
        # create cookie for username
        pickle.dump(browser.get_cookies(),
                    open('{0}{1}_cookie.pkl'.format(logfolder,username), 'wb'))
        return True
    else:
        return False


def custom_login_user(browser,
               username,
               password,
               logfolder,
               switch_language=True,
               bypass_suspicious_attempt=False, logger=None, cmp=None, force_login=False):
    """Logins the user with the given username and password"""
    assert username, 'Username not provided'
    assert password, 'Password not provided'

    #browser.get('https://www.instagram.com')
    # update server calls
    #update_activity()
    cookie_loaded = False
    logger.info("custom_login_user: Trying to login...")

    if force_login is not True:
        # try to load cookie from username
        try:
            #logger.info("login_user: Accesing google to get the cookie...")
            #browser.get('https://www.google.com')
            for cookie in pickle.load(open('{0}{1}_cookie.pkl'
                                           .format(logfolder,username), 'rb')):
                browser.add_cookie(cookie)
                cookie_loaded = True
        except (WebDriverException, OSError, IOError):
            logger.info("custom_login_user: Cookie file not found. Going to manually login...")

    #logger.info("SLeeping 1 second to prevent getting stuck on google.com")
    # include time.sleep(1) to prevent getting stuck on google.com
    #time.sleep(1)

    if cookie_loaded==True:
        logger.info("custom_login_user: Cookie was loaded, going to check if user is automatically logged in...")
        logger.info("custom_login_user: Accessing https://www.instagram.com/ too  see if user is logged in.")
        browser.get("https://www.instagram.com/")
        sleep(1)
        if is_user_logged_in(username, browser, logger, cmp, force_login)==True:
            logger.info("custom_login_user: The user was successfully logged in...")
            return True
        else:
            logger.info("custom_login_user: The user was not automatically logged in. Maybe error with the cookie ?. Going to manually login...")
            return execute_login(username, password, browser, switch_language, bypass_suspicious_attempt, logger, logfolder, cmp, force_login)

    return execute_login(username, password, browser, switch_language, bypass_suspicious_attempt, logger, logfolder, cmp, force_login)


def execute_login(username, password, browser,switch_language,bypass_suspicious_attempt, logger, logfolder, cmp, force_login=False):
    # Changes instagram language to english, to ensure no errors ensue from
    # having the site on a different language
    # Might cause problems if the OS language is english

    logger.info("execute_login: Started login process... going to open instagram login page")

    browser.get("https://www.instagram.com/accounts/login/")
    #not sure if this is needed in our use cases
    #if switch_language:
    #    browser.find_element_by_xpath(
    #      "//select[@class='hztqj']/option[text()='English']").click()


    logger.info("execute_login: Going to fill in username and password.")
    # Enter username and password and logs the user in
    # Sometimes the element name isn't 'Username' and 'Password'
    # (valid for placeholder too)
    #sleep(2)
    input_username = browser.find_elements_by_xpath(
        "//input[@name='username']")

    ActionChains(browser).move_to_element(input_username[0]). \
        click().send_keys(username).perform()
    time.sleep(0.3)
    input_password = browser.find_elements_by_xpath(
        "//input[@name='password']")
    if not isinstance(password, str):
        password = str(password)
    ActionChains(browser).move_to_element(input_password[0]). \
        click().send_keys(password).perform()

    logger.info("execute_login: Done... going to click log in button")

    login_button = browser.find_element_by_xpath(
        "//form/span/button[text()='Log in']")
    ActionChains(browser).move_to_element(login_button).click().perform()



    if bypass_suspicious_attempt is True:
        logger.info("execute_login: Bypass_suspicious_attempt is true...")
        bypass_suspicious_login(browser)

    if force_login is not True:
        logger.info("execute_login: Sleeping 1 second")
        sleep(1)

    if is_user_logged_in(username, browser, logger, cmp, force_login)==True:
        # create cookie for username
        logger.info("execute_login: Login was successfully. Going to create the cookie")
        pickle.dump(browser.get_cookies(), open('{0}{1}_cookie.pkl'.format(logfolder, username), 'wb'))
        return True

    return False



def is_user_logged_in(username, browser, logger, cmp, force_login=False):

    logger.info("is_user_logged_in: Checking if user %s is logged in by searching for Profile Button...", username)

    edit_profile_button = browser.find_elements_by_xpath("//a[text()='Profile']")

    logger.info("is_user_logged_in: Done searching for  Profile button !")

    if len(edit_profile_button) == 0:
        logger.info("is_user_logged_in: Profile button was NOT found, going to assume user is not logged in. Going to check for login issues...")
        find_login_issues(browser, logger, cmp, force_login)
        return False
    else:
        logger.info("is_user_logged_in: Profile button was found... user succesffully LOGGED IN")
        return True

def find_login_issues(browser, logger, cmp, force_login=False):
    logger.info("find_login_issues: Starting to detect login issues...")

    #CHECK INVALID CREDENTIALS
    check_invalid_credentials(browser, logger, cmp, force_login)

    #CHECK FOR PHONE VALIDATION
    check_phone_verification(browser, logger, cmp, force_login)

    #CHECK IF INSTAGRAM DETECTED UNSUAL LOGIN ATTEMPT
    check_unusual_login_attempt(browser, logger, cmp, force_login)

    logger.info("find_login_issues: I couldn't detect why you can't login... :(")

def check_invalid_credentials(browser, logger, campaign, force_login=False):
    # CHECK FOR INVALID CREDENTIALS
    invalidCredentials = browser.find_elements_by_xpath("//p[contains(text(), 'password was incorrect')]")
    if len(invalidCredentials) > 0:
        logger.info("find_login_issues: Invalid credentials")
        api_db.insert(
            "INSERT INTO `instagram_log` (`id_user`, `log`, `operation`, `details`, `timestamp`) VALUES (%s, %s, %s, %s, now())",
            campaign['id_user'], "INVALID_CREDENTIALS", "login", "login_error")

        if force_login is not True:
            logger.info("Going to send an email to the user.")
            browser.get('https://rest.angie.one/email/notifyUserInvalidCredentials?id='+str(campaign['id_user']))

        raise Exception("INVALID_CREDENTIALS")
    return True



def check_phone_verification(browser, logger, campaign, force_login=False):
    instagramWantsToConfirmPhoneNumber = browser.find_elements_by_xpath("//h2[contains(text(), 'Phone')]")

    if len(instagramWantsToConfirmPhoneNumber) > 0:
        logger.info("find_login_issues: Instagram wants to verify the phone number, ask user for input")
        api_db.insert(
            "INSERT INTO `instagram_log` (`id_user`, `log`, `operation`, `details`, `timestamp`) VALUES (%s, %s, %s, %s, now())",
            campaign['id_user'], "ADD_PHONE_NUMBER", "login", "login_error")
        if force_login is not True:
            logger.info("Going to send an email to the user.")
            browser.get('https://rest.angie.one/email/notifyUserConfirmPhoneNumber?id=' + str(campaign['id_user']))
        raise Exception("ADD_PHONE_NUMBER")

def check_unusual_login_attempt(browser, logger,campaign, force_login=False):

    unusualAttempt = browser.find_elements_by_xpath("//h2[contains(text(), 'We Detected An Unusual Login Attempt')]")

    if len(unusualAttempt) > 0:
        logger.info("find_login_issues: Instagram wants to verify the phone number, ask user for input")
        api_db.insert(
            "INSERT INTO `instagram_log` (`id_user`, `log`, `operation`, `details`, `timestamp`) VALUES (%s, %s, %s, %s, now())",
            campaign['id_user'], "UNUSUAL_LOGIN_ATTEMPT", "login", "login_error")

        if force_login is not True:
            logger.info("Going to send an email to the user.")
            browser.get('https://rest.angie.one/email/notifyUserUnusualLoginAttempt?id=' + str(campaign['id_user']))
        raise Exception("UNUSUAL_LOGIN_ATTEMPT")



def isLogginAllowed(campaign, logger):
    logger.info("canBotStart: Checking if bot can start...")
    result = api_db.fetchOne("select count(*) as total_login_failures from instagram_log where date(timestamp)=CURDATE() and id_user=%s and details=%s", campaign['id_user'], "login_error")

    if result['total_login_failures']>1:
        logger.error("canBotStart: BOT CANNOT START, login failures: %s", result['total_login_failures'])
        raise Exception("BOT CANNOT START, too many login failures.")

    logger.error("canBotStart: Bot can start login failures: %s. Maximum amount is 2", result['total_login_failures'])
    return True
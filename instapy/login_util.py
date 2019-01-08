"""Module only used for the login part of the script"""
import time
import pickle
from selenium.webdriver.common.action_chains import ActionChains

from .time_util import sleep
from .util import update_activity
from .util import web_address_navigator
from .util import explicit_wait
from .util import click_element

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from .util import update_activity
import pickle
import time
import api_db
import login_issues


def bypass_suspicious_login(browser):
    """Bypass suspicious loggin attempt verification. This should be only enabled
    when there isn't available cookie for the username, otherwise it will and
    shows "Unable to locate email or phone button" message, folollowed by
    CRITICAL - Wrong login data!"""
    # close sign up Instagram modal if available
    try:
        close_button = browser.find_element_by_xpath("[text()='Close']")

        (ActionChains(browser)
         .move_to_element(close_button)
         .click()
         .perform())

        # update server calls
        update_activity()

    except NoSuchElementException:
        pass

    try:
        # click on "This was me" button if challenge page was called
        this_was_me_button = browser.find_element_by_xpath(
            "//button[@name='choice'][text()='This Was Me']")

        (ActionChains(browser)
         .move_to_element(this_was_me_button)
         .click()
         .perform())

        # update server calls
        update_activity()

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
        "//button[text()='Send Security Code']")

    (ActionChains(browser)
     .move_to_element(send_security_code_button)
     .click()
     .perform())

    # update server calls
    update_activity()

    print('Instagram detected an unusual login attempt')
    print('A security code was sent to your {}'.format(user_email))
    security_code = input('Type the security code here: ')

    security_code_field = browser.find_element_by_xpath((
        "//input[@id='security_code']"))

    (ActionChains(browser)
     .move_to_element(security_code_field)
     .click()
     .send_keys(security_code)
     .perform())

    # update server calls for both 'click' and 'send_keys' actions
    for i in range(2):
        update_activity()

    submit_security_code_button = browser.find_element_by_xpath(
        "//button[text()='Submit']")

    (ActionChains(browser)
     .move_to_element(submit_security_code_button)
     .click()
     .perform())

    # update server calls
    update_activity()

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

    ig_homepage = "https://www.instagram.com"
    web_address_navigator(browser, ig_homepage)
    cookie_loaded = False

    # try to load cookie from username
    try:
        googledotcom = "https://www.google.com"
        web_address_navigator(browser, googledotcom)
        for cookie in pickle.load(open('{0}{1}_cookie.pkl'
                                               .format(logfolder, username), 'rb')):
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
        logger.info("Issue with cookie for user " + username + ". Creating new cookie...")

    # Changes instagram language to english, to ensure no errors ensue from
    # having the site on a different language
    # Might cause problems if the OS language is english
    if switch_language:
        language_element_ENG = browser.find_element_by_xpath(
            "//select[@class='hztqj']/option[text()='English']")
        click_element(browser, language_element_ENG)

    # Check if the first div is 'Create an Account' or 'Log In'
    login_elem = browser.find_element_by_xpath(
        "//article/div/div/p/a[text()='Log in']")

    if login_elem is not None:
        (ActionChains(browser)
         .move_to_element(login_elem)
         .click()
         .perform())

        # update server calls
        update_activity()

    # Enter username and password and logs the user in
    # Sometimes the element name isn't 'Username' and 'Password'
    # (valid for placeholder too)

    # wait until it navigates to the login page
    login_page_title = "Login"
    explicit_wait(browser, "TC", login_page_title, logger)

    # wait until the 'username' input element is located and visible
    input_username_XP = "//input[@name='username']"
    explicit_wait(browser, "VOEL", [input_username_XP, "XPath"], logger)

    input_username = browser.find_element_by_xpath(input_username_XP)

    (ActionChains(browser)
     .move_to_element(input_username)
     .click()
     .send_keys(username)
     .perform())

    # update server calls for both 'click' and 'send_keys' actions
    for i in range(2):
        update_activity()

    sleep(1)

    #  password
    input_password = browser.find_elements_by_xpath(
        "//input[@name='password']")

    if not isinstance(password, str):
        password = str(password)

    (ActionChains(browser)
     .move_to_element(input_password[0])
     .click()
     .send_keys(password)
     .perform())

    # update server calls for both 'click' and 'send_keys' actions
    for i in range(2):
        update_activity()

    login_button = browser.find_element_by_xpath(
        "//button[text()='Log in']")

    (ActionChains(browser)
     .move_to_element(login_button)
     .click()
     .perform())

    # update server calls
    update_activity()

    dismiss_get_app_offer(browser, logger)

    if bypass_suspicious_attempt is True:
        bypass_suspicious_login(browser)
    print("login_user: Sleeping 5 seconds")
    sleep(5)

    # Check if user is logged-in (If there's two 'nav' elements)
    nav = browser.find_elements_by_xpath('//nav')
    if len(nav) == 2:
        # create cookie for username
        pickle.dump(browser.get_cookies(),
                    open('{0}{1}_cookie.pkl'.format(logfolder, username), 'wb'))
        return True
    else:
        return False


def dismiss_get_app_offer(browser, logger):
    """ Dismiss 'Get the Instagram App' page after a fresh login """
    offer_elem = "//*[contains(text(), 'Get App')]"
    dismiss_elem = "//*[contains(text(), 'Not Now')]"

    # wait a bit and see if the 'Get App' offer rises up
    offer_loaded = explicit_wait(browser, "VOEL", [offer_elem, "XPath"], logger, 5, False)

    if offer_loaded:
        dismiss_elem = browser.find_element_by_xpath(dismiss_elem)
        click_element(browser, dismiss_elem)

def connect_with_instagram(browser,
                      username,
                      password,
                      logfolder,
                      switch_language=True,
                      bypass_suspicious_attempt=False, logger=None, cmp=None, unusual_login_token=None, two_factor_auth_token=None):

    logger.info("connect_with_instagram: Trying to connect with instagram ...")

    status = execute_login(username, password, browser, switch_language, bypass_suspicious_attempt, logger, logfolder,cmp)

    if status is True:
        # create cookie
        logger.info("connect_with_instagram: Login was successfully. Going to create the cookie")
        pickle.dump(browser.get_cookies(), open('{0}{1}_cookie.pkl'.format(logfolder, username), 'wb'))
        return True
    else:
        logger.info("connect_with_instagram: Failed, going to detect login issues")
        login_issue = find_login_issues(browser, logger, cmp)

        if login_issue == login_issues.UNUSUAL_LOGIN_ATTEMPT:
            return handle_unusual_login_attempt(browser, username, logger, logfolder, cmp, unusual_login_token)

        elif login_issue == login_issues.TWOFACTOR_PHONE_CODE_VERIFICATION:
            return handle_two_factor_login_attempt(browser, username, logger, logfolder, cmp, two_factor_auth_token)
        else:
            raise Exception(login_issue)

def handle_two_factor_login_attempt(browser, username, logger, logfolder, cmp, two_factor_auth_token=None):

    logger.info("handle_two_factor_login_attempt: Going to handle two factor login...")


    if two_factor_auth_token is None:
        logger.info("handle_two_factor_login_attempt: Token is missing, going to raise the exception.")

        raise Exception(login_issues.TWOFACTOR_PHONE_CODE_VERIFICATION)

    logger.info("handle_two_factor_login_attempt: Going to test the token provided by user: %s", two_factor_auth_token)

    input = browser.find_elements_by_xpath("//input")[0]
    input.click()
    input.send_keys(two_factor_auth_token)
    browser.find_elements_by_xpath("//button[contains(text(), 'Confirm')]")[0].click()
    logger.info("handle_two_factor_login_attempt: Sleeping 2 seconds for instagram response.")
    time.sleep(2)

    errorMessageList = browser.find_elements_by_xpath("//p[contains(text(), 'Please check the security code')]")

    if len(errorMessageList) > 0:
        logger.info("handle_two_factor_login_attempt: 2Factor token is invalid: %s", two_factor_auth_token)
        raise Exception(login_issues.INVALID_2FACTOR_LOGIN_TOKEN)
    else:
        logger.info("handle_two_factor_login_attempt: check if user is logged in")
        loggedIn = is_user_logged_in(username, browser, logger, cmp)
        if loggedIn is True:
            # create cookie
            logger.info("handle_two_factor_login_attempt: Login was successfully. Going to create the cookie")
            pickle.dump(browser.get_cookies(), open('{0}{1}_cookie.pkl'.format(logfolder, username), 'wb'))
            return True
        else:
            logger.info("handle_two_factor_login_attempt: User is still not logged in after inserting the 2factor login token: %s", two_factor_auth_token)
            raise Exception(login_issues.UNKNOWN_LOGIN_ISSUE)




def handle_unusual_login_attempt(browser, username, logger, logfolder, cmp, unusual_login_token=None):
    logger.info("handle_unusual_login_attempt: Going to generate a new security token for unusual login.")
    sendCodeButtonList = browser.find_elements_by_xpath("//button[contains(text(), 'Send Security Code')]")

    sendCodeButtonList[0].click()
    time.sleep(2)

    if unusual_login_token is None:
        logger.info("handle_unusual_login_attempt: token is not provided, going to return...")
        raise Exception(login_issues.UNUSUAL_LOGIN_ATTEMPT)

    logger.info("Going to fill in the unusual_login_token: %s", unusual_login_token)
    tokenInput = browser.find_elements_by_xpath("//input")[0]
    tokenInput.click()
    tokenInput.send_keys(unusual_login_token)
    browser.find_elements_by_xpath("//button[contains(text(), 'Submit')]")[0].click()
    time.sleep(3)

    errorMessageList = browser.find_elements_by_xpath("//p[contains(text(), 'Please check the code we sent')]")
    if len(errorMessageList) > 0:
        logger.info("handle_unusual_login_attempt: Unusual token is invalid: %s", unusual_login_token)
        raise Exception(login_issues.INVALID_UNUSUAL_LOGIN_TOKEN)

    else:
        logger.info("handle_unusual_login_attempt: check if user is logged in")
        loggedIn = is_user_logged_in(username, browser, logger, cmp)
        if loggedIn is True:
            # create cookie
            logger.info("handle_unusual_login_attempt: Login was successfully. Going to create the cookie")
            pickle.dump(browser.get_cookies(), open('{0}{1}_cookie.pkl'.format(logfolder, username), 'wb'))
            return True
        else:
            logger.info("handle_unusual_login_attempt: User is still not logged in after inserting the unusual login token: %s", unusual_login_token)
            raise Exception(login_issues.UNKNOWN_LOGIN_ISSUE)

def custom_login_user(browser,
                      username,
                      password,
                      logfolder,
                      switch_language=True,
                      bypass_suspicious_attempt=False, logger=None, cmp=None, force_login=False):
    """Logins the user with the given username and password"""
    assert username, 'Username not provided'
    assert password, 'Password not provided'

    # browser.get('https://www.instagram.com')
    # update server calls
    # update_activity()
    cookie_loaded = False
    logger.info("custom_login_user: Trying to login, force login is: %s...", force_login)

    if force_login is not True:
        # try to load cookie from username
        try:
            # logger.info("login_user: Accesing google to get the cookie...")
            # browser.get('https://www.google.com')
            for cookie in pickle.load(open('{0}{1}_cookie.pkl'
                                                   .format(logfolder, username), 'rb')):
                browser.add_cookie(cookie)
                cookie_loaded = True
        except (WebDriverException, OSError, IOError):
            logger.info("custom_login_user: Cookie file not found. Going to manually login...")

    # logger.info("SLeeping 1 second to prevent getting stuck on google.com")
    # include time.sleep(1) to prevent getting stuck on google.com
    # time.sleep(1)

    if cookie_loaded == True:
        logger.info("custom_login_user: Cookie was loaded, going to check if user is automatically logged in...")
        logger.info("custom_login_user: Accessing https://www.instagram.com/ too  see if user is logged in.")
        browser.get("https://www.instagram.com/")
        sleep(1)

        # check if user was automatically logged in after cookie was loaded
        if is_user_logged_in(username, browser, logger, cmp) == True:
            logger.info("custom_login_user: The user was successfully logged in...")
            return True
        else:
            logger.info(
                "custom_login_user: The user was not automatically logged in. Maybe error with the cookie ?. Going to manually login...")

    status = execute_login(username, password, browser, switch_language, bypass_suspicious_attempt, logger, logfolder,cmp)

    if status is True:
        # create cookie
        logger.info("custom_login_user: Login was successfully. Going to create the cookie")
        pickle.dump(browser.get_cookies(), open('{0}{1}_cookie.pkl'.format(logfolder, username), 'wb'))
        return True
    else:
        logger.info("custom_login_user: Failed, going to detect login issues")
        issue = find_login_issues(browser, logger, cmp)
        handle_login_issue(browser, cmp, issue, logger)

    return False


def execute_login(username, password, browser, switch_language, bypass_suspicious_attempt, logger, logfolder, cmp):
    # Changes instagram language to english, to ensure no errors ensue from
    # having the site on a different language
    # Might cause problems if the OS language is english

    logger.info("execute_login: Started login process... going to open instagram login page")

    browser.get("https://www.instagram.com/accounts/login/")
    # not sure if this is needed in our use cases
    # if switch_language:
    #    browser.find_element_by_xpath(
    #      "//select[@class='hztqj']/option[text()='English']").click()

    logger.info("execute_login: Going to fill in username and password.")
    # Enter username and password and logs the user in
    # Sometimes the element name isn't 'Username' and 'Password'
    # (valid for placeholder too)
    # sleep(2)
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
        "//button[text()='Log in']")

    (ActionChains(browser)
     .move_to_element(login_button)
     .click()
     .perform())

    return is_user_logged_in(username, browser, logger, cmp)


def bypass_two_auth(browser, twoFactorRecoveryCode, logger):
    logger.info("Going to bypass two factor auth using code: %s", twoFactorRecoveryCode)
    # todo: enter the code into instagram input and click OK.


def is_user_logged_in(username, browser, logger, cmp):
    check_it_was_me_popup(browser, logger, cmp)
    logger.info("is_user_logged_in: Checking if user %s is logged in by searching for Profile Button...", username)

    edit_profile_button = browser.find_elements_by_xpath("//a[contains(@href,'" + username + "')]")

    logger.info("is_user_logged_in: Done searching for  Profile button !")

    if len(edit_profile_button) == 0:
        logger.info("is_user_logged_in: Profile button was NOT found, going to assume user is not logged in")
        return False
    else:
        logger.info("is_user_logged_in: Profile button was found... user succesffully LOGGED IN")
        return True


# this is not actually an error. Instagram shows a popup asking about a previous login. Just click this was me and continue with the normal flow.
def check_it_was_me_popup(browser, logger, cmp):
    buttons = browser.find_elements_by_xpath("//button[contains(text(), 'This Was Me')]")
    if len(buttons) > 0:
        logger.info("check_it_was_me_popup: It was me popup is true, going to click 'This was me' to hide it !")
        buttons[0].click()

    return True



def handle_login_issue(browser, campaign, login_issue, logger):
    logger.info("handle_login_issue: Going to handle login issue: %s", login_issue)

    if login_issue == login_issues.INVALID_CREDENTIALS:
        logger.info("Going to send an email to the user.")
        browser.get('https://rest.angie.one/email/notifyUserInvalidCredentials?id=' + str(campaign['id_user']))
        raise Exception(login_issue)

    elif login_issue == login_issues.ADD_PHONE_NUMBER:
        logger.info("Going to send an email to the user.")
        browser.get('https://rest.angie.one/email/notifyUserConfirmPhoneNumber?id=' + str(campaign['id_user']))
        raise Exception(login_issue)

    elif login_issue == login_issues.TWOFACTOR_PHONE_CODE_VERIFICATION:
        logger.info("Going to send an email to the user.")
        browser.get('https://rest.angie.one/email/notifyUserTwoFactorAuthentication?id=' + str(campaign['id_user']))
        raise Exception(login_issue)

    elif login_issue == login_issues.UNUSUAL_LOGIN_ATTEMPT:
        logger.info("Going to send an email to the user.")
        browser.get('https://rest.angie.one/email/notifyUserUnusualLoginAttempt?id=' + str(campaign['id_user']))
        raise Exception(login_issue)

    else:
        logger.info("handle_login_issue: Could not handle/detect login issue with value: %s", login_issue)
        api_db.insert("INSERT INTO campaign_log (`id_campaign`, event, `details`, `timestamp`) VALUES (%s, %s, %s, now())",campaign['id_campaign'], "UNSUCCESSFUL_LOGIN_NO_REASON", "login_error")
        raise Exception(login_issues.UNKNOWN_LOGIN_ISSUE)



def find_login_issues(browser, logger, cmp):
    logger.info("find_login_issues: Starting to detect login issues...")

    path = "/home/instapy-log/campaign/logs/" + str(cmp['id_campaign']) + "/" + time.strftime(
        "%d.%m.%Y.%H.%M.%S") + ".png"
    browser.get_screenshot_as_file(path)
    logger.info("find_login_issues: Done saving a print screen with the issue. location: %s", path)

    logger.info("find_login_issues: Going to detect the loggin issue...")

    # CHECK INVALID CREDENTIALS
    status = check_invalid_credentials(browser, logger, cmp)
    if status is not False:
        return status

    # CHECK IF INSTAGRAM DETECTED UNSUAL LOGIN ATTEMPT
    status = check_unusual_login_attempt(browser, logger, cmp)
    if status is not False:
        return status

    # CHECK INSTAGRAM USERNAME
    status = check_invalid_username(browser, logger, cmp)
    if status is not False:
        return status

    # INSTAGRAM ASKINF FOR USER'S PHOEN NUMBER
    status = check_phone_verification(browser, logger, cmp)
    if status is not False:
        return status

    status = check_phone_code_verification_2auth(browser, logger, cmp)
    if status is not False:
        return status

    logger.info("find_login_issues: I couldn't detect why you can't login... :(")


    return False




def check_phone_code_verification_2auth(browser, logger, campaign):
    #maybe the selector for 2factor auth is not that good
    phoneCodeVerification = browser.find_elements_by_xpath("//div[contains(text(), 'Enter the code we sent')]")
    if len(phoneCodeVerification) > 0:
        logger.info("check_phone_code_verification_2auth: Instagram requires phone code verification for 2 factor login")

        api_db.insert("INSERT INTO `campaign_log` (`id_campaign`, `event`, `details`, `timestamp`) VALUES (%s, %s, %s, now())",campaign['id_campaign'], login_issues.TWOFACTOR_PHONE_CODE_VERIFICATION, "login_error")
        return login_issues.TWOFACTOR_PHONE_CODE_VERIFICATION

    return False


def check_invalid_username(browser, logger, campaign):
    # CHECK FOR INVALID CREDENTIALS
    invalidCredentials = browser.find_elements_by_xpath("//p[contains(text(), 'Please check your username')]")
    if len(invalidCredentials) > 0:
        logger.info("find_login_issues: Invalid username")

        api_db.insert("INSERT INTO `campaign_log` (`id_campaign`, `event`, `details`, `timestamp`) VALUES (%s, %s, %s, now())",campaign['id_campaign'], "INVALID_CREDENTIALS", "login_error")
        return login_issues.INVALID_CREDENTIALS

    return False


def check_invalid_credentials(browser, logger, campaign):
    # CHECK FOR INVALID CREDENTIALS
    invalidCredentials = browser.find_elements_by_xpath("//p[contains(text(), 'password was incorrect')]")
    if len(invalidCredentials) > 0:
        logger.info("find_login_issues: Invalid credentials")

        api_db.insert("INSERT INTO `campaign_log` (`id_campaign`, `event`, `details`, `timestamp`) VALUES (%s, %s, %s, now())",campaign['id_campaign'], login_issues.INVALID_CREDENTIALS, "login_error")
        return login_issues.INVALID_CREDENTIALS

    return False


# instagram asking for user phone number
def check_phone_verification(browser, logger, campaign):
    instagramWantsToConfirmPhoneNumber = browser.find_elements_by_xpath("//h2[contains(text(), 'Phone')]")
    if len(instagramWantsToConfirmPhoneNumber) > 0:
        logger.info("find_login_issues: Instagram wants to verify the phone number, ask user for input")
        api_db.insert("INSERT INTO `campaign_log` (`id_campaign`, `event`, `details`, `timestamp`) VALUES (%s, %s, %s, now())",campaign['id_campaign'], login_issues.ADD_PHONE_NUMBER, "login_error")
        return login_issues.ADD_PHONE_NUMBER

    return False

# todo: a complex scenario is when instagram asks for verification code and then asks for oauth code. -> after first is inserted nothing happens(logged out)
def check_unusual_login_attempt(browser, logger, campaign):
    unusualAttempt = browser.find_elements_by_xpath("//h2[contains(text(), 'We Detected An Unusual Login Attempt')]")

    if len(unusualAttempt) > 0:
        logger.info(
            "find_login_issues: Instagram detected an unsual login attempt.")
        api_db.insert("INSERT INTO `campaign_log` (`id_campaign`, `event`, `details`, `timestamp`) VALUES (%s, %s, %s, now())",campaign['id_campaign'], login_issues.UNUSUAL_LOGIN_ATTEMPT, "login_error")

        return login_issues.UNUSUAL_LOGIN_ATTEMPT

    return False



def isLogginAllowed(campaign, force_login, logger):
    if force_login == True:
        return True

    logger.info("canBotStart: Checking if bot can start...")
    result = api_db.fetchOne(
        "select count(*) as total_login_failures from campaign_log where date(timestamp)=CURDATE() and id_campaign=%s and details=%s",
        campaign['id_campaign'], "login_error")

    if result['total_login_failures'] > 2:
        logger.error("canBotStart: BOT CANNOT START, login failures: %s", result['total_login_failures'])
        raise Exception("BOT CANNOT START, too many login failures.")

    logger.error("canBotStart: Bot can start login failures: %s. Maximum amount is 2", result['total_login_failures'])
    return True

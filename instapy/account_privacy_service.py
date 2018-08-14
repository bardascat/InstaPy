class AccountPrivacyService:
    def __init__(self, instapy):
        self.instapy = instapy
        self.logger = instapy.logger

    def isAccountPrivate(self):
        self.logger.info("getAccountPrivacy: Getting privacy status for account: %s", self.instapy.campaign['username'])
        self.instapy.browser.get("https://www.instagram.com/accounts/privacy_and_security")

        checkboxValue = self.instapy.browser\
            .find_element_by_xpath("//h2[contains(text(), 'Account Privacy')]")\
            .find_element_by_xpath('..')\
            .find_element_by_tag_name("input")\
            .get_attribute("checked")

        return checkboxValue == "true"

    def switchToPublic(self):
        isAccountPrivateBool = self.isAccountPrivate()

        if isAccountPrivateBool==False:
            self.logger.info("switchToPublic: The privacy for this account is already set to public. Going to return...")
            return False

        self.logger.info("switchToPublic: Going to switch account to public privacy")

        self.instapy.browser\
            .find_element_by_xpath("//h2[contains(text(), 'Account Privacy')]")\
            .find_element_by_xpath('..')\
            .find_element_by_xpath(".//label[contains(text(), 'Private Account')]")\
            .click()

        okayButton = self.instapy.browser.find_element_by_xpath("//h3[contains(text(), 'Change Privacy')]").find_element_by_xpath("//button[contains(text(), 'Okay')]")

        okayButton.click()

        self.logger.info("switchToPublic: Done switching account to public... returning...")

        self.instapy.browser.get("https://instagram.com")
        return True


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType

chrome_options = Options()
# chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--mute-audio")
chrome_options.add_argument('--dns-prefetch-disable')
chrome_options.add_argument('--lang=en-US')
chrome_options.add_argument('--disable-setuid-sandbox')
chrome_options.add_argument('--disable-plugins')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--enable-logging --v=1')
chrome_options.add_argument('--log-path=/home/ubuntut/chromedriver.log')

#chrome_options.add_argument('--headless')
#chrome_options.add_argument('--no-sandbox')

chromedriver_location='/Users/cbardas/instapy-log/assets/chromedriver'

browser = webdriver.Chrome(chromedriver_location,chrome_options=chrome_options)

browser.get("http://google.ro")
browser.get("https://serverfault.com/questions/305524/memory-usage-by-bytes-top-10")
browser.get("https://www.instagram.com/p/BvPK32FFxbz/")
browser.get("https://www.instagram.com/p/BvPK32FFxbz2/")
browser.get("https://www.instagram.com/p/BvPK32FFxb4/")
browser.get("https://www.instagram.com/p/BvPK32FFxbz5/")
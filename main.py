from selenium import webdriver
from time import sleep
from json import loads as json
import logging
from os import getenv
from sys import exit
from datetime import timedelta, datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as cond

def convertToSec(timestr):
    timeSuffix = timestr[-1]
    if timeSuffix == 's':
        seconds = float(timestr[:-1])
    elif timeSuffix == 'm':
        seconds = float(timestr[:-1]) * 60
    elif timeSuffix == 'h':
        seconds = float(timestr[:-1]) * 60**2
    elif timeSuffix == 'd':
        seconds = float(timestr[:-1]) * 60**2 * 24
    else:
        print('Failed format for sleeptime. Use "s/m/h/d"')
        exit(1)
    return seconds

usernames = json(getenv('usernames', '[]'))
passwords = json(getenv('passwords', '[]'))
sleeptime = convertToSec(getenv('sleeptime', '1d'))
if getenv("debug", 'False').lower() in ('true', '1', 't'):
    debug = True
else:
    debug = False

logger = logging.getLogger(__name__)
# Set the logging level to INFO
if debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
# Create a handler that logs to the Docker logs
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

logger.info("Spotify auto-login service was started")

i = 0
retry = 0

while(True):
    if i>=len(usernames):
        i = 0
        logger.info("All tasks is done, sleeping for " + getenv('sleeptime', '1d') + ". Next startup is planned on " + str(datetime.now() + timedelta(seconds=sleeptime)) )
        sleep(sleeptime)
    else:
        user_data_dir = getenv('profiles_dir', "/src/profiles/") + usernames[i]
        options = Options()
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-crash-reporter")
        options.add_argument("--disable-oopr-debug-crash-dump")
        options.add_argument("--no-crash-upload")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-low-res-tiling")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless')
        options.add_argument('--start-maximized')
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--use-file-for-fake-audio-capture=/src/profiles/hello.wav')
        options.set_capability("ignoreDefaultArgs", ["--mute-audio"])
        options.add_argument("--user-data-dir={}".format(user_data_dir))
        # Use this if you need to have multiple profiles
        options.add_argument('--profile-directory=Default')
        if debug:
            logger.debug("WARNING! Debug mode is enabled! NOT for production. Listen on 0.0.0.0:9222")
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument('--remote-debugging-address=0.0.0.0')
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2}
        )
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()

        try:
            try:
                driver.get("https://accounts.spotify.com/en/login?continue=https:%2F%2Faccounts.spotify.com%2Fen%2Fstatus%2F")
                if debug: sleep(180)
                WebDriverWait(driver,30).until(cond.presence_of_element_located((By.CSS_SELECTOR, "div.sc-ezOQGI")))
                logger.info(driver.title)
                logger.info (driver.find_element(By.CSS_SELECTOR, "div.sc-ezOQGI").text + " " + driver.find_element(By.CSS_SELECTOR, "div.sc-ezOQGI:nth-child(3)").text)
                sleep(10)
                driver.find_element(By.XPATH, '//button[@data-testid="web-player-link"]').send_keys(Keys.ENTER)
                sleep(30)
                driver.close()
                driver.quit()
                sleep(30)
                i += 1
            except:
                if retry==1:
                    driver.get("https://accounts.spotify.com/en/login?continue=https:%2F%2Fopen.spotify.com")
                elif retry==2:
                    driver.get("https://accounts.spotify.com/ru/login?continue=https%3A%2F%2Fwww.spotify.com%2Fus%2Fabout-us%2Fcontact%2F%3F")
                else:
                    driver.get("https://accounts.spotify.com/en/login?continue=https:%2F%2Faccounts.spotify.com%2Fen%2Fstatus%2F")
                WebDriverWait(driver,30).until(cond.presence_of_element_located((By.ID, "login-password")))
                WebDriverWait(driver,30).until(cond.presence_of_element_located((By.ID, "login-username")))
                username_field = driver.find_element(By.ID, "login-username")
                username_field.clear()
                username_field.send_keys(usernames[i])

                password_field = driver.find_element(By.ID, "login-password")
                password_field.clear()
                password_field.send_keys(passwords[i])

                driver.find_element(By.ID, "login-button").send_keys(Keys.ENTER)

                WebDriverWait(driver,30).until(cond.presence_of_element_located((By.CSS_SELECTOR, "div.sc-ezOQGI")))
                logger.info(driver.title)
                logger.info (driver.find_element(By.CSS_SELECTOR, "div.sc-ezOQGI").text + " " + driver.find_element(By.CSS_SELECTOR, "div.sc-ezOQGI:nth-child(3)").text)
                driver.find_element(By.XPATH, '//button[@data-testid="web-player-link"]').send_keys(Keys.ENTER)
                sleep(30)
                driver.close()
                driver.quit()
                sleep(30)
                i += 1

        except:
            logger.exception("Auth error")
            logger.info(driver.title)
            logger.info("Retrying with " + usernames[i])
            logger.debug(driver.find_element(By.TAG_NAME, "body").text)
            driver.close()
            driver.quit()
            sleep(30)
            retry += 1
            if retry>=int(getenv('retries', "10")):
                retry=0
                logger.warning("Too many retries with " + usernames[i] + ". Give up")
                i += 1

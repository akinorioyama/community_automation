# -*- coding: utf-8 -*-
import configparser

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException
from time import sleep
import os
from retry import retry

config = configparser.ConfigParser()
config.read('../community.ini', encoding='utf8')


WAIT_SECOND = 1
WAIT_SECOND_LONGER = 2
WAIT_NUMBER_OF_TRIAL = 10

class ProcessFailed(RuntimeError):
    """Exception raise when a DDE errpr occures."""
    def __init__(self, msg =""):
        RuntimeError.__init__(self, msg)

class webmanagerobj(object):

    def __init__(self, obj_context=None,
                 obj_name=None
                 ):
        self.browser = None
        self.sessionID = None
        self.exe_url = None

    def createBrowser(self):

        exe_webdriver_path = os.environ["community_selenium_chromedriver"]

        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.add_argument('log-level=3') #hide logs of info console in headless mode
        browser = webdriver.Chrome( executable_path=exe_webdriver_path,options=options)
        browser.set_window_size(width=1100, height=1024)

        self.browser = browser
        return True

    def get_agenda_list(self, year, month, day):

        self.browser.get('https://calendar.google.com/calendar/u/0/r/agenda/'
                         + str(year) + '/'
                         + str(month) + '/'
                         + str(day)
                         + '?tab=rc')
        sleep(WAIT_SECOND_LONGER)

    def login(self):

        web_account = config['account.config']['account']
        web_password = config['account.config']['password']
        browser = self.browser
        try:
            email_address, __ = wait_until_available_by_xpath(browser, name="//input[@type='email']",
                                                   frame=browser, multiple=False,
                                                   click=False)
            email_address.send_keys(web_account)
            __, __ = wait_until_available_by_xpath(browser, name='//*[text()="次へ"]',
                                                   frame=browser, multiple=False,
                                                   click=True)
            sleep(WAIT_SECOND_LONGER)
            email_password, __ = wait_until_available_by_xpath(browser, name="//input[@type='password']",
                                                   frame=browser, multiple=False,
                                                   click=False)
            email_password.send_keys(web_password)
            __, __ = wait_until_available_by_xpath(browser, name='//*[text()="次へ"]',
                                                   frame=browser, multiple=False,
                                                   click=True)
            sleep(WAIT_SECOND_LONGER)
        except Exception as e:
            print(e)
            return None

    def create_slots(self, title, starttime_in_hhmm, endtime_in_hhmm, slot_detail_text = None):

        browser = self.browser

        try:
            __, __ = wait_until_available_by_xpath(browser, name='//*[text()="作成"]',
                                                   frame=browser, multiple=False,
                                                   click=True)
            sleep(WAIT_SECOND)
            slot_title, __ = wait_until_available_by_xpath(browser, name="//input[@aria-label='タイトルを追加']",
                                                   frame=browser, multiple=False,
                                                   click=True)
            slot_title.send_keys(title)
            __ , __ = wait_until_available_by_xpath(browser, name="//span[text()='予約枠']",
                                                   frame=browser, multiple=False,
                                                   click=True)

            span_element = browser.find_element_by_xpath("//span[@id='tabAppointmentSlots']")

            elements = span_element.find_elements_by_xpath("//input[@id='xStTiIn']")

            for elem in elements:
                if elem.is_displayed() == False:
                    continue
                try:
                    elem.click()
                    elem.send_keys(Keys.HOME)
                    elem.send_keys(Keys.SHIFT + Keys.END)
                    elem.send_keys(Keys.DELETE)
                    elem.send_keys(starttime_in_hhmm)

                except Exception as e:
                    print(e)

            elements = span_element.find_elements_by_xpath("//input[@id='xEnTiIn']")

            for elem in elements:
                if elem.is_displayed() == False:
                    continue
                try:
                    elem.click()
                    elem.send_keys(Keys.HOME)
                    elem.send_keys(Keys.SHIFT + Keys.END)
                    elem.send_keys(Keys.DELETE)
                    elem.send_keys(endtime_in_hhmm)

                except Exception as e:
                    print(e)
            slot_title.click()

            browser.find_element_by_xpath("//div[@aria-label='予約枠の種類']").click()
            sleep(WAIT_SECOND)
            for elem in browser.find_elements_by_xpath("//span[text()='1 件の予約枠']"):
                if elem.is_displayed() == False:
                    continue
                try:
                    elem.click()
                except Exception as e:
                    print(e)
            sleep(WAIT_SECOND)

            slot_title.click()

            if slot_detail_text is not None:
                __, __ = wait_until_available_by_xpath(browser, name="//span[text()='その他のオプション']",
                                                       frame=browser, multiple=False,
                                                       click=True)
                slot_details, __ = wait_until_available_by_xpath(browser, name="//div[@aria-label='説明']",
                                                                 frame=browser, multiple=False,
                                                                 click=True)
                slot_details.send_keys(slot_detail_text)
                sleep(WAIT_SECOND)

            __, __ = wait_until_available_by_xpath(browser, name='//*[text()="保存"]',
                                                   frame=browser, multiple=False,
                                                   click=True)
            sleep(WAIT_SECOND_LONGER)
            return True
        except Exception as e:
            print(e)
            return None

    def readBrowserData(self):
        browser = self.browser
        print(f"URL: {browser.command_executor._url}")
        print(f"Session_id:{browser.session_id}")

    def tryClose(self):
        browser = self.browser
        browser.implicitly_wait(WAIT_SECOND_LONGER)
        browser.close()

def wait_until_available_by_id(browser, name, click=False):

    frame0 = None
    found = False
    counter = 0
    while found == False:
        try:
            frame0 = browser.find_element_by_id(name)
            if click == True:
                frame0.click()
            found = True
            return frame0, True
        except NoSuchElementException:
            counter = counter + 1
            print("timeout:" + str(counter) + "/name=" + name)
            if counter >= WAIT_NUMBER_OF_TRIAL:
                print("timeout max try reached")
                raise ProcessFailed
            continue


def wait_until_available_by_name(browser, name):

    frame0 = None
    found = False
    counter = 0
    while found == False:
        try:
            # WebDriverWait(browser, WAIT_SECOND).until(
            #     EC.presence_of_element_located((By.NAME, name )))
            frame0 = browser.find_element_by_name(name)
            found = True
            return frame0, True
        # except TimeoutException or NoSuchElementException:
        except NoSuchElementException:
            counter = counter + 1
            print("timeout:" + str(counter) + "/name=" + name)
            if counter >= WAIT_NUMBER_OF_TRIAL:
                print("timeout max try reached")
                raise ProcessFailed
            continue

@retry(tries=2, delay=0.1)
def wait_until_available_by_xpath(browser, name, frame, multiple = False, click = False):
    frame0 = None
    found = False
    counter = 0
    try:
        # WebDriverWait(browser, WAIT_SECOND).until(
        #     EC.presence_of_element_located((By.XPATH, name )))
        if multiple == True:
            frame0 = frame.find_elements_by_xpath(name)
        else:
            frame0 = frame.find_element_by_xpath(name)
        if click == True:
            frame0.click()
        found = True
        return frame0, True
    # except TimeoutException or NoSuchElementException:
    except ( NoSuchElementException, NoSuchWindowException ) as e:
        print("timeout:/xpath=" + name + "(e:" , e)
        raise e
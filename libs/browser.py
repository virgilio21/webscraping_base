#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

import geckodriver_autoinstaller
import coloredlogs, logging

from libs.common import get_random_item
from libs.common import config
from libs.common import naptime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options


logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(name)s - %(levelname)s: %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger)

geckodriver_autoinstaller.install()

class Browser():
    """Browser class"""

    def __init__(self):
        self.browser = self.get_browser()
        
    def get_browser(self):
        """Get the browser instance"""

        options = Options()
        options.headless = config().get('general').get('headless', False)
        user_agent = get_random_item('users_agent')
        language = get_random_item('languages')
        width, height = get_random_item('window_sizes').split(',')

        options.add_argument('--hide-scrollbars')
        options.set_preference("general.useragent.override", user_agent)
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference('useAutomationExtension', False)
        options.set_preference("intl.accept_languages", language)
        options.set_preference("dom.disable_open_during_load", False)
        options.set_preference('dom.webnotifications.enabled', False)
        browser = Firefox(options=options)
        browser.set_window_size(width, height)
        logger.info('Browser initialized')

        return browser
    
    def until_presence_of_element_or_wait_n_seconds(self, css_selector, wait_n_seconds):
        """Wait until the element is rendered or n seconds have passed"""

        logger.info(f'Wait the presence of element {css_selector}')
        wait_n_seconds = WebDriverWait(self.browser, wait_n_seconds)
        wait_n_seconds.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, css_selector)))

    def killbrowser(self, site_name):
        """Take screenshot and kill browser"""

        logger.info('Closing browser................')
        screenshot_name = f"/tmp/{site_name}_killbrowser.png"
        self.browser.save_screenshot(screenshot_name)
        self.browser.quit()

    def move_to_element(self, html_element):
        """Scroll to element and try to center"""
        self.browser.execute_script("arguments[0].scrollIntoView()", html_element)
        self.browser.execute_script("window.scrollBy(0, -250);")
    
    def scroll_down_page(self, speed=175, init=0):
        """Scroll to height page"""

        current_scroll_position = init
        new_height = current_scroll_position + 1
        while current_scroll_position <= new_height:
            random_scroll_speed = random.randint(speed, speed + 70)
            current_scroll_position += random_scroll_speed
            self.browser.execute_script("window.scrollTo({}, {});".format(init, current_scroll_position))
            naptime(1, 2)
            new_height = self.browser.execute_script("return document.body.scrollHeight")

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bs4

from libs.common import config
from libs.common import naptime

class HomesPage():
    """Base class"""
    apartment = 'departamento'
    house = 'casa'

    def __init__(self, news_site_name, browser):
        self._config = config()['homes_sites'][news_site_name]
        self._queries = self._config['queries']
        self._my_browser = browser
        self._name = news_site_name
        self._html = None
    
    def _visit(self, url, css_selector, time_to_wait):
        """Visit the url"""

        self._my_browser.browser.get(url)
        naptime(2)
        self._my_browser.until_presence_of_element_or_wait_n_seconds(css_selector, time_to_wait)
        naptime(4, 5)
        self._html = bs4.BeautifulSoup(self._my_browser.browser.page_source.encode('utf-8'), 'html.parser')
    
    def _get_html_soup_from_current_page(self):
        """Get html soup from current page"""

        self._html = bs4.BeautifulSoup(self._my_browser.browser.page_source.encode('utf-8'), 'html.parser')

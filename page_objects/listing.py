#!/usr/bin/env python
# -*- coding: utf-8 -*-

import coloredlogs, logging

from libs.common import naptime

from page_objects.homes import HomesPage

from selenium.webdriver.common.keys import Keys


logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(name)s - %(levelname)s: %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger)


class Listing(HomesPage):
    """Listing class"""

    def __init__(self, news_site_name, browser):
        super().__init__(news_site_name, browser)
        self._my_browser.until_presence_of_element_or_wait_n_seconds(
                        self._config['listing']['first_element_to_load'], 
                        40
        )

    @property
    def home_links(self):
        """Get list of home links order by more newest"""

        self._sorted_by_more_newest()
        links = []

        for page in range(self._config['pagination_limit']):
            try:
                logger.info(f'Page: {page + 1}')
                self._get_html_soup_from_current_page()
                current_card_homes = self._html.select(self._config['listing']['home_links'])
                current_links = [ home['href'] for home in current_card_homes if home.get('href') ]
                links += current_links
                self._click_next_button()
                naptime(2)
                self._my_browser.until_presence_of_element_or_wait_n_seconds(
                                self._config['listing']['first_element_to_load'], 
                                40
                            )
            except Exception as err:
                logger.error(f'something is wrong with pagination, continuing execution: {err}')

        return links

    def _sorted_by_more_newest(self):
        """Ordering homes by most recent"""

        logger.info('Ordering by newest................')
        dropdown_sorting = self._my_browser.browser.find_element_by_css_selector(
                                    self._config['listing']['dropdown_sorting_homes']
                            )
        dropdown_sorting.click()
        naptime(3)
        more_newest_option = self._my_browser.browser.find_element_by_css_selector(
                                    self._config['listing']['more_newest_option']
                            )
        more_newest_option.click()
        self._my_browser.until_presence_of_element_or_wait_n_seconds(
                            self._config['listing']['first_element_to_load'],
                            40
                        )
        naptime(3)

    def _click_next_button(self):
        """Click next button to paginate results"""

        logger.info('Clicking next page button................')
        next_button = self._my_browser.browser.find_element_by_css_selector(self._config['listing']['next_page_link'])
        self._my_browser.move_to_element(next_button)
        naptime(2)
        next_button.click()

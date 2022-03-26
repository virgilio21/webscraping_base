#!/usr/bin/env python
# -*- coding: utf-8 -*-

from libs.common import naptime

from page_objects.homes import HomesPage

from selenium.webdriver.common.keys import Keys


class Index(HomesPage):
    """Index page"""

    def __init__(self, news_site_name, browser):
        super().__init__(news_site_name, browser)
        self._go_to_index_page()

    def _go_to_index_page(self):
        """Visit the index page(init page)"""

        self._visit(self._config['url'], self._config['index']['first_element_to_load'], 40)
    
    def search_homes(self, text_to_search, apartment_type):
        """Search apartments"""

        rent_link = self._my_browser.browser.find_element_by_css_selector(
                        self._config['index']['for_sale_link']
                    )
        rent_link.click()
        naptime(2, 3)
        dropdown_apartment_type = self._my_browser.browser.find_element_by_css_selector(
                                    self._config['index']['dropdown_property_type']
                                )
        dropdown_apartment_type.click()
        naptime(2, 3)
        self._select_apartment_type(apartment_type)
        input_search_field = self._my_browser.browser.find_element_by_css_selector(
                                self._config['index']['input_search_field']
                            )
        input_search_field.send_keys(text_to_search)
        naptime(6, 7)
        input_search_field.send_keys(Keys.ARROW_DOWN)
        naptime(2, 3)
        input_search_field.send_keys(Keys.ENTER)
        naptime(4, 6)
    
    def _select_apartment_type(self, apartment_type):
        """Select of apartment_type"""

        option_list = None
        if self.__class__.apartment == apartment_type:
           option_list = self._my_browser.browser.find_element_by_css_selector(
                             self._config['index']['apartment_type_option']   
                        )
        else:
           option_list = self._my_browser.browser.find_element_by_css_selector(
                             self._config['index']['house_type_option']   
                        )
        
        option_list.click()

        

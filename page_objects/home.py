#!/usr/bin/env python
# -*- coding: utf-8 -*-


from libs.common import naptime
from libs.common import get_data_regex
from libs.common import clean_text
from libs.common import faker_phone

from page_objects.homes import HomesPage

class Home(HomesPage):
    """Home Features Page"""

    def __init__(self, news_site_name, browser, url):
        super().__init__(news_site_name, browser)
        self._url = url
        self._visit(self._url, self._queries['title'], 20)
        naptime(1, 3)

    @property
    def title(self):
        title = self._html.select_one(self._queries['title'])

        return title.text if title else ''

    @property
    def description(self):
        description = self._html.select_one(self._queries['description'])

        return clean_text(description.text) if description else ''

    @property
    def rooms(self):
        rooms_regex = self._queries['rooms']
        rooms = self._search_important_feature(rooms_regex)

        return int(rooms) if rooms else None

    @property
    def publisher(self):
        publisher = self._html.select_one(self._queries['publisher'])

        return publisher.text.strip() if publisher else ''

    @property
    def alternative_publisher(self):
        alternative_publisher = self._html.select_one(self._queries['publisher_alternative'])

        return alternative_publisher.text.strip() if alternative_publisher else ''

    def fill_form_to_see_phone(self):
        """Try get publihser info"""
        try:
            phone_link = self._my_browser.browser.find_element_by_css_selector(
                            self._config['home']['phone_link']
            )
            naptime(1)
            phone_link.click()
            naptime(1)
            self._my_browser.until_presence_of_element_or_wait_n_seconds(
                                self._config['home']['input_phone'], 5
            )
            naptime(2)
            input_phone = self._my_browser.browser.find_element_by_css_selector(
                            self._config['home']['input_phone']
            )
            input_phone.send_keys(faker_phone())
            naptime(2)
            button_send = self._my_browser.browser.find_element_by_css_selector(
                            self._config['home']['send_button']
            )
            button_send.click()

        except Exception:
            pass

        naptime(3)
        self._get_html_soup_from_current_page()
        naptime(2)

    def _search_important_feature(self, text_regex):
        """Search important feature from elements html with regex expression"""

        features = self._html.select(self._queries['important_features_container'])

        for feature in features:
            feature_text = (
                clean_text(feature.text)
                .replace('m2', '')
                .replace('(', '')
                .replace(')', '')
            )
            if feature_match := get_data_regex(feature_text, text_regex):
                return feature_match[0]

        return None

    def serialize_home_features(self):
        """Serialize features to dict"""

        return {
            'site': self._name,
            'title': self.title,
            'description': self.description,
            'url': self._url,
            'rooms': self.rooms,
        }

import re

from libs.common import config


def rents_scraping_validations(home):
    assert_min_price(home)
    assert_features_not_none(home)
    assert_blacklist_filter(home)


def blacklist_filter(text):
    validations = config()['general']['blacklist']
    for validation in validations:
        search = re.search(
            validation,
            text,
            re.IGNORECASE
        )
        if search:
            return False

    return True


def assert_blacklist_filter(home):
    url = home.get('url')
    assert blacklist_filter(home['title']), f'Title error: {url}'
    assert blacklist_filter(home['url']), f'Url error: {url}'


def assert_min_price(home):
    minimum_price = 0
    url = home.get('url')
    price = home.get('price', 0)
    assert price > minimum_price, f'Price error: {url}'


def assert_features_not_none(home):
    url = home.get('url')
    assert home, f'The link did not return results: {url}'
    assert home.get('rooms'), f'Could not get the rooms: {url}'
    assert home.get('latitude'), f'Latitude is not found: {url}'
    assert home.get('longitude'), f'Longitude not found {url}'

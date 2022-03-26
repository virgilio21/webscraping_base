#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import time
import random
import requests
import urllib
import re
import environ
import phonenumbers

from unidecode import unidecode


__config = None
__browser = None


def config():
    """Read the configuration of the environment in which it is executed"""

    env = environ.Env()
    env.read_env('.env')
    ENVIRONMENT = env('ENVIRONMENT')
    global __config
    if not __config:
        with open('config.yaml', mode='r', encoding='utf-8') as f:
            __config = yaml.safe_load(f)
            __config = __config.get(ENVIRONMENT, {})

    return __config


def naptime(min=2, max=4):
    """Function that sleeps the execution for a certain time"""

    if min <= max:
        time.sleep(random.randint(min, max))
    else:
        time.sleep(min)


def geo_to_neighborhood(lat, lng):
    """Returns the state, city and colony from latitude and longitude"""

    endpoint = config()['maps_api']['endpoint']
    key = config()['maps_api']['token']
    url = f'{endpoint}?latlng={lat},{lng}&key={key}'
    response = requests.get(url)
    body = response.json()
    ubication = {}
    if response.status_code == 200 and len(body['results']) > 0:

        for description in body['results'][0]['address_components']:
            if 'sublocality' in description['types']:
                ubication['neighborhood'] = unidecode(description['long_name']).lower()
            if 'neighborhood' in description['types']:
                ubication['neighborhood'] = unidecode(description['long_name']).lower()
            if 'administrative_area_level_1' in description['types']:
                ubication['state'] = unidecode(description['long_name']).lower()
            if 'country' in description['types']:
                ubication['country'] = unidecode(description['long_name']).lower()
        
        if 'formatted_address' in body['results'][0]:
            ubication['address'] = unidecode(body['results'][0]['formatted_address'])
        
        city_keys = ['administrative_area_level_3', 'administrative_area_level_2', 'locality']

        for city_key in city_keys:
            if ubication.get('city'):
                break
            for description in body['results']:
                if ubication.get('city'):
                    break
                if _get_city_from_response(description, city_key):
                    ubication['city'] = _get_city_from_response(description, city_key)
            
    return ubication


def _get_city_from_response(response_json, key_response):
    """Returns the city of the apartment"""

    for address in response_json['address_components']:
        if key_response in address['types']:

            return unidecode(address['long_name']).lower()


def neighborhood_to_geo(state, city, neighborhood):
    """Returns latitude and longitude from the state, city and colony"""
    state = unidecode(state)
    city = unidecode(city)
    neighborhood = unidecode(neighborhood)
    endpoint = config()['general']['maps_api']['endpoint']
    key = config()['general']['maps_api']['token']
    search_format = f'{state},{city},{neighborhood}'
    search = urllib.parse.quote(search_format, safe='')
    source_abs = f'{endpoint}?key={key}&address={search}'
    response = requests.get(source_abs)
    body = response.json()
    if response.status_code == 200 and len(body['results']) > 0:
        body = body['results'][0]
        return {'latitude': body['geometry']['location']['lat'],
            'longitude': body['geometry']['location']['lng']}

    return {'latitude': None, 'longitude': None}


def usd_to_mxn():
    """Returns the conversion factor from US dollar to Mexican peso"""

    config_money_change = config()['general']['change_money']
    apilayer = config_money_change['api_layer']
    currency_converter = config_money_change['currency_converter']
    cambiotoday = config_money_change['cambio_today']

    url_apilayer = f"{apilayer['endpoint']}?access_key={apilayer['token']}&currencies=MXN&format=1"
    url_currencyconverter = f"{currency_converter['endpoint']}{currency_converter['token']}"
    url_cambiotoday = f"{cambiotoday['endpoint']}{cambiotoday['token']}"

    r = requests.get(url_currencyconverter)
    if r.status_code == 200:
        data = r.json()
        return data['USD_MXN']['val']

    r = requests.get(url_apilayer)
    if r.status_code == 200:
        data = r.json()
        exchange = data['quotes']['USDMXN'] if 'quotes' in data else 0.0
        return exchange

    r = requests.get(url_cambiotoday)
    if r.status_code == 200:
        data = r.json()
        if data.get('status') == 'OK':
            return data['result']['value']

    return 0.0


def _config_browser():
    """Return browser settings"""

    global __browser
    if not __browser:
        with open('browser-info.json', mode='r', encoding='utf-8') as f:
            __browser = yaml.safe_load(f)

    return __browser


def get_random_item(item_key):
    """Get a random item from the browser config based on the key"""

    browser_list_options = _config_browser()[item_key]

    return random.choice(browser_list_options)


def clean_phone(raw_phone):
    """Clean phone number string"""
    
    phone = re.sub(' ', '', raw_phone)
    clean_phone = re.sub('[a-zA-Z]*', '', phone)

    return clean_phone


def get_price_from_text(price_text):
    """Extract the price from a text string"""

    dirty_price = price_text.replace(',', '')
    price = float(re.search(r'\d+', dirty_price).group())

    return price


def is_usd_price(mone_dollar, price_raw_text,):
    """Return True if the price is in dollars else False"""

    if mone_dollar in price_raw_text:
        return True

    return False


def get_data_regex(text, regex):
    """Returns the string that matches the regex"""

    if not text or not regex:
        return None
    else:
        match = re.search(regex, text)
        return match.groups() if match else None


def clean_text(text_raw):
    """Clean text from special characters"""

    clean_text = unidecode(text_raw.strip().lower())
    text = (clean_text
            .replace('\n', '')
            .replace('\t', '')
            .replace('\xa0', '')
        )

    return text


def faker_phone():
    """get random phone from MX"""

    phone_prefix = config()['general']['phone_lada']
    phone = str(random.choice(phone_prefix))

    for _ in range(7):
        phone += str(random.randint(0, 9))

    return phone


def parse_number(raw_phone, country_code='MX'):
    """Parse the phone to the country format"""

    parse_type = None if raw_phone[0] == '+' else country_code
    try:
        phone_representation = phonenumbers.parse(raw_phone, parse_type)
        is_valid = phonenumbers.is_valid_number(phone_representation)
        if is_valid:
            return str(
                phonenumbers.format_number(
                    phone_representation,
                    phonenumbers.PhoneNumberFormat.E164))
    except Exception:
        pass

    return None


def clean_phone(phone):
    """Clean the phone before parse it"""

    phone = phone.strip()
    phone = re.sub(' ', '', phone)
    phone = re.sub('[a-zA-Z]*', '', phone)

    return parse_number(phone)

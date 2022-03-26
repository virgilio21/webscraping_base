#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback
import argparse
import coloredlogs, logging

from libs.common import *
from libs.dbcontroller import *
from libs.validations import rents_scraping_validations

from page_objects.home import Home
from page_objects.index import Index
from page_objects.listing import Listing
from libs.browser import Browser

from selenium.common.exceptions import TimeoutException
from datetime import timedelta

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(name)s - %(levelname)s: %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger)



def scraper_homes(home_site_name, my_browser):
    """Main flow for homes, obtaining urls and then trying to save them"""
    
    logger.info(f'Start scraping homes for: {home_site_name}')
    list_states = config().get('general').get('states', ['Ciudad de México'])
    types_apartments = config().get('general').get('type_apartments')
    links_to_scrap = []

    for type_apartment in types_apartments:
        logger.warning(f'Apartment type: {type_apartment}')
        for state in list_states:
            logger.warning(f'State: {state}')
            index_page = Index(home_site_name, my_browser)
            index_page.search_homes(state, type_apartment)
            listing_page = Listing(home_site_name, my_browser)
            links_to_scrap += listing_page.home_links

    logger.info('Fetching urls finished')
    home_links = list(set(links_to_scrap))
    logger.info(f'Total number of urls to review: {len(home_links)}')

    for home_url in home_links:
        row = Rents.get_or_none(Rents.url == home_url)
        if not row:
            logger.warning(f'Trying to add {home_url} to DB')
            with database.transaction() as txn:
                try:
                    home_features = _fetch_home(home_site_name, my_browser, home_url)
                    logger.info(home_features)
                    rents_scraping_validations(home_features)
                    _save_home(home_features, txn)
                    logger.warning(f'{home_url} inserted\n')

                except TimeoutException as err:
                    logger.error(f'Timeout error: {err}')
                    logger.warning(f'Failed to get features url: {home_url}, continuing with the next')

                except AssertionError as err:
                    warning_msg = f'Assertion problem with {home_url}: {err}'
                    logger.error(warning_msg)

                except Exception as err:
                    warning_msg = f'Some problem with {home_url}: {err}'
                    logger.error(warning_msg)
                    txn.rollback()

    logger.info(f'End scraping homes for: {home_site_name} :D')


def scraper_phones(home_site_name, my_browser):
    """Main flow for phones, visiting urls and then trying to save them"""

    logger.info(f'Start scraping phones for: {home_site_name}')
    days_to_review = config()['homes_sites'][home_site_name]['phones']['days']
    limit_to_review = config()['homes_sites'][home_site_name]['phones']['review']
    min_time = datetime.now() - timedelta(days=days_to_review)
    rents = Rents.select(
                    Rents.url,
                    Rents.id
                ).join(
                    Phonebook,
                    JOIN.LEFT_OUTER,
                    on=(Rents.id == Phonebook.rent_id)
                ).where(
                    (Rents.date_in >= min_time)
                    & (Phonebook.rent_id.is_null())
                    & (Rents.site == home_site_name)
                ).limit(limit_to_review)

    for rent in rents:
        with database.transaction() as txn:
            try:
                publisher_features = _fetch_publisher(home_site_name, my_browser, rent.url, rent.id)
                Phonebook.create(**publisher_features)

                message = (
                            f"Phone save: {publisher_features.get('phone')}, "
                            f"Publisher: {publisher_features.get('name')}\n"
                )
                logger.warning(message)
                txn.commit()

            except TimeoutException as err:
                logger.error(f'Timeout error: {err}')
                logger.warning(f'Failed to get publisher features url: {rent.url}, continuing with the next')

            except AssertionError as err:
                warning_msg = f'Assertion problem with {rent.url}: {err}'
                logger.error(warning_msg)

            except Exception as err:
                logger.error(f'Error could not insert URL: {rent.url} - {err}')
                txn.rollback()

    logger.info(f'End scraping phones for: {home_site_name} :D')

def _fetch_home(home_site_name, browser, home_url):
    """Obtaining department features"""

    logger.info(f'Getting home features from {home_url}')

    home = Home(home_site_name, browser, home_url)
    home_features = home.serialize_home_features()

    return home_features

def _save_home(home_features, txn):
    """Save the obtained home in the DB"""

    rent = Rents.create(**home_features)
    rent.response = home_features
    rent.price_x_mt2 = (rent.price / rent.covered_area) if rent.covered_area > 0 else 0
    rent.save()
    txn.commit()

def _fetch_publisher(home_site_name, browser, home_url, rent_id):
    """Obtaining publisher features"""

    home = Home(home_site_name, browser, home_url)
    publisher = home.publisher if home.publisher else home.alternative_publisher
    home.fill_form_to_see_phone()
    phone = home.phone
    assert phone, 'Phone number not found'
    phone_format = clean_phone(phone)
    phone = phone_format if phone_format else phone
    is_valid = True if phone_format else False

    return {

        'rent_id': rent_id,
        'site': home_site_name,
        'url': home_url,
        'phone': phone,
        'name': publisher,
        'is_valid': is_valid
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    homes_sites_choices = list(config()['homes_sites'].keys())
    example_text = """examples:

    python run.py site_name --scraping-homes
    python run.py site_name --scraping-phones
    """

    parser = argparse.ArgumentParser(prog='python run.py',
                                    description='Webscraper to get information on apartments or telephone numbers of advertisers',
                                    epilog=example_text,
                                    formatter_class=argparse.RawDescriptionHelpFormatter
            )

    parser.add_argument('home_site_name',
                        help='the homes site that you want to scrape',
                        type=str,
                        choices=homes_sites_choices,
    )
    parser.add_argument("--scraping-homes",
                        help="executes the function to obtain apartments",
                        action='store_true'
    )
    parser.add_argument("--scraping-phones",
                        help="executes the function to obtain phone-numbers",
                        action='store_true'
    )

    args = parser.parse_args()

    try:

        if not args.scraping_homes and not args.scraping_phones:
            raise ValueError('Your command is not correct, try python run.py -h for help or check the documentation')

        browser = Browser()
        if args.scraping_homes:
            scraper_homes(args.home_site_name, browser)
        
        if args.scraping_phones:
            scraper_phones(args.home_site_name, browser)

        browser.killbrowser(args.home_site_name)
    except ValueError as err:
        logger.error(err)

    except Exception as err:
        browser.killbrowser(args.home_site_name)
        traceback_str = str(traceback.format_exc())
        logger.error(f'{err}\n{traceback_str}')

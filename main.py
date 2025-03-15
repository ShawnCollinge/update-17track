from datetime import timedelta, date
import logging
import re
from imapclient import IMAPClient
from mailparser import parse_from_bytes
from custom_components.email.parsers import *  
import asyncio
import os
from aiohttp import ClientSession
from pyseventeentrack import Client


from custom_components.const import (
    CONF_EMAIL, CONF_PASSWORD, CONF_IMAP_SERVER,
    CONF_IMAP_PORT, CONF_SSL, CONF_EMAIL_FOLDER, CONF_DAYS_OLD,
    ATTR_TRACKING_NUMBERS, EMAIL_ATTR_FROM, EMAIL_ATTR_SUBJECT,
    EMAIL_ATTR_BODY, ATTR_COUNT)


from custom_components.parsers.ups import ATTR_UPS, EMAIL_DOMAIN_UPS, parse_ups
from custom_components.parsers.amazon import ATTR_AMAZON, EMAIL_DOMAIN_AMAZON, parse_amazon
from custom_components.parsers.amazon_de import ATTR_AMAZON_DE, EMAIL_DOMAIN_AMAZON_DE, parse_amazon_de
from custom_components.parsers.fedex import ATTR_FEDEX, EMAIL_DOMAIN_FEDEX, parse_fedex
from custom_components.parsers.paypal import ATTR_PAYPAL, EMAIL_DOMAIN_PAYPAL, parse_paypal
from custom_components.parsers.usps import ATTR_USPS, EMAIL_DOMAIN_USPS, parse_usps
from custom_components.parsers.ali_express import ATTR_ALI_EXPRESS, EMAIL_DOMAIN_ALI_EXPRESS, parse_ali_express
from custom_components.parsers.newegg import ATTR_NEWEGG, EMAIL_DOMAIN_NEWEGG, parse_newegg
from custom_components.parsers.rockauto import ATTR_ROCKAUTO, EMAIL_DOMAIN_ROCKAUTO, parse_rockauto
from custom_components.parsers.bh_photo import ATTR_BH_PHOTO, EMAIL_DOMAIN_BH_PHOTO, parse_bh_photo
from custom_components.parsers.ebay import ATTR_EBAY, EMAIL_DOMAIN_EBAY, parse_ebay
from custom_components.parsers.dhl import ATTR_DHL, EMAIL_DOMAIN_DHL, parse_dhl
from custom_components.parsers.hue import ATTR_HUE, EMAIL_DOMAIN_HUE, parse_hue
from custom_components.parsers.google_express import ATTR_GOOGLE_EXPRESS, EMAIL_DOMAIN_GOOGLE_EXPRESS, parse_google_express
from custom_components.parsers.western_digital import ATTR_WESTERN_DIGITAL, EMAIL_DOMAIN_WESTERN_DIGITAL, parse_western_digital
from custom_components.parsers.monoprice import ATTR_MONOPRICE, EMAIL_DOMAIN_MONOPRICE, parse_monoprice
from custom_components.parsers.georgia_power import ATTR_GEORGIA_POWER, EMAIL_DOMAIN_GEORGIA_POWER, parse_georgia_power
from custom_components.parsers.best_buy import ATTR_BEST_BUY, EMAIL_DOMAIN_BEST_BUY, parse_best_buy
from custom_components.parsers.dollar_shave_club import ATTR_DOLLAR_SHAVE_CLUB, EMAIL_DOMAIN_DOLLAR_SHAVE_CLUB, parse_dollar_shave_club
from custom_components.parsers.nuleaf import ATTR_NULEAF, EMAIL_DOMAIN_NULEAF, parse_nuleaf
from custom_components.parsers.timeless import ATTR_TIMELESS, EMAIL_DOMAIN_TIMLESS, parse_timeless
from custom_components.parsers.dsw import ATTR_DSW, EMAIL_DOMAIN_DSW, parse_dsw
from custom_components.parsers.wyze import ATTR_WYZE, EMAIL_DOMAIN_WYZE, parse_wyze
from custom_components.parsers.reolink import ATTR_REOLINK, EMAIL_DOMAIN_REOLINK, parse_reolink
from custom_components.parsers.chewy import ATTR_CHEWY, EMAIL_DOMAIN_CHEWY, parse_chewy
from custom_components.parsers.groupon import ATTR_GROUPON, EMAIL_DOMAIN_GROUPON, parse_groupon
from custom_components.parsers.zazzle import ATTR_ZAZZLE, EMAIL_DOMAIN_ZAZZLE, parse_zazzle
from custom_components.parsers.home_depot import ATTR_HOME_DEPOT, EMAIL_DOMAIN_HOME_DEPOT, parse_home_depot
from custom_components.parsers.swiss_post import ATTR_SWISS_POST, EMAIL_DOMAIN_SWISS_POST, parse_swiss_post
from custom_components.parsers.bespoke_post import ATTR_DSW, EMAIL_DOMAIN_DSW, parse_bespoke_post
from custom_components.parsers.manta_sleep import ATTR_MANTA_SLEEP, EMAIL_DOMAIN_MANTA_SLEEP, parse_manta_sleep
from custom_components.parsers.prusa import ATTR_PRUSA, EMAIL_DOMAIN_PRUSA, parse_prusa
from custom_components.parsers.adam_eve import ATTR_ADAM_AND_EVE, EMAIL_DOMAIN_ADAM_AND_EVE, parse_adam_and_eve
from custom_components.parsers.target import ATTR_TARGET, EMAIL_DOMAIN_TARGET, parse_target
from custom_components.parsers.gamestop import ATTR_GAMESTOP, EMAIL_DOMAIN_GAMESTOP, parse_gamestop
from custom_components.parsers.litter_robot import ATTR_LITTER_ROBOT, EMAIL_DOMAIN_LITTER_ROBOT, parse_litter_robot
from custom_components.parsers.the_smartest_house import ATTR_SMARTEST_HOUSE, EMAIL_DOMAIN_SMARTEST_HOUSE, parse_smartest_house
from custom_components.parsers.ubiquiti import ATTR_UBIQUITI, EMAIL_DOMAIN_UBIQUITI, parse_ubiquiti
from custom_components.parsers.nintendo import ATTR_NINTENDO, EMAIL_DOMAIN_NINTENDO, parse_nintendo
from custom_components.parsers.pledgebox import ATTR_PLEDGEBOX, EMAIL_DOMAIN_PLEDGEBOX, parse_pledgebox
from custom_components.parsers.guitar_center import ATTR_GUITAR_CENTER, EMAIL_DOMAIN_GUITAR_CENTER, parse_guitar_center
from custom_components.parsers.sony import ATTR_SONY, EMAIL_DOMAIN_SONY, parse_sony
from custom_components.parsers.sylvane import ATTR_SYLVANE, EMAIL_DOMAIN_SYLVANE, parse_sylvane
from custom_components.parsers.adafruit import ATTR_ADAFRUIT, EMAIL_DOMAIN_ADAFRUIT, parse_adafruit
from custom_components.parsers.thriftbooks import ATTR_THRIFT_BOOKS, EMAIL_DOMAIN_THRIFT_BOOKS, parse_thrift_books
from custom_components.parsers.lowes import ATTR_LOWES, EMAIL_DOMAIN_LOWES, parse_lowes

from custom_components.parsers.generic import ATTR_GENERIC, EMAIL_DOMAIN_GENERIC, parse_generic


logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

TRACKING_NUMBER_URLS = {
    'ups': "https://www.ups.com/track?loc=en_US&tracknum=",
    'usps': "https://tools.usps.com/go/TrackConfirmAction?tLabels=",
    'fedex': "https://www.fedex.com/apps/fedextrack/?tracknumbers=",
    'dhl': 'https://www.logistics.dhl/us-en/home/tracking/tracking-parcel.html?submit=1&tracking-id=',
    'swiss_post': 'https://www.swisspost.ch/track?formattedParcelCodes=',
    'unknown': 'https://www.google.com/search?q=',
}

parsers = [
    (ATTR_UPS, EMAIL_DOMAIN_UPS, parse_ups),
    (ATTR_FEDEX, EMAIL_DOMAIN_FEDEX, parse_fedex),
    (ATTR_AMAZON, EMAIL_DOMAIN_AMAZON, parse_amazon),
    (ATTR_AMAZON_DE, EMAIL_DOMAIN_AMAZON_DE, parse_amazon_de),
    (ATTR_PAYPAL, EMAIL_DOMAIN_PAYPAL, parse_paypal),
    (ATTR_USPS, EMAIL_DOMAIN_USPS, parse_usps),
    (ATTR_ALI_EXPRESS, EMAIL_DOMAIN_ALI_EXPRESS, parse_ali_express),
    (ATTR_NEWEGG, EMAIL_DOMAIN_NEWEGG, parse_newegg),
    (ATTR_ROCKAUTO, EMAIL_DOMAIN_ROCKAUTO, parse_rockauto),
    (ATTR_BH_PHOTO, EMAIL_DOMAIN_BH_PHOTO, parse_bh_photo),
    (ATTR_EBAY, EMAIL_DOMAIN_EBAY, parse_ebay),
    (ATTR_DHL, EMAIL_DOMAIN_DHL, parse_dhl),
    (ATTR_HUE, EMAIL_DOMAIN_HUE, parse_hue),
    (ATTR_GOOGLE_EXPRESS, EMAIL_DOMAIN_GOOGLE_EXPRESS, parse_google_express),
    (ATTR_WESTERN_DIGITAL, EMAIL_DOMAIN_WESTERN_DIGITAL, parse_western_digital),
    (ATTR_MONOPRICE, EMAIL_DOMAIN_MONOPRICE, parse_monoprice),
    (ATTR_GEORGIA_POWER, EMAIL_DOMAIN_GEORGIA_POWER, parse_georgia_power),
    (ATTR_BEST_BUY, EMAIL_DOMAIN_BEST_BUY, parse_best_buy),
    (ATTR_DOLLAR_SHAVE_CLUB, EMAIL_DOMAIN_DOLLAR_SHAVE_CLUB, parse_dollar_shave_club),
    (ATTR_NULEAF, EMAIL_DOMAIN_NULEAF, parse_nuleaf),
    (ATTR_TIMELESS, EMAIL_DOMAIN_TIMLESS, parse_timeless),
    (ATTR_DSW, EMAIL_DOMAIN_DSW, parse_dsw),
    (ATTR_WYZE, EMAIL_DOMAIN_WYZE, parse_wyze),
    (ATTR_REOLINK, EMAIL_DOMAIN_REOLINK, parse_reolink),
    (ATTR_CHEWY, EMAIL_DOMAIN_CHEWY, parse_chewy),
    (ATTR_GROUPON, EMAIL_DOMAIN_GROUPON, parse_groupon),
    (ATTR_ZAZZLE, EMAIL_DOMAIN_ZAZZLE, parse_zazzle),
    (ATTR_HOME_DEPOT, EMAIL_DOMAIN_HOME_DEPOT, parse_home_depot),
    (ATTR_SWISS_POST, EMAIL_DOMAIN_SWISS_POST, parse_swiss_post),
    (ATTR_DSW, EMAIL_DOMAIN_DSW, parse_bespoke_post),
    (ATTR_MANTA_SLEEP, EMAIL_DOMAIN_MANTA_SLEEP, parse_manta_sleep),
    (ATTR_PRUSA, EMAIL_DOMAIN_PRUSA, parse_prusa),
    (ATTR_ADAM_AND_EVE, EMAIL_DOMAIN_ADAM_AND_EVE, parse_adam_and_eve),
    (ATTR_TARGET, EMAIL_DOMAIN_TARGET, parse_target),
    (ATTR_GAMESTOP, EMAIL_DOMAIN_GAMESTOP, parse_gamestop),
    (ATTR_LITTER_ROBOT, EMAIL_DOMAIN_LITTER_ROBOT, parse_litter_robot),
    (ATTR_SMARTEST_HOUSE, EMAIL_DOMAIN_SMARTEST_HOUSE, parse_smartest_house),
    (ATTR_UBIQUITI, EMAIL_DOMAIN_UBIQUITI, parse_ubiquiti),
    (ATTR_NINTENDO, EMAIL_DOMAIN_NINTENDO, parse_nintendo),
    (ATTR_PLEDGEBOX, EMAIL_DOMAIN_PLEDGEBOX, parse_pledgebox),
    (ATTR_GUITAR_CENTER, EMAIL_DOMAIN_GUITAR_CENTER, parse_guitar_center),
    (ATTR_SONY, EMAIL_DOMAIN_SONY, parse_sony),
    (ATTR_SYLVANE, EMAIL_DOMAIN_SYLVANE, parse_sylvane),
    (ATTR_ADAFRUIT, EMAIL_DOMAIN_ADAFRUIT, parse_adafruit),
    (ATTR_THRIFT_BOOKS, EMAIL_DOMAIN_THRIFT_BOOKS, parse_thrift_books),
    (ATTR_LOWES, EMAIL_DOMAIN_LOWES, parse_lowes),
    
    (ATTR_GENERIC, EMAIL_DOMAIN_GENERIC, parse_generic),
]

def find_carrier(tracking_number, email_domain):
    """Determine the carrier based on tracking number or email domain."""
    if isinstance(tracking_number, dict):
        return {
            'tracking_number': tracking_number.get('tracking_number', ''),
            'carrier': email_domain,
            'origin': email_domain,
            'link': tracking_number.get('link', ''),
        }
    
    carrier, link = "Unknown", TRACKING_NUMBER_URLS["unknown"]
    if tracking_number.startswith('http'):
        link, carrier = tracking_number, email_domain
    elif email_domain in TRACKING_NUMBER_URLS:
        link, carrier = TRACKING_NUMBER_URLS[email_domain], email_domain
    
    return {
        'tracking_number': tracking_number,
        'carrier': carrier,
        'origin': email_domain or carrier,
        'link': f'{link}{tracking_number}',
    }

class EmailEntity():
    """Email Entity."""

    def __init__(self):
        """Init the Email Entity."""
        self._attr = {
            ATTR_TRACKING_NUMBERS: {},
	        ATTR_COUNT: 0
        }
        config = {
        'email': os.getenv("TRACKING_EMAIL"),
        'password': os.getenv("TRACKING_EMAIL_PASSWORD"),
        'imap_server': "imap.gmail.com",
        'imap_port': 993,
        'ssl': True,
        'email_folder': "INBOX",
        'days_old': 1
        }

        self.imap_server = config["imap_server"]
        self.imap_port = config["imap_port"]
        self.email_address = config["email"]
        self.password = config["password"]
        self.email_folder = config["email_folder"]
        self.ssl = config["ssl"]
        self.days_old = int(config["days_old"])

        self.flag = [u'SINCE', date.today() - timedelta(days=self.days_old)]

    async def update(self):
        """Update data from Email API."""
        self._attr = {
            ATTR_TRACKING_NUMBERS: {},
	        ATTR_COUNT: 0
        }
        already_added = set()
        res = []
        self.flag = [u'SINCE', date.today() - timedelta(days=self.days_old)]
        _LOGGER.debug(f'flag: {self.flag}')

        emails = []
        server = IMAPClient(self.imap_server, port=self.imap_port, use_uid=True, ssl=self.ssl)

        try:
            server.login(self.email_address, self.password)
            server.select_folder(self.email_folder, readonly=True)
        except Exception as err:
            _LOGGER.error('IMAPClient login error {}'.format(err))
            return False

        try:
            messages = server.search(self.flag)
            for uid, message_data in server.fetch(messages, 'RFC822').items():
                try:
                    mail = parse_from_bytes(message_data[b'RFC822'])
                    
                    emails.append({
                        EMAIL_ATTR_FROM: mail.from_,
                        EMAIL_ATTR_SUBJECT: mail.subject,
                        EMAIL_ATTR_BODY: mail.body
                    })
                except Exception as err:
                    _LOGGER.warning(
                        'mailparser parse_from_bytes error: {}'.format(err))

        except Exception as err:
            _LOGGER.error('IMAPClient update error: {}'.format(err))

        # empty out all parser arrays
        for ATTR, EMAIL_DOMAIN, parser in parsers:
            self._attr[ATTR_TRACKING_NUMBERS][ATTR] = []

        # for each email run each parser and save in the corresponding ATTR
        async with ClientSession() as session:
            client = Client(session=session)
            await client.profile.login(os.getenv("SEVENTEEN_EMAIL"), os.getenv("SEVENTEEN_PASSWORD"))

            packages = await client.profile.packages()
            for package in packages:
                already_added.add(package.tracking_number)
                if (package.status == "Delivered"):
                    await client.profile.archive_package(package.tracking_number)
                    
            for email in emails:
                email_from = email[EMAIL_ATTR_FROM]
                _LOGGER.debug(f'parsing email from {email_from}')
                if isinstance(email_from, (list, tuple)):
                    email_from = list(email_from)
                    email_from = ''.join(list(email_from[0]))
                
                # run through all parsers for each email if email domain matches
                for ATTR, EMAIL_DOMAIN, parser in parsers:
                    _LOGGER.debug(f'parsing email for parser {EMAIL_DOMAIN}')
                    try:
                        if EMAIL_DOMAIN in email_from:
                            tracking_numbers = parser(email=email)
                            for tracking in tracking_numbers:
                                if tracking not in already_added:
                                    already_added.add(tracking)
                                    friendly_name = ATTR if ATTR != 'generic' else email_from.split("@")[1]
                                    res.append({
                                        'tracking_number': tracking,
                                        'name': friendly_name
                                    })
                                    await client.profile.add_package(tracking, friendly_name)

                    except Exception as err:
                        _LOGGER.error('{} error: {}'.format(ATTR, err))
        server.logout()


if __name__ == "__main__":
    email = EmailEntity()
    asyncio.run(email.update())



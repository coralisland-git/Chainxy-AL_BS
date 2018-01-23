# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import scrapy
import json
import csv
import requests
import re
import chainxy.utils as utils
from pprint import pprint
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import html
from lxml import etree

class janieandjack(scrapy.Spider):
    name = "janieandjack"
    start_urls = ['http://www.janieandjack.com/on/demandware.store/Sites-JanieAndJack-Site/default/Stores-GetNearestStores?latitude=41.850033&longitude=-87.6500523&countryCode=US&distanceUnit=mi&maxdistance=10000']

    def parse(self, response):
        stores = json.loads(response.body)['stores']
        for key, store in stores.items():
            item = ChainItem()
            item['store_name'] = store['name']
            item['store_type'] = store['storeType']
            item['store_number'] = ''
            item['address'] = store['address1']
            item['address2'] = store['address2']
            item['city'] = store['city']
            item['state'] = store['stateCode']
            item['zip_code'] = store['postalCode']
            item['country'] = store['countryCode']
            item['phone_number'] = store['phone']
            item['latitude'] = store['latitude']
            item['longitude'] = store['longitude']
            item['store_hours'] = store['storeHours']
            for cnt in range(2, 5):
                item['store_hours'] += ', ' + store['storeHours'+str(cnt)]
            item['coming_soon'] = ''
            item['other_fields'] = ''
            yield item

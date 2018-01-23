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
from chainxy.seeds import Seed
from lxml import html
from lxml import etree

class michaelkors(scrapy.Spider):
    name = 'michaelkors'
    domain = ''
    history = []

    def start_requests(self):
        init_url = 'https://www.michaelkors.ca/server/stores'
        header = {
            "Accept":"application/json, text/plain, */*",
            "Accept-Encoding":"gzip, deflate, br",
            "Content-Type":"application/json;charset=UTF-8"
        }
        location_list = [{'country': 'United States', 'abbr': 'US'}, {'country':'Canada', 'abbr': 'CA'}]
        for location in location_list: 
            seed = Seed()
            seed.setConfig(seed_type="grid", distance="250", countries=[location['abbr']], regions=['ALL'], sample=False)
            s = seed.query_points()
            for p in s['results']:
                payload = {
                    "latitude":p['latitude'],
                    "longitude":p['longitude'],
                    "radius":"500",
                    "country":location['country']
                    }
                yield scrapy.FormRequest(url=init_url, formdata=payload, method='post', callback=self.parse)

    def parse(self, response):
        store_list = json.loads(response.body)['stores']
        if len(store_list) != 0:
            for store in store_list:
                item = ChainItem()
                item['store_name'] = self.validate(store['displayName'])
                if 'locationId' in store:
                    item['store_number'] = self.validate(store['locationId'])
                item['address'] = ''
                if 'address' in store:
                    if 'addressLine1' in store['address']:
                        item['address'] = self.validate(store['address']['addressLine1'])
                    if 'addressLine2' in store['address']:
                        item['address2'] = self.validate(store['address']['addressLine2'])
                    if 'city' in store['address']:
                        item['city'] = self.validate(store['address']['city']['name'])
                    if 'state' in store['address']:
                        item['state'] = self.validate(store['address']['state']['name'])
                    if 'zipcode' in store['address']:
                        item['zip_code'] = self.validate(store['address']['zipcode'])
                    if 'country' in store['address']:
                        item['country'] = self.validate(store['address']['country']['name'])

                item['phone_number'] = ''
                if 'phone_number' in store:
                    item['phone_number'] = self.validate(store['address']['phone'])
                if 'geolocation' in store:
                    item['latitude'] = self.validate(store['geoLocation']['latitude'])
                    item['longitude'] = self.validate(store['geoLocation']['longitude'])
                if 'operatingHours' in store:
                    item['store_hours'] = self.validate(store['operatingHours'])
                if 'type' in store:
                    item['store_type'] = self.validate(store['type'])
                if item['address']+item['phone_number'] not in self.history:
                    self.history.append(item['address']+item['phone_number'])
                    yield item  

    def validate(self, item):
        try:
            return item.strip().replace(';',', ').encode('ascii','ignore').replace('\xe9', '')
        except:
            return ''

    def eliminate_space(self, items):
        tmp = []
        for item in items:
            if self.validate(item) != '':
                tmp.append(self.validate(item))
        return tmp
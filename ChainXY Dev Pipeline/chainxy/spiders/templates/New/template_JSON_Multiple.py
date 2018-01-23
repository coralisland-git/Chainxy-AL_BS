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

class TemplateSpider(scrapy.Spider):
    name = "template"
    start_urls = []
    #handle_httpstatus_list = [301]
    #parse_address={'enabled':True}
    history = []
    headers = {}
    base_url = ''
    location_list = []


    def __init__(self, *args, **kwargs):

        with open('seed_file.json') as locations:
            self.location_list = json.loads(locations.read())


    def start_requests(self):

        for location in self.location_list:
            stateCode = location['code']
            body = {
                '1': 'A',
                '2': stateCode
            }
            yield FormRequest(url=self.base_url, formdata = body, callback=self.parse_cities, meta = {'state':stateCode})

    def parse_cities(self, response):

        cities = json.loads(response.body)
        stateCode = response.meta['state']
        for city in cities:
            city = city['city']
            body = {
                '1':'A',
                '2': city,
                '3': stateCode
            }
            yield FormRequest(url=self.base_url, formdata = body, callback=self.parse_stores)


    def parse_stores(self, response):

        stores = json.loads(response.body)

        for store in stores:
            if store['id'] not in self.history:
                self.history.append(store['id'])

                item = ChainItem()

                item['store_name'] = store["store_name"]
                item['store_number'] =
                item['address'] =
                item['phone_number'] =
                item['city'] =
                item['state'] =
                item['zip_code'] =
                item['country'] =
                item['latitude'] =
                item['longitude'] =
                item['store_type'] =
                item['store_hours'] =
                item['other_fields'] =
                item['coming_soon'] =

                yield item

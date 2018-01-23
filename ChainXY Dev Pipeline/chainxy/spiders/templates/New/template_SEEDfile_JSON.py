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

    def __init__(self, *args, **kwargs):
        with open('seed.json') as seed_file:
            self.location_list = json.loads(seed_file.read())

    def start_requests(self):
        for location in self.location_list:
            url = 'https://url.com/?lat='+location['latitude']+'&lng='+location['longitude']+'&max_results=25&search_radius=25'
            yield Request(url=url, headers = self.headers, callback=self.parse)

    def parse(self, response):
        stores = json.loads(response.body)

        for store in stores:
            if item['store_number'] not in self.history:
                self.history.append(item['store_number'])
                item = ChainItem()

                htmlWithinJSON = etree.HTML(store['property1']['property2'])
                item['coming_soon'] = htmlWithinJSON.xpath('').extract()

                item['store_name'] = store["store"]
                item['store_number'] = ''
                item['address'] = ''
                item['phone_number'] = ''
                item['city'] = ''
                item['state'] = ''
                item['zip_code'] = ''
                item['country'] = ''
                item['latitude'] = ''
                item['longitude'] = ''
                item['store_type'] = ''
                item['store_hours'] = ''
                item['other_fields'] = ''
                item['coming_soon'] = ''

                yield item

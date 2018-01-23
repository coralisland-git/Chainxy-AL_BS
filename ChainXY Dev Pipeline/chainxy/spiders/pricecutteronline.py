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

class pricecutteronline(scrapy.Spider):
    name = "pricecutteronline"
    domain = 'https://www.pricecutteronline.com'

    def start_requests(self):
        init_url = 'https://api.freshop.com/1/stores?limit=-1&has_address=true&token=ac48a09d75818edcb945f40dc8230a75&app_key=price_cutter'
        header = {
            "accept":"application/json, text/javascript, */*; q=0.01",
            "accept-encoding":"gzip, deflate, br"
        }
        yield scrapy.Request(url=init_url, headers=header, method="get", callback=self.body) 

    def body(self, response):
        store_list = json.loads(response.body)['items']
        for store in store_list:
            item = ChainItem()
            item['store_name'] = self.validate(store['name'])
            item['store_number'] = self.validate(store['id'])
            item['address'] = self.validate(store['address_1'])
            item['city'] = self.validate(store['city'])
            item['state'] = self.validate(store['state'])
            item['zip_code'] = self.validate(store['postal_code'])
            item['country'] = 'United States'
            item['phone_number'] = self.validate(store['phone']).split('\n')[0]
            item['latitude'] = str(self.validate(store['latitude']))
            item['longitude'] = str(self.validate(store['longitude']))
            try:
                item['store_hours'] = self.validate(store['hours'])
            except:
                pass
            yield item  

    def validate(self, item):
        try:
            return item.strip()
        except:
            return ''
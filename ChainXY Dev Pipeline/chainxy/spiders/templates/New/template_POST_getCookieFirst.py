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

class TemplateSpider(Spider):
    name = "template"
    base_url = 'yourPostMethodRequestURL'

    def start_requests(self):
        payload = {'form': 'data',
                   }

        yield scrapy.FormRequest(url = self.base_url, formdata = payload, callback = self.getCookie)


    def getCookie(self, response):
        cookie = response.headers.getlist('Set-Cookie')[0].split(';')[0]
        header = {
            'cookie':cookie,
        }
        payload = {'form': 'data',
                   }

        # IMPORTANT
        # dont_filter = True
        # allows to request the same url
        yield scrapy.FormRequest(url = self.base_url, formdata = payload, headers = header, callback = self.parse_stores, dont_filter = True)

    def parse_stores(self, response):

        x = response.body.split('JSON VALUE=[')[1].split(']-->')[0]
        stores = json.loads(x)

        item = ChainItem()

        for store in stores:
            item['coming_soon'] = '0'
            item['store_name'] = store['title']
            item['store_number'] = ''
            item['address'] = ''
            item['address2'] = ''
            item['city'] = ''
            item['state'] = ''
            item['zip_code'] = ''
            item['country'] = ''
            item['phone_number'] = ''
            item['latitude'] = ''
            item['longitude'] = ''
            item['store_hours'] = ''
            item['store_type'] = ''
            item['other_fields'] = ''
            yield item

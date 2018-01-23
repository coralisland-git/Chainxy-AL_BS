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
    name = "teamplate"
    allowed_domains = []
    start_urls = []
    history = []

    def start_requests(self):

        headers = {}
        body={}
        url = ''
        yield scrapy.FormRequest(url=url, formdata=body, headers = headers, callback=self.parse_details)


    def parse_details(self, response):

        stores = response.xpath('')

        for store in stores:

            if store['id'] not in self.history:

                self.history.append(store['id'])

                item = ChainItem()
                item['store_name'] = response.xpath('').extract_first()
                item['store_type'] = ''
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
                item['coming_soon'] = ''

                yield item

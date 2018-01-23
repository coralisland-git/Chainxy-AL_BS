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
    base_url = ''
    #handle_httpstatus_list = [301]
    #parse_address={'enabled':True}

    def start_requests(self):
        url = ''
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for link in response.xpath('@href').extract():
            yield scrapy.Request(url=link, callback=self.parse_store)

    def parse_store(self, store):
        item = ChainItem()
        item['store_name'] = store.xpath('').extract_first()
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

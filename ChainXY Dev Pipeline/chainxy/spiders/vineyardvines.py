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

class vineyardvines(scrapy.Spider):
    name = "vineyardvines"
    start_urls = ['https://global.vineyardvines.com/stores']
    base_url = ''
    #handle_httpstatus_list = [301]
    parse_address={'enabled':True}

    def parse(self, response):
        stores = response.xpath('//div[@class="store_content"]')
        for store in stores:
            item = ChainItem()
            item['store_name'] = store.xpath('.//p[@class="store_name"]//text()').extract_first()
            item['store_type'] = ''
            item['address2'] = ''
            item['city'] = ''
            item['state'] = ''
            item['zip_code'] = ''
            item['country'] = 'United States'
            detail = store.xpath('.//p[@class="store_content_reg"]//text()').extract()
            address = ''
            for de in detail:
                if '(' in de or len(de.split('-')) == 3:
                    item['phone_number'] = de
                else:
                    if self.validate(de) != '':
                        address += self.validate(de) + ', '
            item['address'] = address
            item['latitude'] = ''
            item['longitude'] = ''
            item['store_hours'] = self.merge(store.xpath('.//p[@class="store_content_sml"]//span[@itemprop="openingHours"]//text()').extract())
            item['other_fields'] = ''
            item['coming_soon'] = ''
            yield item

    def merge(self, items):
        val = ''
        for item in items:
            if self.validate(item) != '':
                val += self.validate(item) + ', '
        return val[1: len(val)-2]

    def validate(self, item):
        try:
            return item.strip().replace('\n', '').replace('\t','').replace('\r', '')
        except:
            pass
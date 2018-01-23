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

class kokofitclub(scrapy.Spider):
    name = "kokofitclub"
    parse_address={'enabled':True}

    def start_requests(self):
        yield scrapy.Request(url='http://kokofitclub.com/locations', callback=self.parse_store)

    def parse_store(self, response):
        store_list = response.xpath('//div[@class="location-card"]')
        for store in store_list:
            item = ChainItem()
            item['store_name'] = self.validate(self.eliminate_space(store.xpath('.//div[@class="card-title"]//p//text()').extract())[0])
            item['store_type'] = ''
            item['address'] = self.validate(self.eliminate_space(store.xpath('.//div[@class="card-address"]//a//text()').extract())[0])
            item['country'] = 'United States'
            if 'AB' in item['address']:
                item['country'] = 'Canada'
            item['phone_number'] = self.validate(self.eliminate_space(store.xpath('.//div[@class="card-phone"]//p//text()').extract())[0].split(':')[1])
            item['latitude'] = ''
            item['longitude'] = ''
            item['store_hours'] = ''
            item['coming_soon'] = ''
            yield item

    def eliminate_space(self, items):
        tmp = []
        for item in items:
            if self.validate(item) != '':
                tmp.append(self.validate(item))
        return tmp

    def validate(self, item):
        try:
            return item.strip().replace('\n', '').replace('\t','').replace('\r', '').encode('ascii','ignore').replace('\u2013', ' ').replace('\u2014', ' ')
        except:
            pass
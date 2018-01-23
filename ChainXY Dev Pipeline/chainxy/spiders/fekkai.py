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

class fekkai(scrapy.Spider):
    name = "fekkai"
    parse_address={'enabled':True}

    def start_requests(self):
        url = 'https://www.fekkai.com/salons'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for link in response.xpath('//ul[@class="salon-list"]//li//a/@href').extract():
            yield scrapy.Request(url=link, callback=self.parse_store)

    def parse_store(self, store):
        item = ChainItem()
        item['store_name'] = store.xpath('//div[@class="salon-location"]/text()').extract_first()
        item['address2'] = ''
        item['city'] = ''
        item['state'] = ''
        item['zip_code'] = ''
        item['country'] = 'United States'
        item['phone_number'] = ''
        detail = store.xpath('//address//text()').extract()
        address = ''
        for de in detail:
            if 'ph' in de.lower():
                item['phone_number'] = de.lower().replace('ph:', '')
            else:
                if self.validate(de) != '':
                    address += self.validate(de) + ', '
        item['address'] = address
        item['latitude'] = ''
        item['longitude'] = ''
        item['store_hours'] = ''
        hour_list = store.xpath('//div[@class="hours"]//div[@class="row"]')
        h_temp = ''
        for hour in hour_list:
            h_temp += hour.xpath('.//span[@class="days"]/text()').extract_first() + ' '+ hour.xpath('.//span[@class="times"]/text()').extract_first() + ', '
        item['store_hours'] = h_temp[0: len(h_temp)-2]
        item['coming_soon'] = ''
        yield item

    def validate(self, item):
        try:
            return item.strip().replace('\n', '').replace('\t','').replace('\r', '').encode('ascii','ignore').strip().replace('\xe9', '')
        except:
            pass
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

class peetsandtea(scrapy.Spider):
    name = "peetsandtea"
    domain = "http://www.peets.com/"
    start_urls = ["http://www.peets.com/stores/peets-stores/stores-store-list.html"]
    parse_address={'enabled':True}

    def parse(self, response):
        store_list = response.xpath('//div[@class="storeItem"]')
        for store in store_list:
            item = ChainItem()
            item['store_name'] = self.validate(store.xpath('./strong/text()').extract_first())
            item['store_hours'] = self.validate(store.xpath('./span[@class="tastingTimes"]/text()').extract_first())
            detail = store.xpath('./text()').extract()
            address = ''
            item['phone_number'] = ''
            for de in detail:
                if '(' in de:
                    item['phone_number'] = self.validate(de)
                else:
                    if self.validate(de) != '':
                        address += self.validate(de) + ', '
            item['country'] = 'United States'
            item['address'] = address
            item['latitude'] =  ''
            item['longitude'] = ''
            item['store_type'] = ''
            item['other_fields'] = ''
            item['coming_soon'] = ''  
            yield item
                

    def validate(self, item):
        try:
            return item.strip().replace('\n', '').replace('\t','').replace('\r', '').encode('ascii','ignore').replace('\u2013', ' ').replace('\u2014', ' ')
        except:
            pass


        


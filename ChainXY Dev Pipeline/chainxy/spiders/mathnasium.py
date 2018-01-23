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

class mathnasium(scrapy.Spider):
    name = 'mathnasium'
    domain = 'http://www.mathnasium.com'
    history = []

    def start_requests(self):
        init_urls = ['http://www.mathnasium.com/maps/maps/search?country=USA',
                    'http://www.mathnasium.com/maps/maps/search?country=CAN']

        for url in init_urls:
            yield scrapy.Request(url=url, callback=self.parse) 

    def parse(self, response):
        state_list = self.eliminate_space(response.xpath('//a[@class="btn btn-mini"]/@href').extract())
        for state in state_list:
            url = self.domain + state
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        data = self.validate(response.body.split('function getCoords(position) {')[1].split('//This assumes that')[0])
        data = data.replace('locations = [', '[')[:-1]
        store_list = json.loads(data)
        url_list = response.xpath('//div[@class="container clear-b"]//div[@class="row"]')
        cnt = 0
        for url in url_list:
            store = store_list[cnt]['UserFranchise']
            item = ChainItem()
            item['store_name'] = self.validate(store['name'])
            item['store_number'] = self.validate(store['webpage_id'])
            item['address'] = self.validate(store['address_1'])
            item['address2'] = self.validate(store['address_2'])
            item['city'] = self.validate(store['city'])
            item['state'] = self.validate(store['state_province'])
            item['zip_code'] = self.validate(store['zip_postal'])
            item['country'] = self.validate(store['country'])
            item['phone_number'] = self.validate(store['phone_number_1'])
            item['latitude'] = self.validate(store['location_latitude'])
            item['longitude'] = self.validate(store['location_longitude'])
            url = self.validate(url.xpath('./div')[3].xpath('./a/@href').extract_first())
            if url:
                url = self.domain + url
                request = scrapy.Request(url=url, callback=self.parse_detail)
                request.meta['item'] = item
                if item['store_number'] not in self.history:
                    self.history.append(item['store_number'])
                    yield request
            else:
                yield item
            cnt += 1

    def parse_detail(self, response):
        item = response.meta['item']
        hour_list = response.xpath('//div[@id="collapseOne"]//div[@class="panel-body"]//table[@class="table"]//tbody//tr')
        h_temp = ''
        hour_list = self.eliminate_space(hour_list.xpath('.//text()').extract())
        cnt = 1
        for hour in hour_list:
            if hour:
                h_temp += hour
                if cnt % 2 == 0:
                    h_temp += ', '
                else:
                    h_temp += ' '
                cnt += 1
        try:
            item['store_hours'] = h_temp[:-2].encode('raw-unicode-escape').replace('\\u2013', ' ')
        except:
            item['store_hours'] = h_temp[:-2]
        yield item

    def eliminate_space(self, items):
        tmp = []
        for item in items:
            if self.validate(item) != '':
                tmp.append(self.validate(item))
        return tmp

    def validate(self, item):
        try:
            return item.strip()
        except:
            return ''
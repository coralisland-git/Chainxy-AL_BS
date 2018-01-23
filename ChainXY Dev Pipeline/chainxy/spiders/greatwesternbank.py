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

class greatwesternbank(scrapy.Spider):
    name = 'greatwesternbank'
    domain = 'https://www.greatwesternbank.com'
    history = []

    def start_requests(self):
        init_url = 'https://www.greatwesternbank.com/locations/'
        yield scrapy.Request(url=init_url, callback=self.parse)

    def parse(self, response):
        count = int(response.xpath('//div[@class="location-search-results"]//li[@class="pag-nav-last"]//a/@href').extract_first().split('=')[1])
        for cnt in range(0, count):
            url = self.domain + '/locations?p=' + str(cnt)
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        location_list = response.xpath('//div[@class="location-search-results"]//div[@class="location"]//h2//a/@href').extract()
        for location in location_list:
            location = self.domain + location
            yield scrapy.Request(url=location, callback=self.parse_detail)

    def parse_detail(self, response):
        item = ChainItem()
        item['store_name'] = self.validate(response.xpath('//h1[@class="space-below"]/text()').extract_first())
        item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]//text()').extract_first())
        item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
        item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())
        item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
        item['country'] = 'United States'
        item['phone_number'] = self.validate(response.xpath('//span[@itemprop="telephone"]/text()').extract_first())
        h_temp = ''
        hour_list = self.eliminate_space(response.xpath('//time[@itemprop="openingHours"]//text()').extract())
        cnt = 1
        for hour in hour_list:
            h_temp += hour
            if cnt % 2 == 0:
                h_temp += ', '
            else:
                h_temp += ' '
            cnt += 1
        item['store_hours'] = h_temp[:-2]
        if item['address'] != '':
            yield item          

    def validate(self, item):
        try:
            return item.strip().replace(';','')
        except:
            return ''

    def eliminate_space(self, items):
        tmp = []
        for item in items:
            if self.validate(item) != '':
                tmp.append(self.validate(item))
        return tmp

    def str_concat(self, items, unit):
        tmp = ''
        for item in items[:-1]:
            if self.validate(item) != '':
                tmp += self.validate(item) + unit
        tmp += self.validate(items[-1])
        return tmp

from __future__ import unicode_literals
import scrapy
import json
import csv
import requests
import re
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem

class TemplateSpider(scrapy.Spider):
    name = "template"

    def start_requests(self):
        url = ''
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for link in response.xpath('').extract():
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
        yield item

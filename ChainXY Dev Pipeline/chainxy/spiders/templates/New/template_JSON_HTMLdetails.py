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
    #parse_address={'enabled':True}

    def parse(self, response):
        #JSON in <script>
        j = response.body.split('var storeLocations = ')[1]
        stores = json.loads(j)

        #JSON in url
        stores = json.loads(response.body)#["features"]
        for store in stores:
            item = ChainItem()

            htmlWithinJSON = etree.HTML(store['property1']['property2'])
            item['coming_soon'] = htmlWithinJSON.xpath('')

            item['store_name'] = store['name']
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

            detailsURL = htmlWithinJSON.xpath('').extract_first()
            request = scrapy.Request(url=self.base_url + detailsURL, callback=self.parse_detail)
            request.meta['item'] = item
            yield request

    def parse_detail(self, response):
        item = response.meta['item']
        item['store_hours'] = response.xpath('').extract()
        yield item

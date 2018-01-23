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
from chainxy.seeds import Seed
from lxml import html
from lxml import etree
import pdb

class Aaronbrothers(scrapy.Spider):
    name = "aaronbrothers"
    domain = "http://www.aaronbrothers.com/"
    history = []

    def start_requests(self):
        seed = Seed()
        seed.setConfig(seed_type="grid", distance="250", countries=['US'], regions=['ALL'], sample=False)
        s = seed.query_points()
        for p in s['results']:
            url="http://www.aaronbrothers.com/wp-admin/admin-ajax.php?action=store_search&lat="+p['latitude']+"&lng="+p['longitude']+"&max_results=100&search_radius=500"
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        store_list = json.loads(response.body)
        if store_list:
            for store in store_list:
                item = ChainItem()
                item['store_name'] = store['store']
                item['store_number'] = store['id']
                item['address'] = store['address']
                item['address2'] = store['address2']
                item['city'] = store['city']
                item['state'] = store['state']
                item['zip_code'] = store['zip']
                item['country'] = store['country']
                item['phone_number'] = store['phone']
                item['latitude'] = store['lat']
                item['longitude'] = store['lng']
                hour_list = etree.HTML(store['hours']).xpath('//text()')
                h_temp = ''
                cnt = 1
                for hour in hour_list:
                    h_temp += hour
                    if cnt % 2 == 0:
                        h_temp += ', '
                    else:
                        h_temp += ' '
                    cnt += 1
                item['store_hours'] = h_temp[:-2]
                item['coming_soon'] = ''
                if item['store_name']+item['store_number'] not in self.history:
                    self.history.append(item['store_name']+item['store_number'])
                    yield item




        


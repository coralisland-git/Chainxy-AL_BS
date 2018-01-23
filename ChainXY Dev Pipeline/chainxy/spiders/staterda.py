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

class staterda(scrapy.Spider):
	name = 'staterda'
	history = []

	def start_requests(self):
		init_url = 'https://state-rda.com/wp-admin/admin-ajax.php'
		header = {
			"Accept":"*/*",
			"Accept-Encoding":"gzip, deflate, br",
			"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
			"X-Requested-With":"XMLHttpRequest"
				}
		seed = Seed()
		seed.setConfig(seed_type="grid", distance="250", countries=['US'], regions=['ALL'], sample=False)
		s = seed.query_points()
		for p in s['results']:
			formdata = {
				"address":"",
				"formdata":"addressInput=",
				"lat":p['latitude'],
				"lng":p['longitude'],
				"name":"",
				"radius":"10000",
				"tags":"",
				"action":"csl_ajax_onload"
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.parse)

	def parse(self, response):
		store_list = json.loads(response.body)['response']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['name'])
			item['store_number'] = self.validate(store['id'])
			item['address'] = self.validate(store['address'])
			item['address2'] = self.validate(store['address2'])
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['state'])
			item['zip_code'] = self.validate(store['zip'])
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store['phone'])
			item['latitude'] = self.validate(store['lat'])
			item['longitude'] = self.validate(store['lng'])
			if item['store_number']+item['store_name'] not in self.history:
				self.history.append(item['store_number']+item['store_name'])
				yield item

	def validate(self, item):
		try:
			return item.strip().replace('#039;', "'").replace(';','')
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
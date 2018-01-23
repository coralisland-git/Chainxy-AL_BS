# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import scrapy
import json
import csv
import os
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

class pretzelmaker(scrapy.Spider):
	name = 'pretzelmaker'
	domain = 'http://pretzelmaker.com/'
	history = []

	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/CA_Cities.json'
		with open(file_path) as data_file:    
			self.location_list.append(json.load(data_file))

	def start_requests(self):
		init_url = 'http://pretzelmaker.com/locations'	
		for location in self.location_list:
			formdata = {
				'locateStore': 'true',
				'address': location['city']
			}
			yield FormRequest(url=init_url, callback=self.body, formdata=formdata)

	def body(self, response):
		data = response.body.decode('utf-8').strip().split('var stores = ')[1].split(';')[0]
		store_list = json.loads(data)
		if store_list:
			for store in store_list:
				item = ChainItem()
				item['store_number'] = self.validate(store['sl_id'])
				item['store_name'] = self.validate(store['sl_name'])
				item['address'] = self.validate(store['sl_address'])
				item['city'] = self.validate(store['sl_city'])
				item['state'] = self.validate(store['sl_state'])
				item['zip_code'] = self.validate(store['sl_zip'])
				item['country'] = self.validate(store['sl_country'])
				item['phone_number'] = self.validate(store['sl_phone'])
				item['latitude'] = self.validate(store['sl_latitude'])
				item['longitude'] = self.validate(store['sl_longitude'])
				if item['store_number']+item['store_name'] not in self.history:
					self.history.append(item['store_number']+item['store_name'])
					yield item

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''
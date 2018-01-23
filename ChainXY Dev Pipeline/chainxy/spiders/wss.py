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

class wss(scrapy.Spider):
	name = "wss"
	domain = "https://www.shopwss.com"
	parse_address={'enabled':True}

	def start_requests(self):
		yield scrapy.Request(url = 'https://www.shopwss.com/core/location-list.htm', callback = self.parse_page)

	def parse_page(self, response):
		store_list = response.xpath('//div[@class="storedetails"]')
		for store in store_list:
			item = ChainItem()
			item['store_number'] = self.validate(store.xpath('.//h1/text()').extract_first()).split('#')[1].split(',')[0].strip()
			item['store_name'] = self.str_concat(self.validate(store.xpath('.//h1/text()').extract_first()).split(',')[1:], ', ')
			detail = self.eliminate_space(store.xpath('.//p//text()').extract())
			address = ''
			item['phone_number'] = ''
			for de in detail:
				if '-' in de and len(de.split('-')) == 3:
					item['phone_number'] = self.validate(de)
					break
				else:
					if self.validate(de) != '':
						address += self.validate(de) + ', '
			item['address'] = address
			item['country'] = "United States"
			item['latitude'] = ''
			item['longitude'] = ''
			item['store_hours'] = detail[len(detail)-1]
			item['other_fields'] = ''
			item['coming_soon'] = ''
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
import scrapy
import json
import csv
import os
import re
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree
from lxml import html

class SouplantationSpider(scrapy.Spider):
        name = 'souplantation'
        history = ['']

        def start_requests(self):
                init_url  = 'https://souplantation.com/'
                yield scrapy.Request(url=init_url, callback=self.body)

        def body(self, response):
                script_dir = os.path.dirname(__file__)
                file_path = script_dir + '/geo/usplaces.json'
                with open(file_path) as data_file:
                        location_list = json.load(data_file)
                for location in location_list:
                        lat = str(location['latitude'])
                        lng = str(location['longitude'])
                        link = 'https://souplantation.com/find-us/?/front/get/'
                        url = link + lat + '/' + lng + '/1'
                        #print(url)
                        yield scrapy.Request(url=url, callback=self.parse)

        def parse(self, store):
                swag = store.xpath('//body').extract_first()
                swag = re.sub('<br>', '@', swag)
                swag = re.sub('<.*?>', '', swag)
                swag = re.sub('\r', '', swag)
                swag = re.sub('\t', '', swag)
                swag = re.sub('\n', '', swag)
                swag = swag.split('},{')
                swag[0] = swag[0][2:]
                swag[-1] = swag[-1][:-2]
                try:
                        for swole in swag:
                                scurr = swole.split(':')
                                if 'Souplantation' in swole and 'error' not in swole and 'Now Closed' not in swole and scurr[1][1:-8] not in self.history:
                                        self.history.append(scurr[1][1:-8])
                                        item = ChainItem()
                                        item['store_number'] = scurr[1][1:-8]
                                        swerve = scurr[4][14:-12].split(' CA ')
                                        swirl = swerve[0].split('@')
                                        item['address'] = swirl[0]
                                        item['city'] = swirl[-1]
                                        item['state'] = 'CA'
                                        item['zip_code'] = swerve[-1]
                                        item['country'] = 'United States'
                                        item['latitude'] = scurr[-3][1:-7]
                                        item['longitude'] = scurr[-2][1:-12]
                                        item['phone_number'] = scurr[5][:-8]
                                        if '92780' in swerve[-1]:
                                                item['zip_code'] = '92780-4689'
                                        if '90712' in swerve[-1]:
                                                item['zip_code'] = '90712-1831'
                                        yield item
                except:
			pass

import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree
import pdb
import datetime
from time import gmtime, strftime
import re
import usaddress
class UbfpersonaltrainingSpider(scrapy.Spider):
    name = "ubfpersonaltraining"
    history = []
        
    def __init__(self, *args, **kwargs):
        states   = open('states.json', 'rb')
        self.states = json.loads(states.read())

    def start_requests(self):
        for state in self.states:
            if 'name' in state:
                request_url = "http://ubfpt.com/" + state['name'].upper() + '/'
                print(request_url)
                request = scrapy.Request(url=request_url, callback=self.parse_store)
                # request.meta['state'] = state['name']
                yield  request

    def parse_store(self, response):
        for store in response.xpath('//div[@id="menu2"]/li'):
            item = ChainItem()

            item['store_name'] =  store.xpath('./a[@class="city"]/text()').extract_first().strip()
            item['store_number'] = ''
            
            addr = store.xpath('./p[@class="address"]/text()').extract()[0]
            
            
            item['address2'] = ''
            try:
                item['phone_number'] = re.findall(r'(\d{3}[-\.\s]\d{3}[-\.\s]\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]\d{4}|\d{3}[-\.\s]\d{4})', addr)[0]
            except:
                item['phone_number'] = ''
            addr = addr[:addr.find(item['phone_number'])] 

            item['city'] = item['store_name']
            # pdb.set_trace()
            item['state'] = ' '.join(addr[addr.rfind(','):].strip().split(' ')[:-1]).replace(',', '')
            item['zip_code'] = addr[addr.rfind(','):].strip().split(' ')[-1]
            item['country'] = "United States"
            if (item['state'] == 'PR' or item['state'] == 'Puerto Rico'):
                item['state'] = 'PR'
                item['country'] = "Puerto Rico"
            item['address'] = addr[:addr.rfind(item['store_name'])].replace('\n','').replace('\r','')

            item['latitude'] = ""
            item['longitude'] = ""

            item['store_hours'] = ''
            
            item['store_type'] = ''
            item['other_fields'] = ''
            item['coming_soon'] = '0'
            
            yield item

    def validate(self, xpath_obj):
        try:
            return xpath_obj.extract_first().strip()
        except:
            return ""


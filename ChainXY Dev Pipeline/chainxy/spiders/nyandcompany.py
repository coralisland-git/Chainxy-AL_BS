from __future__ import unicode_literals
import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from selenium import webdriver
from lxml import html
import time
import usaddress
from chainxy.webdriverfactory import WebDriverFactory

class nyandcompany(scrapy.Spider):
    name = 'nyandcompany'
    domain = 'http://www.nyandcompany.com'
    history = []
    webDriverFactory = WebDriverFactory()

    def start_requests(self):
        self.driver = self.webDriverFactory.get()
        init_url = 'http://www.nyandcompany.com'
        yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        url = 'http://www.nyandcompany.com/locations'
        self.driver.get(url)
        time.sleep(2)
        source = self.driver.page_source.encode("utf8")
        tree = etree.HTML(source)
        location_list = self.eliminate_space(tree.xpath('//select[@id="state"][@class="mobile"]//option/text()'))
        for location in location_list:
            self.driver.find_element_by_xpath('//select[@id="state"][@class="mobile"]').send_keys(location)
            time.sleep(1)
            source = self.driver.page_source.encode("utf8")
            tree = etree.HTML(source)
            store_list = tree.xpath('//ul[@class="results"]//li[@class="storeClass"]//dl[@class="store"]')
            for store in store_list:
                item = ChainItem()
                item['store_name'] = self.validate(store.xpath('./div[@class="title clearfix"]/h3/text()')[0])
                detail = self.eliminate_space(store.xpath('./p[@class="spaced-vert"]')[0].xpath('./text()'))
                address = ''
                for de in detail:
                    address += de + ', '
                address = address[:-2]
                item['address'] = ''
                item['city'] = ''
                addr = usaddress.parse(address)
                for temp in addr:
                    if temp[1] == 'PlaceName':
                        item['city'] += temp[0].replace(',','') + ' '
                    elif temp[1] == 'StateName':
                        item['state'] = temp[0].replace(',','')
                    elif temp[1] == 'ZipCode':
                        item['zip_code'] = temp[0].replace(',','')
                        #if len(item['zip_code']) == 9:
                        #    item['zip_code'] = item['zip_code'][:5]+ '-' + item['zip_code'][-4:]
                    else:
                        item['address'] += temp[0].replace(',', '') + ' '
                item['country'] = 'United States'
                item['phone_number'] = self.validate(store.xpath('./p[@class="spaced-vert"]')[0].xpath('./strong/text()')[0])
                h_temp = ''
                hour_list = self.eliminate_space(store.xpath('./p[@class="hours"]//text()'))
                cnt = 1
                for hour in hour_list:
                    h_temp += hour
                    if cnt % 2 == 0:
                        h_temp += ', '
                    else:
                        h_temp += ' '
                    cnt += 1
                item['store_hours'] = h_temp[:-2]
                if item['store_name']+item['phone_number'] not in self.history:
                    self.history.append(item['store_name']+item['phone_number'])
                    yield item

    def close(self):
        self.webDriverFactory.close()

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
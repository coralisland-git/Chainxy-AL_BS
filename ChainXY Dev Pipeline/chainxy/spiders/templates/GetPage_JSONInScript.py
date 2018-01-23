import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from chainxy.items import ChainItem

class SinglePage_JSONInScript(scrapy.Spider):
    name = "sample"
    uid_list = []
  
    def start_requests(self):
        yield scrapy.Request(url = 'https://www.worldgym.com/findagym?s=search', callback = self.parse_page)

    def parse_page(self, response):
        domain = 'https://www.worldgym.com/'

        #
        # JSON data built into the page
        #
        j = response.body.split('var franhiseeLocations = ')[1].split('];')[0]
        stores = json.loads(j+']')
        
        for store in stores:
            item = ChainItem()

            item['store_name'] = store['LocationName']
            item['address'] = store['Line1']
            item['city'] = store['City']
            item['state'] = store['State']
            item['zip_code'] = store['Postal']
            item['phone_number'] = store['Phone']
            item['latitude'] = store['Latitude']
            item['longitude'] = store['Longitude']
            item['store_number'] = store['LocationNumber']
                        
            yield item        

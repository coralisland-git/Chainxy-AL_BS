import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem

class sevenelevenusa(scrapy.Spider):
    name = "sevenelevenusa"
    uid_list = []

    headers = { "Content-Type": "application/json", "Accept":"*/*" }

    def start_requests(self):
        request_url = "https://www.7-eleven.com/sevenelevenapi/stores_V3/"
        form_data = {
            'features' : [],
            "limit" : "10000",
            "lat" : "34.0522342",
            "lon": "-118.2436849",
            "radius": "500"
        }
        yield scrapy.Request(url=request_url, method="POST", body=json.dumps(form_data), headers=self.headers, callback=self.parse_store)

    # get longitude and latitude for a state by using google map.
    def parse_store(self, response):
        # try:
        stores = json.loads(response.body)
        for store in stores:
            item = ChainItem()
            item['store_name'] = store['name']
            item['store_number'] = store['id']
            item['address'] = store['address']
            item['phone_number'] = store['phone']
            item['city'] = store['city']
            item['state'] = store['state']
            item['zip_code'] = store['zip']
            item['latitude'] = store['lat']
            item['longitude'] = store['lon']
            item['other_fields'] = ""
            item['coming_soon'] = ""
            item['country'] = 'United States'
            if ( item['store_number'] != "" and item["store_number"] in self.uid_list):
                return
            self.uid_list.append(item["store_number"])


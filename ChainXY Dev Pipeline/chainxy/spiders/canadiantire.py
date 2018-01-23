import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from chainxy.seeds import Seed
import pdb

class canadianTire(scrapy.Spider):
    name = "canadiantire"
    search_url = "http://www.canadiantire.ca/dss/services/v2/stores?lang=en&radius=20000&maxCount=1000&lat=44.3403645&lng=-76.1487864"
    split_spiders = ['900','5584']

    def start_requests(self):
        yield FormRequest(url=self.search_url, callback=self.parse_store)

    def parse_store(self, response):
        print('!!!!!!!!!!!!!!!!!')
        seed = Seed()
        seed.setConfig(seed_type="grid", distance="50", countries=['US'], regions=['ALL'], sample=True)
        s = seed.query_points()
        # for p in s['results']:
        pdb.set_trace()
        # stores = json.loads(response.body)
        # for loc in stores:
        #     hours=""
        #     item = ChainItem()

        #     if loc['storeType'] == 'CTP':
        #         item['chain_id'] = '5584'
        #     else:
        #         item['chain_id'] = '900'
        #     item['store_name'] = loc["storeName"]
        #     item['store_number'] = loc["storeNumber"]
        #     item['address'] = loc["storeAddress1"]
        #     item['phone_number'] = loc["storeTelephone"]
        #     item['city'] = loc["storeCityName"]
        #     item['state'] = loc["storeProvince"]
        #     item['zip_code'] = loc["storePostalCode"]
        #     item['country'] = "Canada"
        #     item['latitude'] = ''
        #     item['longitude'] = ''

        #     if hasattr(loc,"workingHours"):
        #         if loc["workingHours"]["general"]["monOpenTime"] == "00:00":
        #            hours = "24 Hours"
        #         else:
        #             hours = "Mon: " + loc["workingHours"]["general"]["monOpenTime"] + "-" + loc["workingHours"]["general"]["monCloseTime"]
        #             hours =  hours + "Tue: " + loc["workingHours"]["general"]["tueOpenTime"] + "-" + loc["workingHours"]["general"]["tueCloseTime"]
        #         item['store_hours'] = hours
        #     else:
        #         item['store_hours'] = ""

        #     item['other_fields'] = ''
        #     # item['geo_accuracy'] = 'Exact'
        #     item['coming_soon'] = '0'
        #     yield item

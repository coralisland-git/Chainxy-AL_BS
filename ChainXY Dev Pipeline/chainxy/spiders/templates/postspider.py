import scrapy
import json
import csv
import re
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem

class PostJsonResponseSpider(scrapy.Spider):
    name = 'postjsonresponsespider'
    history = []

    def __init__(self,*args,**kwargs):
        # load json seed file
        with open('master_us_zip_keyseeds.json') as f:
            self.locations = json.load(f)
    
    def start_requests(self):       
        request_url = 'http://www.goldsgym.com/wp-content/themes/Gold/components/geo-locator/geo-locator.php'
        for location in self.locations:
        
            #
            # change form data for post request
            form_data = {
                "latitude": str(location['latitude']),
                "longitude": str(location['longitude']),
                "radius":"300"
            }
            yield FormRequest(url=request_url, method="POST", formdata=form_data, callback=self.parse)                       
			
    def parse(self, response):
        stores = json.loads(response.body)
        if 'gyms' in stores:
            for store in stores['gyms']:
                if store['gymNumber'] not in self.history:
                    item = ChainItem()
                    try:
                        item['phone_number'] = store['gymPhone1']
                    except:
                        item['phone_number'] = ''
                    try:
                        item['store_hours'] = store['gymHours']
                    except:
                        item['store_hours'] = ''
                    item['store_name'] = store['gymName']
                    item['store_number'] = store['gymNumber']
                    item['address'] = store['gymAddress1']
                    item['address2'] = store['gymAddress2']
                    item['city'] = store['gymCity']
                    item['state'] = store['gymState']
                    item['zip_code'] = store['gymZip']
                    item['country'] = store['gymCountry']
                    #item['phone_number'] = store['gymPhone1'] 
                    item['latitude'] = store['latitude']
                    item['longitude'] = store['longtitude']
                    #item['store_hours'] = store['gymHours']
                    
                    self.history.append(store['gymNumber'])
                    yield item

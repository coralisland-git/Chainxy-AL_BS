import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector

# required import
from chainxy.items import ChainItem

class Spider_MultiPostReq_JsonRes(scrapy.Spider):
    name = "chain name here"
    
    # keep a history of stores to eliminate duplicates
    history = []

    #
    # Override Standard Settings,  use-case: reduce likelihood of being banned by the website
    custom_settings = {
        'CONCURRENT_REQUESTS':1,'DOWNLOAD_DELAY':3,
        'USER_AGENT':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'
    }
    
    #
    # custom header request.  e.g. make sure output is json
    headers = {
        "X-Requested-With":"XMLHttpRequest",
        "Accept":"*/*",
        "Content-Type":"application/json"
    }
    
    def start_requests(self):
        # load seed file
        self.seeds = json.loads(open('cities.json', 'rb').read())

        url = 'https://www.kingsoopers.com/stores/api/graphql'

        form_data = {"query":"query storeSearch($searchText: String!, $filters: [String]!) {\n  storeSearch(searchText: $searchText, filters: $filters) {\n    stores {\n      ...storeSearchResult\n    }\n    fuel {\n      ...storeSearchResult\n    }\n    shouldShowFuelMessage\n  }\n}\n\nfragment storeSearchResult on Store {\n  banner\n  vanityName\n  divisionNumber\n  storeNumber\n  phoneNumber\n  showWeeklyAd\n  showShopThisStoreAndPreferredStoreButtons\n  distance\n  latitude\n  longitude\n  address {\n    addressLine1\n    addressLine2\n    city\n    countryCode\n    stateCode\n    zip\n  }\n  pharmacy {\n    phoneNumber\n  }\n}\n","variables":{"searchText":"AI","filters":[]},"operationName":"storeSearch"}
       
        #
        # loop through seeds to get all locations.  different seed files are used depending on 'density' of chain      
        for seed in self.seeds:
            form_data = {"query":"query storeGeolocationSearch($latitude: String!, $longitude: String!, $filters: [String]!) {\n  storeGeolocationSearch(latitude: $latitude, longitude: $longitude, filters: $filters) {\n    stores {\n      ...storeSearchResult\n    }\n    fuel {\n      ...storeSearchResult\n    }\n    shouldShowFuelMessage\n  }\n}\n\nfragment storeSearchResult on Store {\n  banner\n  vanityName\n  divisionNumber\n  storeNumber\n  phoneNumber\n  showWeeklyAd\n  showShopThisStoreAndPreferredStoreButtons\n  distance\n  latitude\n  longitude\n  address {\n    addressLine1\n    addressLine2\n    city\n    countryCode\n    stateCode\n    zip\n  }\n  pharmacy {\n    phoneNumber\n  }\n}\n",
                         "operationName":"storeSearch"}
            variables = { 'latitude': str(seed['latitude']), 'longitude': str(seed['longitude']), 'filters' : [] }
            form_data['variables'] = variables
            
            yield  scrapy.Request(url=url, method="POST", body=json.dumps(form_data), headers=self.headers, callback=self.parse_store)
            
    def parse_store(self, response):
        
        if json.loads(response.body)["data"]["storeSearch"] is None:
            return
            
        for store in json.loads(response.body)["data"]["storeSearch"]['stores']:
            item = ChainItem()
            
            item['store_name'] = store["vanityName"]
            item['store_number'] = str(store["storeNumber"])
            item['store_type'] = store["banner"]
            item['phone_number'] = store["phoneNumber"]

            item['address'] = store["address"]["addressLine1"]
            item['city'] = store["address"]["city"]
            item['state'] = store["address"]["stateCode"]
            item['zip_code'] = store["address"]["zip"]
            item['country'] = store["address"]["countryCode"]

            item['latitude'] = store["latitude"]
            item['longitude'] = store["longitude"]
            item['geo_accuracy'] = 'original'
            
            # Store Hours
            item['store_hours'] = "  "
            hours = store['hours']
            item['store_hours'] += "Monday " + hours['mondayOpen'] + ' - ' + hours['mondayClose'] + ";" if hours['mondayOpen'] != 'Close' else  " ; Monday Closed"
            item['store_hours'] += "Tuesday " + hours['tuesdayOpen'] + ' - ' + hours['tuesdayClose'] + ";"  if hours['tuesdayOpen'] != 'Close' else  " ; tuesday Closed"
            item['store_hours'] += "Wednesday " + hours['wednesdayOpen'] + ' - ' + hours['wednesdayClose'] + ";"  if hours['wednesdayOpen'] != 'Close' else  " ; Wednesday Closed"
            item['store_hours'] += "Thursday " + hours['thursdayOpen'] + ' - ' + hours['thursdayClose'] + ";"  if hours['thursdayOpen'] != 'Close' else " ; Thursday Closed"
            item['store_hours'] += "Friday " + hours['fridayOpen'] + ' - ' + hours['fridayClose'] + ";"  if hours['fridayOpen'] != 'Close' else " ; Friday Closed"
            item['store_hours'] += "Saturday " + hours['saturdayOpen'] + ' - ' + hours['saturdayClose'] + ";"  if hours['saturdayOpen'] != 'Close' else " ; Saturday Closed"
            item['store_hours'] += "Sunday " + hours['sundayOpen'] + ' - ' + hours['sundayClose']  + ";" if hours['sundayOpen'] != 'Close' else " ; Sunday Closed"

            item['store_hours'] = item['store_hours'][:-2]

            #
            # only return store if not already retrieved by another seed reqest
            if item["store_number"] not in self.history:
                self.history.append(item["store_number"])
                yield item


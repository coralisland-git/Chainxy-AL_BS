from pprint import pprint
import scrapy
import json
from chainxy.items import ChainItem


class mcdonalds(scrapy.Spider):
    name = "mcdonalds"
    store_phones = []
    exact_intl_locations = {'enabled': True}
    # start_urls = ['https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=49.24414580000001&longitude=-123.08692329999997&radius=100000&maxResults=250000&country=us&language=en-us&showClosed=&hours24Text=Open%2024%20hr']
    week_days = ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']

    split_spiders = []
    urls_to_visit = [['3119','https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=44.97&longitude=-93.21&radius=100000&maxResults=250000&country=us&language=en-us'],
                        ['3096', 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=44.97&longitude=-93.21&radius=100000&maxResults=250000&country=ca&language=en-ca'],
                        ['3118', 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=44.97&longitude=-93.21&radius=100000&maxResults=250000&country=gb&language=en-gb'],
                        ['6587', 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=44.97&longitude=-93.21&radius=100000&maxResults=250000&country=se&language=sv-se'],
                        ['6587', 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=55.9394691&longitude=10.17994550000003&radius=100000&maxResults=250000&country=dk&language=da-dk'],
                        ['6587', 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=60.7893233&longitude=10.689804200000026&radius=100000&maxResults=250000&country=no&language=en-no'],
                        ['3108', 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=24.0799008&longitude=45.29000099999996&radius=100000&maxResults=250000&country=saj&language=en-sa'],
                        ['3108', 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=29.3365728&longitude=47.67552909999995&radius=100000&maxResults=250000&country=kw&language=en-kw'],
                        ['3108', 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=24.1671413&longitude=56.114225300000044&radius=100000&maxResults=250000&country=om&language=en-om'],
                        ['3108', 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=23.659703&longitude=53.7042189&radius=100000&maxResults=250000&country=ae&language=en-ae'],
                        ['3108', 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=26.1621079&longitude=50.4501947&radius=100000&maxResults=250000&country=bh&language=en-bh'],
                        ['3108', 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=25.2854473&longitude=51.53103979999992&radius=100000&maxResults=250000&country=qa&language=en-q']]
    for s in urls_to_visit:
        split_spiders.append(s[0])

    def start_requests(self):

        for s in self.urls_to_visit:
            # pprint(s)
            url = s[1]
            request = scrapy.Request(url=url, callback=self.parse)
            request.meta['chain_id'] = s[0]
            yield request



    def parse(self, response):
        stores = json.loads(response.body)
        # pprint(stores)
        if 'features' in stores:
            for store in stores['features']:
                item = ChainItem()


                item['chain_id'] = response.meta['chain_id']
                item['store_number'] = store['properties']['identifiers']['gblnumber']

                item['address'] = store['properties']['addressLine1'].strip()
                #item['address2'] = store['properties']['addressLine2'].strip()
                try:
                    item['phone_number'] = store['properties']['telephone']
                except:
                    pass

                item['latitude'] = store['geometry']['coordinates'][1]
                item['longitude'] = store['geometry']['coordinates'][0]
                item['city'] =  store['properties']['addressLine3'].strip()
                item['state'] = store['properties']['subDivision'].strip()
                item['zip_code'] = store['properties']['postcode'].strip()
                item['country'] = store['properties']['addressLine4'].strip()
                item['geo_accuracy'] = "Exact"

                try:
                    item['store_hours'] = 'Mon: ' + store['properties']['restauranthours']['hoursMonday']
                    item['store_hours'] += '; Tue: ' + store['properties']['restauranthours']['hoursTuesday']
                    item['store_hours'] += '; Wed: ' + store['properties']['restauranthours']['hoursWednesday']
                    item['store_hours'] += '; Thu: ' + store['properties']['restauranthours']['hoursThursday']
                    item['store_hours'] += '; Fri: ' + store['properties']['restauranthours']['hoursFriday']
                    item['store_hours'] += '; Sat: ' + store['properties']['restauranthours']['hoursSaturday']
                    item['store_hours'] += '; Sun: ' + store['properties']['restauranthours']['hoursSunday']
                except:
                    pass

                item['other_fields'] = ", ".join(store['properties']['filterType'])

                for ft in store['properties']['filterType']:
                    if ft =='WALMARTLOCATION':
                        item['store_name']="Walmart"
                        item['store_type']="Walmart"
                    else:
                        item['store_name']="McDonalds"
                        item['store_type']="McDonalds"

                item['coming_soon'] = "1" if store['properties']['openstatus'] == 'COMINGSOON' else "0"
                if item['chain_id'] != '':
                    yield item

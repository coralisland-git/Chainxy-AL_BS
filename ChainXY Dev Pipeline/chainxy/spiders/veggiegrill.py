import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from geopy.geocoders import Nominatim
from lxml import etree
import pdb
import re

class veggiegrill(scrapy.Spider):
    name = "veggiegrill"

    start_urls = ['https://www.veggiegrill.com/all-locations.html']
    storeNumbers = []

    # def __init__(self, *args, **kwargs):
    #     fp = open('cities_us.json', 'rb')
    #     self.cities_ca = json.loads(fp.read())
    #     self.storeNumbers = []


    def start_requests(self):
        url = "https://www.veggiegrill.com/near-you.html?address=los+angeles&bounds=36.642021474426386%2C-119.64109219003905%7C36.914258798286184%2C-119.19477260996092"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        data = response.xpath('//ul[@class="locations__list"]/li/div[@class="location-info"]')
        for d_item in data:
            try:
                item = ChainItem()
                item['store_name'] = d_item.xpath('./p[1]/b/text()').extract_first()
                item['store_number'] = ""
                address = d_item.xpath('./p[1]/text()').extract()
                addr = []
                for addre in address:
                    if addre.strip() != '':
                        addr.append(addre.strip())

                item['address'] = addr[0]
                item['address2'] = ""

                item['phone_number'] =  d_item.xpath('./p[1]/a[1]/text()').extract_first().replace('.', '-')
                item['latitude'] = ""
                item['longitude'] = ""

                item['city'] = addr[-1].split(',')[0]
                item['state'] = addr[-1].split(',')[1].strip().split(' ')[0]
                item['zip_code'] = addr[-1].split(',')[1].strip().split(' ')[1]
                item['country'] = "United States"

                hours = '; '.join(d_item.xpath('./p[2]//text()').extract()).replace('to', '-').replace('; 1', '1').replace(';  ', '').replace('- ;', ' - ')

                item['store_hours'] = hours

                #item['store_type'] = info_json["@type"]
                item['other_fields'] = ""
                item['coming_soon'] = "0" if hours.strip() != '' else '1'

                if item['address'] in self.storeNumbers:
                        continue

                self.storeNumbers.append(item['address'])
                
                yield item

            except:
                pdb.set_trace()
                continue

    def validate(self, item):
        try:
          return item.strip().replace('\n', '').replace('\t','').replace('\r', '').encode('ascii','ignore').replace('\xa0', ' ')
        except:
          pass
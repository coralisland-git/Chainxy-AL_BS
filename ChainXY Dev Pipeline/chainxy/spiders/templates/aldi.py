# -*- coding: utf-8 -*-
import scrapy
import json
from chainxy.items import ChainItem
from chainxy.seeds import Seed
import re


class AldiSpider(scrapy.Spider):
    name = "aldi"
    allowed_domains = ["aldi.us", "yellowmap.de"]
    start_urls = ['https://aldi.us/stores/']

    history = []

    def parse(self, response):
        seed = Seed()
        seed.setConfig(seed_type="grid", distance="10", countries=['US'], regions=['ALL'], sample=False)
        s = seed.query_points()
        for p in s['results']:
            print "Row " + str(p['rowcount']) + " of " + str(s['rowcount']) + ": \n" + str(p)
            url = 'https://aldi.us/stores/en-us/Search?SingleSlotGeo=&LocX=%s&LocY=%s&Mode=None' % (p['longitude'],p['latitude'])
            yield scrapy.Request(url=url, callback=self.parse_details)

    def parse_details(self, response):
        for res in response.xpath('.//ul[@id="resultList"]/li[@data-json]'):
            str_json = res.xpath('./div[@class="row"]/ancestor::li[@data-json]/@data-json').extract_first()
            dt = json.loads(str_json)
            sid = dt['id']
            item = ChainItem()

            item['store_name'] = res.xpath('.//strong[@class="resultItem-CompanyName" and  @itemprop="name"]/text()').extract_first()
            item['store_number'] = ''
            item['address'] = res.xpath('.//address[@itemprop="address"]/div[@itemprop="streetAddress"]/text()').extract_first().strip()
            item['address2'] = ''
            item['phone_number'] = res.xpath('.//a[@itemprop="telephone"]/text()').extract_first()
            if item['phone_number']: item['phone_number'] = item['phone_number'].strip()
            item['city'] = res.xpath('.//div[@itemprop="addressLocality"]/@data-city').extract_first().split(',')[0]
            item['state'] = res.xpath('.//div[@itemprop="addressLocality"]/@data-city').extract_first().split(',')[-1]
            item['zip_code'] = res.xpath('.//div[@itemprop="addressLocality"]/text()').extract_first().strip().split(' ')[-1]
            item['country'] = 'us'
            item['latitude'] = dt['locY']
            item['longitude'] = dt['locX']
            st1=[]
            for h in res.xpath('.//table[@class="openingHoursTable"]/tr'):
                d1 = h.xpath('.//td[@class="open"]/text()').extract_first()
                d2 = h.xpath('.//td[@class="open openingTime"]/text()').extract_first()
                st1.append('%s %s' % (d1,d2))

            other=[]
            for feat in dt['bcInformation']:
                other.append(feat['text'])
            # try:
            #     item['other_fields'] = "Comments: " + dt['comment'] + "; Features: " + ", ".join(other)
            # except:
            item['other_fields'] = "Features: " + ", ".join(other)

            # CANT TRUST THE ISOPEN ATTRIBUTE - DOESNT SEEM TO BE RIGHT
            # if dt['isOpen'] is True:
            item['coming_soon'] = '0'
            #
            # else:
            #     item['coming_soon'] = '1'
            #     item['store_hours'] = ''
            # item['coming_soon'] = '0'
            try:
                item['store_hours'] = ';'.join(st1)
            except:
                item['store_hours'] = ''

            if sid not in self.history:
                self.history.append(sid)
                yield item

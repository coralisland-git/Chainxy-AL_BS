# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import scrapy
from chainxy.items import ChainItem


class AcecanadaSpider(scrapy.Spider):
    name = 'acecanada'
    allowed_domains = ['ace-canada.com']
    start_urls = ['http://www.ace-canada.com/cms/app/system/modules/ca.truserv.web/apps/storeLocatorHandler.jsp']

    item = ChainItem()
    history = ['']

    def parse(self, response):
        data = json.loads(response.body_as_unicode())
        for store in data['stores']:
            self.item['store_number'] = store['sID']
            self.item['store_name'] = store['sName']
            lines = store['sAd'].rsplit(',', 3)
            self.item['address'] = lines[0]
            self.item['address2'] = ''
            self.item['city'] = lines[1]
            self.item['state'] = lines[2]
            self.item['zip_code'] = lines[3]
            self.item['country'] = 'CA'
            self.item['phone_number'] = store['sPh']
            if self.item['phone_number'] is None:
                self.item['phone_number'] = ''
            self.item['latitude'] = store['sLat']
            self.item['longitude'] = store['sLong']
            self.item['store_hours'] = ''
            self.item['store_type'] = ''
            self.item['other_fields'] = ''

            if (self.item['address']+self.item['phone_number']) not in self.history:
                self.history.append(self.item['address']+self.item['phone_number'])
                yield self.item

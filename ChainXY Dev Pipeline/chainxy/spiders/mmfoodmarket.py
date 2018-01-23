import scrapy
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
import urllib2
import requests
import json

session = requests.Session()
headers = {'Content-Type': 'application/json; charset=UTF-8',
           'X-Requested-With': 'XMLHttpRequest',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
           }

class MMFoodMarketSpider(Spider):
    name = "mmfoodmarket"
    start_urls = ['https://www.mmfoodmarket.com/en/store-locator']

    def parse(self, response):

        item = ChainItem()
        
        for x in range(0, 600):
            url = 'https://www.mmfoodmarket.com/en/stores/' + str(x)
            page_text = urllib2.urlopen(url)
            sh = ''
            item['address'] = ''
            for line in page_text:
                if '<div class="store-info store-details">' in line:
                    next(page_text)
                    item['store_name'] = next(page_text).split('<')[0].replace('\t','').strip()
                    item['store_number'] = str(x)
                    g = next(page_text)
                    h = next(page_text)
                    i = next(page_text)
                    j = next(page_text)
                    k = next(page_text)
                    l = next(page_text)
                    item['country'] = 'Canada'
                    item['address'] = h.split('<')[0].replace('\t','').strip()
                    item['address2'] = ''
                    if '<br />' in i:
                        item['address2'] = i.split('<')[0].replace('\t','').strip()
                        item['city'] = i.split('>')[1].split(',')[0]
                    else:
                        item['city'] = i.split(',')[0].replace('\t','').strip()
                    item['state'] = j.split('&')[0].replace('\t','').strip()
                    item['zip_code'] = k.split('<')[0].replace('\t','').strip()
                    item['phone_number'] = l.replace('\t','').strip().replace('\r','').replace('\n','')
                if 'hdnLat" value="' in line:
                    item['latitude'] = line.split('hdnLat" value="')[1].split('"')[0]
                    item['longitude'] = next(page_text).split('hdnLong" value="')[1].split('"')[0]
                if 'StoreHours_lbl' in line:
                    if sh == '':
                        sh = line.split('StoreHours_lbl')[1].split('Time_')[0] + ': ' + line.split('">')[1].split('<')[0]
                    else:
                        sh = sh + ';' + line.split('StoreHours_lbl')[1].split('Time_')[0] + ': ' + line.split('">')[1].split('<')[0]
            item['store_hours'] = sh
            item['store_type'] = "M&M Food Market"
            item['other_fields'] = ''
            item['coming_soon'] = '0'
            if item['address'] != '':
                yield item


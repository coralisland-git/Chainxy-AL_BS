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

class MasterCutsSpider(Spider):
    name = "mastercuts"
    start_urls = ['http://www.borics.com']

    def parse(self, response):
        urls = []
        url = 'https://www.signaturestyle.com/content/dam/sitemaps/signaturestyle/sitemap_signaturestyle_en_us.xml'
        page_text = urllib2.urlopen(url)
        for line in page_text:
            if '/mastercuts-' in line and '.html' in line:
                urls.append(line.split('<loc>')[1].split('<')[0])

        item = ChainItem()
        for url in urls:
            page_text = urllib2.urlopen(url)
            sh = ''
            for line in page_text:
                if 'var salonDetailSalonID = "' in line:
                    item['store_number'] = line.split('var salonDetailSalonID = "')[1].split('"')[0]
                if '<h2 class="hidden-xs salontitle_salonlrgtxt">' in line:
                    item['store_name'] = line.split('<h2 class="hidden-xs salontitle_salonlrgtxt">')[1].split('<')[0]
                if '<span itemprop="streetAddress">' in line:
                    item['address'] = line.split('<span itemprop="streetAddress">')[1].split('<')[0]
                    item['address2'] = ''
                    item['country'] = 'United States'
                if 'itemprop="addressLocality">' in line:
                    item['city'] = line.split('op="addressLocality">')[1].split('<')[0]
                if 'itemprop="addressRegion">' in line:
                    item['state'] = line.split('itemprop="addressRegion">')[1].split('<')[0]
                if '"postalCode">' in line:
                    item['zip_code'] = line.split('"postalCode">')[1].split('<')[0]
                if 'id="sdp-phone" href="">' in line:
                    item['phone_number'] = line.split('id="sdp-phone" href="">')[1].split('<')[0]
                if 'itemprop="latitude" content="' in line:
                    item['latitude'] = line.split('itemprop="latitude" content="')[1].split('"')[0]
                if 'itemprop="longitude" content="' in line:
                    item['longitude'] = line.split('itemprop="longitude" content="')[1].split('"')[0]
                if '<span class="' in line and 'day">' in line:
                    if sh == '':
                        sh = next(page_text).split('content="')[1].split('"')[0]
                    else:
                        sh = sh + ';' + next(page_text).split('content="')[1].split('"')[0]
            item['store_type'] = "MasterCuts"
            if item['state'] == 'PR':
                item['country'] = 'Puerto Rico'
            if ' ' in item['zip_code']:
                item['country'] = 'Canada'
            item['other_fields'] = ''
            item['store_hours'] = sh
            item['coming_soon'] = '0'
            yield item


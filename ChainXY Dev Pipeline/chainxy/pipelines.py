# -*- coding: utf-8 -*-
import csv
import time
import datetime
import hashlib
import re
import logging
import os
import platform
import socket
import json
import urllib2
import requests
import pprint
from chainxy.AddressParser import AddressParser
from pprint import pprint
import sys
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import HTMLParser
from decimal import Decimal
from scrapy import signals, exceptions
from scrapy.exporters import CsvItemExporter

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from scrapy.exceptions import NotConfigured
from mapbox import Geocoder


class ChainxyPipeline(object):
    addressParser = AddressParser()
    geocoder = ''
    in_test_mode = False
    is_split_spider = False
    record_count = 1

    parser = HTMLParser.HTMLParser()

    # HANDLE LOGGING
    stream = StringIO()
    files = {}
    logger = logging.getLogger()
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter('[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # FILES TO CLEANUP COUNTRIES AND REGIONS
    with open('./chainxy/pipelines_country_matching.json') as data_file:
        country_list = json.load(data_file)

    with open('./chainxy/pipelines_region_matching.json') as data_file2:
        region_list = json.load(data_file2)

    def init_mapbox_geocoder(self):
        self.geocoder = Geocoder(access_token='pk.eyJ1IjoidGV0cmFkIiwiYSI6ImNqY2pwd2xocjNmemczM28zeDB6NjdsdzEifQ.n5uAAYe8taTEvLUOClSo1Q')

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):

        self.logger.debug('##########################################')
        self.logger.info('New Spider Opened')
        spider.started_on = datetime.datetime.now()
        spider.master_chain_id = 0
        spider.master_scrape_id = 0
        self.logger.info("This scrape is being run in TEST mode and will NOT write records to ChainXY, just the CSV export")

        ids = []

        self.is_split_spider = hasattr(spider, 'split_spiders')

        # Get Chain Id's all cleaned up
        if self.is_split_spider and len(spider.split_spiders) > 1:
            # Remove Duplicates from split_spiders
            chainset = set(spider.split_spiders)
            result = list(chainset)
            for ch_id in result:
                ids.append(str(ch_id))
            self.logger.info('This is a split spider scrape. The Chain Id\'s used are: ' + ", ".join(ids))
        elif self.is_split_spider and len(result) == 0:
            sys.exit('This is a split_spiders scrape, but no Chain Id\'s were specified in split_spiders')
        else:
            ids.append(spider.master_chain_id)
            self.logger.info('This is a single spider scrape running in Test Mode. A Chain Id of \'0\' was assigned.')

        spider.chain_id = ids
        spider.chain_run_ids = []

        # Create Chain Run(s) (Scrape ID)
        counter = 0
        for ids in spider.chain_id:
            spider.chain_run_ids.append([str(ids), str(counter)])
            counter += 1
        self.logger.debug('The following Scrape Id\'s are system generated because you\'re in test mode')

        for scrapes in spider.chain_run_ids:
            if str(spider.master_chain_id) == str(scrapes[0]):
                spider.master_scrape_id = scrapes[1]
                self.logger.info('The master Scrape Id was set to: ' + str(spider.master_scrape_id))


        try:
            if self.is_split_spider:
                file = open('scrape_%s_multi_%s.csv' % (spider.name, datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d')), 'w+b')
            else:
                file = open('scrape_%s_%s.csv' % (spider.name, datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d')), 'w+b')
        except:
            # if the file is opened/locked etc
            try:
                if self.is_split_spider:
                    file = open('scrape_%s_multi_%s.csv' % (spider.name, datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d-%H%M')), 'w+b')
                else:
                    file = open('scrape_%s_%s.csv' % (spider.name, datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d-%H%M')), 'w+b')
            except:
                self.logger.warn('Could not write the export file. ')

        self.files[spider] = file
        self.exporter = CsvItemExporter(file)
        self.exporter.fields_to_export = ['chain_id','chain_run_id','store_type','store_number','store_name','address','address2','city','state','zip_code','country','phone_number','distributor_name','coming_soon','closed','geo_accuracy','latitude','longitude','store_hours','other_fields','hash_primary','hash_secondary']
        self.exporter.start_exporting()


    def process_item(self, item, spider):
        # Allow the record to be exported
        export = True

        """Save Chain_Record in the database.
        This method is called for every item pipeline component.
        """
        self.logger.debug("******************")
        self.logger.info("New Record")

        # UTF Encoding
        for p in item.fields.iterkeys():
            if p in item and item[p] is not None:
                item[p] = str(item[p]).encode('utf-8').strip()
                item[p] = self.parser.unescape(item[p])
            else:
                item[p] = ''


        # If the spider has ignore_distributors set to True
        if hasattr(spider, 'ignore_distributors') and spider.ignore_distributors:
            if item['distributor_name'] != '': #$  or item['distributor_name'] is not None:
                export = False
                self.logger.info("Ignoring Record because contains a distributior_name (" + str(item['distributor_name']) + ")")

        # If the item has no Chain ID, but the split_spiders attribute is there
        if self.is_split_spider and (item['chain_id'] == '' or item['chain_id'] is None):
            self.logger.critical('This is a split chain spider, but a location was received that did not have a Chain ID Assigned. Fix it.')
            export = False
            return

        if item['chain_id'] == '':
            item['chain_id'] = spider.master_chain_id

        try:
            for ids in spider.chain_run_ids:
                if str(ids[0]) == str(item['chain_id']):
                    self.logger.debug("Record was assigned to ChainScrape Id " + str(ids[1]))
                    item['chain_run_id'] = ids[1]
        except Exception as e:
            self.logger.critical("Could not set the chain run id for the location.")
            return


        if item['geo_accuracy'].lower() == 'exact':
            item['geo_accuracy'] = 'Exact'
            self.logger.info('The geo_accuracy was set to Exact because it was set to Exact in the spider.')


        try:
            item['latitude'] = Decimal(item['latitude'])
            item['longitude'] = Decimal(item['longitude'])
        except Exception as e:
            item['latitude'] = 0
            item['longitude'] = 0

        if Decimal(item['latitude']) <= -90 or Decimal(item['latitude']) >= 90 or Decimal(item['longitude']) <= -180 or Decimal(item['longitude']) >= 180:
            self.logger.warn("An Invaid Lat/Long was found. Setting it to 0/0 instead.")
            item['latitude'] = 0
            item['longitude'] = 0

        try:
            item['coming_soon'] = (True if item['coming_soon'] == '1' else False)
        except Exception as e:
            self.logger.info("Could not set coming soon properly: " + str(e))
            item['coming_soon'] = False

        try:
            item['closed'] = (True if item['closed'] == '1' else False)
        except Exception as e:
            self.logger.info("Could not set closed status properly: " + str(e))
            item['closed'] = False

        try:
            item['store_name'] = item['store_name'][:120]
        except Exceptuib as e:
            self.logger.info("Could not cleanup store name properly: " + str(e))
            item['store_name'] = ''

        item['city'] = item['city'][:79]
        item['zip_code'] = item['zip_code'][:29]

        # check for coming soon
        for p in item.fields.iterkeys():
            if p in item and item[p] is not None and isinstance(item[p], basestring):
                if 'other_fields' not in p:
                    if ('coming soon' in item[p].lower() or 'opening soon' in item[p].lower() or 'coming ' in item[p].lower() or 'opening ' in item[p].lower()) and 'lycoming' not in item[p].lower():
                        item['coming_soon'] = '1'
        if export:
            self.fill_address(item)

        if hasattr(spider, 'parse_address') and spider.parse_address and export:
            self.parse_singleaddress(item, spider.parse_address)

        if (item['zip_code'] == '' or item['state'] == '' or item['country'] == '' or item['city'] == '') and export:
            if item['latitude'] != 0:
                self.fill_address_reverse(item)
            else:
                self.fill_address_forward(item)

        if item['latitude'] != 0 and len(item['geo_accuracy']) == 0:
            item['geo_accuracy'] = 'CHAIN'

        self.fix_country(item)
        self.clean_statezip(item)
        self.strip_tags(item)
        self.breaks_to_commas(item)
        self.strip_tags(item)
        self.strip_stuff(item)
        self.strip_non_alphanumeric(item)
        self.fix_country(item)
        self.state_prov_to_abbrev(item)

        if hasattr(spider, 'exact_intl_locations') and spider.exact_intl_locations and export:
            if item['country'].lower() not in ['united states', 'canada', 'puerto rico', 'american samoa', 'guam', 'us virgin islands','northern mariana islands'] and (item['latitude'] != 0 and item['latitude'] != 0):
                item['geo_accuracy'] = "Exact"
                self.logger.info("Setting Geo Accuracy to Exact because exact_intl_locations is enabled, and the country is not Canada or the US")

        if hasattr(spider, 'force_countries') and export:
            allowed_countries = [k.lower() for k in spider.force_countries]
            if 'united states' in allowed_countries:
                allowed_countries.append('guam')
                allowed_countries.append('american samoa')
                allowed_countries.append('puerto rico')
                allowed_countries.append('us virgin islands')
                allowed_countries.append('northern mariana islands')
            if item['country'].lower() not in allowed_countries:
                export = False
                self.logger.info("Ignoring Record from " + item['country'] + " because it was not specified in the force_countries parameter (" + str(spider.force_countries) + ")")

        if export:
            self.logger.info('Exporting Record #' + str(self.record_count) + '\n' + str(item))
            self.record_count += 1
            if hasattr(self, 'exporter'):
                self.exporter.export_item(item)
                # return item

    def spider_closed(self, spider, reason):
        cxy_status_code = 0
        cxy_status_comment = []

        if str(reason).lower() != 'finished'.lower():
            cxy_status_code = 999
            cxy_status_comment.append("The spider was prematurely terminated (" + str(reason) + ")")
            self.logger.warn("Scrape ended prematurely because of: " + str(reason))

        stats = spider.crawler.stats.get_stats()

        logging.info('The spider has been closed! Reason: ' + str(reason))
        if 'item_scraped_count' not in stats:
            logging.error("The scrape returned no records")
            cxy_status_comment.append("The scrape returned no records")
            cxy_status_code = 999
        elif ('log_count/ERROR' in stats and stats['log_count/ERROR'] > 0) or ('log_count/CRITICAL' in stats and stats['log_count/CRITICAL'] > 0):
            # cxy_status_comment.append("")
            cxy_status_code = 999

        self.logger.info("Updating Chain Status and Logs")
        self.write_log_output(spider)

    def get_extract_notes(self, spider):
        extract_method = ['--Extract Notes---']
        try:
            extract_method.append("In Test Mode: " + str(self.in_test_mode))
        except:
            logging.debug("Could not append is_server_run to the log")
        try:
            extract_method.append("Time to run: " + str(datetime.datetime.now() - spider.started_on))
        except:
            logging.debug("Could not append time to run to the log")

        try:
            extract_method.append("Spider: " + str(spider.name))
        except:
            logging.debug("Could not append Spider Name to the log")

        if self.is_split_spider:
            extract_method.append("Split Spider: Yes")
        else:
            extract_method.append("Split Spider: No")


        try:
            extract_method.append("Username: " + os.getlogin())
        except:
            logging.debug("Could not append username to the log")
        try:
            extract_method.append("Platform: " + str(os.uname()))
        except:
            logging.debug("Could not append platform to the log")

        try:
            extract_method.append("Hostname: " +  socket.gethostname())
        except:
            logging.debug("Could not append hostname to the log")

        return "\n".join(extract_method)


    def write_log_output(self, spider):
        # Write the log file to disk
        log_contents = self.get_extract_notes(spider)
        log_contents = log_contents + "\n\n--Log File--\n"
        log_contents = log_contents + self.stream.getvalue()
        try:
            if self.is_split_spider:
                file_1 = open('scrape_%s_multi_%s.log' % (spider.name, datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d')), 'w+')
            else:
                file_1 = open('scrape_%s_%s.log' % (spider.name, datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d')), 'w+')

            with file_1 as f:
                f.write(log_contents)
            logging.debug("Wrote the log file successfully to disk.")
        except:
            if self.is_split_spider:
                file_1 = open('scrape_%s_multi_%s.log' % (spider.name, datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d-%H%M')), 'w+')
            else:
                file_1 = open('scrape_%s_%s.log' % (spider.name, datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d-%H%M')), 'w+')

            with file_1 as f:
                f.write(log_contents)
            logging.debug("The original log file is probably open and was probably locked, so it wrote to a new file with the time appended to the filename.")

    def fill_address(self, item):
        if item['latitude'] != 0:
            if item['zip_code'] == '' or item['state'] == '' or item['country'] == '':
                response = self.geocoder.reverse(lon=item['longitude'], lat=item['latitude'])
                self.logger.info("Geocoder Reponse - Status: " + str(response.status_code).strip())
                georesponse = response.geojson()
                if georesponse is not None and 'features' in georesponse:
                    logged = []
                    for f in georesponse['features']:
                        if f['id'].startswith('postcode') and item['zip_code'] == '':
                            item['zip_code'] = f['text']

                        if f['id'].startswith('region') and item['state'] == '':
                            item['state'] = f['text']

                        if f['id'].startswith('country') and item['country'] == '':
                            item['country'] = f['text']
                        logged.append('  {place_name}: {id}'.format(**f))
                    self.logger.info("Geocoder Address Returned:\n" + " \n".join(logged))

    def fill_address_reverse(self, item):
        if item['zip_code'] == '' or item['state'] == '' or item['country'] == '' or item['city'] == '':
            if item['latitude'] != 0:
                response = self.geocoder.reverse(lon=item['longitude'], lat=item['latitude'])
                self.logger.info("Geocoder \n\n Reponse - Status: " + str(response.status_code).strip())
                json = response.geojson()
                if 'features' in json:
                    logged = []
                    for f in json['features']:
                        if f['id'].startswith('postcode') and item['zip_code'] == '':
                            item['zip_code'] = f['text']

                        if f['id'].startswith('region') and item['state'] == '':
                            item['state'] = f['text']

                        if f['id'].startswith('country') and item['country'] == '':
                            item['country'] = f['text']

                        if f['id'].startswith('place') and item['city'] == '' and 'Montreal' not in item['city']:
                            item['city'] = f['text']

                        if item['city'] == 'Washington':
                            item['city'] = 'District of Columbia'
                            item['state'] = 'Washington'
                        logged.append('  {place_name}: {id}'.format(**f))
                    self.logger.info("Geocoder Address Returned:\n" + " \n".join(logged))

    def fill_address_forward(self, item):
        acc = ''
        if len(item['address']) > 0:
            acc += str(item['address'])
        if len(item['address2']) > 0:
            acc += str(item['address2'])
        if len(item['city']) > 0:
            acc += ', ' + str(item['city'])
        if len(item['state']) > 0:
            acc += ', ' + str(item['state'])
        if len(item['zip_code']) > 0:
            acc += ', ' + str(item['zip_code'])
        if len(item['country']) > 0:
            acc += ', ' + str(item['country'])

        response = self.geocoder.forward(acc)
        json = response.geojson()
        if 'features' in json:
            features = json['features']
            if (features is not None and len(features) > 0):
                if 'context' in features[0]:
                    self.logger.info("Geocode Results:")
                    for f in features[0]['context']:
                        # self.logger.debug(f['id'] + ' ----> ' + f['text'])
                        if f['id'].startswith('postcode') and (item['zip_code'] == '' or item['zip_code'] is None):
                            self.logger.info('Filled zip_code with: ' + f['text'])
                            item['zip_code'] = f['text']
                        if f['id'].startswith('region') and item['state'] == '':
                            self.logger.info('Filled state with: ' + f['text'])
                            item['state'] = f['text']

                        if f['id'].startswith('country') and (item['country'] == '' or item['country'] is None):
                            self.logger.info('Filled country with: ' + f['text'])
                            item['country'] = f['text']

                        if f['id'].startswith('place') and item['city'] == '':
                            self.logger.info('Filled city with: ' + f['text'])
                            item['city'] = f['text']

    def fix_country(self, item):
        if item['country']:
            try:
                if self.country_list[item['country'].lower()]:
                    loc = self.country_list[item['country'].lower()]
                    if loc != "":
                        item['country'] = loc
            except:
                pass

    def clean_statezip(self, item):
        if item['country'] in ['United States','Canada']:
            state = item['state'].title()
            if state.lower() in self.region_list:
                item['state'] = self.region_list[state.lower()]

        item['state'] = item['state'].upper()
        item['zip_code'] = item['zip_code'].upper()

    def strip_tags(self, item):
        cleanr = re.compile('<.*?>')
        for i in item:
            item[i] = re.sub(cleanr, '', str(item[i]))
            item[i] = re.sub("\u2013", "-", item[i])

    def breaks_to_commas(self, item):
        cleanr = re.compile('\n')
        for i in item:
            item[i] = re.sub(cleanr, ', ', str(item[i]))

    def parse_singleaddress(self, item, options):
        time.sleep(0.1)

        self.addressParser.parse(item, options)

    def strip_non_alphanumeric(self, item):
        cleanr = re.compile('Saturday.')
        for i in item:
            if i == 'store_hours':
                item[i] = re.sub(cleanr, 'Saturday ', str(item[i]))

    def strip_tags(self, item):
        cleanr = re.compile('<.*?>')
        for i in item:
            item[i] = re.sub(cleanr, '', str(item[i]))

    def breaks_to_commas(self, item):
        cleanr = re.compile('\n')
        for i in item:
            item[i] = re.sub(cleanr, ', ', str(item[i]))

    def strip_stuff(self, item):
        cleanr = re.compile('&.*?;')
        for i in item:
            if i == 'store_name':
                item[i] = re.sub(cleanr, '', str(item[i]))

    def state_prov_to_abbrev(self, item):
        item['state'] = item['state'].decode('utf-8')
        if item['state'].lower() in self.region_list.keys():
            item['state'] = self.region_list[item['state'].lower()]

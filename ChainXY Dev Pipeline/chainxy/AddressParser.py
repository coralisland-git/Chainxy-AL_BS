import requests
import json
from pprint import pprint
import logging

class AddressParser():

    logger = logging.getLogger('scrapy.chainxy.addressparser')

    def parse(self, item, options):
        result = requests.get("http://libpostal.chainxy.com?address="+item['address'].replace('#','%23').replace('&','%26'))
        try:
            print ""
            parsed = result.json()
            self.logger.info("Using Parse Address yielded the following results:\n" + str(parsed))
        except:
            self.logger.warn("Could not parse address!")
            return

        addPart = ['','','','']
        unit = road = housenumber = house = center = ''

        hasRoad = False
        lastWasNumber = False

        for itm in parsed:
            key = itm['component']
            value = itm['value']

            #print '>>> ' + key + ' ---- ' + value

            if key == 'postcode':
                item['zip_code'] = value.upper()
                lastWasNumber = False
            elif key == 'country':
                if item['country'] == '' or item['country'] is None:
                    item['country'] = value.title()
                lastWasNumber = False
            elif key == 'city':
                if item['city'] == '' or item['city'] is None:
                    item['city'] = value.title()
                    lastWasNumber = False
            elif key == 'state':
                if item['state'] == '' or item['state'] is None:
                    item['state'] = value.title()
                    lastWasNumber = False
            elif key == 'unit':
                unit = value.title()
                lastWasNumber = False
            elif key == 'suburb':
                if lastWasNumber:
                    # first road is usually the center
                    center = road
                road = value.title()
                lastWasNumber = False
            elif key == 'road':
                if lastWasNumber:
                    # first road is usually the center
                    center = road
                road = value.title()
                lastWasNumber = False
            elif key == 'house':
                house = value.title()
                lastWasNumber = False
            elif key == 'house_number':
                if value.title().startswith('#'):
                    unit = value.title()
                    lastWasNumber = False
                else:
                    housenumber = value.title()
                    lastWasNumber = True

        item['address'] = ('%s %s' % (housenumber, road)).strip()
        if len(unit) > 0:
            item['address'] = item['address'] + ', ' + unit
        if len(house) > 0:
            popAddress2 = True
            if 'ignoreAddress2' in options:
                popAddress2 = not options['ignoreAddress2']

            if popAddress2:
                item['address2'] = ('%s' % (house)).strip()

        if len(item['address']) == 0 and len(item['address2']) > 0:
            item['address'] = item['address2']
            item['address2'] = ''

        # workaround for cases where address line 1 is parsed with only a single character (e.g. 4 Complexe Desjardins)
        if len(item['address']) < 3 and len(item['address2']) > 0:
            item['address'] = item['address'] + ' ' + item['address2']
            item['address2'] = ''

    #def fix_abbrev(self):
    #    for key in dictionary.iterkeys():
    #        address.upper().replace(key, dictionary[key])

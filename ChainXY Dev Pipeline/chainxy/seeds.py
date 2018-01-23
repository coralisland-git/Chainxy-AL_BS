import sqlite3
from pprint import pprint
import logging
import os
import scrapy


class Seed(object):
    logger = logging.getLogger('scrapy.chainxy.seeds')

    def setConfig(self, seed_type="grid", distance="250", countries=[''], regions=['US'], sample=False):
        self.logger.info("Setting up new grid. Config being used:")

        # Samples
        self.Sample = sample

        # Seed Types
        self.Seed_Type = seed_type
        self.logger.info("Seed Type: {}".format(self.Seed_Type))

        # Distances
        self.Distance = distance
        if self.Distance not in ["10", "30", "50", "70", "90", "110", "150", "190", "250"]:
            raise ValueError("Distance for grid is not valid. '10','30','50','70','90','110','150','190','250' are all valid disrances.")
        else:
            self.logger.info("Seed Distance: {}".format(self.Distance))

        # countries
        self.Countries = countries
        self.logger.info("Seed Countries: {}".format(self.Countries))
        if isinstance(self.Countries, list) is False:
            raise ValueError("Countries provided need to be in the form of a list, even if there is only one country. You must specify at least one country. ")
        elif self.Countries[0] == '':
            raise ValueError("No Country was provided. You must specifiy at least one country. ")
        else:
            # self.Countries = map(str.upper, self.Countries)
            self.Countries = self.Countries
            if 'UK' in self.Countries:
                self.Countries.append('GB')
                self.Countries.remove('UK')
            # Add US Territories
            if 'US' in self.Countries:
                self.Countries.append('PR')
                self.Countries.append('AS')
                self.Countries.append('GU')
                self.Countries.append('MP')
                self.Countries.append('VI')

        # regions
        self.Regions = regions
        self.logger.info("Seed Regions: {}".format(self.Regions))

    def get_config(self, config_type):
        if config_type.lower() == 'type'.lower():
            return self.Seed_Type
        elif config_type.lower() == 'distance'.lower():
            return self.Distance
        elif config_type.lower() == 'countries'.lower():
            return self.Countries
        elif config_type.lower() == 'regions'.lower():
            return self.Regions
        elif config_type.lower() == 'sample'.lower():
            return self.Sample
        else:
            self.logger.error("Config Type not found")

    def query_points(self):
        self.logger.debug("=======================================")
        self.logger.info("Connecting to applicable databases...")
        records = []
        rowcount = 0
        if self.get_config('countries')[0] == 'ALL':
            self.Countries = []
            files = [f for f in os.listdir('./chainxy/seed_files/')]
            for f in files:
                # print f
                if 'seed_' in f and 'master' not in f and '.db' in f:
                    self.Countries.append(f.split('_')[1].split('.')[0])

        for c in self.get_config('countries'):
            self.logger.debug("Opening ./chainxy/seed_files/seed_" + c + ".db")
            try:
                conn = sqlite3.connect('./chainxy/seed_files/seed_' + c + '.db')
            except:
                self.logger.error("Could not connect to seed database")
            self.c = conn.cursor()

            # STANDARD DISTANCE-BASED GRIDs
            if self.get_config('type') == 'grid' and self.get_config('distance'):
                # self.logger.debug('Running Grid Seed File')

                query = 'SELECT pts.point_id, pts.latitude, pts.longitude, prs.pair_type, prs.pair_key, prs.pair_text, pts.country_code, pts.country_name, pts.region_code, pts.region_name, pts.closest_full_postal, pts.closest_short_postal '
                query = query + ' from main.pairs prs '
                query = query + ' inner join main.points pts on pts.point_id = prs.point_id '
                if self.get_config('Countries')[0] != 'ALL':
                    query = query + " and pts.country_code in ('" + "','".join(self.Countries) + "') "
                if self.get_config('Regions')[0] != 'ALL':
                    query = query + " and pts.region_code in ('" + "','".join(self.Regions) + "') "
                query = query + ' where prs.pair_type = "' + self.get_config('type') + '" and pair_key = "' + self.get_config('distance') + '" '
                query = query + ' and  (pts.nothing_there = 0 or pts.nothing_there is null)'

            elif self.get_config('type') == 'postalcode':
                self.logger.debug('Running Unique Postal Code Seed File')

                query = 'SELECT pts.point_id, pts.latitude, pts.longitude, prs.pair_type, prs.pair_key, prs.pair_text, pts.country_code, pts.country_name, pts.region_code, pts.region_name, pts.closest_full_postal, pts.closest_short_postal '
                query = query + ' from main.pairs prs '
                query = query + ' inner join main.points pts on pts.point_id = prs.point_id '
                query = query + ' where prs.pair_type = "postalcode" '
                if self.get_config('Countries')[0] != 'ALL':
                    query = query + " and pts.country_code in ('" + "','".join(self.Countries) + "') "
            else:
                self.logger.error('Type received was not recognized. ')

            if self.get_config('sample'):
                query = query + ' limit 10'
            query = query + ' ;'

            try:
                result = self.c.execute(query)
            except:
                self.logger.error("Could not execute query")
            for row in result:
                rowcount += 1
                records.append({
                    'rowcount': rowcount,
                    'id': row[0],
                    'latitude': str(row[1]),
                    'longitude': str(row[2]),
                    'type': row[3],
                    'value': row[4],
                    'country_code': row[6],
                    'country_name': row[7],
                    'region_code': row[8],
                    'region_name': row[9],
                    'full_postal': row[10],
                    'short_postal': row[11]
                })
        results = []
        if rowcount == 0:
            results = {'status': 'ERROR', 'rowcount': rowcount, 'message': 'No seed points were returned with the query provided', 'query': query}
            self.logger.error(results)
        else:
            results = {'status': 'OK', 'rowcount': rowcount, 'results': records, 'query': query}
            self.logger.info("Seed File Returned " + str(rowcount) + " points. ")
            self.logger.debug("=======================================")

            return(results)

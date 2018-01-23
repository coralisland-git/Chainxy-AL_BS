# print("=========  Checking	========")
# with open('response-'+self.name+'.html', 'wb') as f:
# 	f.write(response.body)





# def validate(self, item):
# try:
#   return item.strip().replace('\n', '').replace('\t','').replace('\r', '').encode('ascii','ignore').replace('\u2013', ' ').replace('\u2014', ' ')
# except:
#   pass



# seed = Seed()
# seed.setConfig(seed_type="grid", distance="250", countries=['US'], regions=['ALL'], sample=False)
# s = seed.query_points()
# for p in s['results']:
# 	formdata = {
# 		"address":"",
# 		"formdata":"addressInput=",
# 		"lat":p['latitude'],
# 		"lng":p['longitude'],
# 		"name":"",
# 		"radius":"10000",
# 		"tags":"",
# 		"action":"csl_ajax_onload"
# 	}
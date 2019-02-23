import urllib
from datetime import datetime
from itertools import product
from agrimetscraper.utils.configsetter import Configger
from agrimetscraper.utils.dbopen import dbconnect
from agrimetscraper.utils.mylogger import SetLog
from agrimetscraper.utils.validations import Validator
from agrimetscraper.utils.converters import StringToList





def __UrlEncodedQuery(**kwargs):

	kw_copy = kwargs.copy()
	for key, value in kwargs.items():

		if value == '':
			del kw_copy[key]

	return urllib.parse.urlencode(kw_copy)


def __UrlJoin(baseurl, encoded_query):
	return baseurl+encoded_query


class UrlPreprocessor:

	def __init__(self, siteids, params, stride=20):
		
		assert type(siteids) == list, "Input 'siteids' should be type of list of a tuple [(site1, ), (site2, )]"
		assert type(params) == list, "Input 'params' should be type of a list"
		assert type(stride) == int, "Input 'stride' should be of type int"
		assert stride > 0 & stride <= 20, "stride value is between 1 and 20"

		self.siteids = siteids
		self.params = params
		self.stride = stride

	@staticmethod
	def __UnpackSiteIDs(idlist):
		"""
		Unpack IDs and combine it with params
		"""

		# itertools import product ---> returns [(x, y), (a, b)]
		assert type(idlist) == list, 'idlist -- type of list'

		product_id_params = [' '.join([i[0], i[1].lower()]) for i in product(idlist, self.params)]

		return ','.join(product_id_params)


	def UrlPipeline(self):

		sites = [i[0] for i in self.siteids]

		if len(self.sites) > 0:
			for i in range(0, len(sites), self.stride):
				partial_ids = sites[i:i+stride]
				yield UrlMaker.__UnpackSiteIDs(partial_ids)
		else:
			raise ValueError('No site ids found')



class UrlAssembly:


	@staticmethod
	def GetSites(cfg_path) 

		Validator.path_checker(cfg_path)

		# set up logger
		logger = SetLog(cfg_path, 'UrlAssembly||GetSites')

		# load database
		config = Configger(cfg_path)
		dbpath = config.Getcfg('DB_SETTINGS', 'database_path')
		station = config.Getcfg('DB_SETTINGS', 'stationtable')


		# states
		states = config.Getcfg('STATION_SETTINGS', 'states')

		if start_time != "":
			start_time = datetime.strptime(start_time, "%Y-%m-%d").date()
		if end_time != "":
			end_time = datetime.strptime(end_time, "%Y-%m-%d").date()
		if type(backdays) == str and backdays != "":
			backdays = int(backdays)


		col_siteid = 'siteid'
		col_state = 'state'


		# turn into list
		
		States = StringToList(states)
		States_placeholder = ','.join(['?']*len(States))
		sql_sites = '''SELECT {} FROM {} WHERE {} in ({})'''.format(col_siteid, station, col_state, States_placeholder)


		try:
			conn = dbconnect(dbpath)
			logger.info('Open database in {}'.format(__name__))
		except:
			logger.error('Error in open database in {}'.format(__name__))
			print('Error in open database in {}'.format(__name__))


		cur.execute(sql_sites, tuple(States))
		sites = cur.fetchall()

		return sites


		@classmethod
		def GetUrls(cls, cfg_path):		

			Validator.path_checker(cfg_path)
			# set up logger
			logger = SetLog(cfg_path, 'UrlAssembly||GetUrls')
			#url
			baseurl = config.Getcfg('URL_SETTINGS', 'baseurl')
			urlformat = config.Getcfg('URL_SETTINGS', 'format')
			wparams = config.Getcfg('URL_SETTINGS', 'weather_parameters')

			start_time = config.Getcfg('URL_SETTINGS', 'start')
			end_time = config.Getcfg('URL_SETTINGS', 'end')
			backdays = config.Getcfg('URL_SETTINGS', 'back')

			params = StringToList(wparams)

			sites = UrlAssembly.GetSites(cfg_path)

			logger.info('Unpacking sites and parameters')
			unpack_sites = [ i for i in UrlPreprocess(sites, params).UrlPipeline()]
			queries = [ __UrlEncodedQuery(list=i, format=urlformat, start=start_time, end=end_time, back=backdays) for i in unpack_sites]

			logger.info('Making Urls')
			urls = [__UrlJoin(baseurl, i) for i in queries]

			logger.info('Urls Generated')
			print('Urls Generated')
			return urls










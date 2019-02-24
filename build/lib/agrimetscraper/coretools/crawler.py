from agrimetscraper.coretools.dataprocess import Dataprocessor
from agrimetscraper.coretools.dataprocess import DataToSql
from agrimetscraper.coretools.downloader import Downloader
from agrimetscraper.coretools.urlbuilder import UrlAssembly
from agrimetscraper.utils.dbopen import dbconnect
from agrimetscraper.utils.configsetter import Configger
import pandas as pd
from agrimetscraper.utils.converters import StringToList

class Crawler:

	def __init__(self, url):
		self.url = url

	@staticmethod
	def __SingleUrlToDataframe(url, params):

		data, description = Downloader.download(url)

		one_df = [ Dataprocessor.Makedf(i, description, params) for i in data ]

		return pd.concat(one_df)

	@staticmethod
	def __MultipleUrlToDataframe(urls, params):
		assert type(urls) == list, "Urls is type of a list"

		weather_df = [ Crawler.__SingleUrlToDataframe(i, params) for i in urls ]

		return pd.concat(weather_df)



	@classmethod
	def WriteCrawlToSql(cls, cfg_path):

		config = Configger(cfg_path)

		wparams = config.Getcfg('URL_SETTINGS', 'weather_parameters')
		params = StringToList(wparams)

		print("Write weather table to configure file")
		dbpath = config.Getcfg('DB_SETTINGS', 'database_path')
		weathertable = 'Weather_data'

		config.Setcfg('DB_SETTINGS', 'weathertable', weathertable)

		sites = UrlAssembly.GetSites(cfg_path)
		urls = UrlAssembly.GetUrls(cfg_path)

		big_df = cls.__MultipleUrlToDataframe(urls, params)


		conn = dbconnect(dbpath)

		print('Writing data to the database')
		DataToSql.WriteToSql(dbpath, weathertable, big_df)




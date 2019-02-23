from agrimetscraper.coretools.dataprocess.Dataprocessor import Makedf
from agrimetscraper.coretools.dataprocess.DataToSql import WriteToSql
from agrimetscraper.coretools.downloader import Downloader
from agrimetscraper.coretools.urlbuilder import UrlAssembly
from agrimetscraper.utils.dbopen import dbconnect
from agrimetscraper.utils.configsetter import Configger
import pandas as pd

class Crawler:

	def __init__(self, url):
		self.url = url

	@staticmethod
	def __SingleUrlToDataframe(url):

		data, description = Downloader.download(url)

		one_df = [ Makedf(i, description) for i in data ]

		return pd.concat(one_df)

	@staticmethod
	def __MultipleUrlToDataframe(urls):
		assert type(urls) == list, "Urls is type of a list"

		weather_df = [ Crawler.__SingleUrlToDataframe(i) for i in urls ]

		return pd.concat(weather_df)



	@classmethod
	def WriteCrawlToSql(cls, cfg_path):

		config = Configger(cfg_path)

		print("Write weather table to configure file")
		dbpath = config.Getcfg('DB_SETTINGS', 'database_path')
		weathertable = 'Weather_data'

		config.Setcfg('DB_SETTINGS', 'weathertable', weathertable)

		sites = UrlAssembly.GetSites(cfg_path)
		urls = UrlAssembly.GetUrls(cfg_path)

		big_df = cls.__MultipleUrlToDataframe(urls)


		conn = dbconnect(dbpath)

		print('Writing data to the database')
		WriteToSql(dbpath, weathertable, big_df)




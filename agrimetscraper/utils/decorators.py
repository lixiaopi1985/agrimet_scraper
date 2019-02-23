from functools import wraps
import sqlite3
import sys
import pandas as pd
from agrimetscraper.utils.configsetter import Configger

def DataToSql_Decorator(dbpath, dbtable):
	def DataToSql(func):
		"""
		This is a decorator for writing Pm, Ram, Rja, into sql using pandas
		"""

		@wraps
		def wrapper(*args, **kwargs):

			try:
				conn = sqlite3.connect(dbpath)
			except sqlite3.DatabaseError as e:
				print(e)

			# load df
			try:
				df_to_sql = func(*args, **kwargs)
			except:
				print('An error occured when loading pandas dataframe in {}'.format(func.__name__))
				sys.exit(1)

			try:
				df_to_sql.to_sql(dbtable, conn)
			except:
				print('An error occured when writing dataframe into database')
				sys.exit(1)


			print("Writing summary {} data to SQL Completed".format(func.__name__))

		return wrapper
	return DataToSql



def scheduler_decorator(cfg_path):
	def cronjob(func):
		def wrapp_cronjob(**kwargs):
			
			config = Configger(cfg_path)
			# settings
			minute = config.Getcfg('SCHEDULER_SETTINGS', 'minutes')
			hour = config.Getcfg('SCHEDULER_SETTINGS', 'hour')
			dom = config.Getcfg('SCHEDULER_SETTINGS', 'dom')
			mon = config.Getcfg('SCHEDULER_SETTINGS', 'mon')
			dow = config.Getcfg('SCHEDULER_SETTINGS', 'dow')

			func(min=minute, hour=hour, dom=dom, mon=mon, dow=dow)

		return wrapp_cronjob
	return cronjob
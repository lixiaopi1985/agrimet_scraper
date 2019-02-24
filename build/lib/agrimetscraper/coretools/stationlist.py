import os
import sys
import pandas as pd
from agrimetscraper.utils import mylogger
from agrimetscraper.utils.validations import Validator
from agrimetscraper.utils.dbopen import dbconnect
from agrimetscraper.utils.configsetter import Configger



def __inject_data(pandas_series, **kwargs):
	series2tuple = tuple(pandas_series)

	existed_data = kwargs['existed']
	cur = kwargs['cur']
	sql = kwargs['sql']

	if series2tuple in existed_data:
		print("Data existed. Skip")
	else:
		cur.execute(sql, series2tuple)




def StationToSql(cfg_path):

	logger = mylogger.SetLog(cfg_path, '{}'.format(__name__))

	stationtable = 'Stations'
	# check path
	logger.info('Checking config file path')
	Validator.path_checker(cfg_path)

	print('Open config file')
	logger.info('Open config file')
	config = Configger(cfg_path)
	stationurl = config.Getcfg('STATION_SETTINGS', 'station_url')
	dbpath = config.Getcfg('DB_SETTINGS', 'database_path')
	config.Setcfg('DB_SETTINGS', 'stationtable', stationtable)
	
	# if pass return request result
	if Validator.url_validator(stationurl):
		stationcsv = pd.read_csv(stationurl, header = 1)


	stationcsv = stationcsv.loc[:, ~stationcsv.columns.str.contains('^Unnamed')]
	cols = ','.join(list(stationcsv.columns))
	cols_placeholder = ','.join(['?']*len(stationcsv.columns))

	try:
		conn = dbconnect(dbpath)
	except:
		logger.error('Error connect to the database', exc_info=True)
		sys.exit(1)

	cur = conn.cursor()
	sql_create = '''CREATE TABLE IF NOT EXISTS {} ({})'''.format(stationtable, cols)
	cur.execute(sql_create)


	# check existed data
	cur.execute('''SELECT * FROM {}'''.format(stationtable))
	existed_data = cur.fetchall()

	sql = '''INSERT INTO {} ({}) VALUES ({})'''.format(stationtable, cols, cols_placeholder)
	logger.info('Writing stations into database')
	stationcsv.apply(__inject_data, axis=1, existed=existed_data, cur=cur, sql=sql)

	conn.commit()
	conn.close()

	logger.info('Successfully write data in the database')
	print('Successfully write data in the database')




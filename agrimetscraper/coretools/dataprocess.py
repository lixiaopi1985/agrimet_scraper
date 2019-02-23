import numpy as np
import pandas as pd
from tqdm import tqdm
from agrimetscraper.utils import configsetter, dbopen, converters, mylogger, validations, decorators
from agrimetscraper.utils.decorators import DataToSql_Decorator


"""

need to fix
num_param
cols
"""


class Dataprocessor:
	"""
	From requests string to dataframe
	"""

	@staticmethod
	def __extractdates(data_string):

		assert type(data_string) == str, "Input data_string is type of a string"
		
		# in list
		data = converters.StringToList(data_string)

		return data[0]


	@staticmethod
	def __extractsites(description):

		assert type(description) == str, "Input description is type of a string"

		tolist = list(map(lambda x: x.split('_')[0], StringToList(description, ',')[1:]))
		sites = []
		for  i in tolist:
			if not i in sites:
				sites.append(i)

		return sites


	@staticmethod
	def __reshape(alist):
		assert type(alist) == list, "alist is type of a list"

		if len(alist) == 0:
			raise ValueError('alist cannot be empty')

		toarrays = np.asarray(alist)

		return reshaped = toarrays.reshape(-1, num_params)


	@staticmethod
	def __datatoarray(data_string):
		assert type(data_string) == str, 'Input data is type of a string'

		data = StringToList(data_string)[1:]

		reshaped_data = Dataprocessor.__reshape(data)

		return reshaped_data


	@classmethod
	def Makedf(cls, data_string, description):

		try:
			dates = cls.__extractdates(data_string)
			sites = cls.__extractsites(description)
			wdata = cls.__datatoarray(data_string)
			df = pd.DataFrame(wdata, columns= cols)

		except:
			print('Error occured when forming database')


		df['Dates'] = dates
		df['Sites'] = sites
		df = df[cls.cols]

		df.replace('', np.nan, inplace=True)
		df.dropna(inplace=True)

		return df


class DataToSql:

	@staticmethod
	def __existed_data(dbpath, dbtable, cols):

		col_placeholder = ','.join(cols)

		conn = dbopen.dbconnect(dbpath)
		cur = conn.cursor()

		try:
			sql_create = '''CREATE TABLE IF NOT EXISTS {} ({})'''.format(dbtable, col_placeholder)
			cur.execute(sql_create)
		except:
			print("An error occured in {}".format(__class__.__name__))


		sql_exist = '''SELECT * FROM {}'''.format(dbtable)
		try:
			cur.execute(sql_exist)
		except:
			print("An error occured in getting existed data")

		existed = cur.fetchall()


		conn.close()

		return existed

	@classmethod
	def WriteToSql(cls, dbpath, dbtable, df):


		cols = df.columns

		cols_placeholder = ','.join(['?']*len(cols))
		sql = '''INSERT INTO {} VALUES ({})'''.format(dbtable, cols_placeholder)

		existed = cls.__existed_data(dbpath, dbtable, cols)


		conn = dbopen.dbconnect(dbpath)
		cur = conn.cursor()

		try:
			for i in tqdm(range(len(df))):
				row = tuple(df.iloc[i, :])
				if not row in existed:
					cur.execute(sql, row)
					conn.commit()

		except:
			print('An error occured in {}'.format(__name__))


		conn.close()
		print('\nWriting Weather data to the database completed.\n')




class DailyDataSummarise:



	def __init__(self, cfg_path):

		self.config = configsetter.Configger(cfg_path)

		self.dbpath = config.Getcfg('DB_SETTINGS', 'database_path')
		self.weathertable = config.Getcfg('DB_SETTINGS', 'Weather_data')
		self.params =  config.Getcfg('URL_SETINGS', 'weather_parameters')

	def DumpToCsv(self):
		"""
		Get Weather data out
		"""

		conn = dbopen.dbconnect(self.dbpath)

		sql = '''SELECT * FROM {}'''.fromat(self.weathertable)
		self.outdf = pd.read_sql_query(sql, conn)

		self.outdf.replace('', np.nan, inplace=True)
		self.outdf.dropna(inplace=True)


		# check column
		if 'Dates' in outdf.columns:
			self.outdf.Dates = pd.to_datetime(self.outdf.Dates, format='%Y-%m-%d')
		else:
			raise ValueError("No column named 'Dates' found")


		self.outdf['Years'] = list(map(lambda x: x.year, self.outdf.Dates))
		self.outdf['Months'] = list(map(lambda x: x.month, self.outdf.Dates))


		params = converters.StringToList(self.params)

		for i in params:
			self.outdf[i] = self.outdf[i].astype(dtype=float)

		return self



	@DataToSql_Decorator(self.dbpath, 'Ram_Summary')
	def TableRam(self, grby=['Years', 'Sites']):
		"""Ram  -  # of days with rain >= 0.25 mm [April & May]"""

		self.config.Setcfg('DB_SETTINGS', 'Ram_Summary', 'Ram_Summary')

		df_copy = self.outdf.copy()
		# change datatype
		df_copy.PP = list(map(LengthConverter, df_copy.PP))
		columns = df_copy.columns

		# select April and May
		df_AM = df_copy[(df_copy['Months'] == 4) | (df_copy['Months'] == 5) ]
		# select PP >= 0.25
		df_25 = df_AM[df_AM.PP >= 0.25]

		df_25_copy = df_25.copy()
		df_25_copy['Ram'] = 1
		#aggregate
		df_ram = df_25_copy.groupby(by=grby).count()

		updated_cols = columns.drop(grby)

		df_ram.drop(updated_cols, inplace=True, axis=1)

		return df_ram

	@DataToSql_Decorator(self.dbpath, 'Rja_Summary')
	def TableRja(self, grby=['Years', 'Sites']):
		"""Rja  -  # of days with rain >= 0.25 mm [July & August]"""


		self.config.Setcfg('DB_SETTINGS', 'Rja_Summary', 'Rja_Summary')

		df_copy = self.outdf.copy()

		# change datatype
		df_copy.PP = list(map(LengthConverter, df_copy.PP))
		columns = df_copy.columns

		# select July and August
		df_AM = df_copy[(df_copy['Months'] == 7) | (df_copy['Months'] == 8) ]
		# select PP >= 0.25
		df_25 = df_AM[df_AM.PP >= 0.25]

		df_25_copy = df_25.copy()
		df_25_copy['Rja'] = 1
		#aggregate
		df_Rja = df_25_copy.groupby(by=grby).count()

		updated_cols = columns.drop(grby)

		df_Rja.drop(updated_cols, inplace=True, axis=1)

		return df_Rja

	@DataToSql_Decorator(self.dbpath, 'Pm_Summary')
	def TablePm(self, grby=['Years', 'Sites']):
		"""
		Pm - Total precipitation during May when daily mininum temperature was >= 5
		"""

		self.config.Setcfg('DB_SETTINGS', 'Pm_Summary', 'Pm_Summary')


		df_copy = self.outdf.copy()
		df_copy.MN = list(map(TemperatureConverter, df_copy.MN))
		df_copy.PP = list(map(LengthConverter, df_copy.PP))

		columns = df_copy.columns

		# select May
		df_may = df[df['Months'] == 5]
		# select MN > 5c
		df_Pm = df_may[df_may.MN >= 5]


		# aggregate
		df_Pm = df_Pm.groupby(by=grby).sum()

		return df_Pm[['PP']]

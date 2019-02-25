#!/usr/bin/env python
import sys
import argparse
from agrimetscraper.coretools.stationlist import StationToSql
from agrimetscraper.coretools.crawler import Crawler
from agrimetscraper.coretools.dataprocess import DailyDataSummarise
from agrimetscraper.utils.mylogger import SetLog



def Pipelines(cfg_path):

	logger = SetLog(cfg_path, 'Pipeline')

	# get station data
	try:
		logger.info("Writing Station Information to the database")
		StationToSql(cfg_path)
	except:
		logger.exception("An error occured in StationToSql", exc_info=True)
		print('An error occured in StationToSql')
		sys.exit(1)

	# Crawl weather data
	try:
		logger.info('Crawling weather data and write to sql')
		Crawler.WriteCrawlToSql(cfg_path)
	except:
		logger.exception('An error occured in Crawler.WriteCrawlerToSql', exc_info=True)
		print('An error occured in Crawler.WriteCrawlerToSql')
		sys.exit(1)

	# Datasummary
	try:
		logger.info('Summarise weather data')
		summ = DailyDataSummarise(cfg_path)
		df = summ.DumpToCsv()
	except:
		logger.exception('An error occured in DailyDataSummarise', exc_info=True)
		print('An error occured in DailyDataSummarise')
		sys.exit(1)
	
	try:
		logger.info('Create Ram Table')
		summ.TableRam()
	except:
		logger.exception('An error occured during Ram Table', exc_info=True)
		print('An error occured during Ram Table')
		sys.exit(1)

	try:
		logger.info('Create Raj Table')
		df.TableRja()
	except:
		logger.exception('An error occured during Rja Table', exc_info=True)
		print('An error occured during Rja Table')
		sys.exit(1)

		
	try:
		logger.info('Create Pm Table')
		df.TablePm()
	except:
		logger.exception('An error occured during Pm Table', exc_info=True)
		print('An error occured during Pm Table')
		sys.exit(1)


	logger.info('Weather data has been successfully updated and summarized\n')
	print('Weather data has been successfully updated and summarized')




if __name__ == '__main__':
    	cfg_path = sys.argv[1]
    	Pipelines(cfg_path)

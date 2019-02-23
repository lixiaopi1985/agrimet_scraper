from agrimetscraper.coretools.crawler import Crawler
from agrimetscraper.dataprocess import DailyDataSummarise
from agrimetscraper.utils.mylogger import SetLog
import sys



def Pipelines(cfg_path):



	logger = SetLog(cfg_path, '{}'.format(__name__))

	# Crawl weather data
	try:
		logger.info('Crawling weather data and write to sql')
		Crawler.WriteCrawlToSql(cfg_path)
	except:
		logger.exception('An error occured in {}'.format(__name__))
		print('An error occured in {}'.format(__name__))
		sys.exit(1)

	# Datasummary
	try:
		logger.info('Summarise weather data')
		summ = DailyDataSummarise(cfg_path).DumpToCsv()
	except:
		logger.exception('An error occured in summarizing weather data')
		print('An error occured in summarizing weather data')
		sys.exit(1)
	

	summ.TableRam()
	summ.TableRja()
	summ.TablePm()

	logger.info('Weather data has been successfully updated and summarized')
	print('Weather data has been successfully updated and summarized')








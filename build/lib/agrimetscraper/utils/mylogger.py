import logging
from agrimetscraper.utils.configsetter import Configger



def SetLog(cfg_path, name):

	config = Configger(cfg_path)
	log_path = config.Getcfg('LOG_SETTINGS', 'logfile_path')
	log_datetimefmt = config.Getcfg('LOG_SETTINGS', 'logfile_datetimefmt')
	log_format = config.Getcfg('LOG_SETTINGS', 'logfile_format')

	logger = logging.getLogger(name)
	loghandler = logging.FileHandler(log_path)
	logging.getLogger().setLevel(logging.INFO)
	formatter = logging.Formatter(log_format, datefmt=log_datetimefmt)
	loghandler.setFormatter(formatter)
	logger.addHandler(loghandler)


	print('Successfully setup log parameters')

	return logger



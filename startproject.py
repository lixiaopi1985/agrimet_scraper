import os
import argparse
import sqlite3
from agrimetscraper.utils import mylogger
from agrimetscraper.utils.settings import basic_settings
from agrimetscraper.utils.configsetter import MyConfig
from agrimetscraper.utils.mylogger import SetLog
import shutil


def StartProject():

	parser = argparse.ArgumentParser(
		prog='StartProject',
		usage='python startproject.py -p myproject',
		description='Initialize project'
		)


	parser.add_argument('-p', dest='project', nargs='?', help='<string> input your name of your project')

	# parse arguments
	args=parser.parse_args()
	project = args.project

	print("""\n####################################################################
###### Starting a new AgriMet Weather Crawler Project ##############
####################################################################\n""")

	main_path = os.getcwd()
	exec_path = os.path.join(main_path, project)


	# in each project, create directories: db, log, config
	if not os.path.exists(exec_path):
		os.makedirs(exec_path)
	else:
		# projects names should be different each time you create them
		raise FileExistsError(f'{project} has exists.')

	dbdir = os.path.join(exec_path, 'Database')
	logdir = os.path.join(exec_path, 'Log')
	configdir = os.path.join(exec_path, 'Config')

	if not os.path.exists(dbdir):
		os.makedirs(dbdir)
	if not os.path.exists(logdir):
		os.makedirs(logdir)
	if not os.path.exists(configdir):
		os.makedirs(configdir)	


	# in exec_path, create a database, a log file and a setting.py
	dbname = project + '.db'
	dbfilepath = dbdir + '/' + dbname

	config_file_name = project + '.ini'
	config_file_path = configdir + '/' + config_file_name

	logname = project + '.log'
	log_path = logdir + '/' + logname

	global_settings = basic_settings


	print(f'Make config file: {config_file_name}\n')
	# add new settings
	global_settings['PROJECT_SETTINGS']['project_name']=project
	global_settings['PROJECT_SETTINGS']['project_path']=exec_path
	global_settings['PROJECT_SETTINGS']['project_setting_path']=config_file_path
	global_settings['DB_SETTINGS']['database_path']=dbfilepath
	global_settings['DB_SETTINGS']['database_name']=(dbname)
	global_settings['LOG_SETTINGS']['logfile_path']=log_path
	global_settings['LOG_SETTINGS']['logfile_name']=logname
	global_settings['LOG_SETTINGS']['logfile_format'] = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	global_settings['LOG_SETTINGS']['logfile_datetimefmt'] = '%Y-%m-%d %H:%M:%S'

	config = MyConfig()
	config.read_dict(global_settings)

	with open(config_file_path, 'w') as config_handle:
		config.write(config_handle)


	# create a log file
	print(f"Make log file: {logname}\n")
	with open(log_path, 'a') as log_handle:
		pass

	# create a db
	print(f"Make database: {dbname}\n")
	conn = sqlite3.connect(dbfilepath)
	conn.commit()
	conn.close()

	#set first log
	logger = SetLog(config_file_path, '{}'.format('StartProject'))
	logger.info('Project Initialized')


	# copy run.py to location
	shutil.copy2('RunProject.py', exec_path)
	print('\nProject has been initialized')

if __name__ == '__main__':
	StartProject()
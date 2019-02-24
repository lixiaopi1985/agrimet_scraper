#!python

import os
import sys
from agrimetscraper.schedulertools.scheduler import Scheduler
from agrimetscraper.pipeline import Pipelines



def main():

	Config_folder = os.path.join(cwd, 'Config')

	cfg_path = None
	for root, dirs, files in os.walk(Config_folder):
		cfg_path = files

	Pipelines(cfg_path)



if __name__ == '__main__':

	pypath = sys.executable
	cwd = os.getcwd()
	Config_folder = os.path.join(cwd, 'Config')
	cfg_path = None
	for root, dirs, files in os.walk(Config_folder):
		cfg_path = files


	file2run = os.path.join(cwd, 'run.py')
	Scheduler(cwd, pypath, file2run).Addjob().SetJob()







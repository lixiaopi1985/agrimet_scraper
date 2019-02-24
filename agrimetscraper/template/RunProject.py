#!/usr/bin/env python

import os
import sys
from agrimetscraper.utils.configsetter import Configger
from agrimetscraper.schedulertools.scheduler import Scheduler
from agrimetscraper.pipeline import Pipelines



def main():

	Config_folder = os.path.join(cwd, 'Config')

	cfg_path = None
	for _, _, files in os.walk(Config_folder):
		cfg_path = files

	Pipelines(cfg_path)



if __name__ == '__main__':

	pypath = sys.executable
	cwd = os.getcwd()
	Config_folder = os.path.join(cwd, 'Config')
	cfg_file = None
	for root, dirs, files in os.walk(Config_folder):
		cfg_file = files
		
	cfg_path = os.path.join(Config_folder, cfg_file)
	config = Configger(cfg_path)
	minute = config.Getcfg('SCHEDULER_SETTINGS', 'minute')
	hour = config.Getcfg('SCHEDULER_SETTINGS', 'hour')
	dom = config.Getcfg('SCHEDULER_SETTINGS', 'dom')
	mon = config.Getcfg('SCHEDULER_SETTINGS', 'mon')
	dow = config.Getcfg('SCHEDULER_SETTINGS', 'dow')

	file2run = os.path.join(cwd, 'RunProject.py')
	Scheduler(cwd, pypath, file2run).Addjob().SetJob(min=minute, hour=hour, dom=dom, mon=mon, dow=dow)







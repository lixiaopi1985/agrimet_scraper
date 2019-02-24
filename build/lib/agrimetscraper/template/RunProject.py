#!/usr/bin/env python

import os
import sys
from agrimetscraper.utils.configsetter import Configger
from agrimetscraper.schedulertools.scheduler import Scheduler

def main():
    	
		pypath = sys.executable
		cwd = os.getcwd()
		Config_folder = os.path.join(cwd, 'Config')
		cfg_file = None
		for _, _, files in os.walk(Config_folder):
			cfg_file = files

		cfg_path = os.path.join(Config_folder, cfg_file[0])
		config = Configger(cfg_path)
		minute = config.Getcfg('SCHEDULER_SETTINGS', 'minute')
		hour = config.Getcfg('SCHEDULER_SETTINGS', 'hour')
		dom = config.Getcfg('SCHEDULER_SETTINGS', 'dom')
		mon = config.Getcfg('SCHEDULER_SETTINGS', 'mon')
		dow = config.Getcfg('SCHEDULER_SETTINGS', 'dow')

		file2run = os.path.join(cwd, 'pipeline.py')
		Scheduler(cwd, pypath, file2run).Addjob(cfg_path).SetJob(min=minute, hour=hour, dom=dom, mon=mon, dow=dow)

if __name__ == '__main__':

	main()







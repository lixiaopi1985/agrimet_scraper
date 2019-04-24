#!/usr/bin/env python

import os
import sys
import argparse
from agrimetscraper.utils.configreader import Configtuner
from agrimetscraper.scheduler.scheduler import Scheduler



def main():

    try:
        parser = argparse.ArgumentParser()

        parser.add_argument('-f', dest="freq", default="daily", choices=["daily", "instant"], type=str, help="<string> refer to config.ini file to choose which baseurl: daily or instant")
        parser.add_argument('-n', dest='dbtable', type=str, help="<string> name for the new table added to the database")

        args = parser.parse_args()

        urlsection = args.freq
        dbtable = args.dbtable


        pypath = sys.executable
        cwd = os.getcwd()
        config_folder = "".join([i for i in os.listdir() if i.endswith("-config")])
        config_file = "".join([i for i in os.listdir(os.path.abspath(config_folder)) if i.endswith('.ini')])
        configfilepath = os.path.join(config_folder, config_file)

        config = Configtuner(configfilepath)
        minute = config.getconfig('SCHEDULER_SETTINGS', 'minute')
        hour = config.getconfig('SCHEDULER_SETTINGS', 'hour')
        dom = config.getconfig('SCHEDULER_SETTINGS', 'dom')
        mon = config.getconfig('SCHEDULER_SETTINGS', 'mon')
        dow = config.getconfig('SCHEDULER_SETTINGS', 'dow')

        file2run = os.path.join(cwd, 'pipeline.py')
        Scheduler(cwd, pypath, file2run).Addjob(configfilepath, urlsection, dbtable).Setjob(min=minute, hour=hour, dom=dom, mon=mon, dow=dow)

    except:
        print('No argument parsed')
        sys.exit(1)


if __name__ == "__main__":
    main()






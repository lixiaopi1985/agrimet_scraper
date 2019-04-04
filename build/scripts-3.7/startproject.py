#!python


"""This module is used to run at command line to initialize project

myproject
| | | |_ db
| | |___ config
| |_____ log
|_______ station info

"""
import argparse
import os
import sqlite3
from configparser import RawConfigParser
import shutil
from agrimetscraper.utils.configurations import basic_configs
from agrimetscraper.utils.configreader import Configtuner
from agrimetscraper.utils.stationinfo import Stationinfo
from agrimetscraper.utils.mylogger import Setlog
from agrimetscraper.template import pipeline, runproject


def main():

    parser = argparse.ArgumentParser(
        prog="startproject",
        usage="startproject.py -p myproject"
    )

    parser.add_argument("-p", dest="project", nargs="?", type=str, help="<string> name of your project")
    parser.add_argument("-s", dest="saveit", action="store_true", help="<bool> store station id into database? if specified, return true")
    args = parser.parse_args()
    project = args.project
    saveStation = args.saveit



    print("""
    Starting a new agrimetscraper project
    """)

    main_path = os.getcwd()
    project_path = os.path.join(main_path, project)


    if not os.path.exists(project_path):
        os.makedirs(project_path)
    else:
        raise FileExistsError(f"{project} existed")

    dbdir = os.path.join(project_path, f"{project}-database")
    logdir = os.path.join(project_path, f"{project}-log")
    configdir = os.path.join(project_path, f"{project}-config")
    stationdir = os.path.join(project_path, f"{project}-stations")

    if not os.path.exists(dbdir):
        os.makedirs(dbdir)
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    if not os.path.exists(configdir):
        os.makedirs(configdir)
    if not os.path.exists(stationdir):
        os.makedirs(stationdir)

    # initialize file names in each directories
    dbname = project + '.db'
    dbfilepath = os.path.join(dbdir, dbname)
    
    logfilename = project + ".log"
    logfilepath = os.path.join(logdir, logfilename)

    configfilename = project + ".ini"
    configfilepath = os.path.join(configdir, configfilename)

    stationfilename = "stations.csv"
    stationfilepath = os.path.join(stationdir, stationfilename)

    global_settings = basic_configs

    # add new settings to config file
    global_settings['PROJECT_SETTINGS']['project_name']=project
    global_settings['PROJECT_SETTINGS']['project_path']=project_path
    global_settings['PROJECT_SETTINGS']['project_setting_path']=configfilepath
    global_settings['DB_SETTINGS']['database_path']=dbfilepath
    global_settings['DB_SETTINGS']['database_name']=(dbname)
    global_settings['LOG_SETTINGS']['logfile_path']=logfilepath
    global_settings['LOG_SETTINGS']['logfile_name']=logfilename
    global_settings['LOG_SETTINGS']['logfile_format'] = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    global_settings['LOG_SETTINGS']['logfile_datetimefmt'] = '%Y-%m-%d %H:%M:%S'
    global_settings['STATION_SETTINGS']['station_dir'] = stationfilepath


    config = RawConfigParser()
    config.read_dict(global_settings)

    print(f"\ninitializing config file: {configfilename}")
    with open(configfilepath, 'w') as config_handle:
        config.write(config_handle)

    # create log file
    print(f"making an empty log file: {logfilename}")
    with open(logfilepath, 'a') as log_handle:
        pass

    # create db file
    print(f"making an database: {dbname}")
    conn = sqlite3.connect(dbfilepath)

    # create stations.csv
    print("retrieving stations information as csv")
    config = Configtuner(configfilepath)
    url = config.getconfig('STATION_SETTINGS', 'station_url')
    station = Stationinfo(url, stationfilepath)
    station_df = station.querysites()
    if saveStation:
        station_df.save2sql("StationInfo", conn)
        config.setconfig("DB_SETTINGS", "database_tables", "StationInfo")

    conn.commit()
    conn.close()


    logger = Setlog(configfilepath, "startproject")
    logger.info(f"{project} finished initialization.")

    # copy files to local project location
    runprojectpath = os.path.realpath(runproject.__file__)
    pipelinepath = os.path.realpath(pipeline.__file__)
    shutil.copy2(runprojectpath, project_path)
    shutil.copy2(pipelinepath, project_path)
    print(f"\n{project} finished initialization.\nYou can modify your local '.ini' file in the config folder to schedule scrape time and then run RunProject!\n")


if __name__ == "__main__":
    main()
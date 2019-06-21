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
import sys
import sqlite3
from configparser import RawConfigParser
import shutil
from agrimetscraper.utils.configurations import basic_configs
from agrimetscraper.utils.configreader import Configtuner
from agrimetscraper.utils.stationinfo import Stationinfo
from agrimetscraper.utils.mylogger import Setlog
from agrimetscraper.template import pipeline, runproject
from agrimetscraper.utils.mongoSetup import Mongosetup
from agrimetscraper.utils.mongoDB import get_db
import getpass

def main():

    try:
        parser = argparse.ArgumentParser(
            prog="startproject",
            usage="startproject.py -p myproject -t dbtype"
        )

        parser.add_argument("-p", dest="project", nargs="?", type=str, help="<string> name of your project")
        parser.add_argument("-t", dest="dbtype", nargs="?", default="sql", choices=['sql', 'mongodb', 'atlas'], help="<string> store data type: sql or mongodb or to the atlas cloud")
        
        args = parser.parse_args()
        project = args.project
        dbtype = args.dbtype

    except argparse.ArgumentError as argerror:
        print(argerror)
        sys.exit(1)


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
    global_settings['DB_SETTINGS']['database_type']=dbtype
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


    # create stations.csv
    print("retrieving stations information as csv")
    config = Configtuner(configfilepath)
    url = config.getconfig('STATION_SETTINGS', 'station_url')
    station = Stationinfo(url, stationfilepath)
    station_df = station.querysites()


    config.setconfig("DB_SETTINGS", "database_tables", "StationInfo")

    logger = Setlog(configfilepath, "startproject")

    connect_string = config.getconfig("DB_SETTINGS", "connect_string")
    

    if dbtype == 'sql':
        # create db file
        print(f"making an database: {dbname}")
        logger.info(f"making an SQL database: {dbname}")
        conn = sqlite3.connect(dbfilepath)
        station_df.save2sql("StationInfo", conn)
        

        conn.commit()
        conn.close()

    elif dbtype == 'mongodb':

        if connect_string != "localhost":
            logger.exception("host selected not match database type. Choose mongodb for local storage in your ini file")
            raise ValueError("dbtype is not matching to the host type. Choose mongodb for local storage in your ini file")

        print(f"making an database: {dbname}")
        logger.info(f"making a mongo database: {dbname}")
        # create collection from panda
        df = station_df.df_filtered
        data = df.to_dict(orient='records')
        mongo_conn = Mongosetup(dbdir, logger)
        mongo_conn.start_mongodb()
        db, _ = get_db(project, connect_string)
        db = db['StationInfo'] # collection
        db.insert_many(data) # no need to consider update, once the project is setup, this collection will stand alone

    elif dbtype == "atlas":
        print(f"connecting to Mongo Atlas: database name: {dbname}")
        logger.info(f"connecting to Mongo Atlas: database name: {dbname}")

        connect_string = input("\nInput your connect string to atlas: ")
        password = getpass.getpass("\nPassword: ")

        connect_string = connect_string.replace('<password>', password)

        if not connect_string.startswith("mongodb+srv://"):
            logger.exception("host selected not match database type. Choose atlas for cloud storage in your ini file")
            raise ValueError("dbtype is not matching to the host type. Choose atlas for cloud storage in your ini file")

        config.setconfig("DB_SETTINGS", "connect_string", connect_string)

        # create collection from panda
        df = station_df.df_filtered
        data = df.to_dict(orient='records')
        db, _ = get_db(project, connect_string)
        db = db['StationInfo']
        db.insert_many(data) # no need to consider update, once the project is setup, this collection will stand alone




    logger.info(f"{project} finished initialization.")

    # copy files to local project location
    runprojectpath = os.path.realpath(runproject.__file__)
    pipelinepath = os.path.realpath(pipeline.__file__)
    shutil.copy2(runprojectpath, project_path)
    shutil.copy2(pipelinepath, project_path)
    print(f"\n{project} finished initialization.\nYou can modify your local '.ini' file in the config folder to schedule scrape time and then run RunProject!\n")




if __name__ == "__main__":
    main()
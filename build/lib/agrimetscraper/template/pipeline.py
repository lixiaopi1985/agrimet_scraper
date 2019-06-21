#!/usr/bin/env python

import sys
import sqlite3
from agrimetscraper.coretools.crawler import Crawler
from agrimetscraper.coretools.dataprocess import dataproc
from agrimetscraper.coretools.urlbuilder import Urlassembly
from agrimetscraper.utils.dbwrite import dataframe_to_sql
from agrimetscraper.utils.mylogger import Setlog
from agrimetscraper.utils.configreader import Configtuner
from agrimetscraper.utils.instantData_aggregate import timeAggregate
import time
from agrimetscraper.utils.mongoSetup import Mongosetup
from agrimetscraper.utils.mongoDB import get_db
import shutil
import re
import numpy as np


# look for config file
def agrimetscrape_pipeline(cfg_path, dbtable, freq):

    logger = Setlog(cfg_path, "Agrimetscraper_Pipeline")
    config = Configtuner(cfg_path)



    to = time.localtime()
    localTime = time.asctime(to)
    startTime = time.time()

    
    if freq == "instant":
        baseurl_section = "URL_INSTANT_SETTINGS"
    elif freq == "daily":
        baseurl_section = "URL_DAILY_SETTINGS"
    else:
        logger.exception("freq parameter is not set")
        raise ValueError("freq is either daily or instant")

    

    # dbbase path
    dbpath = config.getconfig("DB_SETTINGS", "database_path")
    dbname = config.getconfig("DB_SETTINGS", "database_name").split(".")[0]
    connect_string = config.getconfig("DB_SETTINGS", "connect_string")
    # dbtype
    dbtype = config.getconfig("DB_SETTINGS", "database_type")

    logger.info(f"""\n------Pipeline Initiated: [[[[ {localTime} ]]]]-----\n
        -->>> dbtyp: {dbtype}""")

    
    # look for what url link: daily or instant
    baseurl = config.getconfig(baseurl_section, "baseurl")
    params_text = config.getconfig(baseurl_section, "weather_parameters")
    linkformat = config.getconfig(baseurl_section, "format")
    startdate = config.getconfig(baseurl_section, "start")
    enddate = config.getconfig(baseurl_section, "end")
    backdays = config.getconfig(baseurl_section, "back")
    flags = config.getconfig(baseurl_section, "flags")
    limit = int(config.getconfig(baseurl_section, "limit"))
    params = params_text.split(",")


    # station info
    states = config.getconfig("STATION_SETTINGS", "states")
    states_list = tuple(states.split(","))

    # check existed data table or collections
    existed_table = config.getconfig("DB_SETTINGS", "database_tables").split(",")

    if dbtable not in existed_table:
        config.setconfig("DB_SETTINGS", "database_tables", dbtable)

    if dbtype == 'sql':

        try:
            logger.info("Pipeline info: connect to station information")
            conn = sqlite3.connect(dbpath)
        except:
            logger.exception("Pipeline Error: connection to database during pipeline")
            sys.exit(1)

        cur = conn.cursor()
        placeholder = ",".join(["?"]*len(states_list))
        site_sql = f"SELECT siteid FROM StationInfo WHERE state in ({placeholder});"
        try:
            cur.execute(site_sql, states_list)
        except:
            logger.exception("Pipeline Error: an error occurred when getting site ids from database")
            print("Pipeline Error: an error occurred when getting site ids from database")
            sys.exit(1)

        sites = [ i[0] for i in cur.fetchall()]

        

        # url assembly
        try:
            logger.info("Pipeline Info: url assembly")
            urlassem = Urlassembly(sites, params, baseurl, limit, start=startdate, end=enddate, back=backdays, format=linkformat)
            urls = urlassem.assemblyURL(logger)
        except:
            logger.exception("Pipeline Error: url assembly error")
            print("Pipeline Error: url assembly error")
            sys.exit(1)

        # crawl
        try:
            
            logger.info("Pipeline Info: start crawler")

            for url in urls:
                logger.info(f"URL ---> \n{url}\n<---\n")
                scraper = Crawler(url)
                response_text = scraper.startcrawl(logger)
                urlformat = scraper.geturlformat()
                # process data
                try:
                    logger.info("Pipeline [Crawl Data] Info: process crawled data")
                    df = dataproc(response_text, urlformat)
                    aggDf = df.copy()

                except:
                    logger.exception("Pipeline [Crawl Data] Error: process crawled data error", exc_info=True)
                    print("Pipeline Error: process crawled data error")
                    sys.exit(1)

                try:
                    logger.info("Pipeline [Crawl Data] Info: write data into database")

                    if freq == "instant":
                        aggDf = timeAggregate(aggDf)

                    df_replace_na = aggDf.replace('NA', np.nan)
                    df_replace_na.replace(re.compile('[0-9]{1,2}\.[0-9]{1,2}[+-]$'), np.nan, inplace=True)
                    # dropna
                    df_replace_na.dropna(inplace=True)
                    dataframe_to_sql(df_replace_na, dbpath, dbtable, logger)
                except:
                    logger.exception("Pipeline [Crawl Data] Error: write data to database error", exc_info=True)
                    sys.exit(1)

                time.sleep(1)

            conn.close()

        except:
            logger.exception("Pipeline Error: crawler error", exc_info=True)
            print("Pipeline Error: crawler error")
            sys.exit(1)

    elif dbtype == 'mongodb':

        logger.info("Pipeline info: connect to station information")
        if connect_string != "localhost":
            logger.exception("host selected not match database type. Choose << mongodb >> for local storage in your ini file")
            raise ValueError("dbtype is not matching to the host type. Choose << mongodb >> for local storage in your ini file")
        # default the connection is open
        # try:
        #     mongo_conn = Mongosetup(dbpath, logger)
        # except:
        #     logger.exception("--------> Mongo db connection error", exc_info = True)
        #     sys.exit(1)

        # mongo_conn.start_mongodb()
        db,client = get_db(dbname, connect_string)
        try:
            logger.info("Pipeline info: << Connect to mongod db >>")
            station_info = db['StationInfo']
            sites_cur = station_info.find({"state": {"$in": list(states_list)}})
            sites = []
            for site in sites_cur:
                sites.append(site["siteid"])
            logger.info("------------------------> Fetched sites from station info")
        except:
            logger.exception("Mongodb error")
            client.close()
            sys.exit(1)

        # url assembly
        try:
            logger.info("Pipeline Info: url assembly")
            urlassem = Urlassembly(sites, params, baseurl, limit, start=startdate, end=enddate, back=backdays, format=linkformat)
            urls = urlassem.assemblyURL(logger)
        except:
            logger.exception("Pipeline Error: url assembly error")
            client.close()
            print("Pipeline Error: url assembly error")
            sys.exit(1)

        # crawl
        # set up collection in mongodb
        try:
            logger.info(f"----------------------------> create {dbtable} collections in database")
            data_mongo = db[dbtable]
        except:
            client.close()
            logger.exception(f"---------Error ----------> create {dbtable} collection error in mongodb")
            sys.exit(1)


        try:
            logger.info("Pipeline Info: start crawler")
            for url in urls:
                logger.info(f"URL ---> \n{url}\n<---\n")
                scraper = Crawler(url)
                response_text = scraper.startcrawl(logger)
                urlformat = scraper.geturlformat()
                # process data
                try:
                    logger.info("Pipeline [Crawl Data] Info: process crawled data")
                    data_df = dataproc(response_text, urlformat)
                    aggDf = data_df.copy()
                    
                    # drop na
                    # convert datetime to datetime and convert parameters to float
                    if freq == "instant":
                        aggDf = timeAggregate(data_df)
                        data_df_row = aggDf.to_dict(orient='records') # list of dict [{}, {}]
                        for _, val in enumerate(data_df_row):
                            _date = val['Dates']
                            _time = val['Time']
                            _site = val['Sites']
                            filter_object = {"DateTime": _date, "Time": _time, "Sites": _site}
                            data_mongo.update(filter_object, {"$set": val}, upsert=True) #mongo db update if no match find
                    else:

                        df_replace_na = aggDf.replace('NA', np.nan)
                        df_replace_na.replace(re.compile('[0-9]{1,2}\.[0-9]{1,2}[+-]$'), np.nan, inplace=True)
                        # dropna
                        df_replace_na.dropna(inplace=True)
                        data_df_row = df_replace_na.to_dict(orient='records') # list of dict [{}, {}]
                        # "DateTime", "Sites", "params"
                        for ind, val in enumerate(data_df_row):
                            _date = val['DateTime']
                            _site = val['Sites']
                            filter_object = {"DateTime": _date, "Sites": _site}
                            data_mongo.update(filter_object, {"$set": val}, upsert=True) #mongo db update if no match find
                except:
                    logger.exception("Pipeline [Crawl Data] Error: process crawled data error", exc_info=True)
                    print("Pipeline Error: process crawled data error")
                    sys.exit(1)

                time.sleep(1)

            client.close()
            logger.info("----------->  |||| Success ---> shutdown server: mongodb")
        

        except:
            client.close()
            logger.info("----------->  |||| Error ---> shutdown server: mongodb")
            logger.exception("Pipeline Error: crawler error", exc_info=True)
            print("Pipeline Error: crawler error")
            sys.exit(1)

    elif dbtype == "atlas":

        logger.info("Pipeline info: connect to station information")

        if not connect_string.startswith("mongodb+srv://"):
            logger.exception("host selected not match database type. Choose << atlas >> for cloud storage in your ini file")
            raise ValueError("dbtype is not matching to the host type. Choose << atlas >> for cloud storage in your ini file")
        # default the connection is open
        # try:
        #     mongo_conn = Mongosetup(dbpath, logger)
        # except:
        #     logger.exception("--------> Mongo db connection error", exc_info = True)
        #     sys.exit(1)

        # mongo_conn.start_mongodb()
        db,client = get_db(dbname, connect_string)

        try:
            logger.info("Pipeline info: << Connect to mongo atlas >>")
            station_info = db['StationInfo']
            sites_cur = station_info.find({"state": {"$in": list(states_list)}})
            sites = []
            for site in sites_cur:
                sites.append(site["siteid"])
            logger.info("------------------------> Fetched sites from station info")
        except:
            logger.exception("Mongodb error")
            client.close()
            sys.exit(1)

        # url assembly
        try:
            logger.info("Pipeline Info: url assembly")
            urlassem = Urlassembly(sites, params, baseurl, limit, start=startdate, end=enddate, back=backdays, format=linkformat)
            urls = urlassem.assemblyURL(logger)
        except:
            logger.exception("Pipeline Error: url assembly error")
            client.close()
            print("Pipeline Error: url assembly error")
            sys.exit(1)

        # crawl
        # set up collection in mongodb
        try:
            logger.info(f"----------------------------> create {dbtable} collections in database")
            data_mongo = db[dbtable]
        except:
            client.close()
            logger.exception(f"---------Error ----------> create {dbtable} collection error in mongodb")
            sys.exit(1)


        try:
            logger.info("Pipeline Info: start crawler")
            for url in urls:
                logger.info(f"URL ---> \n{url}\n<---\n")
                scraper = Crawler(url)
                response_text = scraper.startcrawl(logger)
                urlformat = scraper.geturlformat()
                # process data
                try:
                    logger.info("Pipeline [Crawl Data] Info: process crawled data")
                    data_df = dataproc(response_text, urlformat)
                    aggDf = data_df.copy()
                    
                    # drop na
                    # convert datetime to datetime and convert parameters to float
                    if freq == "instant":
                        aggDf = timeAggregate(data_df)
                        data_df_row = aggDf.to_dict(orient='records') # list of dict [{}, {}]
                        for _, val in enumerate(data_df_row):
                            _date = val['Dates']
                            _time = val['Time']
                            _site = val['Sites']
                            filter_object = {"DateTime": _date, "Time": _time, "Sites": _site}
                            data_mongo.update(filter_object, {"$set": val}, upsert=True) #mongo db update if no match find
                    else:

                        df_replace_na = aggDf.replace('NA', np.nan)
                        df_replace_na.replace(re.compile('[0-9]{1,2}\.[0-9]{1,2}[+-]$'), np.nan, inplace=True)
                        # dropna
                        df_replace_na.dropna(inplace=True)
                        data_df_row = df_replace_na.to_dict(orient='records') # list of dict [{}, {}]
                        # "DateTime", "Sites", "params"
                        for ind, val in enumerate(data_df_row):
                            _date = val['DateTime']
                            _site = val['Sites']
                            filter_object = {"DateTime": _date, "Sites": _site}
                            data_mongo.update(filter_object, {"$set": val}, upsert=True) #mongo db update if no match find
                except:
                    logger.exception("Pipeline [Crawl Data] Error: process crawled data error", exc_info=True)
                    print("Pipeline Error: process crawled data error")
                    sys.exit(1)

                time.sleep(1)

            client.close()
            logger.info("----------->  |||| Success ---> shutdown server: mongodb")
        

        except:
            client.close()
            logger.info("----------->  |||| Error ---> shutdown server: mongodb")
            logger.exception("Pipeline Error: crawler error", exc_info=True)
            print("Pipeline Error: crawler error")
            sys.exit(1)


    endTime = time.time()

    deltaTime = endTime - startTime

    
    logger.info(f"\n\n----------- Completed current crawling request. Used time {deltaTime} s-----------------------\n\n")
    print("Completed current crawling request")

if __name__ == "__main__":
    # parse throught flags -u -n, see runproject for details
    cfg_path = sys.argv[1]
    section = sys.argv[2]
    dbtable = sys.argv[3]

    agrimetscrape_pipeline(cfg_path, dbtable, section)


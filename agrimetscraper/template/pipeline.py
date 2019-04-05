#!/usr/bin/env python

import sys
import sqlite3
from agrimetscraper.coretools.crawler import Crawler
from agrimetscraper.coretools.dataprocess import dataproc
from agrimetscraper.coretools.urlbuilder import Urlassembly
from agrimetscraper.utils.dbwrite import dataframe_to_sql
from agrimetscraper.utils.mylogger import Setlog
from agrimetscraper.utils.configreader import Configtuner
import time


# look for config file
def agrimetscrape_pipeline(cfg_path, dbtable, freq):

    to = time.localtime()
    localTime = time.asctime(to)
    startTime = time.time()

    logger = Setlog(cfg_path, "Agrimetscraper_Pipeline")
    config = Configtuner(cfg_path)

    logger.info(f"Pipeline Initiated: [[[[ {localTime} ]]]]")

    # dbbase path
    dbpath = config.getconfig("DB_SETTINGS", "database_path")

    
    if freq == "instant":
        baseurl_section = "URL_INSTANT_SETTINGS"
    elif freq == "daily":
        baseurl_section = "URL_DAILY_SETTINGS"
    else:
        raise ValueError("freq is either daily or instant")



    # look for what url link: daily or instant
    baseurl = config.getconfig(baseurl_section, "baseurl")
    params_text = config.getconfig(baseurl_section, "weather_parameters")
    linkformat = config.getconfig(baseurl_section, "format")
    startdate = config.getconfig(baseurl_section, "start")
    enddate = config.getconfig(baseurl_section, "end")
    backdays = config.getconfig(baseurl_section, "back")
    flags = config.getconfig(baseurl_section, "flags")
    limit = int(config.getconfig(baseurl_section, "limit"))


    # station info
    states = config.getconfig("STATION_SETTINGS", "states")
    states_list = tuple(states.split(","))
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
    params = params_text.split(",")

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

        existed_table = config.getconfig("DB_SETTINGS", "database_tables").split(",")
        if dbtable not in existed_table:
            config.setconfig("DB_SETTINGS", "database_tables", dbtable)
        

        for url in urls:
            logger.info(f"URL ---> \n{url}\n<---\n")
            scraper = Crawler(url)
            response_text = scraper.startcrawl(logger)
            urlformat = scraper.geturlformat()
            # process data
            try:
                logger.info("Pipeline [Crawl Data] Info: process crawled data")
                df = dataproc(response_text, urlformat)
            except:
                logger.exception("Pipeline [Crawl Data] Error: process crawled data error", exc_info=True)
                print("Pipeline Error: process crawled data error")
                sys.exit(1)

            # write to data base
            try:
                logger.info("Pipeline [Crawl Data] Info: write data into database")
                dataframe_to_sql(df, dbpath, dbtable, logger)
            except:
                logger.exception("Pipeline [Crawl Data] Error: write data to database error", exc_info=True)
                sys.exit(1)

            time.sleep(5)

    except:
        logger.exception("Pipeline Error: crawler error", exc_info=True)
        print("Pipeline Error: crawler error")
        sys.exit(1)

    endTime = time.time()

    deltaTime = endTime - startTime

    conn.close()
    logger.info(f"\n\n----------- Completed current crawling request. Used time {deltaTime} s-----------------------\n\n")
    print("Completed current crawling request")

if __name__ == "__main__":
    # parse throught flags -u -n, see runproject for details
    cfg_path = sys.argv[1]
    section = sys.argv[2]
    dbtable = sys.argv[3]

    agrimetscrape_pipeline(cfg_path, dbtable, section)


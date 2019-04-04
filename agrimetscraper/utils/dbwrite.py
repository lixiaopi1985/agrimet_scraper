"""Writing data frame to database
"""

import sqlite3
import pandas as pd
from datetime import datetime as dt 
import sys
import re


def coltypes(df):
    """Decides column types to store for database
    
    Arguments:
        df {pandas dataframe} -- [pandas dataframe]
    """
    cols = df.columns.tolist()

    floattypes = re.compile(r"^[Ll]atitude$|^LATITUDE$|^[Ll]ongitude$|^LONGITUDE$|^ELEVATION.*?$|^[Ee]levation.*?$|^[A-Za-z]{2,4}$|^[A-Za-z]{2}[0-9]{1}$")


    objectypes = re.compile(r"^[Dd]ate.*?$|^DATE.*?$|[Yy]ear.*?$|^YEAR.*?$|^[Tt]ime$|^[Dd]ay.*?$|^[Mm]onth.*?$|^MONTH.*?$|[Ss]ite.*|SITE.*|^[Dd]escription.*?$|^DESCRIPTION$")


    coltypes = {}
    for i in cols:
        if floattypes.search(i):
            coltypes[i] = 'REAL'
        elif objectypes.search(i):
            coltypes[i] = 'TEXT'

    return coltypes


def dataframe_to_sql(df, dbpath, dbtable, logger):
    """
    insert each row into defined database and datatable

    df {pandas dataframe}
    dbpath {database path}
    dbtable {table name}
    """


    coltype = coltypes(df) # dictionary
    colname = df.columns.tolist()
    placeholder_col = ",".join(["?"]*(len(colname)+1))
    # (col1 TEXT, col2 FLOAT)
    # add primary keys datetime and  siteid
    datepattern = re.compile(r"^[Dd]ate.*?$|^DATE.*?$")
    sitepattern = re.compile(r"^[Ss]ite.*?$|^SITE.*?$")

    datecol = "".join([ i for i in colname if datepattern.search(i)])
    sitecol = "".join([ i for i in colname if sitepattern.search(i)])
    

    col_tuple = ",".join([ " ".join([i, coltype[i]]) for i in colname])
    createtable = f"""CREATE TABLE IF NOT EXISTS {dbtable} ({ "PrimeKeys PRIMARY KEY,"+col_tuple});""" # add datetime and siteid as primary keys to prevent duplicates


    try:
        conn = sqlite3.connect(dbpath)
    except sqlite3.DatabaseError as dbE:
        print(dbE)
        sys.exit(1)


    cur = conn.cursor()
    cur.execute(createtable)


    # insert data
    insertsql = f"""INSERT OR IGNORE INTO {dbtable} VALUES ({placeholder_col});"""


    for i in range(len(df)):

        primekey = (df.loc[i, datecol] + "-" + df.loc[i, sitecol], )

        row = primekey + tuple(df.loc[i, :])

        try:
            cur.execute(insertsql, row)
            conn.commit()
        except:
            logger.exception("Error: insert into data table", exc_info=True)
            sys.exit(1)
    
    logger.info(f"Completed: row data insertion completed in {dbtable}")


# def sql_to_dataframe(dbpath, dbtable, sqlcommand, logger):

#     try:
#         conn = sqlite3.connect(dbpath)
#     except sqlite3.DatabaseError as dbE:
#         print(dbE)
#         sys.exit(1)

#     outdf = pd.read_sql_query(sqlcommand, conn)
#     outdf.dropna(inplace=True)






# This function is used to aggregate 15 minutes to 1 hour
import re
import pandas as pd
import numpy as np


def col_types(df):
    """Decides column types to store for database
    
    Arguments:
        df {pandas dataframe} -- [pandas dataframe]
    """
    cols = df.columns.tolist()

    floattypes = re.compile(r"^[Ll]atitude$|^LATITUDE$|^[Ll]ongitude$|^LONGITUDE$|^ELEVATION.*?$|^[Ee]levation.*?$|^[A-Za-z]{2,4}$|^[A-Za-z]{2}[0-9]{1}$")
    datetimetypes = re.compile(r"^[Dd]ate.*?$|^DATE.*?$|[Yy]ear.*?$|^YEAR.*?$|^[Tt]ime$|^[Dd]ay.*?$|^[Mm]onth.*?$|^MONTH.*?$")
    sites = re.compile(r"[Ss]ite.*?$")


    coltypes = {}
    for i in cols:
        if floattypes.search(i):
            coltypes[i] = 'float'
        elif datetimetypes.search(i):
            coltypes[i] = 'datetime'
        elif sites.search(i):
            coltypes[i] = 'sites'

    return coltypes

def timeAggregate(df, fmt="%Y-%m-%d %H:%M", freq='H'):
    """This function is used to aggregate your pandas df to a certain freq interval. Note: NA will be removed, data with flags will be removed too
    
    Arguments:
        df {string} -- pandas dataframe

    
    Keyword Arguments:
        fmt {string} -- datetime format
        freq {str} -- frequency (default: {'H'})

    return new aggregated df
    """
    # get col data types index mapping
    colnames = df.columns.tolist()
    coltypes  = col_types(df)
    sitecol = [ i for i in colnames if coltypes[i] == 'sites']
    datecol = [ i for i in colnames if coltypes[i] == 'datetime']

    # remove na and mark number with flags na
    df_replace_na = df.replace('NA', np.nan)
    df_replace_na.replace(re.compile('[0-9]{1,2}\.[0-9]{1,2}[e+-]$'), np.nan, inplace=True)
    # dropna
    df_replace_na.dropna(inplace=True)
    # conver to datetime
    df_replace_na[datecol[0]] = pd.to_datetime(df_replace_na[datecol[0]], format=fmt)

    # conver types
    for i in colnames:
        if coltypes[i] == 'float':
            df_replace_na[i] = df_replace_na[i].astype('float')


    # group

    df_grouped = df_replace_na.groupby([sitecol[0], df_replace_na[datecol[0]].dt.date, pd.Grouper(key=datecol[0], freq=freq)]).mean()
    df_new = df_grouped.rename_axis(['Sites', 'Dates', 'Time']).reset_index()
    # save Dates to string for mongdb
    df_new['Dates'] = df_new['Dates'].apply(lambda x: str(x) )
    df_new['Time'] = df_new['Time'].apply(lambda x: x.hour)

    return df_new





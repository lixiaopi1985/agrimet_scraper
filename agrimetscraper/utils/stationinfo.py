import requests
import pandas as pd
import json
import re
import numpy as np


class Stationinfo:
    def __init__(self, url, savedir):
        self.url = url
        self.savedir = savedir

    @staticmethod
    def columntypes(df):
        """Decides column types to store for database
        
        Arguments:
            df {pandas dataframe} -- [pandas dataframe]
        """
        cols = df.columns.tolist()

        floattypes = re.compile("^[Ll]atitude$|^LATITUDE$|^[Ll]ongitude$|^LONGITUDE$|^ELEVATION.*?$|^[Ee]levation.*?$|^[A-Za-z]{2,4}$|^[A-Za-z]{2}[0-9]{1}$")


        objectypes = re.compile("^[Dd]ate.*?$|^DATE.*?$|[Yy]ear.*?$|^YEAR.*?$|^[Tt]ime$|^[Dd]ay.*?$|^[Mm]onth.*?$|^MONTH.*?$|[Ss]ite.*|SITE.*|^[Dd]escription.*?$|^DESCRIPTION$")


        coltypes = {}
        for i in cols:
            if floattypes.search(i):
                coltypes[i] = 'float'
            elif objectypes.search(i):
                coltypes[i] = 'string'

        return coltypes

    def querysites(self):
        """retrieve station information from cfg_path url
        
        Arguments:
            url {string} -- [url that fetches station information]

        return csv file in the location
        """

        try:
            response = requests.get(self.url)
            response.raise_for_status()
        except requests.ConnectionError:
            print("Connection error")
        except requests.HTTPError:
            print("Http error")
        except requests.RequestException:
            print("Invalid URL")

        resp_text = response.text

        if resp_text.startswith("[{"):
            df = pd.read_json(resp_text)

        else:
            df = pd.read_csv(self.url, header=1)

        df_selected = df.loc[:, ["siteid", "state", "description", "latitude", "longitude", "elevation"]].copy()
        self.df_filtered = df_selected[ ~((df_selected['latitude'] == 0 ) & (df_selected['longitude'] == 0 )) ]
        self.df_filtered.sort_values(by="siteid", inplace=True)
        self.df_filtered['siteid'] = self.df_filtered['siteid'].str.strip()
        self.df_filtered.to_csv(self.savedir, index=None, header=True)

        return self


    def save2sql(self, dbtable, conn):

        coltypes = Stationinfo.columntypes(self.df_filtered)

        self.df_filtered.to_sql(dbtable, conn, if_exists="replace", dtype = coltypes, index=False)

        



from bs4 import BeautifulSoup as bs
import numpy as np
import pandas as pd


def transformData(theads, tdata):
    """transform requests text return from agrimet into a data frame
    
    Arguments:
        theads {list} -- the first section of requests text containing description for the data such as DateTime, Site_MM
        tdata {list} -- the last section of requests containing the actual data
    
    Returns:
        [type] -- [description]
    """

    parameters = []
    for i in theads[1:]:
        pam = i.split("_")[1].upper()
        if not pam in parameters:
            parameters.append(pam)

    sites = []
    for i in theads[1:]:
        thesite = i.split("_")[0]
        if not thesite in sites:
            sites.append(thesite)

    ## transforming to DateTime Sites Parameters
    # looks like
    # DateTime Sites MM MX
    # 2019-03-15 acki 0.5 0.5
    dates = [ [tdata[i]]*len(sites) for i in range(0, len(tdata), len(theads))]
    flatten_dates = [ j for i in dates for j in i ]
    flatten_data = [ val for i, val in enumerate(tdata) if i % len(theads) != 0]

    data_array = np.array(flatten_data).reshape((-1, len(parameters)))
    

    flatten_sites = sites*(len(dates))

    df = pd.DataFrame(data_array, columns = parameters)
    df[theads[0]] = flatten_dates
    df['Sites'] = flatten_sites

    column_order = [theads[0]] + ['Sites'] + parameters
    df = df[column_order]

    return df


def htmlFormatter(htmltext):
    """format request return if url format is html
    
    Arguments:
        htmltext {text string} -- requests text return if url&format=html
    Returns:
        A data frame
    """

    soup = bs(htmltext, "html.parser")

    isflag = False
    theads_original = []
    theads = []
    tdata =[]
    data_nodate = []
    datetime = []

    for i in soup.findAll('th'):
        if i.text != 'flag':
            theads.append(i.text) #look like ['DateTime', 'abei_mm', 'abei_mx']
        else:
            isflag = True

    if isflag:
        for i, val in enumerate(soup.findAll("td")):
            if i % len(theads_original) !=0:
                data_nodate.append(val.text)
            else:
                datetime.append(val.text)

        for i, val in enumerate(data_nodate):
            if i % 2 != 1:
                if val == "" or val == " ":
                    tdata.append("NA")
                else:
                    tdata.append(val)

        #insert date time
        n = 0
        for i, val in enumerate(tdata):
            if i % len(theads) == 0:
                tdata.insert(i, datetime[n])
                n += 1 

    else:
        for i in soup.findAll('td'):
            if len(i.contents) == 0:
                tdata.append("NA")
            else:
                tdata.append(i.text) #look like ['2019-03-19', '38.81', '55.20'],

    df = transformData(theads, tdata)

    return df



def csvFormatter(csvtext):
    """format request return if url format is csv
    
    Arguments:
        csvtext {text string} -- [description]
    """

    query_list = csvtext.strip().split("\n")
    theads = [ i for i in query_list[0].split(",") if i != "flag"]
    tdata = [ "NA" if j == "" else j for i in query_list[1:] for j in i.split(",") ]
    df = transformData(theads, tdata)

    return df
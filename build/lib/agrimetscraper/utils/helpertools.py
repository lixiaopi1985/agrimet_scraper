import urllib
import re


def urlencodedquery(**kwargs):
    kw_copy = kwargs.copy()
    for key, val in kwargs.items():
        if val == "":
            del kw_copy[key]
    return urllib.parse.urlencode(kw_copy)


def urlcheck(url):
    """check if url is valid for agrimet api
    
    Arguments:
        url {string} -- http://www.usbr.gov/pn-bin/
    """
    match = True

    pattern = r"https?:\/\/www\.usbr\.gov\/?.*?$"

    regex = re.compile(pattern)

    if regex.search(url) is None:
        match = False

    return match

    

def urlformatdetect(url):

    pattern = r".*format=(.*).*"
    regex = re.compile(pattern)

    match = "Not Found"

    if urlcheck(url):

        regex_result = regex.search(url)

        if regex_result is not None:
            match = regex_result.group(1)


    return match

        



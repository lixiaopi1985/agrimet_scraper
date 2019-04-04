from agrimetscraper.utils.requestformatter import htmlFormatter, csvFormatter


def dataproc(request_text, inputformat):
    """put requests return text string into dataframe

    Arguments:
        request_text {string} -- string text returned from crawler
        inputformat {string} -- csv or html or Not Found
    
    Returns:
        df -- a df constructed
        None -- if not format found matched
    """


    if inputformat == "csv":
        return csvFormatter(request_text)

    elif inputformat == 'html':
        return htmlFormatter(request_text)

    else:
        raise ValueError("Format Not Found")


    


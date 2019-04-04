"""Build urls based on 
"""
from datetime import datetime as dt
from itertools import product
from agrimetscraper.utils.helpertools import urlencodedquery


class Urlpreprocessor:
    """Combine sites and parameters

    call urlpipe
    
    Raises:
        ValueError -- [description]
        ValueError -- [description]
    
    Returns:
        chunk sized id and parameters(limit 20 a batch)
    """


    def __init__(self, siteids, params, limit=20):
        assert type(siteids) == list, "Input 'siteids' should be type of list of a tuple [(site1, ), (site2, )]" # fetch from database
        assert type(params) == list, "Input 'params' should be type of a list"
        assert type(limit) == int, "Input 'stride' should be of type int"
        assert limit > 0 & limit <= 20, "stride value is between 1 and 20"

        if type(siteids[0]) == tuple:
            self.siteids = [ i[0] for i in siteids]

        self.siteids = siteids
        self.params = params
        self.limit = limit


    def __unpackID(self, idlist):
        """Unpack ids and combine it with params
        for example: abei MM, abei MN, abei MM
        
        Arguments:
            idlist {list} -- a list of site ids
        """

        assert type(idlist) == list, "idlist is type of a list"

        if len(idlist) > 0:
            product_id_params = [' '.join([i[0], i[1].lower()]) for i in product(idlist, self.params)]
        else:
            raise ValueError("idlist can not be empty")

        return ",".join(product_id_params)

    def urlpipe(self):
        if len(self.siteids) > 0:
            for i in range(0, len(self.siteids), self.limit):
                chunk = self.siteids[i:i+self.limit]
                yield self.__unpackID(chunk)
        else:
            raise ValueError("list of siteids is empty")





class Urlassembly:
    """
    Assemble urls with other options

    such as format, start and end
    """

    def __init__(self, siteids, params, baseurl, limit, **kwargs):
        self.siteids = siteids
        self.params = params 
        self.baseurl = baseurl
        self.kwargs = kwargs
        self.limit = limit

    def assemblyURL(self, logger):
        """assemble urls
        
        Arguments:
            logger {[type]} -- [description]
        
        Returns:
            A generator -- a url generator
        """


        logger.info("Urlassermbly")
        try:
            preprocess = Urlpreprocessor(self.siteids, self.params, self.limit)
        except:
            logger.error("Error: Urlpreprocessor")
            print("Error: Urlpreprocessor")
            return
            
        unpacked_sites = preprocess.urlpipe()

        queries = ( urlencodedquery(list=i, **self.kwargs) for i in unpacked_sites )

        urls = ( self.baseurl+i for i in queries ) 

        return urls

    def __str__(self):
        return f"baseurl is {self.baseurl}"





    

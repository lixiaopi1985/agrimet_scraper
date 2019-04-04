import requests
from fake_useragent import UserAgent
import sys
from agrimetscraper.utils.helpertools import urlcheck, urlformatdetect


class Crawler:

    ua = UserAgent()
    
    def __init__(self, url):
        self.url = url

    def startcrawl(self, logger):
        """crawl the url provided

            return response text 
        """
        headers = {'user-agent': Crawler.ua.random}

        if urlcheck(self.url): 
            pass
        else:
            logger.error("url error --- not valid")
            raise ValueError("Url is not valid. Please check it")

        try:

            self.response = requests.get(self.url, headers=headers)
            logger.info(f"Crawl Status: {self.response.status_code}")
            self.response.raise_for_status()
        except requests.ConnectionError:
            print("Error: Connection error")
            logger.error(f"Error in {__file__}: Connection Error")
            sys.exit(1)
        except requests.Timeout:
            print("Error: Timeout")
            logger.error(f"Error in {__file__}: Timeout Error")
            sys.exit(1)
        except requests.HTTPError:
            print("Error: Http error")
            logger.error(f"Error in {__file__}: Http Error")
            sys.exit(1)

        return self.response.text


    def checkstatus(self):
        return self.response.status_code


    def geturlformat(self):
        """detect url format, can parse it to dataprocess object 
        
        Returns:
            string -- html or csv or Not Found
        """

        return urlformatdetect(self.url)



    def __str__(self):
        return f"startcrawl url: {self.url}, status: {self.response.status_code}"



        


        




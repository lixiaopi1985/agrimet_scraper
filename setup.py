import setuptools
import agrimetscraper

with open("README.md", "r") as fh:
    long_description = fh.read()



setuptools.setup(
        name="agrimetscraper",
        version=agrimetscraper.__version__,
        author="Xiaoping Li",
        author_email="lixiaopi@oregonstate.edu",
        description="A package to scrape AgriMet weather data",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/lixiaopi1985/agrimet_scraper",
        scripts=['agrimetscraper/bin/startproject.py',],
        packages=setuptools.find_packages(),
        install_requires=['pandas', 'numpy', 'python-crontab', 'requests', 'fake_useragent', 'bs4', 'pymongo', 'dnspython'],
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            ],
 )

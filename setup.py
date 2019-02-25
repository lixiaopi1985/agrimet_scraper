import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
        name="agrimetscraper",
        version="0.0.18",
        author="Xiaoping Li",
        author_email="lixiaopi@oregonstate.edu",
        description="A package to scrape AgriMet weather data",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/lixiaopi1985/agrimet_scraper",
        scripts=['agrimetscraper/bin/agrimet-admin.py',],
        packages=setuptools.find_packages(),
        install_requires=['pandas', 'numpy', 'tqdm', 'python-crontab', 'requests'],
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            ],
 )

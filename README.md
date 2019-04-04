# agrimetscraper


### introduction

agrimetscraper crawls AgriMet weather data and summarise for later data usage.

### usage

Python virtual environment is preferred

`pip install agrimetscraper`

`startproject -p <yourproject> -s <load station information into database>`

It will create a directory for your project, this folder will contain yourproject-config, yourproject-log, yourproject-database, yourproject-stations

cd into your project, change .ini file if needed


**There are two baseurls for agrimet API: one is for daily, the other is for instant, are all defined in ini file**

run project: python runproject.py -u urlsection -n dbtable


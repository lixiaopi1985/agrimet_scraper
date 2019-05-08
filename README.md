# agrimetscraper


### introduction

agrimetscraper crawls AgriMet weather data and summarise for later data usage.

### basic usage

Python virtual environment is preferred

`pip install agrimetscraper`

`startproject -p <yourproject> -t <select database type: mongodb or sql>`

It will create a directory for your project, this folder will contain yourproject-config, yourproject-log, yourproject-database, yourproject-stations


cd into your project, change .ini file if needed


**There are two baseurls for agrimet API: one is for daily, the other is for instant, are all defined in ini file**

run project: python runproject.py -f "instant"|"daily" -n dbtable

set scheduler in .ini file (this program uses crontab)

**For instant data, program will aggregate 15 minutes into 1 hour interval and average the parameters


import os
import subprocess
import shutil
import sys
import shlex



class Mongosetup:

    def __init__(self, dbpath):
        self.dbpath = dbpath
    
    @staticmethod
    def check_mongo_installed():

        if not shutil.which('mongod'):
            raise EnvironmentError("No mongodb install in the path")



    def start_mongodb(self):

        try:
            Mongosetup.check_mongo_installed()
        except EnvironmentError as err:
            print(err)
            sys.exit(1)


        cmd = f"mongod --dbpath={self.dbpath}"
        cmd_list = shlex.split(cmd)
        try:
            subprocess.Popen(cmd_list)
        except:
            print("Subprocess error")
            sys.exit(1)


    def stop_mongodb(self):

        try:
            Mongosetup.check_mongo_installed()
        except EnvironmentError as err:
            print(err)
            sys.exit(1)


        cmd = f"mongod --dbpath={self.dbpath} --shutdown"
        cmd_list = shlex.split(cmd)
        try:
            subprocess.Popen(cmd_list)
        except:
            print('Subprocess error')
            sys.exit(1)












    
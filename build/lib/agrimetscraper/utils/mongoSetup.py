import os
import subprocess
import shutil
import sys
import shlex
import time


class Mongosetup:

    def __init__(self, dbpath, logger):
        self.dbpath = dbpath
        self.logger = logger
    
    @staticmethod
    def check_mongo_installed():

        if not shutil.which('mongod'):
            raise EnvironmentError("No mongod installed in the path")


    def start_mongodb(self):

        try:
            self.logger.info("Checking if mongo db is installed")
            Mongosetup.check_mongo_installed()
        except EnvironmentError as err:
            self.logger.exception("Error when checking mongo path", exc_info=True)
            print(err)
            sys.exit(1)


        cmd = f"mongod --dbpath={self.dbpath}"
        cmd_list = shlex.split(cmd)
        try:
            self.logger.info("Starting mongod process")
            self.proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE)
        except:
            self.logger.exception("Error occured when spawning subprocess")
            print("Subprocess error")
            sys.exit(1)

        

    def stop_mongodb(self):

        cmd = f"mongod --dbpath={self.dbpath} --shutdown"
        cmd_list = shlex.split(cmd)
        try:
            self.logger.info("Killing mongod process")
            subprocess.Popen(cmd_list, stdin=self.proc)
        except:
            self.logger.exception("Error occured when killing subprocess")
            print('Subprocess error')
            sys.exit(1)

        time.sleep(5)












    
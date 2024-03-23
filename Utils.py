import subprocess as sp
import os
from Drupal import *

class Utils:
    def __init__(self, globals):
        self.globals = globals

    def dbCleanUp(self):
        print('DB backups clean up')

        backups = [entry.name for entry in sorted(
            os.scandir("{}/{}".format(self.globals.home_directory,self.globals.backup)),key=lambda x: x.stat().st_mtime, reverse=True)]
        for backup in backups[3:]:
            os.remove("{}/{}/{}".format(self.globals.home_directory, self.globals.backup, backup))

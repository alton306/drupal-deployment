#system libs
import os,sys
import Globals
import subprocess as sp
from pathlib import Path
from Drupal import *
from Utils import *

Globals.initialize()

#restore to local to prev commit

#Main build function that handles all the logic for the script
def main():

    # checks the drupal version in the .env file and run the correct commands
    if(Globals.platform == 'drupal'):
        print('Drupal')
        drupal = Drupal(Globals)
        if(Globals.drupal_version == '7'):
            try:
                drupal.drupal7Deploy()
            except Exception as exception:
                raise
        elif(Globals.drupal_version == '8' or Globals.drupal_version == '9'):
            try:
                drupal.drupal8Deploy()
            except Exception as exception:
                print(exception)
                raise
    elif(Globals.platform == 'laravel'): 
        print('Laravel')
    else:
        print('please set the PLATFORM (drupal/laravel) variable in the .env file')
        raise

    # Cleanup backups keeps latest 3
    Utils(Globals).dbCleanUp()

if __name__ == "__main__":
    main()
import os
import subprocess as sp
from pathlib import Path
from dotenv import load_dotenv
dotenv_path = Path('./.env')
load_dotenv(dotenv_path=dotenv_path)

def initialize():
    global project_name
    global backup
    global enviroment_var
    global drupal_version
    global config_sync
    global theme
    global server_engine
    global project_path
    global headless
    global nextjs_path
    global home_directory
    global platform

    platform = os.getenv('PLATFORM')

    directory_path = os.getcwd()
    project_name = os.path.basename(directory_path)

    #variables in the env file
    enviroment_var = os.getenv('APP_ENV')
    drupal_version = os.getenv('DRUPAL_VERSION')
    config_sync = os.getenv('CONFIG_SYNC')
    theme = os.getenv('THEME')
    headless = os.getenv('HEADLESS')

    #standard Variables
    #project_name=project
    if headless:
        project_path='/var/www/vhosts/{}/drupal'.format(project_name)
        nextjs_path='/var/www/vhosts/{}/next.js'.format(project_name)
    else:
        project_path='/var/www/vhosts/{}'.format(project_name)
    
    backup="site-backups/{}".format(project_name)

    home_directory = os.path.expanduser( '~' )
    
    #checks to see what engine the server is using apache or njinx
    if(sp.run('ps -acx|grep apache|wc -l > 0', shell=True, check=True)):
        server_engine = 'apache'
    else:
        server_engine = 'nginx'

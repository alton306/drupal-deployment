# Fluid Deployment Script

There are Two main files to this script **Main.py** and **globals.py**. as well as a **.env** file that needs to be placed inside the site root directory

**Main.py** contains all of the logic for the script to run

**Globals.py** contains all the variables that are used via the script.

**.env** contains site specific variables that are used in the script

## How to run Script
In the jenkins build section run the following
```
ssh -tt -i KEY USER@SITE_IP << EOF
cd /SITE/LOCATION/ON/SERVER
python3.6 /SCRIPT/LOCATION/deployment/main.py
exit
EOF
```

- Key = ssh key to connect to server
- User = ssh user
- SITE_IP = Server's ip connecting too
- /SITE/LOCATION/ON/SERVER = Location of the site on the server
- /SCRIPT/LOCATION/ = Location of the scripts on the server

## .env file

The .env file consists of the below 4 variables that are required by the script to run. The file will need placing in the root of the site in order for it to work, If the site already has a .env file just add the following variables too it.

- 'THEME=' - This is the name of the theme being used by the site
- 'APP_ENV=' - This is the enviroment the site is currently on. it will accept either **staging** or **live**
- 'CONFIG_SYNC=' - This tell the script if config sync is being used by the site. it will accept either **True** or **False**
- 'DRUPAL_VERSION=' - This tell the script which version of drupal is being used. it will accept either **7**, **8** or **9**

## Current Features
- Pulls Site data from Git
- Creates Backup from site and Restores site from Backup
- Runs composer install command
- Runs Config Sync
- Run Drupal commands that are needed for sites drupal version
- Reverts site files to commit in use before build

## Possible Features
- Test updates on a clone of the Lives sites database before attempting a live build
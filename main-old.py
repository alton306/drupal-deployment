#system libs
import os,sys
import Globals
import subprocess as sp
import datetime
from pathlib import Path


Globals.initialize()

currentCommit = sp.run('git rev-parse --verify HEAD', shell=True, check=True, stdout=sp.PIPE).stdout.decode('utf-8')
repo = sp.run('git config --get remote.origin.url', shell=True, check=True, stdout=sp.PIPE).stdout.decode('utf-8')

# timestamp for the backup
current_time = datetime.datetime.now()
backup_time = current_time.strftime("%d_%m_%Y_%H_%M_%S")

#Function that handles the restore process if the build falls over
def restore_from_backup():
    try:
        #restore database
        sp.run("cd {}/{} && gunzip {}_{}.sql.gz".format(Globals.home_directory,Globals.backup,Globals.project_name, backup_time), shell=True, check=True)
        sp.run("cd {}/web && drush sql-drop -y && drush sql-cli < {}/{}/{}_{}.sql".format(Globals.project_path,Globals.home_directory,Globals.backup,Globals.project_name, backup_time), shell=True, check=True)
        #restore permissions
        sp.run('cd {} && find web -type d -exec chmod 755 {{}} \;'.format(Globals.project_path), shell=True, check=True)
        sp.run('cd {} && find web -type f -exec chmod 644 {{}} \;'.format(Globals.project_path), shell=True, check=True)
        sp.run('cd {} && chmod 444 web/.htaccess;'.format(Globals.project_path), shell=True, check=True)
        sp.run('cd {} && chmod 644 web/sites/default/settings.php'.format(Globals.project_path), shell=True, check=True)
        sp.run('cd {} && chmod -R 775 web/sites/default/files'.format(Globals.project_path), shell=True, check=True)
        sp.run('cd {} && chgrp -R www-data web'.format(Globals.project_path), shell=True, check=True)
        sp.run('cd {}/web/themes/{} && rm -rf node_modules && npm i'.format(Globals.project_path, Globals.theme), shell=True, check=True)
        #restore to local to prev commit
        sp.run('git reset --hard {}'.format(currentCommit), shell=True, check=True)
    except Exception as exception:
        print('Unable to restore site from back up try to do a manual restore')
        print(exception)
        raise
    print('restored')

#Main build function that handles all the logic for the script
def main():

    print('To reset Git Manually use: git reset --hard {}'.format(currentCommit))

    print('Pulling latest Merge/Commit')
    try:
        sp.run('git reset --hard', shell=True, check=True)
        sp.run('git pull', shell=True, check=True)
    except Exception as exception:
        print('Unable to pull site')
        print(exception)
        raise

    #makes a copy of the sites database and stored it in a folder under /home/ubuntu/site-backups/SITENAME
    if(Globals.enviroment_var == "live"):
        try:
            # checks for backup folder if missing creates it
            if not os.path.exists('{}/{}'.format(Globals.home_directory, Globals.backup)):
                print('Creating backup folder')
                os.makedirs('{}/{}'.format(Globals.home_directory, Globals.backup))
            else:
                print('Making Database Backup')
                sp.run("cd {}/web && drush sql-dump | gzip -c > {}/{}/{}_{}.sql.gz".format(Globals.project_path ,Globals.home_directory, Globals.backup ,Globals.project_name, backup_time), shell=True, check=True)    
        except Exception as exception:
            print('Unable to create backup')
            print(exception)
            raise
        else:
            print("Database backup compelted. File is located at: {} ".format(Globals.backup+"/"+Globals.project_name+"_"+backup_time+".sql.gz"))

    # checks the drupal version in the .env file and run the correct commands

    if(Globals.drupal_version == '7'):
        try:
            print('Running Drupal DB updates and clearing cache')
            sp.run('cd {}/web && drush updb -y && drush cr'.format(
                Globals.project_path), shell=True, check=True)
        except Exception as exception:
            print('Unable to apply Drupal database updates')
            print(exception)
            if(Globals.enviroment_var == "live"):
                restore_from_backup()
            raise
    elif(Globals.drupal_version == '8' or Globals.drupal_version == '9'):
        try:
            print('Running Composer updates')
            sp.run('cd {} && composer install'.format(
                Globals.project_path), shell=True, check=True)
        except Exception as exception:
            print('Running composer install failed')
            if(Globals.enviroment_var == "live"):
                restore_from_backup()
            print(exception)
            raise

        if(Globals.config_sync == 'TRUE'):
            try:
                print('Running Config Sync')
                sp.run('cd {}/web && drush cr && drush cim -y && drush cr '.format(
                    Globals.project_path), shell=True, check=True)
            except Exception as exception:
                print('Unable to apply Drupal Config updates')
                print(exception)
                raise
    
        try:
            print('Running Drupal DB updates and clearing cache')
            sp.run('cd {}/web && drush updb -y && drush cr'.format(
                Globals.project_path), shell=True, check=True)
        except Exception as exception:
            print('Unable to apply Drupal database updates')
            print(exception)
            if(Globals.enviroment_var == "live"):
                restore_from_backup()
            raise

    # builds the theme for the site
    if(Globals.headless == 'TRUE'):
        print('Compiling React/NextJs')
        print('Running npm updates')
        try:
            sp.run('cd {} && npm install'.format(Globals.nextjs_path), shell=True, check=True)
        except Exception as exception:
            print('npm install failed')
            sys.exit(-1)

        # Checks to see if the process is already runnin
        # if so just build the project instead of reload
        if(sp.run('pm2 pid {}'.format(Globals.project_name), shell=True, check=True, stdout=sp.PIPE).stdout.decode('utf-8').strip() != ''):
            print('Running Next build')
            try:
                sp.run('npm run build', shell=False, check=True)
            except:
                print('Next build failed. Run locally to check for TypeScript errors')
                sys.exit(-1)
        else:
            print('Reloading PM2')
            try:
                sp.run('pm2 reload "{}"'.format(Globals.project_name), shell=True, check=True)
            except Exception as exception:
                print('Could not reload process manager')
                print(exception)
                sys.exit(-1)

    else:
        print('Compiling theme')
        try:
            sp.run('cd {}/web/themes/{} && npm run compile:all'.format(Globals.project_path, Globals.theme), shell=True, check=True)
        except Exception as exception:
            print('Unable to compile theme')
            print(exception)
            raise

    # Cleanup backups keeps latest 3
    print('DB backups clean up')
    backups = [entry.name for entry in sorted(os.scandir('site-backups/barchester-d9'),key=lambda x: x.stat().st_mtime, reverse=True)]
    for backup in backups[3:]:
        os.remove("{}/{}/{}".format(Globals.home_directory, Globals.backup, backup))

if __name__ == "__main__":
    main()
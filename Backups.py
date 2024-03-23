import os
import subprocess as sp
import datetime

class Backups:

    def __init__(self, globals):
        # timestamp for the backup
        self.current_time = datetime.datetime.now()
        self.backup_time = self.current_time.strftime("%d_%m_%Y_%H_%M_%S")
        self.globals = globals

    def createDrupalRestorPoint(self):
        #sets git restore point

        self.currentCommit = sp.run('git rev-parse --verify HEAD', shell=True, check=True, stdout=sp.PIPE).stdout.decode('utf-8')
        self.repo = sp.run('git config --get remote.origin.url', shell=True, check=True, stdout=sp.PIPE).stdout.decode('utf-8')
        print('To reset Git Manually use: git reset --hard {}'.format(self.currentCommit))
        
        #makes a copy of the sites database and stored it in a folder under /home/ubuntu/site-backups/SITENAME
        try:
            # checks for backup folder if missing creates it
            if not os.path.exists('{}/{}'.format(self.globals.home_directory, self.globals.backup)):
                print('Creating backup folder')
                os.makedirs('{}/{}'.format(self.globals.home_directory, self.globals.backup))
            else:
                print('Making Database Backup')
                sp.run("cd {}/web && drush sql-dump | gzip -c > {}/{}/{}_{}.sql.gz".format(self.globals.project_path ,self.globals.home_directory, self.globals.backup ,self.globals.project_name, self.backup_time), shell=True, check=True)    
        except Exception as exception:
            print('Unable to create backup')
            print(exception)
            raise
        else:
            print("Database backup compelted. File is located at: {} ".format(self.globals.backup+"/"+self.globals.project_name+"_"+self.backup_time+".sql.gz"))

    def restorDrupalBackup(self):
        #restores database
        sp.run("cd {}/{} && gunzip {}_{}.sql.gz".format(self.globals.home_directory, self.globals.backup, self.globals.project_name, self.backup_time), shell=True, check=True)
        sp.run("cd {}/web && drush sql-drop -y && drush sql-cli < {}/{}/{}_{}.sql".format(self.globals.project_path,self.globals.home_directory,self.globals.backup,self.globals.project_name, self.backup_time), shell=True, check=True)
        #restores to previous commit
        sp.run('git reset --hard {}'.format(self.currentCommit), shell=True, check=True)
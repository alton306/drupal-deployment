import subprocess as sp
from Backups import *
from Next import *

class Drupal:
    def __init__(self, globals):
        self.globals = globals

    def databaseUpdate(self):
        try:
            print('Running Drupal DB updates and clearing cache')
            sp.run('cd {}/web && drush updb -y'.format(
                self.globals.project_path), shell=True, check=True)
        except Exception as exception:
            print('Unable to apply Drupal database updates')
            print(exception)
            raise

    def configSyncImport(self):
        try:
            print('Running Config Sync Import')
            sp.run('cd {}/web && drush cr && drush cim -y && drush cr '.format(
                self.globals.project_path), shell=True, check=True)
        except Exception as exception:
            print('Unable to apply Drupal Config updates')
            print(exception)
            raise

    def configSyncExport(self):
        try:
            print('Running Config Sync Export')
            sp.run('cd {}/web && drush cr && drush cex -y '.format(
                self.globals.project_path), shell=True, check=True)
        except Exception as exception:
            print('Unable to apply Drupal Config updates')
            print(exception)
            raise

    def compileTheme(self):
        print('Compiling theme')
        try:
            sp.run('cd {}/web/themes/{} && npm run compile:all'.format(self.globals.project_path, self.globals.theme), shell=True, check=True)
        except Exception as exception:
            print('Unable to compile theme')
            print(exception)
            raise

    def permissions(self):
        sp.run('cd {} && sudo find web -type d -exec chmod 755 {{}} \;'.format(self.globals.project_path), shell=True, check=True)
        sp.run('cd {} && sudo find web -type f -exec chmod 644 {{}} \;'.format(self.globals.project_path), shell=True, check=True)
        
        if(os.path.exists("{}/web/.htaccess".format(self.globals.project_path))):
            sp.run('cd {} && sudo chmod 444 web/.htaccess;'.format(self.globals.project_path), shell=True, check=True)

        sp.run('cd {} && sudo chmod 644 web/sites/default/settings.php'.format(self.globals.project_path), shell=True, check=True)
        sp.run('cd {} && sudo chmod -R 775 web/sites/default/files'.format(self.globals.project_path), shell=True, check=True)
        sp.run('cd {} && sudo chgrp -R www-data web'.format(self.globals.project_path), shell=True, check=True)
        sp.run('cd {}/web/themes/{} && rm -rf node_modules && npm i'.format(self.globals.project_path, self.globals.theme), shell=True, check=True)

    def drupal8Deploy(self):
        try:
            print('Running drupal 8 deployment')
            Backup = Backups(self.globals)
            Backup.createDrupalRestorPoint()

            print('Pulling latest Merge/Commit')
            sp.run('git reset --hard', shell=True, check=True)
            sp.run('git pull', shell=True, check=True)

            print('Running install')
            sp.run('cd {} && composer install'.format(
                self.globals.project_path), shell=True, check=True)
            self.configSyncImport()
            self.databaseUpdate()
            if self.globals.headless:
                next = Next(self.globals)
                if(self.globals.enviroment_var == "live"):
                    next.fullLiveDeploy()
                else:
                    next.fullStagingDeploy()

            else:
                self.compileTheme()

        except Exception as exception:
            print('Running drupal 8 deployment failed')
            print(exception)
            if(self.globals.enviroment_var == "live"):
                Backup.restorDrupalBackup()
                self.permissions()
            raise

    def drupal7Deploy(self):
        try:
            Backup = Backups(self.globals)
            Backup.createDrupalRestorPoint()

            print('Pulling latest Merge/Commit')
            sp.run('git reset --hard', shell=True, check=True)
            sp.run('git pull', shell=True, check=True)

            print('Running Drupal DB updates and clearing cache')
            sp.run('cd {}/web && drush updb -y && drush cc all'.format(
                self.globals.project_path), shell=True, check=True)
        except Exception as exception:
            print('Running drupal 7 deployment failed')
            print(exception)
            if(self.globals.enviroment_var == "live"):
                Backup.restorDrupalBackup()
                self.permissions()
            raise
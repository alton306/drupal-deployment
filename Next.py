import sys
import subprocess as sp

class Next:
    def __init__(self, globals):
        self.globals = globals
    
    def runNpmInstall(self):
        print('Running npm updates')
        try:
            sp.run('cd {} && npm install'.format(self.globals.nextjs_path), shell=True, check=True)
        except Exception as exception:
            print('npm install failed')
            sys.exit(-1)

    def runBuild(self):
        print('Running Next build')
        try:
            sp.run('cd {} && npm run build'.format(self.globals.nextjs_path), shell=False, check=True)
        except:
            print('Next build failed. Run locally to check for TypeScript errors')
            sys.exit(-1)

    def pm2Reload(self):
        print('Reloading PM2')
        try:
            sp.run('pm2 reload "{}"'.format(self.globals.project_name), shell=True, check=True)
        except Exception as exception:
            print('Could not reload process manager')
            print(exception)
            sys.exit(-1)

    def fullStagingDeploy(self):
        self.runNpmInstall()
        self.pm2Reload()

    def fullLiveDeploy(self):
        self.runNpmInstall()
        self.runBuild()
        self.pm2Reload()

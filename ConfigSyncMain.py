import Globals
import subprocess as sp
import datetime

Globals.initialize()

git_command = ["git", "status", "--porcelain"]
currentTime = datetime.datetime.now()
createdTime = currentTime.strftime("%d_%m_%Y_%H_%M_%S")

def has_changes():
    try:
        # Run the Git status command
        result = sp.run(git_command, cwd=Globals.project_path, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
        # Check if there is any output, which means there are changes
        return bool(result.stdout.strip().replace('?? ', ''))
    except Exception as e:
        print(f"Error checking Git status: {e}")
        return False
    
def reset_branch():
    sp.run('git reset --hard', shell=True, check=True)
    sp.run('git clean -fd', shell=True, check=True)
    sp.run('git clean -df', shell=True, check=True)
    sp.run('git checkout master', shell=True, check=True)
    sp.run('git branch -D config-sync-{}'.format(createdTime), shell=True, check=True)

def main():
    
    try:
        sp.run('git reset --hard', shell=True, check=True)
        sp.run('git clean -fd && git clean -df', shell=True, check=True)
        sp.run('git checkout -b "config-sync-{}"'.format(createdTime), shell=True, check=True)
        sp.run('cd {}/web && drush cr && drush cex -y'.format(
            Globals.project_path), shell=True, check=True)

        if(has_changes()):
            sp.run('git add config', shell=True, check=True)
            sp.run('git commit -m "Jenkins git commit"'.format(), shell=True, check=True)
            sp.run('git push --set-upstream origin config-sync-{}'.format(createdTime), shell=True, check=True)
            sp.run('git checkout master', shell=True, check=True)
            
        else:
            print("No changes detected.")
            reset_branch()

    except Exception as exception:
        print('Unable create config sync export resetting branch')
        #reset_branch()
        print(exception)
        raise

if __name__ == "__main__":
    main()
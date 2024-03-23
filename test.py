#system libs
import os,sys
import subprocess as sp
import datetime

def main():
    if(sp.run('pm2 pid test', shell=True, check=True, stdout=sp.PIPE).stdout.decode('utf-8').strip() != ''):
        print('hi')
    else:
        print('bye') 

if __name__ == "__main__":
    main()
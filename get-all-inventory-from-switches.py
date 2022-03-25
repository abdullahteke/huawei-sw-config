#!/usr/bin/python
 
import threading
from subprocess import call
import os
import re
import glob
import datetime
import time
 
def delete():
 
    files = glob.glob('tmp/*.txt')
    for f in files:
        os.remove(f)
 
def getVersionInformation(ip):
    call(["/root/EnvanterList/showVersion.sh", ip])        
    call(["/root/EnvanterList/showLicense.sh", ip])
    call(["/root/EnvanterList/showInventory.sh", ip])
 
def isDeviceAlive(ip):
    response = os.system("ping -c 1 " +ip+">/dev/null 2>&1")
 
    if response == 0:
        return True        
    else:
        return False
         
 
def worker(ip):
    if (isDeviceAlive(ip)==True):
        print (ip+' up')
        getVersionInformation(ip)
    else:
        print (ip+' down')
 
os.chdir('/root/EnvanterList')
 
 
#delete()
 
threads = []
 
with open('deviceList.csv') as fp:
    for line in fp:
                t = threading.Thread(target=worker, args=(line.strip(),))
                threads.append(t)
                t.start()
var=True
while var==True:
    print (threading.activeCount())
    if threading.activeCount()==1:
        var=False
        print('All tasks has been finished')
    else:
        time.sleep(5)    
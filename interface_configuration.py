'''
Created on 24 Mar 2022

@author: ateke
'''
#!/usr/bin/python
 
import threading
import subprocess
import os
import re
import glob
import pexpect
import datetime
import time
import smtplib
 
def checkDescription(line):
        match=re.search(r"(PC|PRinter|IPTLFN|Printer|AP)",line)
        if match:
                return True
        return False
 
def checkPortDefinition(str,array):
        for i in array:
                if (str in i):
                        return True
        return False
 
def delete():
        if os.path.isfile('configuredStaticVlanInterfaces.csv'):
                os.unlink('configuredStaticVlanInterfaces.csv')
        if os.path.isfile('setInterfaceLog.log'):
                os.unlink('setInterfaceLog.log')
 
        interfaceFile = open('configuredStaticVlanInterfaces.csv', 'w')
        interfaceFile.write('IP,INTERFACE,VLAN\n')
        interfaceFile.close()
 
        setInterfaceLogFile= open('setInterfaceLog.log', 'w')
        setInterfaceLogFile.write('')
        setInterfaceLogFile.close()
 
        files = glob.glob('tmp/*.txt')
        for f in files:
                os.remove(f)
 
def getAuthenticatedPorts(ip):
        child = pexpect.spawn('ssh ecetin@'+ip)
        child.log=open("tmp/authenticatedPorts_"+ip.strip()+".txt", "w")
        child.expect('Password')
        child.sendline('1q2w3e4R')
        child.expect('>')
        child.sendline('disp current-configuration interface')
 
        var='true'
        while var == 'true':
                index=child.expect(['---- More ----','>',pexpect.EOF,pexpect.TIMEOUT])
                if index == 0:
                        child.log.write(child.before)
                        child.sendline(' ')
                elif index == 1:
                        var='false'
                        child.log.write(child.before)
                        child.close()
                elif index == 2:
                        child.close()
                elif index == 3:
                        child.close()
        child.close();
        child.log.close()
 
def isDeviceAlive(ip):
        response = os.system("ping -c 1 " +ip+">/dev/null 2>&1")
 
        if response == 0:
                return True
        else:
                return False
def setDisable8021xFromInterface(ip):
        f=open('configuredStaticVlanInterfaces.csv','a')
 
        child = pexpect.spawn('ssh ecetin@'+ip)
        child.log=open("setInterfaceLog.log", "a")
        child.expect('Password')
        child.sendline('1q2w3e4R')
        child.expect('>')
        child.sendline('sys')
        child.expect(']')
 
        file= open('tmp/authenticatedPorts_'+ip.strip()+'.txt','r')
 
        fileContent=file.read().split("#")
 
        intName=''
        descripton=''
 
        for intBlock in fileContent:
                blockParts=intBlock.split("\n")
                if (len(blockParts)>2 and ("interface" in blockParts[1]) and checkDescription(blockParts[2])):
                        intName=blockParts[1]
                        description=blockParts[2]
                        if (not checkPortDefinition("port-security enable",blockParts) or not checkPortDefinition("port-security mac-address sticky",blockParts)):
                                child.sendline(intName.strip())
                                child.expect(']')
                                child.sendline('shutdown')
                                child.expect(']')
                                child.sendline('undo port-security enable')
                                child.expect(']')
                                child.sendline('undo port-security mac-address sticky')
                                child.expect(']')
                                child.sendline('port-security enable')
                                child.expect(']')
                                child.sendline('port-security mac-address sticky')
                                child.expect(']')
                                child.sendline('undo shutdown')
                                child.expect(']')
                                child.sendline('quit')
                                child.expect(']')
        fp.close()
        f.close()
        child.sendline('quit\r')
        child.expect('>')
        child.sendline('save')
        child.expect('Y/N]')
        child.sendline('Y')
        child.log.close()
 
        child.close()
def deneme(ip):
        f=open('configuredStaticVlanInterfaces.csv','a')
 
        child = pexpect.spawn('ssh ecetin@'+ip)
        child.log=open("setInterfaceLog.log", "a")
        child.expect('Password')
        child.sendline('1q2w3e4R')
        child.expect('>')
        child.sendline('sys')
        child.expect(']')
 
        with open('tmp/authenticatedPorts_'+ip.strip()+'.txt','r') as fp:
                for line in fp:
                        match=re.search(r".*GE.* (PC|PRinter|IPTLFN|Printer|DIGITAL-SIGNAGE|KAPI-SIRA-MONITOR|KOSK)",line)
                        if match:
                                interface,other=re.search(r".*GE(.*) .* (PC|PRinter|IPTLFN|Printer|DIGITAL-SIGNAGE|KAPI-SIRA-MONITOR|KOSK)",line).groups()
                                intName=interface.split(" ")[0]
                                child.sendline('interface G '+intName.strip())
                                child.expect(']')
                                child.sendline('shutdown')
                                child.expect(']')
                                child.sendline('undo port-security enable')
                                child.expect(']')
                                child.sendline('undo port-security mac-address sticky')
                                child.expect(']')
                                child.sendline('port-security enable')
                                child.expect(']')
                                child.sendline('port-security mac-address sticky')
                                child.expect(']')
                                child.sendline('undo shutdown')
                                child.expect(']')
                                child.sendline('quit')
                                child.expect(']')
 
        fp.close()
        f.close()
 
        child.sendline('quit\r')
        child.expect('>')
        child.sendline('save')
        child.expect('Y/N]')
        child.sendline('Y')
        child.log.close()
 
        child.close()
def worker(ip):
        if (isDeviceAlive(ip)==True):
                getAuthenticatedPorts(ip)
                deneme(ip)
                #setDisable8021xFromInterface(ip)
        else:
                print (ip+' down')
 
os.chdir('/root/scripts/SetSecurity')
 
 
delete()
 
threads = []
 
with open('deviceList.txt') as fp:
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
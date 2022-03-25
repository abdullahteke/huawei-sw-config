#!/usr/bin/python

import threading
import subprocess
import os
import re
import glob
import pexpect
import datetime
import time

def sentMail():
        d=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        msg=MIMEMultipart('alternative')
        msg['Subject'] = "802.1x Interface Report_"+d 
        msg['From'] = "test@server.abdullahteke.com"
        msg['To'] =  "abdullahteke@gmail.com"

        html =  """\
                <html>
                        <head></head>
                                <body>
                                        <p>Konfigurasyonu yapilan port bilgileri
                                        </p>
                                </body>
                </html>
                """ 
        msg.attach(MIMEText(html,'html'))

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open("configuredStaticVlanInterfaces.csv", "rb").read())
        email.encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="configuredStaticVlanInterfaces.csv"')
        msg.attach(part)

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open("setInterfaceLog.log", "rb").read())
        email.encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="setInterfaceLog.log"')
        msg.attach(part)

        s = smtplib.SMTP('10.133.133.20')
        s.sendmail("testmail@gmail.com", "abdullahteke@gmail.com", msg.as_string())
        s.quit()
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

def getVersionInformation(ip):
        child = pexpect.spawn('ssh fatihvpn@'+ip)
        child.log=open("tmp/"+ip.strip()+"_showVersion.txt", "w")
        child.expect('Password')
        child.sendline('fatih.vpn2018')
        child.expect('>')
        child.sendline('show version')
	
	var='true'
	while var == 'true':
		index=child.expect(['---- More ----','>',pexpect.EOF,pexpect.TIMEOUT])
		if index == 0:
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

def getLicenseInformation(ip):
        child = pexpect.spawn('ssh fatihvpn@'+ip)
        child.log=open("tmp/"+ip.strip()+"_showLicense.txt", "w")
        child.expect('Password')
        child.sendline('fatih.vpn2018')
        child.expect('>')
        child.sendline('show license')
	
	var='true'
	while var == 'true':
		index=child.expect(['---- More ----','>',pexpect.EOF,pexpect.TIMEOUT])
		if index == 0:
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

def getInventoryInformation(ip):
        child = pexpect.spawn('ssh fatihvpn@'+ip)
        child.log=open("tmp/"+ip.strip()+"_showLicense.txt", "w")
        child.expect('Password')
        child.sendline('fatih.vpn2018')
        child.expect('>')
        child.sendline('show inventory')
	
	var='true'
	while var == 'true':
		index=child.expect(['---- More ----','>',pexpect.EOF,pexpect.TIMEOUT])
		if index == 0:
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
		

def worker(ip):
	if (isDeviceAlive(ip)==True):
		getVersionInformation(ip)
		getLicenseInformation(ip)
		getInventoryInformation(ip)
	else:
		print (ip+' down')

os.chdir('/root/EnvanterList')


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
		sentMail()
	else:
		time.sleep(5)

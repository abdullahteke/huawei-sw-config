'''
Created on Mar 2, 2017

@author: ateke
'''


import threading
import os
import re
import glob
import pexpect
import datetime
import time
import smtplib
import email.encoders

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
def getAuthenticatedPorts(ip):
        user = "ateke"
        password = "1234"
        child = pexpect.popen_spawn.PopenSpawn('ssh '+user+'@'+ip)
        child.log=open("tmp/authenticatedPorts_"+ip.strip()+".txt", "w")
        child.expect('Password')
        child.sendline(password)
        child.expect('>')
        child.sendline('disp mac-address authen')

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

def setDisable8021xFromInterface(ip):
        f=open('configuredStaticVlanInterfaces.csv','a')
        user = "ateke"
        password = "1234"

        child = pexpect.popen_spawn.PopenSpawn('ssh '+user+'@'+ip)
        child.log=open("setInterfaceLog.log", "a")
        child.expect('Password')
        child.sendline(password)
        child.expect('>')
        child.sendline('sys')
        child.expect(']')

        with open('tmp/authenticatedPorts_'+ip.strip()+'.txt','r') as fp:
                for line in fp:
                        match=re.search(r".* (.*)/- .* GE(.*) authen.*",line)
                        if match:
                                vlan,interface=re.search(r".* (.*)/- .* GE(.*) authen.*",line).groups()
                                if (vlan.strip() !='3613') and (vlan.strip() != '1') and (vlan.strip() != '2953'):
                                        print ('ip:'+ip+' interface:'+interface.strip()+' vlan:'+vlan)
                                        f.write(ip.strip()+','+interface.strip()+','+vlan.strip()+'\n')
                                        child.sendline('interface G '+interface.strip())
                                        child.expect(']')
                                        child.sendline('shutdown')
                                        child.expect(']')
                                        child.sendline('undo port link-type')
                                        child.expect(']')
                                        child.sendline('undo authentication dot1x')
                                        child.expect(']')
                                        child.sendline('undo authentication mode')
                                        child.expect(']')
                                        child.sendline('undo dot1x authentication-method')
                                        child.expect(']')
                                        child.sendline('port link-type access')
                                        child.expect(']')
                                        child.sendline('port def vlan '+vlan.strip())
                                        child.expect(']')
                                        child.sendline('undo shutdown')
                                        child.expect(']')
                                        child.sendline('quit')
                                        child.expect(']')
                                        child.log.write(child.before)
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
                setDisable8021xFromInterface(ip)
        else:
                print (ip+' down')

os.chdir('/root/scripts/pythonSample')


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
import os
import csv
import sys
import time
import socket
import datetime
import requests
import piglow
import smbus

lanip="192.168.1.1"
wanip="185.151.30.154"
dnsip="8.8.8.8"
checkurl="sunrise.ch"
checkip="8.8.8.8"
statusfile="status.csv"
summaryfile="summary.csv"
localstatus = dnsstatus = httpstatus = httpdnsstatus = False
piglow.clear_on_exit = False

upstream = downstream = ping = "0"
runspeedtest = True
showLight = True


def current_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def check(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        return False

def speedtest():
  # https://github.com/sivel/speedtest-cli/blob/master/speedtest.py
  # https://pypi.org/project/speedtest-cli/
  global upstream
  global downstream
  global ping
  try:
    response = subprocess.Popen('/usr/bin/speedtest-cli --simple', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    print(response)
    pingtime = re.findall('Ping:\s(.*?)\s', response, re.MULTILINE)
    download = re.findall('Download:\s(.*?)\s', response, re.MULTILINE)
    upload = re.findall('Upload:\s(.*?)\s', response, re.MULTILINE)
    ping = pingtime[0].replace(',', '.')
    downstream = download[0].replace(',', '.')
    upstream = upload[0].replace(',', '.')
    return downstream
  except Exception as ex:
    return False

def cloudpost(trigger, value1="value", value2="value", value3="value" ):
  #curl -X POST -H "Content-Type: application/json" -d '{"value1":"a","value2":"b","value3":"c"}' https://maker.ifttt.com/trigger/speedtest/with/key/bwsApCHUKW7lsihEPoT2tg
  url = 'https://maker.ifttt.com/trigger/'+trigger+'/with/key/bwsApCHUKW7lsihEPoT2tg'
  myobj = {"value1":value1,"value2":value2,"value3":value3}
  try:
    x = requests.post(url, data = myobj)
    return(x.text)
  except Exception as ex:
    return False

def statustext(status):
  if status:
    return "UP"
  else:
    return "Down"

def writestatus(file, values):
  with open(file, mode='a') as status_file:
      status_writer = csv.writer(status_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      status_writer.writerow(values)
  return("done")

def glow(color="green"):
  if showLight:
      print("Make the World bright")
      try:
        if color=="green":
          piglow.green(200)
          piglow.red(0)
          piglow.orange(0)
        elif color=="red":
          piglow.green(0)
          piglow.red(150)
          piglow.orange(0)
        else:
          piglow.green(0)
          piglow.red(0)
          piglow.orange(150)
        piglow.show()
      except Exception as ex:
        print(ex)

localstatus=check(lanip, 80, 3)
print("Local: ("+lanip+"): "+statustext(localstatus))
dnsstatus=check(dnsip, 53, 3)
print("DNS: ("+dnsip+"): "+statustext(dnsstatus))
httpstatus=check(wanip, 80, 3)
print("WAN IP: ("+wanip+"): "+statustext(httpstatus))
httpdnsstatus=check(checkurl, 80, 3)
print("WAN HTTP ("+checkurl+"): "+statustext(httpdnsstatus))

allup = (localstatus and dnsstatus and httpstatus and httpdnsstatus)
anyup = (localstatus or dnsstatus or httpstatus or httpdnsstatus)
alldown = (not localstatus and not dnsstatus and not httpstatus and not httpdnsstatus)
anydown = (not localstatus or not dnsstatus or not httpstatus or not httpdnsstatus)


#print (localstatus and dnsstatus and httpstatus and httpdnsstatus)
if allup:
  speedtest()
  #Speedtest Resultat auf Dropbox speichern
  cloudpost("speedtest", ping, upstream, downstream)
  glow("green")
elif anyup:
  glow("orange")
else:
  glow("green")
  

#Textzeile definieren
textzeile=[current_timestamp(), statustext(localstatus), statustext(dnsstatus), statustext(httpstatus), statustext(httpdnsstatus), ping, upstream, downstream ]
#Status ins File schreiben
print(writestatus(statusfile, textzeile))

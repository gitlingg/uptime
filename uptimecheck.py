import os
import csv
import sys
import time
import socket
import datetime
import requests

lanip="185.151.30.154"
wanip="185.151.30.154"
dnsip="lingg.be"
checkurl="sunrise.ch"
checkip="8.8.8.8"
statusfile="status.csv"
summaryfile="summary.csv"
localstatus = dnsstatus = httpstatus = httpdnsstatus = False
upstream = downstream = ping = "0"
runspeedtest = True


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
    response = subprocess.Popen('/usr/local/bin/speedtest-cli --simple', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    pingtime = re.findall('Ping:\s(.*?)\s', response, re.MULTILINE)
    download = re.findall('Download:\s(.*?)\s', response, re.MULTILINE)
    upload = re.findall('Upload:\s(.*?)\s', response, re.MULTILINE)
    ping = pingtime[0].replace(',', '.')
    downstream = download[0].replace(',', '.')
    upstream = upload[0].replace(',', '.')
    return downstream
  except Exception as ex:
    return False

def writestatus(file, values):
  with open(file, mode='a') as status_file:
      status_writer = csv.writer(status_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      status_writer.writerow(values)
  return("done")

localstatus=check(lanip, 80, 3)
print(localstatus)
dnsstatus=check(dnsip, 53, 3)
print(dnsstatus)
httpstatus=check(wanip, 80, 3)
print(httpstatus)
httpdnsstatus=check(checkurl, 80, 3)
print(httpdnsstatus)

allup = (localstatus and dnsstatus and httpstatus and httpdnsstatus)
anyup = (localstatus or dnsstatus or httpstatus or httpdnsstatus)
alldown = (not localstatus and not dnsstatus and not httpstatus and not httpdnsstatus)
anydown = (not localstatus or not dnsstatus or not httpstatus or not httpdnsstatus)
print("AllUp:\t\t"+str(allup))
print("AnyUp:\t\t"+str(anyup))
print("AllDown:\t"+str(alldown))
print("AnyDown:\t"+str(anydown))
print(current_timestamp()+"\t..."+str(anyup))

#print (localstatus and dnsstatus and httpstatus and httpdnsstatus)
if allup:
  speedtest()

def switch(value):
  if value:
    return "UP"
  else:
    return "Down"


localstatus = switch(localstatus)
dnsstatus = switch(dnsstatus)
httpstatus = switch(httpstatus)
httpdnsstatus = switch(httpdnsstatus)


def cloudpost(trigger, value1="value", value2="value", value3="value" ):
  #curl -X POST -H "Content-Type: application/json" -d '{"value1":"a","value2":"b","value3":"c"}' https://maker.ifttt.com/trigger/speedtest/with/key/bwsApCHUKW7lsihEPoT2tg
  url = 'https://maker.ifttt.com/trigger/'+trigger+'/with/key/bwsApCHUKW7lsihEPoT2tg'
  myobj = {"value1":value1,"value2":value2,"value3":value3}
  try:
    x = requests.post(url, data = myobj)
    return(x.text)
  except Exception as ex:
    return False

print(cloudpost("speedtest", localstatus, dnsstatus, httpstatus))
print(cloudpost("iPhonePush", "Hey!!"))
textzeile=[current_timestamp(), localstatus, dnsstatus, httpstatus, httpdnsstatus, ping, upstream, downstream ]
print(writestatus(statusfile, textzeile))

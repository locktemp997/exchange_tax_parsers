#Donation address: xrb_33jc7cshocfi3pmx7jfnux4z16dqu1b59y9jp9u6ui3naipfzymysc8hxwst

#Python script to scrape kucoin order history and format csv's for use to import trades to bitcoin.tax website

#README:
#Tested on ubuntu with python 2.7 and python 3.5 but should work on Windows too.
#requires a kucoin api key to use, user will be asked for the key/secret upon running script

#outputs: kucointrades_bitcointaxformat.csv

# INSTALL INSTRUCTIONS:
# python 2.7 https://www.python.org/download/releases/2.7/ (or apt-get python in ubuntu)
# on WINDOWS download https://bootstrap.pypa.io/get-pip.py into the folder you installed Python27 (probably C:/Python27/)
# might need to use pip to install missing modules but they may already be included by default in your python

# IF you get an error about "no module named builtins" when trying to run the script, you need to do:
# pip install future  (or on windows pip.exe install future)

# RUN by typing in cmd/terminal: python kucoin_parser.py

# PROBLEMS:
# If you get an error about invalid nonce, please make sure your system time is synchronized and accurate! Kucoin checks that the 
# nonce conforms to your system time I guess?

import hashlib
import hmac
import time
import requests
import json
import base64
import sys
import csv
from builtins import input



url = 'https://api.kucoin.com/v1/order/dealt'

print("To run this parser, you need to setup an API key/secret pair on Kucoin's website")
print("To do this, go to your account settings -> API Keys -> Create")
print("This key will ONLY be used to grab dealt orders, and you should delete/deactivate the key pair from kucoins website after running this script")




mykey = input("Enter the API Key now \n")
if len(mykey) > 10:
    mysecret = input("Enter the API Secret now \n")
    if len(mysecret) < 10:
        print("Secret might be too short, are you sure it's correct? Results may be garbage")
else:
    print("Key might be too sure , are you sure it's correct? Results may be garbage")


timezone = input("Please enter timezone in UTC (e.g. for PST enter: -8)")
timezone_v = float(timezone)
timezone = '%0.2i'%timezone_v + '00'

pagenum = 1

#First do an API req and make sure nonce works - sometimes on machines that have inaccurate time, kucoin get's upset and declares the nonce to be invalid
#We use their return timestamp on the response to correct the difference if that's the case

nonce = int(time.time() * 1000)
path = '/v1/order/dealt'
query_str = 'page=%i'%(pagenum)
sig_str = ("{}/{}/{}".format(path, nonce, query_str)).encode('utf-8')
m = hmac.new(mysecret.encode('utf-8'),base64.b64encode(sig_str),hashlib.sha256)
payload={}
headers = {'KC-API-KEY':mykey,'KC-API-SIGNATURE':'0','KC-API-NONCE':str(nonce)}
params = {'page':str(pagenum)}
headers['KC-API-SIGNATURE'] = m.hexdigest()

try:
    response = requests.request('GET',url,params=params,data=payload,headers=headers,timeout=10.0)
except:
    print("timed out, try runnning again")
    sys.exit()

j1 = response.json()
if j1['msg'] == 'Invalid nonce':
    #Need to correct time offset
    print("Correcting time offset with Kucoin API, make sure resulting CSV datestamp looks correct")
    time_offset = j1['timestamp'] - nonce
else:
    time_offset = 0




z2 = []
while True:
    print("Grabbing trades from page %i" % pagenum)
    nonce = int(time.time() * 1000 + time_offset)
    
    path = '/v1/order/dealt'
    #limit = 72
    
    #query_str = 'limit=%i&page=%i'%(limit,page)
    query_str = 'page=%i'%(pagenum)
    sig_str = ("{}/{}/{}".format(path, nonce, query_str)).encode('utf-8')
    m = hmac.new(mysecret.encode('utf-8'),base64.b64encode(sig_str),hashlib.sha256)
    
    payload={}
    headers = {'KC-API-KEY':mykey,'KC-API-SIGNATURE':'0','KC-API-NONCE':str(nonce)}
    #params = {'limit':str(limit),'page':str(page)}
    params = {'page':str(pagenum)}
    headers['KC-API-SIGNATURE'] = m.hexdigest()

    try:
        response = requests.request('GET',url,params=params,data=payload,headers=headers,timeout=10.0)
    except:
        print("timed out, try runnning again")
        sys.exit()
    
    js = response.json()
    
    if js['success'] != True:
        print("failure in getting api data")
        print(js['msg'])
        sys.exit()
    else:
        j=js['data']['datas']
        if j == []:
            #found end, quit
            break
        
        for k in j:
            amount = k['amount']
            coinType = k['coinType']
            coinTypePair = k['coinTypePair']
            datestamp = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime( (k['createdAt']/1000.0) + timezone_v*60*60) )
            datestamp = datestamp + ' ' + timezone
            action = k['direction']
            price = k['dealPrice']
            dealValue = k['dealValue']
            fee = k['fee']
            #kucoin always does the fee on the coin that you ended up with after the trade
            if action == 'BUY':
                #fee currency is in first coin
                feecoin = coinType
            else:
                feecoin = coinTypePair
            z2.insert(0,[datestamp,'Kucoin',action,coinType,'%f'%amount,coinTypePair,'%f'%price,'%f'%fee,feecoin])
        
        if len(j) < js['data']['limit']:
            #found end quit
            break
    pagenum = pagenum + 1
            

        
z2.insert(0,['Date','Source','Action','Symbol','Volume','Currency','Price','Fee','FeeCurrency'])
 
if (sys.version_info > (3, 0)):
    with open("kucointrades_bitcointaxformat.csv","w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(z2)            
else:
    with open("kucointrades_bitcointaxformat.csv","wb") as f:
        writer = csv.writer(f)
        writer.writerows(z2)     

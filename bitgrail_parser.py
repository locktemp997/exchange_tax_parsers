# Donation address: xrb_33jc7cshocfi3pmx7jfnux4z16dqu1b59y9jp9u6ui3naipfzymysc8hxwst

# Python script to scrape bitgrail API order history and format csv's for use to import trades to bitcoin.tax and cointracking.info websites

# README:
# Tested on ubuntu but should work on Windows too - check that the output csv file look formatted okay in notepad though!
# tested on python 2.7 but I've made some tweaks to make it compatible with python 3+

# outputs: bitgrailtrades_cointrackingformat.csv and bitgrailtrades_bitcointaxformat.csv

# INSTALL INSTRUCTIONS:
# python 2.7 https://www.python.org/download/releases/2.7/ (or apt-get python in ubuntu)

# RUN by typing in cmd/terminal: python bitgrail_parsery.py


import csv
import time
import requests
import hmac
import hashlib
from builtins import input

url = 'https://api.bitgrail.com/v1/lasttrades'

timezone = input("Please enter timezone in UTC (e.g. for PST enter: -8)")
timezone_v = float(timezone)
timezone = '%0.2i'%timezone_v + '00'

print("This script requires an API key generated from the https://bitgrail.com/api-keys website")
print("The key does not need to have trading or withdrawal enabled and you can delete it immediately after running script")

mykey = input('Type or C/P the API Key \n')
mysecret = input('Type or C/P the API Secret \n')

#API doesn't provide fee amount so we must calc it manually
#Bitgrail fee has always been 0.2%, hopefully doesnt change in future
fee_percent = 0.002


def nonce():
    return int(time.time()*1000)

n=nonce()
payload = {'nonce':n}
headers = {'KEY':mykey,'SIGNATURE':'0'}

signature = hmac.new(mysecret, 'nonce=%i' % n, digestmod=hashlib.sha512)

headers['SIGNATURE'] = signature.hexdigest()

#Standard requests method

response = requests.request('POST',url,data=payload,headers=headers,timeout=10.0)

js=response.json()
z = []
if js['success'] == 1:
    j=js['response']
    #convret dictionary to list and then sort it
    j = list(j.values())
    j = sorted(j,key = lambda d: d['date'])
    #Loop thru and parse the trades into a list of lists
    for i in j:
        market = i['market']
        amount = i['amount']
        price = i['price']
        datestamp = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime( float(i['date']) + timezone_v*60*60) )
        action = i['type']
        fee = amount*price*fee_percent
        #On cointracking, fee should already be included in the amounts!
        if action == 'sell':
            start_coin = market[market.find('-')+1:]
            end_coin = market[0:market.find('-')]
            amount_first_coin = amount
            amount_second_coin = amount*price - fee
            fee_cur = end_coin
        else:
            start_coin = market[0:market.find('-')]
            end_coin = market[market.find('-')+1:]
            amount_second_coin = amount
            amount_first_coin = amount*price + fee
            fee_cur = start_coin
            
        z.append(["Trade","%f"%amount_second_coin,"%s"%end_coin,"%f"%amount_first_coin,"%s"%start_coin,"%f"%fee,"%s"%fee_cur,"Bitgrail","","","%s"%datestamp])
        
        
    z.insert(0,["Type","Buy","Cur.","Sell","Cur.","Fee","Cur.","Exchange","Group","Comment","Date"])
    with open("bitgrailtrades_cointrackingformat.csv","w") as f:
        writer = csv.writer(f)
        writer.writerows(z)         
else:
    print("Failed to grab trades, check your keys and internet connection")
    
z2 = []
if js['success'] == 1:
    j=js['response']
    #convret dictionary to list and then sort it
    j = list(j.values())
    j = sorted(j,key = lambda d: d['date'])
    #Loop thru and parse the trades into a list of lists
    for i in j:
        market = i['market']
        volume = i['amount']
        price = i['price']
        datestamp = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime( float(i['date']) + timezone_v*60*60) )
        datestamp = datestamp + ' ' + timezone
        action = i['type']
        fee = volume*price*fee_percent
        symbol = market[market.find('-')+1:]
        currency = market[0:market.find('-')]        
        #On cointracking, fee should NOT be included in amounts already.
        if action == 'buy':
            action = 'BUY'
        else:
            action = 'SELL'
        z2.append([datestamp,'Bitgrail',action,symbol,'%f'%volume,currency,'%f'%price,'%f'%fee])


    z2.insert(0,['Date','Source','Action','Symbol','Volume','Currency','Price','Fee'])


    with open("bitgrailtrades_bitcointaxformat.csv","w") as f:
        writer = csv.writer(f)
        writer.writerows(z2)
     
else:
    print("Failed to grab trades, check your keys and internet connection")
        


import hashlib
import hmac
import time
import requests
import json
import base64
import sys
import csv
from builtins import input
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


#Liqui api does not return fee amounts and does not include them at all in the api data, so they must be calculated
#however we also dont know if the trade was executed as maker(0.1%) or taker(0.25%)

#For this we'll assume all orders are executed as the average of these fees
fee_percent = (0.001 + 0.0025)/2


print("To run this parser, you need to setup an API key/secret pair on Liqui's website")
print("To do this, go to Profile -> API Keys and create a key with Info permission")
print("This key will ONLY be used to grab dealt orders, and you should delete/deactivate the key pair from Liquis website after running this script")
print("Currently this is set to try to grab 10k trades - no idea if api will actually work at such large number of trades")


mykey = input("Enter the API Key now \n")
if len(mykey) > 10:
    mysecret = input("Enter the API Secret now \n")
    if len(mysecret) < 10:
        print("Secret might be too short, are you sure it's correct? Results may be garbage")
else:
    print("Key might be too sure , are you sure it's correct? Results may be garbage")
    
    

params = {'method':'TradeHistory','nonce':int(time.time()),'count':10000}
data = urlencode(params)

headers = {'Key':mykey,'Sign':hmac.new(mysecret.encode(),data.encode(),hashlib.sha512).hexdigest()}
resp = requests.post('https://api.liqui.io/tapi',data=params, headers=headers)
data = resp.json()

if data['success'] == 1:
    #parse trades
    orders = data['return']
    z2=[]
    for key in orders:
        volume = orders[key]['amount']
        pair = orders[key]['pair']
        coin1 = pair[:pair.find('_')].upper()
        coin2 = pair[pair.find('_')+1:].upper()
        price = orders[key]['rate']
        
        timestamp_raw = orders[key]['timestamp']
        datestamp = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(timestamp_raw ) )       
        trade_type = orders[key]['type']
        if trade_type == 'buy':
            action = 'BUY'
        else:
            action = 'SELL'
            
        #assuming fee is always taken on the coin that you end up with after the trade - unsure if this is correct..
        if action == 'BUY':
            #fee currency is in first coin
            fee = volume*fee_percent
            feecoin = coin1
        else:
            fee = volume*price*fee_percent
            feecoin = coin2        
        z2.insert(0,[datestamp,'Liqui',action,coin1,'%f'%volume,coin2,'%f'%price,'%f'%fee,feecoin])
        
        
    z2.insert(0,['Date','Source','Action','Symbol','Volume','Currency','Price','Fee','FeeCurrency'])
    
    if (sys.version_info > (3, 0)):
        with open("liquitrades_bitcointaxformat.csv","w", newline='') as f:
            writer = csv.writer(f)
            writer.writerows(z2)            
    else:
        with open("liquitrades_bitcointaxformat.csv","wb") as f:
            writer = csv.writer(f)
            writer.writerows(z2)     
    
else:
    print('Error getting api data')
    print(data['stat']['errors'])
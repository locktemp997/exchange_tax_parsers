#Donation address: xrb_33jc7cshocfi3pmx7jfnux4z16dqu1b59y9jp9u6ui3naipfzymysc8hxwst

#Python script to take mercatox csv data and format for upload to bitcoin.tax 

#README:
#Go to mercatox Transactions History and click "Download CSV", make sure its saved as trade.csv in same folder as this script.
#Uses Python 2.7
#Tested on ubuntu but should work on Windows too.
#Output: mercatoxtrades_bitcointaxformat.csv


# INSTALL:
# python 2.7 https://www.python.org/download/releases/2.7/ (or apt-get python in ubuntu)

# RUN by typing in cmd/terminal: python mercatox_parsery.py

import csv
z=[]
#turns out mercatox reports timestamps in utc 0
#timezone = raw_input("Please enter timezone in UTC (e.g. for PST enter: -8)")
#timezone = float(timezone)
#timezone = '%0.2i'%timezone + '00'

timezone = '0000'

def month_string_to_number(string):
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr':4,
         'may':5,
         'jun':6,
         'jul':7,
         'aug':8,
         'sep':9,
         'oct':10,
         'nov':11,
         'dec':12
        }
    s = string.strip()[:3].lower()

    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')

with open('trade.csv','rb') as csvfile:
    r = csv.reader(csvfile,delimiter=',')
    for row in r:
        if row[0] == 'txid':
            continue
        price = row[1]
        #price is always in currency of second coin
        amount = row[2]
        #amount always in first coin
        total = row[3] 
        #total = price*amount + fee, always in second coin currency
        pair_id = row[4]
        first_coin = pair_id[0:pair_id.find('/')]
        second_coin = pair_id[pair_id.find('/')+1:]
        
        action = row[5]
        if action == 'buy':
            action = 'BUY'
        elif action == 'sell':
            action = 'SELL'
        else:
            print "WTF"
            break
        timestamp = row[6]
        
        #fix timestamp
        month = timestamp[0:timestamp.find(' ')]
        month = '%0.2i'%month_string_to_number(month)
        day = timestamp[timestamp.find(' ')+1:timestamp.find(',')]
        day = '%0.2i'%int(day)
        year = timestamp[timestamp.find(',')+2:timestamp.find(',')+6]
        tmp = timestamp[timestamp.find(',')+6:]
        hour = tmp[tmp.find(' ')+1:tmp.find(':')]
        if tmp.find('AM') > -1:
            minsec = tmp[tmp.find(':')+1:tmp.find(':')+6]
        else:
            minsec = tmp[tmp.find(':')+1:tmp.find(':')+6]
            hour = str(int(hour)+12)

        #new date
        date = year+'-'+month+'-'+day+' '+hour+':'+minsec+' '+timezone
        if action == 'BUY':
            fee = str(float(amount)*float(price)*0.0025)
        else:
            fee = '0'
        #what currency are we buying or selling? always the first coin
        z.append([date,'Mercatox',action,first_coin,'%f'%float(amount),second_coin,'%f'%float(price),'%f'%float(fee)])

z.insert(0,['Date','Source','Action','Symbol','Volume','Currency','Price','Fee'])

with open("mercatoxtrades_bitcointaxformat.csv","wb") as f:
    writer = csv.writer(f)
    writer.writerows(z)

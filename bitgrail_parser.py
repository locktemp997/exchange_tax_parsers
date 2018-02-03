#Donation address: xrb_33jc7cshocfi3pmx7jfnux4z16dqu1b59y9jp9u6ui3naipfzymysc8hxwst

#Python script to scrape bitgrail order history and format csv's for use to import trades to bitcoin.tax and cointracking.info websites

#NOTE: Bitgrail does not store a year with its date string.
#So this script assumes you joined bitgrail sometime AFTER end of March 2017 and you're running this script BEFORE end of March 2018.

#README:
#Tested on ubuntu but should work on Windows too.

#outputs: bitgrailtrades_cointrackingformat.csv and bitgrailtrades_bitcointaxformat.csv

# INSTALL INSTRUCTIONS:
# python 2.7 https://www.python.org/download/releases/2.7/ (or apt-get python in ubuntu)
# for UBUNTU install chromium, for windows chrome
# also need to download the chromedriver https://sites.google.com/a/chromium.org/chromedriver/
# On UBUNTU place this in /usr/local/bin/ for WINDOWS place in c:\Windows\

# RUN by typing in cmd/terminal: python bitgrail_parsery.py




import csv
import time
from selenium import webdriver

timezone = raw_input("Please enter timezone in UTC (e.g. for PST enter: -8)")
timezone = float(timezone)
timezone = '%0.2i'%timezone + '00'

driver = webdriver.Chrome()
driver.get("https://bitgrail.com")


raw_input('Press enter once logged in successfully')


driver.get("https://bitgrail.com/orders")
driver.implicitly_wait(10)

#If missing some trades, maybe page isnt loading fast enough, could sleep here
#time.sleep(10)

x = driver.find_elements_by_class_name("table2")[1]
z=x.text
lines = z.splitlines()
#remove beginning shit
lines = lines[1:]


#Loop thru and parse the trades into a list of lists

z = []
for i in range(0,len(lines)):
    #Check if this is a buy or sell
    if lines[i].find('Sell') > -1:
        #this means we are selling the second coin in the pair (e.g. BTC/XRB -> Selling XRB)
        start_coin = lines[i][lines[i].find('-')+1:lines[i].find(' ')]
        end_coin = lines[i][0:lines[i].find('-')]
        tmp = lines[i][lines[i].find('Sell')+5:]
        tmp = tmp.split()
        price_in_second_coin_units = float(tmp[2])
        price_in_first_coin_units = 1.0/price_in_second_coin_units
        amount_first_coin = float(tmp[0])
        amount_second_coin = float(tmp[6])
        fee_cur = end_coin
        
    elif lines[i].find('Buy') > -1:
        #this means we are Buying the second coin and selling the first (e.g. BTC/XRB -> Buying XRB)
        end_coin = lines[i][lines[i].find('-')+1:lines[i].find(' ')]
        start_coin = lines[i][0:lines[i].find('-')]
        tmp = lines[i][lines[i].find('Buy')+4:]
        tmp = tmp.split()
        price_in_first_coin_units = float(tmp[2])
        price_in_second_coin_units = 1.0/price_in_first_coin_units
        amount_first_coin = float(tmp[6])
        amount_second_coin = float(tmp[0])
        fee_cur = start_coin
    else:
        print "WTF"
        break
    
    
    fee = float(tmp[4])
    #grab date str and
    tmp2 = lines[i].split()
    month = float(tmp2[1][:2])
    if month > 6:
        date = tmp2[1]+'/2017'
    else:
        date = tmp2[1]+'/2018'
    
    time = tmp2[2]
    
    
    month = float(tmp2[1][:2])
    #assuming you joined bitgrail april 2017
    if month > 3:
        year = '2017'
    else:
        year = '2018'
    
    month = tmp2[1][:2]
    day = tmp2[1][3:5]
    
    date = year+'-'+month+'-'+day+' '+tmp2[2]  
    
    #store in the list
    z.insert(0,["Trade","%f"%amount_second_coin,"%s"%end_coin,"%f"%amount_first_coin,"%s"%start_coin,"%f"%fee,"%s"%fee_cur,"Bitgrail","","","%s"%date])


z.insert(0,["Type","Buy","Cur.","Sell","Cur.","Fee","Cur.","Exchange","Group","Comment","Date"])

with open("bitgrailtrades_cointrackingformat.csv","wb") as f:
    writer = csv.writer(f)
    writer.writerows(z)
    
    
z2 = []

for i in range(0,len(lines)):
    #Check if this is a buy or sell
    tl = []
    #grab date str and
    tmp = lines[i].split()
    month = float(tmp[1][:2])
    #assuming you joined bitgrail after june 2017
    if month > 3:
        year = '2017'
    else:
        year = '2018'
    
    month = tmp[1][:2]
    day = tmp[1][3:5]
    
    date = year+'-'+month+'-'+day+' '+tmp[2]+' '+timezone
    
    
    
    if lines[i].find('Sell') > -1:
        action = 'SELL'
        tmp2 = lines[i][lines[i].find('Sell')+5:]
        tmp2 = tmp2.split()        
    else:
        action = 'BUY'
        tmp2 = lines[i][lines[i].find('Buy')+4:]
        tmp2 = tmp2.split()        
    
    symbol = lines[i][lines[i].find('-')+1:lines[i].find(' ')]
    volume = float(tmp2[0])
    currency = lines[i][0:lines[i].find('-')]
    price = float(tmp2[2])
    fee = float(tmp2[4])
 
 
    z2.insert(0,[date,'Bitgrail',action,symbol,'%f'%volume,currency,'%f'%price,'%f'%fee])


z2.insert(0,['Date','Source','Action','Symbol','Volume','Currency','Price','Fee'])


with open("bitgrailtrades_bitcointaxformat.csv","wb") as f:
    writer = csv.writer(f)
    writer.writerows(z2)

#Donation address: xrb_33jc7cshocfi3pmx7jfnux4z16dqu1b59y9jp9u6ui3naipfzymysc8hxwst

#SELENIUM VERSION OF KUCOIN PARSER - USE FOR NOW WHEN YOU HAE MORE THAN 100 TRADES
#I'm working on seeing if the API can be fixed but use this until then.

#Python script to scrape kucoin order history and format csv's for use to import trades to bitcoin.tax website

#README:
#Tested on ubuntu with python 2.7 and python 3.5 but should work on Windows too.

#outputs: kucointrades_bitcointaxformat.csv

# INSTALL INSTRUCTIONS:
# python 2.7 https://www.python.org/download/releases/2.7/ (or apt-get python in ubuntu)
# on WINDOWS download https://bootstrap.pypa.io/get-pip.py into the folder you installed Python27 (probably C:/Python27/)
# might need to use pip to install missing modules but they may already be included by default in your python

# IF you get an error about "no module named builtins" when trying to run the script, you need to do:
# pip install future  (or on windows pip.exe install future)

# RUN by typing in cmd/terminal: python kucoin_parser.py


import csv
import time
import re
import sys
from selenium import webdriver
from builtins import input
timezone = input("Please enter timezone in UTC (e.g. for PST enter: -8)")
timezone = float(timezone)
timezone = '%0.2i'%timezone + '00'

driver = webdriver.Chrome()

driver.get("https://kucoin.com")

input('Press enter once logged in successfully')

driver.set_page_load_timeout(5)
try:
    driver.get("https://www.kucoin.com/#/user/account/deal-orders")
except:
    pass

time.sleep(3)
#driver.implicitly_wait(10)

#If missing some trades, maybe page isnt loading fast enough, could sleep here
#time.sleep(10)

tmp=driver.find_element_by_class_name("ant-pagination")
numPages = int(tmp.text[-1])
z2 = []
for nn in range(1,numPages+1):
    x=driver.find_element_by_class_name("ant-table-tbody")
    x = x.text
    lines = x.splitlines()
    for i in range(0,len(lines)):
        date = lines[i][lines[i].find('20'):lines[i].find('20')+19]
        date = date + ' ' + timezone
        tradepair = lines[i][0:lines[i].find('20')-1]
        coin1 = tradepair[0:tradepair.find('/')-1]
        coin2 = tradepair[tradepair.find('/')+2:]
        if lines[i].find('Sell') > -1:
            action = 'SELL'
            tmp2 = lines[i][lines[i].find('Sell')+5:]
            tmp2 = tmp2.split()        
        else:
            action = 'BUY'
            tmp2 = lines[i][lines[i].find('Buy')+4:]
            tmp2 = tmp2.split()              
        
        price = float(re.findall(r'([\d.]+)', tmp2[0])[0])
        amount_first = float(re.findall(r'([\d.]+)', tmp2[1])[0])
        amount_second = float(re.findall(r'([\d.]+)', tmp2[2])[0])
        z2.insert(0,[date,'Kucoin',action,coin1,'%f'%amount_first,coin2,'%f'%price])
        
    if nn < numPages:
        y=driver.find_element_by_class_name("ant-pagination-next")
        y.click()
        time.sleep(3)

z2.insert(0,['Date','Source','Action','Symbol','Volume','Currency','Price','Fee'])
if (sys.version_info > (3, 0)):
    with open("kucointrades_bitcointaxformat.csv","w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(z2)            
else:
    with open("kucointrades_bitcointaxformat.csv","wb") as f:
        writer = csv.writer(f)
        writer.writerows(z2)     
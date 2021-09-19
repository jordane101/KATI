'''
Kraken Automated Trading Interface (KATI)
@author: Eli Jordan

This file is the main script that runs the command for the bot to interface with
humans. The purpose of this script is to analyze and trade automatically.

'''

import krakenLibrary as kl
import time
import krakenex
import os
from dotenv import load_dotenv

load_dotenv('keys.env')
api_key = os.environ.get('API_KEY_KRAKEN')
api_sec = os.environ.get('API_SEC_KRAKEN')

kraken = krakenex.API(key=api_key,secret=api_sec)

print("Early Testing of the Kraken Automated Trading Interface (KATI)")
print("enter 'q' to quit")
while True:
    #while loop to access commands
    p = input("Enter a command:")
    if p == 'q':
        break
        kraken.close()
    elif p.lower() == 'balance':
        #access balance in account
        resp = kraken.query_private('Balance')
        print(resp['result'])
    elif p.lower() == 'assets':
        #generate the entire list of tradeable assets
        response = kraken.query_public('AssetPairs')
        print(response['result'])
    elif p.lower() == 'ticker':
        #get current ticker info for asset pair
        assetpair = input("Enter asset pair to retrieve ticker:")
        response = kraken.query_public(f'Ticker?pair={assetpair.upper()}')
        print(response['result'])
    elif p.lower() == 'autotrade':
        kl.autoTrade()
        
    elif p.lower() == 'analysis':
        a = input('Which asset would you like analysis for?')
        analysis = kl.query_analysis(a)
        print(analysis)
    elif p.lower() == 'cancel all':
        resp = kl.cancelAll()
        if not resp['error']:
            print('All orders canceled successfully')

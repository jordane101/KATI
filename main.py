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
    elif p.lower() == 'run':
        #auto buy/sell based on technical analysis API
        # initialize variables
        running = True
        queriable = False
        query_time = 0
        # initial query to start program, then wait
        analysis = kl.query_analysis('btc')
        query_time = analysis[0]
        data = analysis[1]
        print(data)
        while running:
            # while loop querying analysis api and automatically adding buy/sell orders
            if time.time() >= query_time + 900:
                #wait 15 minutes between queries
                analysis = kl.query_analysis('btc')
                query_time = analysis[0]
                data = analysis[1]
                
                volumeData = 100 / data['price_btc']
                priceData = data['price_btc']
                print(data)
                buy = data['recommendation'] == 'buy' and data['sentiment'] > 25
                sell = data['recommendation'] == 'sell' and data['sentiment'] < 20
                if buy:
                    resp = kl.addOrder('buy', priceData, volumeData, 'limit')
                    if not resp['error']:
                        print('Buy order added!')
                    else:
                        print('error when adding order')
                elif sell:
                    resp = kl.addOrder('sell', priceData, volumeData, 'limit')
                    if not resp['error']:
                        print('Sell order added!')
                    else:
                        print('error when adding order')
                else:
                    print('hodling')
            
    elif p.lower() == 'analysis':
        a = input('Which asset would you like analysis for?')
        analysis = kl.query_analysis(a)
        print(analysis)
    elif p.lower() == 'cancel all':
        resp = kl.cancelAll()
        if not resp['error']:
            print('All orders canceled successfully')

'''
Date: 12/10/2021
@author: Eli Jordan

This file is meant to be imported into KATI.py to provide recommendations of buying/selling assets.


'''

import pandas as pd #dataframes to organize api data
import requests #api calls
import time
import datetime
import matplotlib.pyplot as plt

class APIData:
    #class to store and update data from the API6
    #this class can be used without an API key or Kraken account
    url = 'https://api.kraken.com'
    def __init__(self,assetPair,period=1):
        self.assetPair=assetPair
        self.period = {'seconds':period*24*60*60, 'minutes':period*24*60,'hours':period*24,'days':period}
        if assetPair[0] == 'X':
            self.urlPair = assetPair[1:4] + assetPair[5:8]
        else:
            self.urlPair = assetPair[:-4] + assetPair[-3:]
        if assetPair == 'XXBTZUSD':
            self.asset = 'BTC'
        elif assetPair == 'XETHZUSD':
            self.asset = 'ETH'
        else:
            self.asset = assetPair[:-4]
        self.getOHLC()
        self.getTicker()
    def getOHLC(self, interval=1):
        #interval only = 1 5 15 30 60 240 1440 10080 21600 in minutes
        #interval default is 1 day
        #API call to get OHLC data and output as a dataframe
        
        since = time.time() - self.period['seconds']*2#double period so rolling average has enough data
        self.interval = {'seconds': interval*60, 'minutes': interval, 'hours': interval/60, 'days': interval/60/24}
        newUrl = type(self).url + f"/0/public/OHLC?pair={self.urlPair}&since={since}&interval={self.interval['minutes']}"
        resp = requests.get(newUrl).json()
        if resp['error']:
            print(resp)
        else:
            del resp['result']['last']
            dataDict = {}
            if self.assetPair[0] == 'X':
                for i in resp['result'][self.assetPair]:
                    work = []
                    for j in i[1:]:
                        work.append(float(j))
                    dataDict[datetime.datetime.fromtimestamp(i[0])] = work
            else:
                for i in resp['result'][self.urlPair]:
                    work = []
                    for j in i[1:]:
                        work.append(float(j))
                    dataDict[datetime.datetime.fromtimestamp(i[0])] = work
                    
            columnList = ['Open','High','Low','Close','Vmap','Volume','Count']
            self.dfOHLC = pd.DataFrame.from_dict(dataDict,orient='index',columns=columnList)
            
        
    def getTicker(self):
        self.price = {}
        newUrl = type(self).url + f'/0/public/Ticker?pair={self.urlPair.upper()}'
        resp = requests.get(newUrl).json()
        
        if resp['error']:
            print(resp)
        else:
            if self.assetPair[0] == 'X':
                self.price['Last trade'] = resp['result'][self.assetPair]['c'][0]
                self.price['High'] = resp['result'][self.assetPair]['h'][0]
                self.price['Low'] = resp['result'][self.assetPair]['l'][0]
            else:
                self.price['Last trade'] = resp['result'][self.urlPair]['c'][0]
                self.price['High'] = resp['result'][self.urlPair]['h'][0]
                self.price['Low'] = resp['result'][self.urlPair]['l'][0]

class Analysis(APIData):
    
    #Handles technical analysis
    def __init__(self,assetPair,period1=14,period2=50):
        super().__init__(assetPair,period1)
        self.dataLong = APIData(assetPair,period2)
        self.updateRec()
    def getRSI(self):
        #updates RSIbuy recommendation
        
        #get the difference in price from the previous period
        delta = self.dfOHLC['Close'].diff(1)
        delta = delta.dropna()
        #get positive and negative gains
        up = delta.copy()
        down = delta.copy()
        
        up[up<0] = 0
        down[down>0] = 0
       
        avgGain = up.rolling(self.period['days']).mean()
        avgLoss = abs(down.rolling(self.period['days']).mean())
        
        #calculate Relative Strength (RS)
        RS = avgGain / avgLoss
        RS = RS.dropna()
        #calculate Relative Strength Index (RSI)
        self.RSI = 100-(100/(1.0 + RS))
        
        if self.RSI.iloc[-1] > (70):
            self.RSIbuy = True
            self.RSIsell = False
        elif self.RSI.iloc[-1] < (30):
            self.RSIsell = True
            self.RSIbuy = False
        else:
            self.RSIbuy = None
            self.RSIsell = None
    def movingAverage(self):
        #defaults to 14-day and 56-day SMA
        self.smaShort = self.dfOHLC['Close'].rolling(self.period['days']).mean().dropna()
        self.smaLong = self.dataLong.dfOHLC['Close'].rolling(self.dataLong.period['days']).mean().dropna()
        # bool values for short and long MVA crossing
        goodCross = (self.smaShort.iloc[-2] < self.smaLong.iloc[-2] and self.smaShort.iloc[-1] > self.smaLong[-1])
        badCross = (self.smaShort.iloc[-2] > self.smaLong.iloc[-2] and self.smaShort.iloc[-1] < self.smaLong[-1])
        
        k = 2/(self.period['days']+1) #smoothing factor for Exponential Moving Average
        self.EMAshort = self.dfOHLC['Close'].rolling(self.period['days']).mean()*(1-k) + self.dfOHLC['Close'].iloc[-1]*k
        self.EMAlong = self.dataLong.dfOHLC['Close'].rolling(self.dataLong.period['days']).mean()*(1-k) + self.dataLong.dfOHLC['Close'].iloc[-1]*k
        self.EMAshort = self.EMAshort.dropna()
        self.EMAlong = self.EMAlong.dropna()
        #calculate MACD
        self.MACD = self.EMAshort - self.EMAlong
        self.MACD = self.MACD.dropna()
        currentMACD = self.MACD.iloc[-1]
        if currentMACD > 0:
            self.MACDbuy = True
            self.MACDsell = False
        elif currentMACD < 0:
            self.MACDsell = True
            self.MACDbuy = False
        if goodCross:
            self.MVAbuy = True
        elif badCross:
            self.MVAsell = True
        else:
            self.MVAbuy = None
            self.MVAsell = None
        
    def forceIndex(self):
        #calculate force index for period['days']
        self.FI = self.dfOHLC['Close'].diff(1) * self.dfOHLC['Volume']
        self.FI = self.FI.dropna()
        self.currentForce = self.FI.iloc[-1]
        self.avgForce = self.FI/self.period['days']
    def updateRec(self):
        #updates indicators for buy/sell signal
        self.getRSI()
        self.movingAverage()
        self.forceIndex()
        buy = self.RSIbuy or self.MVAbuy or self.MACDbuy
        sell = self.RSIsell or self.MVAsell or self.MACDsell
        if buy:
            self.recommendation = 'buy'
        elif sell:
            self.recommendation = 'sell'
        else:
            self.recommendation = None
        
    def showData(self):
        self.updateRec()
        print('EMAshort: \n', self.EMAshort)
        print('EMAlong: \n', self.EMAlong)
        print('SMAshort: \n', self.smaShort)
        print('SMAlong: \n', self.smaLong)
        print('Force Index: \n', self.FI)
        print('Relative Strength Index: \n', self.RSI)
        print('MACD: \n', self.MACD)
#====================Test Code================









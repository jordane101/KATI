'''
Created on 11/15/2021
Updated on 11/19/2021
@author: Eli Jordan

Kraken
Automated
Trading
Interface

This file is an OOP script designed to interface with the Kraken exchange for price information and facilitate
automated trading. 

'''
import pandas as pd #dataframes to organize api data
import requests #api calls
import json #conv api data to python dict
import time
import urllib.parse
import os
import hashlib
import hmac
import base64
from dotenv import load_dotenv #store api keys in a seperate file
import turtle
import threading #multithreading for multiple loops

##===============================Data Organization=====================================
class APIData:
    #class to store and update data from the API
    #this class can be used without an API key or Kraken account
    url = 'https://api.kraken.com'
    def __init__(self,assetPair,days=14):
        self.assetPair=assetPair
        self.days = days
        if assetPair[0] == 'X':
            self.urlPair = assetPair[1:4] + assetPair[5:8]
        else:
            self.urlPair = assetPair
        if assetPair == 'XXBTZUSD':
            self.asset = 'BTC'
        elif assetPair == 'XETHZUSD':
            self.asset = 'ETH'
        else:
            self.asset = assetPair[:-4]
        self.getOHLC()
        self.getTicker()
    def getOHLC(self, interval=1440):
        #API call to get OHLC data and output as a dataframe
        since = self.days*2*24*60*60#double number of days so rolling average has enough data
        seconds = time.time() - since
        
        newUrl = type(self).url + f'/0/public/OHLC?pair={self.urlPair}&since={seconds}&interval={interval}'
        resp = requests.get(newUrl).json()
        if resp['error']:
            print(resp)
        else:
            clean = resp['result'][self.assetPair]
            ohlcList = {'o': [],
                        'h': [],
                        'l': [],
                        'c': []}
            for i in clean:
                #for loop to convert str to int and create new list
                
                openwork = (i[0], float(i[1]))
                ohlcList['o'].append(openwork)
                highwork = (i[0],float(i[2]))
                ohlcList['h'].append(highwork)
                lowwork = (i[0], float(i[3]))
                ohlcList['l'].append(lowwork)
                closework = (i[0], float(i[4]))
                ohlcList['c'].append(closework)
            #calculate moving averages for OHLC
            self.openMV = pd.DataFrame(ohlcList['o']).rolling(self.days).mean()[1].dropna() #rolling method for rolling average, dropna to clean out empty cells
            self.highMV = pd.DataFrame(ohlcList['h']).rolling(self.days).mean()[1].dropna()
            self.lowMV = pd.DataFrame(ohlcList['l']).rolling(self.days).mean()[1].dropna()
            self.closeMV = pd.DataFrame(ohlcList['c']).rolling(self.days).mean()[1].dropna()
            
        
    def getTicker(self):
        self.price = {}
        newUrl = type(self).url + f'/0/public/Ticker?pair={self.urlPair.upper()}'
        resp = requests.get(newUrl).json()
        
        if resp['error']:
            print(resp)
        else:
            self.price['Last trade'] = resp['result'][self.assetPair]['c'][0]
            self.price['High'] = resp['result'][self.assetPair]['h'][0]
            self.price['Low'] = resp['result'][self.assetPair]['l'][0]

class userData:
    #all methods in this class require a Kraken account
    url = 'https://api.kraken.com'
    def __init__(self,apiKey,secKey):
        self.api_key = apiKey
        self.api_sec = secKey
        self.updateBalance()
    def get_kraken_signature(self, urlpath, data, secret):
        # build kraken signage
        #borrowed and modified from docs.kraken.com
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()
    # Attaches auth headers and returns results of a POST request
    def kraken_request(self, uri_path, data, api_key, api_sec):
        #borrowed and modified from docs.kraken.com
        headers = {}
        headers['API-Key'] = api_key
        # get_kraken_signature() as defined in the 'Authentication' section
        headers['API-Sign'] = self.get_kraken_signature(uri_path, data, api_sec)             
        req = requests.post((type(self).url + uri_path), headers=headers, data=data)
        return req
    def updateBalance(self):
    # function to update the current balance of the account
        balanceurl = '/0/private/Balance'
        resp = self.kraken_request(balanceurl,
        {"nonce": str(int(1000*time.time()))},
        self.api_key, self.api_sec).json()
        if resp['error']:
            self.balance = None
            print(resp)
        else:
            self.balance = resp['result']
    def addOrder(self,buySell, price, volume, orderType, refid, assetPair='BTCUSD'):
        #function to send buy/sell order
        tradeuri ='/0/private/AddOrder'
        data = {
        "nonce": str(int(1000*time.time())),
        "ordertype": orderType,
        "type": buySell,
        "volume": volume,
        "pair": assetPair,
        "price": price,
        "userref": refid
        }
        resp = self.kraken_request(tradeuri,data,self.api_key,self.api_sec).json()
        return resp
    def getOpenOrders(self):
        orderUrl = '/0/private/OpenOrders'
        data = {"nonce": str(int(1000*time.time())), "trades": True}
        resp = self.kraken_request(orderUrl,data ,self.api_key,self.api_sec).json()
        self.openOrders = resp
    def cancelOrders(self):
        endpoint = '/0/private/CancelAll'
        data = {"nonce": str(int(1000*time.time()))}
        resp = self.kraken_request(endpoint,data,self.api_key,self.api_sec).json()
        print(resp)
##====================================Visuals================================================
class Bubble(turtle.Turtle):
    #Super class for Trader with turtle funcs
    
    def __init__(self, dataObj):
        super().__init__()
        self.x = None
        self.y = None
        self.data = dataObj
        self.colorVar = (0,0,0)
    def draw(self):
        self.shape('circle')
        self.ht()
        self.up()
        self.speed(0)
        self.goto(self.x,self.y)
        sizeConstant = 0.5 #adjustable for different ranges of bots, needs fluidity while running
        self.shapesize(sizeConstant * self.tradeDollars)#shapesize based on $ in asset
        self.st()
        self.drawText()
    def drawText(self):
        textTurt = turtle.Turtle()
        textTurt.ht()
        textTurt.up()
        textTurt.goto(self.x-10,self.y)
        textTurt.write(f"{self.data.asset}",font=('Arial',20,'normal'))
        textTurt.goto(self.x-10,self.y-10)
        textTurt.write(f"{self.data.price['Last trade']}",font=('Arial',10,'normal'))
                        
    
#================================Data Application=================================================        
class Trader(Bubble):
    #all methods in this class require a TA key
    #class to buy/sell automatically based on TA API
    lastBuy = 0
    def __init__(self,user,ta_key,data, tradeDollars):
        #*args for many dataObjs
        self.tradeDollars = tradeDollars
        self.running = True
        self.userObj = user
        self.dataObj = data
        self.taKey = ta_key
        super().__init__(self.dataObj)
        self.onclick(self.stopLoop)
    def updateLoop(self,timer=3):
        #timer is time in minutes to wait between API calls
        #THIS IS A LOOP
        while self.running:  
            TAurl = f'https://technical-analysis-api.com/api/v1/analysis/{self.dataObj.asset}?apiKey={self.taKey}'
            resp = requests.get(TAurl).json()
            self.recommendation = resp['recommendation']
            self.buySell()
            self.draw()
            time.sleep(60*timer) #timer to prevent going over API call limit per 24 hrs
    def buySell(self):
        self.dataObj.getTicker()
        currentPrice = float(self.dataObj.price['Last trade'])
        self.userObj.getOpenOrders()
        volumeData = self.tradeDollars/currentPrice
        if not self.userObj.balance:
            print('No money!!')
            self.running = False
        if self.userObj.openOrders.get('open'):
            print('No open orders')
            
        elif self.recommendation == 'buy':
            resp = self.userObj.addOrder('buy',currentPrice, volumeData,'limit',300,self.dataObj.assetPair)
            self.colorVar = (0,200,0)
            self.color('green')
            if not resp['error']:
                type(self).lastBuy = currentPrice
                print(f"Buy order added! TX id: {resp['result'].get('txid')}")
            else:
                print(resp)
        elif (self.recommendation == 'sell' and currentPrice > type(self).lastBuy):
            resp = self.userObj.addOrder('sell',currentPrice, volumeData,'limit',300,self.dataObj.assetPair,)
            self.colorVar=(200,0,0)
            self.color('red')
            if not resp['error']:
                print(f"Sell order added! TX id: {resp['result'].get('txid')}")
            else:
                print(resp)
    def stopLoop(self,x,y):
        self.running = False
    
#===========================================Manager Class=============================================            
class KATI:
    #class to manage program instance
    load_dotenv('testKeys.env')
    api_key = os.environ.get('API_KEY_KRAKEN')
    api_sec = os.environ.get('API_SEC_KRAKEN')
    ta_key = os.environ.get('API_TECHNICAL_ANALYSIS')
    url = 'https://api.kraken.com'
    tradeableAssets = []
    resp = requests.get(url + '/0/public/Assets').json()
    if not resp['error']:
        assets = resp['result']
    else:
        print(resp)
    for i in assets.keys():
        tradeableAssets.append(i)
    bubbleCounter = 0
    
    def __init__(self, *kwargs):
        
        self.userObj = userData(type(self).api_key,type(self).api_sec)
        self.viewer = [] #becomes a list of Bubble class objs
        self.threads = [] #becomes a list of threads of while loops
        panel = turtle.Screen()
        self.h = 500
        self.w = 500
        panel.setup(self.w,self.h)
        panel.title("KATI v1.0")
        #create both buttons
        button = turtle.Turtle('square')
        balanceButton = turtle.Turtle('square')
        button.shapesize(stretch_wid=2)
        balanceButton.shapesize(stretch_wid=2)
        button.up()
        balanceButton.up()
        balanceButton.speed(0)
        button.speed(0)
        balanceButton.ht()
        button.ht()
        balanceButton.goto(-self.w/2+50, -self.h/2+50)
        button.goto(self.w/2 -50,-self.h/2+50)
        button.st()
        balanceButton.st()
        balanceButton.onclick(self.printBalance)
        button.onclick(self.addBubble)
        self.running = True
    def startup(self):
        
        ready = False
        
        while not ready:
            p = input("Type '?' for a list of assets\nXs only\nEnter asset to trade:")
            if p.upper() in type(self).tradeableAssets:
                assetPair = f"{p.upper()}"+'ZUSD'
                if p.upper()[0] == 'X':
                    if p.upper() == 'XBT':
                        global asset
                        asset = 'BTC'
                    elif p.upper() == 'XETH':
                        
                        asset = 'ETH'
                    else:
                        asset = p.upper()[1:4]
                
                type(self).tradeableAssets.remove(p.upper())
                data = APIData(assetPair, 14)
                tradeDollars = int(input('How much would you like to trade? (USD)'))
                ready = True
                return assetPair, data, tradeDollars
            elif p == '?':
                print(type(self).tradeableAssets)
            else:
                ready = False
        
    def addBubble(self, x,y):
        #creates a new instance of Trader class with on-screen UI element
         type(self).bubbleCounter += 1
         userInput = self.startup()
         assetPair = userInput[0]
         dataObj = userInput[1]
         tradeDollars = userInput[2]
         self.viewer.append(Trader(self.userObj,type(self).ta_key,dataObj, tradeDollars))
         self.viewer[type(self).bubbleCounter-1].x = -self.w/2+75*(type(self).bubbleCounter)
         if type(self).bubbleCounter > 5:
             self.viewer[type(self).bubbleCounter].y = 0
         else:
             self.viewer[type(self).bubbleCounter-1].y = 200
         self.viewer[type(self).bubbleCounter-1].draw()
         self.threads.append(threading.Thread(target=self.viewer[type(self).bubbleCounter-1].updateLoop))
         self.threads[type(self).bubbleCounter-1].start()
         self.running = True
    def printBalance(self,x,y):
        #prints balance to command line
         self.userObj.updateBalance()
         print(self.userObj.balance)
#============================= Debug Code =============================
if __name__ == '__main__':
    instance = KATI()
    turtle.done()
    

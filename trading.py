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


 #multithreading for multiple loops
import analysis as ta
import time
from userData import *
from tkinter import *
from tkinter import ttk

##====================================Visuals================================================
class Bubble(Canvas):
    #Super class for Trader with turtle funcs
    h=100
    w=100
    def __init__(self, dataObj,master=None):
        super().__init__(master)
        self['height']=type(self).h
        self['width']=type(self).w
        self.data = dataObj
        self.colorVar = (0,0,0)
        
    def draw(self):
        self.circle = self.create_oval(10,10,90,90,fill='white')
        self.create_text(50,50,text=f'{self.dataObj.asset}')
        self.create_text(60,60,text=f"{self.data.price['Last trade']}")
#================================Data Application=================================================        
class Trader(Bubble):
    #all methods in this class require a TA key
    #class to handle buy/sell automatically based on TA API
    
    def __init__(self,user,data, tradeDollars,row,column,master=None):
        #*args for many dataObjs
        self.tradeDollars = tradeDollars
        self.running = True
        self.userObj = user
        self.dataObj = data
        self.analysis = ta.Analysis(self.dataObj.assetPair,self.dataObj.period['days'],50)
        
        super().__init__(self.dataObj,master)
        self.grid(row=row,column=column)

        self.lastBuy = float(self.dataObj.price['Last trade'])
        self.lastSell = float(self.dataObj.price['Last trade'])
    def updateLoop(self,timer=1):
        #timer is time in minutes to wait between API calls
        #THIS IS A LOOP
        while self.running:  
            self.analysis.updateRec()
            self.buySell()
            
            time.sleep(60*timer) #timer to prevent going over API call limit
    def buySell(self):
        self.dataObj.getTicker()
        currentPrice = float(self.dataObj.price['Last trade'])
        self.userObj.getOpenOrders()
        volumeData = self.tradeDollars/currentPrice
        
        if not self.userObj.balance:
            print('No money!!')
            self.running = False
        if not self.userObj.openOrders.get('open'):
            print('No open orders')
            orderable = True
        else:
            print('Open orders, waiting to trade')
            orderable = False
        sell = (self.analysis.recommendation == 'sell' and currentPrice > self.lastBuy and orderable == True)
        buy = (self.analysis.recommendation == 'buy' and currentPrice < self.lastSell and orderable == True)
        if buy:
            resp = self.userObj.addOrder('buy',currentPrice, volumeData,'limit',300,self.dataObj.assetPair)
            self.itemconfigure(self.circle,fill = 'green')
            if not resp['error']:
                type(self).lastBuy = currentPrice
                print(f"Buy order added@{currentPrice} TX id: {resp['result'].get('txid')}")
            else:
                print(resp)
        
        elif sell:
            resp = self.userObj.addOrder('sell',currentPrice, volumeData,'limit',300,self.dataObj.assetPair,)
            self.itemconfigure(self.circle,fill='red')
            if not resp['error']:
                print(f"Sell order added@{currentPrice}! TX id: {resp['result'].get('txid')}")
            else:
                print(resp)
    def stopLoop(self,x,y):
        self.running = False
              

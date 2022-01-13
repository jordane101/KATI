#!/usr/local/bin/python

import threading
import os
from dotenv import load_dotenv
import requests
from userData import userData
import analysis as ta
from trading import Trader
from tkinter import *
from tkinter import ttk

class KATI(ttk.Frame):
    #class to manage program instance
    load_dotenv('keys.env')
    api_key = os.environ.get('API_KEY_KRAKEN')
    api_sec = os.environ.get('API_SEC_KRAKEN')
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
    
    def __init__(self,master=None, *kwargs):
        w = 600
        h = 600
        super().__init__(master,width=w,height=h)
        self.userObj = userData(type(self).api_key,type(self).api_sec)
        self.viewer = [] #becomes a list of Bubble class objs
        self.threads = [] #becomes a list of threads of while loops
        self.grid()
        
        
        self.createWidgets()
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
                        asset = p.upper()[:-4]
                
                type(self).tradeableAssets.remove(p.upper())
                data = ta.APIData(assetPair, 14)
                tradeDollars = int(input('How much would you like to trade? (USD)'))
                ready = True
                return assetPair, data, tradeDollars
            elif p == '?':
                print(type(self).tradeableAssets)
            else:
                ready = False
        
    def addBubble(self):
        #creates a new instance of Trader class with on-screen UI element
         type(self).bubbleCounter += 1
         if 0< type(self).bubbleCounter <=4:
             r = 0
             c = type(self).bubbleCounter
         elif 4 < type(self).bubbleCounter <=8:
             r = 1
             c = type(self).bubbleCounter - 4
         elif 8 < type(self).bubbleCounter <=12:
             r = 2
             c = type(self).bubbleCounter - 8
         elif 12 < type(self).bubbleCounter <=16:
             r = 3
             c = type(self).bubbleCounter - 12
         userInput = self.startup()
         assetPair = userInput[0]
         dataObj = userInput[1]
         tradeDollars = userInput[2]
         self.viewer.append(Trader(self.userObj,dataObj, tradeDollars,r,c,self))
         self.viewer[type(self).bubbleCounter-1].draw()
         self.threads.append(threading.Thread(target=self.viewer[type(self).bubbleCounter-1].updateLoop))
         self.threads[type(self).bubbleCounter-1].start()
         self.running = True
    def printBalance(self):
        #prints balance to command line
         self.userObj.updateBalance()
         print(self.userObj.balance)
    def createWidgets(self):
        self.addButton = ttk.Button(self,text='Add',command=self.addBubble)
        self.balanceButton = ttk.Button(self,text='Balance',command=self.printBalance)
        
        self.addButton.grid(column=3,row=6)
        self.balanceButton.grid(row=6)
        
        
if __name__ == '__main__':
    root = Tk()
    KATI(root).grid()
    root.mainloop()

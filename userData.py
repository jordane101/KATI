import urllib.parse, hashlib
import hmac
import os, time
import base64
import requests

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

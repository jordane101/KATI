import requests
import os
import time
import urllib.parse
import hashlib
import hmac
import base64
from dotenv import load_dotenv


load_dotenv('keys.env')
api_url = "https://api.kraken.com"
api_key = os.environ.get('API_KEY_KRAKEN')
api_sec = os.environ.get('API_SEC_KRAKEN')
analysis_key = os.environ.get('API_KEY_ANALYSIS')



def assetInfo(asset):
    # a function to call the API for the asset name information
    url = api_url + "/0/public/Assets"
    response = requests.get(url).json()
    if not response['error']:
        #check for valid response from API request
        output = response['result'].get(f'{asset.upper()}')
        if output:
            return output
        else:
            for i in response['result']: 
                print(i)
    

def tickerInfo(assetPair='XBTUSD',info='p'):
    url = f"https://api.kraken.com/0/public/Ticker?pair={assetPair}"
    response = requests.get(url).json()
    if not response['error']:
        output = [response['result'].get('XXBTZUSD').get(f'{info}')]
        return output
    else:
        print('Error')
    

def ohlcData(assetPair='XBTUSD'):
    # function to find the OHLC data for the past 24 hrs
    #86400 seconds in 1 day for unixtime
    since = time.time()-86400
    url = f'https://api.kraken.com/0/public/OHLC?pair={assetPair}&interval=1440&since={since}'
    response = requests.get(url).json()
    if not response['error']:
        output = response['result'].get('XXBTZUSD')
        print(time.time())
        return output
    else:
        print("Error")

def get_kraken_signature(urlpath, data, secret):

    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

# Attaches auth headers and returns results of a POST request
def kraken_request(uri_path, data, api_key, api_sec):
    headers = {}
    headers['API-Key'] = api_key
    # get_kraken_signature() as defined in the 'Authentication' section
    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)             
    req = requests.post((api_url + uri_path), headers=headers, data=data)
    return req


def checkBalance(var):
    # function to print the current balance of the account
    balance_uri = '/0/private/Balance'
    trade_uri = '/0/private/TradeBalance'
    if var.lower() == 'asset':
        response = kraken_request(balance_uri, {"nonce": str(int(1000*time.time()))}, api_key, api_sec).json()
        if not response['error']:
            account_response = response['result']
    elif var.lower() == 'trade':
        response = kraken_request(trade_uri, {"nonce": str(int(1000*time.time()))}, api_key, api_sec).json()
        if not response['error']:
            account_response = response['result']
    return account_response

def addOrder(buySell, price, volume, orderType, assetPair='BTCUSD'):
    # function to create order data for the specified asset
    data = {
        "nonce": str(int(1000*time.time())),
        "ordertype": orderType,
        "type": buySell,
        "volume": volume,
        "pair": assetPair,
        "price": price
        }
    response = kraken_request('/0/private/AddOrder', data, api_key, api_sec).json()
    return response
    
def query_analysis(asset):
    analysis_url = f'https://technical-analysis-api.com/api/v1/analysis/{asset.upper()}?apiKey={analysis_key}'
    response = requests.get(analysis_url).json()
    return time.time(), response
def cancelAll():
    resp = kraken_request('/0/private/CancelAll', {"nonce": str(int(1000*time.time()))}, api_key, api_sec).json()
    return resp



    

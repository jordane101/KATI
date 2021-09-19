# KATI
The Kraken Automated Trading Interface (KATI) is a python script I have developed to use analysis from the Technical Analysis API and the Kraken Trading API to automatically determine buying and selling of cryptocurrency.

You can find the Technical Analysis API at this link: https://technical-analysis-api.com/
And the Kraken exchange is at: kraken.com

I have intentions of making this program possible to distribute but that is far down the line. Currently I am just testing the viability of this concept and the flexibility of the script is low priority. I am making this code public so that anyone can stumble across it and possibly give me some tips. 

After downloading the files, you will need to create a .env file called 'keys.env' as well as have a Kraken API key and a Technical Analysis key. These are referenced in krakenLibrary as 'API_KEY_KRAKEN', 'API_SEC_KRAKEN', and 'API_KEY_ANALYSIS' in the keys.env file. 

Also, I recommend using a virtual environment to install the modules required for this application. They can all be installed using pip

Required installed modules:
krakenex
dotenv

Future Plans (in order of importance):
automatic installation of python virtual environment
library documentation (sorry it's a mess at the moment)
multiple coins for analysis/trading
deeper analysis using sentiment in the Technical Analysis API


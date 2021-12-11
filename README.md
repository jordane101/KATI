# KATI
The Kraken Automated Trading Interface (KATI) is a python program I have developed to use analysis from the Technical Analysis API and the Kraken Trading API to automatically determine buying and selling of cryptocurrency.

And the Kraken exchange is at: kraken.com

Currently I am just testing the viability of this concept. I am making this code public so that anyone can stumble across it and possibly give me some tips.

This is a rough start of what the GUI might possibly look like in the future. Currently the analysis is being done fully from an API. The main concept behind this project is the automatic trading. 

Currently, only Bitcoin and Ethereum are fully working with this version. Full support for others is coming soon.

REQUIREMENTS:
a kraken account and api key/ secret key pair
a keys.env file in the same folder as KATI.py with the api keys labeled as 'API_KEY_KRAKEN' and 'API_SEC_KRAKEN' respectively.
finally, you will need an API key for the Technical Analysis API which can be found at https://technical-analysis-api.com/
store the TA key in the same keys.env file with the name 'API_TECHNICAL_ANALYSIS'

Happy Trading!!

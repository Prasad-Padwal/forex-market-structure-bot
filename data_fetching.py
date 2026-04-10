# Data fetching implementation

import requests

class DataFetcher:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_data(self, symbol, interval):
        url = f'https://api.forex.com/data/{symbol}?interval={interval}&apikey={self.api_key}'
        response = requests.get(url)
        return response.json()
import pandas as pd
import requests
import time
import re

class NepseFetcher:
    def __init__(self):
        self.base_url = "https://www.nepalstock.com.np"
        # Official NOTS API endpoint
        self.api_url = f"{self.base_url}/api/nots/nepse-data/today-price?size=500"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': f"{self.base_url}/",
            'Accept-Language': 'en-US,en;q=0.9',
        }

    def get_live_data(self):
        session = requests.Session()
        try:
            # First hit to get cookies
            session.get(self.base_url, headers=self.headers, timeout=10)
            time.sleep(1)
            
            # Actual API request
            response = session.get(self.api_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            raw_data = response.json().get('content', [])
            if not raw_data:
                return pd.DataFrame()

            df = pd.DataFrame(raw_data)
            
            # Map and Hard-Clean
            mapping = {
                'symbol': 'symbol', 'lastTradedPrice': 'ltp',
                'openPrice': 'open', 'highPrice': 'high', 'lowPrice': 'low',
                'totalQty':
            

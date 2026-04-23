import pandas as pd
import requests
import time

class NepseFetcher:
    def __init__(self):
        self.base_url = "https://www.nepalstock.com.np"
        self.api_url = f"{self.base_url}/api/nots/nepse-data/today-price?size=500"
        self.session = requests.Session()
        # Headers are mandatory to avoid being flagged as a bot
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': f"{self.base_url}/",
            'Connection': 'keep-alive'
        }

    def get_live_data(self):
        try:
            # Step 1: Visit the home page to establish a "Human" session and get cookies
            self.session.get(self.base_url, headers=self.headers, timeout=10)
            time.sleep(1) # Small delay to mimic human behavior

            # Step 2: Fetch the actual JSON data
            response = self.session.get(self.api_url, headers=self.headers, timeout=20)
            
            if response.status_code != 200:
                return self._fallback_logic()

            data = response.json().get('content', [])
            if not data:
                return self._fallback_logic()

            df = pd.DataFrame(data)

            # Mapping official API keys to our analysis variables
            # NEPSE API keys often use camelCase
            mapping = {
                'symbol': 'symbol',
                'lastTradedPrice': 'ltp',
                'openPrice': 'open',
                'totalQty': 'volume',
                'totalTurnover': 'turnover'
            }
            df = df.rename(columns=mapping)
            
            # Convert to numeric and clean
            for col in ['ltp', 'open', 'volume', 'turnover']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            return df[['symbol', 'ltp', 'open', 'volume', 'turnover']]

        except Exception as e:
            st.error(f"API Connection Failed: {e}")
            return self._fallback_logic()

    def _fallback_logic(self):
        """Scrapes a public mirror if official API is blocked"""
        try:
            # Mirror sites are often easier to scrape when official ones are down
            url = "https://nepsealpha.com/live-nepse"
            df = pd.read_html(url)[0]
            df.columns = [str(c).upper() for c in df.columns]
            df = df.rename(columns={'SYMBOL': 'symbol', 'LTP': 'ltp', 'VOLUME': 'volume', 'OPEN': 'open'})
            return df
        except:
            return pd.DataFrame()
            

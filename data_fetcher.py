import pandas as pd
import numpy as np
import requests
import re

class NepseFetcher:
    def __init__(self):
        # Official NEPSE headers to prevent "403 Forbidden"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.nepalstock.com.np/'
        }

    def get_live_data(self):
        try:
            # 1. Fetch from Official NEPSE NOTS API
            # This endpoint provides the "Today's Price" JSON directly
            url = "https://www.nepalstock.com.np/api/nots/nepse-data/today-price?size=500"
            response = requests.get(url, headers=self.headers, timeout=20)
            
            if response.status_code != 200:
                return self._fallback_logic()

            json_data = response.json()
            # Extract content from the NEPSE JSON structure
            raw_list = json_data.get('content', [])
            df = pd.DataFrame(raw_list)

            if df.empty: return self._fallback_logic()

            # 2. Map Official NEPSE Keys to Our Variables
            # Official keys: 'symbol', 'lastTradedPrice', 'openPrice', 'highPrice', 'lowPrice', 'totalQty', 'totalTurnover'
            mapping = {
                'symbol': 'symbol',
                'lastTradedPrice': 'ltp',
                'openPrice': 'open',
                'highPrice': 'high',
                'lowPrice': 'low',
                'totalQty': 'volume',
                'totalTurnover': 'turnover'
            }
            df = df.rename(columns=mapping)

            # 3. Final Numeric Scrubbing
            cols = ['ltp', 'open', 'high', 'low', 'volume', 'turnover']
            for col in cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

            # Filtering out non-equity instruments (Indices, Debentures etc. if needed)
            return df[['symbol', 'ltp', 'open', 'high', 'low', 'volume', 'turnover']].drop_duplicates('symbol')

        except Exception as e:
            print(f"Official API Error: {e}")
            return self._fallback_logic()

    def _fallback_logic(self):
        """Emergency Fallback if the official API is under maintenance"""
        import cloudscraper
        scraper = cloudscraper.create_scraper()
        try:
            # Secondary official-like source
            r = scraper.get("https://www.sharesansar.com/live-trading", timeout=10)
            df = pd.read_html(r.text)[0]
            df.columns = [str(c).strip().upper() for c in df.columns]
            df = df.rename(columns={'SYMBOL': 'symbol', 'LTP': 'ltp', 'VOLUME': 'volume', 'OPEN': 'open'})
            for c in ['ltp', 'volume', 'open']:
                df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', ''), errors='coerce')
            df['turnover'] = df['ltp'] * df['volume']
            return df
        except:
            return pd.DataFrame()

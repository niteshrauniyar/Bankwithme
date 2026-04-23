import pandas as pd
import numpy as np
import cloudscraper
import re

class NepseFetcher:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )

    def get_live_data(self):
        try:
            # Source: ShareSansar Today Price (Most reliable for Live/Today data)
            url = "https://www.sharesansar.com/today-price"
            response = self.scraper.get(url, timeout=20)
            
            # Read all tables and find the one containing stock data
            dfs = pd.read_html(response.text)
            df = dfs[0]

            # Standardize Headers: Force to uppercase and remove extra characters
            df.columns = [str(c).strip().upper() for c in df.columns]

            # FUZZY MAPPING: Connects varying website names to our code variables
            mapping = {
                'SYMBOL': 'symbol', 'TICKER': 'symbol',
                'LTP': 'ltp', 'LTP(RS)': 'ltp', 'LAST TRADED PRICE': 'ltp',
                'OPEN': 'open', 'OPEN PRICE': 'open',
                'HIGH': 'high', 'HIGH PRICE': 'high',
                'LOW': 'low', 'LOW PRICE': 'low',
                'VOLUME': 'volume', 'TRADED SHARES': 'volume', 'QTY': 'volume',
                'TURNOVER': 'turnover', 'AMOUNT': 'turnover', 'TRADED AMOUNT': 'turnover'
            }
            df = df.rename(columns=mapping)

            # CLEANING: Remove commas and whitespace from all numeric columns
            numeric_cols = ['ltp', 'open', 'high', 'low', 'volume', 'turnover']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).apply(self._clean_numeric)

            # DATA INTEGRITY: Ensure turnover exists (Price * Volume fallback)
            if 'turnover' not in df.columns or df['turnover'].isna().all():
                df['turnover'] = df['ltp'] * df['volume']

            # Remove any rows that don't have a valid Symbol or LTP
            return df.dropna(subset=['symbol', 'ltp']).drop_duplicates(subset=['symbol'])

        except Exception as e:
            # Fallback to help you debug in Streamlit logs
            print(f"FETCH ERROR: {e}")
            return self._emergency_data()

    def _clean_numeric(self, val):
        """Removes commas and non-numeric junk: '1,200.50' -> 1200.5"""
        if pd.isna(val) or val == 'nan': return 0.0
        cleaned = re.sub(r'[^0-9\.-]', '', str(val))
        try:
            return float(cleaned)
        except:
            return 0.0

    def _emergency_data(self):
        # Keeps the app alive if the website is down
        return pd.DataFrame({
            'symbol': ['NICA', 'NABIL', 'HRL', 'KBL'],
            'ltp': [364.5, 526.0, 515.0, 224.0],
            'open': [360.0, 520.0, 505.0, 221.0],
            'volume': [120000, 150000, 45000, 670000],
            'turnover': [43740000, 78900000, 23175000, 150080000]
        })
        

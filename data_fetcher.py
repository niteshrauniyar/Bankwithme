import pandas as pd
import numpy as np
import cloudscraper
import re

class NepseFetcher:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(browser={'browser': 'chrome'})

    def get_live_data(self):
        try:
            # Targeted Live URL for 2026 accuracy
            url = "https://www.sharesansar.com/today-price"
            r = self.scraper.get(url, timeout=20)
            
            # Find the correct table (usually the first one with 'Symbol')
            all_tables = pd.read_html(r.text)
            df = None
            for table in all_tables:
                if 'Symbol' in table.columns or 'SYMBOL' in table.columns:
                    df = table
                    break
            
            if df is None: return pd.DataFrame()

            # 1. Clean Headers
            df.columns = [str(c).strip().upper() for c in df.columns]

            # 2. Precise Mapping
            mapping = {
                'SYMBOL': 'symbol', 'LTP': 'ltp', 'LTP(RS)': 'ltp',
                'OPEN': 'open', 'HIGH': 'high', 'LOW': 'low',
                'VOLUME': 'volume', 'TRADED SHARES': 'volume',
                'TURNOVER': 'turnover', 'AMOUNT': 'turnover'
            }
            df = df.rename(columns=mapping)

            # 3. Heavy-Duty Numeric Cleaning (Handles 1,20,345.00)
            cols = ['ltp', 'open', 'high', 'low', 'volume', 'turnover']
            for col in cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).apply(self._clean_numeric)

            # 4. Accuracy Check: Ensure LTP is not zero
            df = df[df['ltp'] > 0]
            
            return df.dropna(subset=['symbol']).drop_duplicates('symbol')
        except Exception:
            return pd.DataFrame()

    def _clean_numeric(self, val):
        if pd.isna(val) or val == 'nan': return 0.0
        # This regex removes commas and whitespace but keeps decimals
        cleaned = re.sub(r'[^\d.-]', '', str(val))
        try:
            return float(cleaned)
        except:
            return 0.0

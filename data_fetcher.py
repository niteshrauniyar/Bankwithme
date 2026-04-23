import pandas as pd
import numpy as np
import cloudscraper
from bs4 import BeautifulSoup
import json
import re

class NepseFetcher:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )

    def get_live_data(self):
        try:
            # Target the Live Market page (highest accuracy)
            url = "https://nepsealpha.com/trading-menu/top-stocks"
            r = self.scraper.get("https://nepsealpha.com/live-nepse", timeout=20)
            
            # Using BeautifulSoup to find the hidden JSON data in the script tags
            # or scraping the direct live table which is more up-to-date
            dfs = pd.read_html(r.text)
            df = dfs[0] # The Live Trading Table

            # 1. Precise Header Alignment
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            mapping = {
                'SYMBOL': 'symbol', 'LTP': 'ltp', 'VALUE': 'ltp',
                'OPEN': 'open', 'HIGH': 'high', 'LOW': 'low',
                'VOL': 'volume', 'VOLUME': 'volume', 'QTY': 'volume',
                'TURNOVER': 'turnover', 'TOTAL TURNOVER': 'turnover',
                'CHANGE': 'change_raw', '% CHANGE': 'change_pct'
            }
            df = df.rename(columns=mapping)

            # 2. Strict Numeric Sanitization
            numeric_cols = ['ltp', 'open', 'high', 'low', 'volume', 'turnover']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).apply(self._clean_string)

            # 3. Data Integrity Check
            # Remove symbols that aren't actually trading (0 volume or 0 price)
            df = df[(df['ltp'] > 0) & (df['volume'] > 0)]
            
            # Recalculate Turnover if it looks like a formatting error (common in Nepal data)
            # Some sites list turnover in '000s or Lakhs. We normalize to absolute NPR.
            df['turnover'] = df['ltp'] * df['volume']

            return df.dropna(subset=['symbol']).drop
            

import pandas as pd
import numpy as np
import cloudscraper
import re

class NepseFetcher:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(browser={'browser': 'chrome'})

    def get_live_data(self):
        try:
            # Sector-wise page is more comprehensive in 2026
            url = "https://www.sharesansar.com/sectorwise-share-price"
            r = self.scraper.get(url, timeout=25)
            all_tables = pd.read_html(r.text)
            
            # Combine all sector tables into one master dataframe
            master_list = []
            for df in all_tables:
                # Standardize headers for each individual table
                df.columns = [str(c).strip().upper() for c in df.columns]
                
                # Check if it's a price table (must have Symbol/LTP)
                if 'SYMBOL' in df.columns:
                    master_list.append(df)
            
            if not master_list:
                return self._emergency_fallback()

            full_df = pd.concat(master_list, ignore_index=True)

            # --- Precise 2026 Mapping ---
            mapping = {
                'SYMBOL': 'symbol', 'LTP': 'ltp', 'LTP(RS)': 'ltp', 
                'OPEN': 'open', 'HIGH': 'high', 'LOW': 'low',
                'VOLUME': 'volume', 'TRADED SHARES': 'volume',
                'TURNOVER': 'turnover', 'AMOUNT': 'turnover',
                'PREV. CLOSING': 'prev_close', '% CHANGE': 'change_pct'
            }
            full_df = full_df.rename(columns=mapping)

            # --- Advanced Numeric Cleaning ---
            # Handles '1,23,456.00', '(10.5)', and other messy formats
            cols_to_fix = ['ltp', 'open', 'high', 'low', 'volume', 'turnover', 'prev_close']
            for col in cols_to_fix:
                if col in full_df.columns:
                    full_df[col] = full_df[col].astype(str).apply(self._clean_numeric_string)

            # Derive turnover if the site has it empty
            full_df['turnover'] = full_df['turnover'].fillna(full_df['ltp'] * full_df['volume'])
            
            # Remove header rows that might have been repeated in the merge
            full_df = full_df[full_df['symbol'] != 'SYMBOL']
            
            return full
            

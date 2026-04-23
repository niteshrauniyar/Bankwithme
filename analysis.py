import pandas as pd
import numpy as np

class InstitutionalEngine:
    @staticmethod
    def apply_metrics(df):
        if df.empty: return df
        df = df.copy()

        # 1. Volatility Calculation
        df['change_pct'] = ((df['ltp'] - df['open']) / df['open'] * 100).fillna(0)
        
        # 2. Amihud Measure (Price Impact)
        # Measures how much volume it takes to move the price 1%
        df['amihud'] = (abs(df['change_pct']) / (df['turnover'] / 1_000_000 + 1e-9))
        
        # 3. Smart Money Detection
        # High Turnover + High Volume relative to market median
        m_turnover = df['turnover'].median()
        m_volume = df['volume'].median()
        
        df['is_institutional'] = (df['turnover'] > m_turnover * 2) & (df['volume'] > m_volume * 1.5)
        
        return df
        

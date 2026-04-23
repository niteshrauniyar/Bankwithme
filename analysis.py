import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

class InstitutionalEngine:
    @staticmethod
    def apply_metrics(df):
        if df.empty: return df
        df = df.copy()

        # 1. Volatility & Returns
        df['returns'] = (abs(df['ltp'] - df['open']) / df['open']).fillna(0)
        
        # 2. Amihud Illiquidity Measure (Price move per 1 Million NPR)
        # Higher = Illiquid/Retail | Lower = Deep Liquidity/Institutional
        df['amihud'] = df['returns'] / ((df['turnover'] / 1_000_000) + 1e-9)
        
        # 3. Relative Volume (Current stock vs Market median)
        df['rvol'] = df['volume'] / (df['volume'].median() + 1e-9)

        # 4. Institutional Clustering (ML)
        try:
            features = df[['volume', 'turnover', 'amihud']].fillna(0)
            # Normalize for KMeans
            features_norm = (features - features.mean()) / (features.std() + 1e-9)
            
            kmeans = KMeans(n_clusters=min(len(df), 3), n_init=10, random_state=42)
            df['cluster'] = kmeans.fit_predict(features_norm)
            
            # Label the high-turnover cluster as 'Smart Money'
            inst_id = df.groupby('cluster')['turnover'].median().idxmax()
            df['is_institutional'] = df['cluster'] == inst_id
        except:
            df['is_institutional'] = False

        return df
        

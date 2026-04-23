import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

class InstitutionalEngine:
    @staticmethod
    def apply_metrics(df):
        if df.empty: return df
        df = df.copy()

        # 1. Kyle's Lambda (Price Impact Proxy)
        # Research: Large trades have concave impact. 
        # Higher Lambda = Informed traders are active / adverse selection risk.
        df['returns'] = (abs(df['ltp'] - df['open']) / df['open']).fillna(0)
        df['kyle_lambda'] = df['returns'] / (np.sqrt(df['volume']) + 1e-9)

        # 2. Amihud Measure (Low-frequency liquidity)
        df['amihud'] = df['returns'] / ((df['turnover'] / 1_000_000) + 1e-9)
        
        # 3. Node Influence (Simplified Centrality)
        # Based on turnover contribution to total market
        total_market_turnover = df['turnover'].sum()
        df['market_centrality'] = (df['turnover'] / total_market_turnover) * 100

        # 4. Clustering (Spectral Cluster Proxy using KMeans)
        try:
            X = df[['volume', 'turnover', 'kyle_lambda']].fillna(0)
            X_norm = (X - X.mean()) / (X.std() + 1e-9)
            kmeans = KMeans(n_clusters=min(len(df), 3), n_init=10)
            df['cluster'] = kmeans.fit_predict(X_norm)
            
            # The cluster with the highest 'Node Strength' (Turnover + Volume)
            inst_id = df.groupby('cluster')['turnover'].median().idxmax()
            df['is_institutional'] = df['cluster'] == inst_id
        except:
            df['is_institutional'] = False

        return df
        

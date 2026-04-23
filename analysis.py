import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

class InstitutionalEngine:
    @staticmethod
    def apply_metrics(df):
        if df.empty: return df
        df = df.copy()

        # --- 3.2 Liquidity & Market Impact (Amihud & Kyle's Lambda Proxy) ---
        # Returns / Turnover = Price impact per rupee traded.
        df['returns'] = (abs(df['ltp'] - df['open']) / df['open']).fillna(0)
        df['amihud'] = df['returns'] / ((df['turnover'] / 1_000_000) + 1e-9)
        
        # Kyle's Lambda Proxy: Impact of volume on price volatility
        df['kyle_lambda'] = df['returns'] / (np.sqrt(df['volume']) + 1e-9)

        # --- 3.1 Order Flow & Trade Size (Relative Strength) ---
        # We look for 'Long Memory' signatures by comparing current volume to market median
        df['v_strength'] = df['volume'] / (df['volume'].median() + 1e-9)

        # --- 3.4 Clustering & ML Methods ---
        try:
            # Using Volume, Turnover, and Kyle's Lambda to find Big Players
            features = df[['volume', 'turnover', 'kyle_lambda']].fillna(0)
            # Normalize for ML
            features_norm = (features - features.mean()) / (features.std() + 1e-9)
            
            # K-Means to find the 'Institutional Cluster'
            kmeans = KMeans(n_clusters=min(len(df), 3), n_init=10, random_state=42)
            df['cluster'] = kmeans.fit_predict(features_norm)
            
            # Identify which cluster has the highest turnover (Big Players)
            inst_cluster = df.groupby('cluster')['turnover'].median().idxmax()
            df['is_institutional'] = df['cluster'] == inst_cluster
        except:
            df['is_institutional'] = False

        return df
        

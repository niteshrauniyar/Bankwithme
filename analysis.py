import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

class InstitutionalEngine:
    @staticmethod
    def apply_metrics(df):
        if df.empty: return df
        df = df.copy()

        # Calculation of Price Impact (Amihud)
        df['returns'] = (abs(df['ltp'] - df['open']) / df['open']).fillna(0)
        df['amihud'] = df['returns'] / ((df['turnover'] / 1_000_000) + 1e-9)
        
        # 3.1 & 3.2 Order Flow Signature (Relative Volume)
        df['rvol'] = df['volume'] / (df['volume'].median() + 1e-9)

        # 3.4 Clustering to find "The Big Player Cluster"
        try:
            X = df[['volume', 'turnover', 'amihud']].fillna(0)
            X_norm = (X - X.mean()) / (X.std() + 1e-9)
            kmeans = KMeans(n_clusters=min(len(df), 3), n_init=10, random_state=42)
            df['cluster'] = kmeans.fit_predict(X_norm)
            
            # The cluster with the massive turnover is our 'Institutional' target
            inst_id = df.groupby('cluster')['turnover'].median().idxmax()
            df['is_institutional'] = df['cluster'] == inst_id
        except:
            df['is_institutional'] = False

        return df
        

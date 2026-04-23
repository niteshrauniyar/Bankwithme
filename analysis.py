import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

class InstitutionalEngine:
    @staticmethod
    def apply_metrics(df):
        if df.empty: return df

        # 1. Volatility Calculation
        df['returns'] = (abs(df['ltp'] - df['open']) / df['open']).fillna(0)
        
        # 2. Amihud Illiquidity Ratio
        # Measures: How much does 1 Million NPR of volume move the price?
        # Institutional logic: They want to move large volume with LOW price impact.
        df['amihud'] = df['returns'] / ((df['turnover'] / 1_000_000) + 1e-9)
        
        # 3. Institutional Clustering (K-Means)
        try:
            # We use Volume and Turnover to find the "Big Fish"
            X = df[['volume', 'turnover']].fillna(0)
            # Normalize for better clustering
            X_norm = (X - X.mean()) / X.std()
            
            kmeans = KMeans(n_clusters=min(len(df), 3), n_init=10, random_state=42)
            df['cluster'] = kmeans.fit_predict(X_norm.fillna(0))
            
            # The cluster with the highest median turnover is flagged as Institutional
            inst_cluster_id = df.groupby('cluster')['turnover'].median().idxmax()
            df['is_institutional'] = df['cluster'] == inst_cluster_id
        except:
            df['is_institutional'] = False

        return df
      

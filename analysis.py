import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

class InstitutionalEngine:
    @staticmethod
    def apply_metrics(df):
        # 1. Amihud Illiquidity (Price Impact)
        # High value = Small volume moves price a lot (Retail Trap)
        # Low value = Large volume absorbed easily (Institutional Accumulation)
        df['returns'] = abs(df['ltp'] - df['open']) / df['open']
        df['amihud'] = df['returns'] / (df['turnover'] / 1_000_000)
        
        # 2. Institutional Presence (K-Means Clustering)
        # We cluster by (Volume, Turnover) to find the 'Outliers' (Institutions)
        if len(df) > 3:
            coords = df[['volume', 'turnover']].fillna(0)
            kmeans = KMeans(n_clusters=3, n_init=10).fit(coords)
            df['cluster'] = kmeans.labels_
            # The cluster with the highest avg volume is institutional
            inst_label = df.groupby('cluster')['volume'].mean().idxmax()
            df['is_institutional'] = df['cluster'] == inst_label
        else:
            df['is_institutional'] = False
            
        # 3. Relative Volume (RVOL)
        df['rvol'] = df['volume'] / df['volume'].median()
        return df
      

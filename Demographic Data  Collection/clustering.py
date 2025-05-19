# clustering.py
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def perform_clustering(city_scores_df):

    try:
        # Make a copy to avoid modifying original dataframe
        df = city_scores_df.copy()
        
        # Select numerical features
        numeric_data = df.select_dtypes(include=['number'])
        
        # Standardize the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_data)
        
        # Perform K-means clustering with optimal k=3
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(scaled_data)
        
        # Add cluster labels to dataframe
        df['Cluster'] = clusters
        
        print("Clustering completed successfully!")
        return df
        
    except Exception as e:
        print(f"Error occurred during clustering: {str(e)}")
        return city_scores_df
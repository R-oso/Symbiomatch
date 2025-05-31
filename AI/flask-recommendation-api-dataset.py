import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

class ContentBasedRecommender:
    def __init__(self, df):
        df.columns = df.columns.str.strip()
        
        self.df = df
        self.prepare_data()

    def prepare_data(self):
        # Preprocess text features for content-based filtering
        # Combine relevant text columns
        self.df['content_features'] = self.df.apply(
            lambda row: f"{row['Resource Name']} {row['Description']} {row['Keywords']} "
                        f"{row['Category 1']} {row['Category 2']} {row['Category 3']} "
                        f"{row['SIC Description']} {row['Supply Type']}", 
            axis=1
        )
        
        # Create TF-IDF vectorizer for content-based similarity
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.content_matrix = self.tfidf.fit_transform(self.df['content_features'])
        
        # Prepare numerical features for content-based filtering
        numerical_features = [
            'Total Quantity', 
            'Available Quantity', 
            'Latitude', 
            'Longitude'
        ]
        
        # Scale numerical features
        scaler = MinMaxScaler()
        self.numerical_features_scaled = scaler.fit_transform(
            self.df[numerical_features].fillna(0)
        )

    def content_based_recommendation(self, preferences, top_n):
        filtered_df = self.df.copy()
        # Filter by categories
        if preferences['PreferredCategories']:
            before = len(filtered_df)
            filtered_df = filtered_df[
                filtered_df['Category 1'].isin(preferences['PreferredCategories']) | 
                filtered_df['Category 2'].isin(preferences['PreferredCategories']) | 
                filtered_df['Category 3'].isin(preferences['PreferredCategories'])
            ]
            after = len(filtered_df)
            print(f"Category filter reduced rows from {before} to {after}")

        # Filter by keywords
        if preferences['PreferredKeywords']:
            before = len(filtered_df)
            filtered_df = filtered_df[
                filtered_df['Keywords'].str.contains('|'.join(preferences['PreferredKeywords']),
                                                    case=False, na=False)
            ]
            after = len(filtered_df)
            print(f"Keyword filter reduced rows from {before} to {after}")

        # Filter by supply type
        if preferences['PreferredSupplyType']:
            before = len(filtered_df)
            filtered_df = filtered_df[
                filtered_df['Supply Type'].isin(preferences['PreferredSupplyType'])
            ]
            after = len(filtered_df)
            print(f"Supply Type filter reduced rows from {before} to {after}")

        # Filter by unit of measure
        if preferences['PreferredUnitOfMeasures']:
            before = len(filtered_df)
            filtered_df = filtered_df[
                filtered_df['Unit of Measure'].isin(preferences['PreferredUnitOfMeasures'])
            ]
            after = len(filtered_df)
            print(f"Unit of Measure filter reduced rows from {before} to {after}")

        # Filter by dates
        before = len(filtered_df)
        filtered_df = filtered_df[
            (filtered_df['Valid From'] >= preferences['PreferredValidFrom']) & 
            (filtered_df['Valid To'] <= preferences['PreferredValidTo'])
        ]
        after = len(filtered_df)
        print(f"Date filter reduced rows from {before} to {after}")

        if filtered_df.empty:
            return []  # No rows remain after filtering

        # Instead of dropping the original index, keep it in a column named 'original_index'.
        filtered_df.reset_index(drop=False, inplace=True)
        filtered_df.rename(columns={'index': 'original_index'}, inplace=True)
        seed_row_original_index = filtered_df.loc[0, 'original_index']
        
        content_sim = cosine_similarity(
            self.content_matrix[seed_row_original_index],  # row from the entire dataset
            self.content_matrix
        )[0]

        numerical_sim = cosine_similarity(
            self.numerical_features_scaled[seed_row_original_index].reshape(1, -1), 
            self.numerical_features_scaled
        )[0]

        combined_sim = 0.7 * content_sim + 0.3 * numerical_sim

        # Sort all rows in descending order of similarity
        overall_ranking = np.argsort(combined_sim)[::-1]  # highest similarity first
        valid_orig_indices = set(filtered_df['original_index'].values)

        # Filter out the seed row itself and keep only the top_n from the valid subset
        recommendations = []
        for idx in overall_ranking:
            if idx == seed_row_original_index:
                continue  # skip the seed row itself
            if idx in valid_orig_indices:
                recommendations.append(idx)
            if len(recommendations) == top_n:
                break

        # If no recommendations found, return empty
        if not recommendations:
            return []
        recommended_rows = filtered_df[filtered_df['original_index'].isin(recommendations)] 
        return recommended_rows

df = pd.read_excel('RESOURCES_CLEANED.xlsx')
df.columns = df.columns.str.strip()

recommender = ContentBasedRecommender(df)

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    data = request.json
    print("Received data:", data) 
    date_format = "%Y-%m-%dT%H:%M:%S"  

    preferences = {
        'PreferredCategories': data.get('preferredCategories', None),  
        'PreferredKeywords': data.get('preferredKeywords', None),  
        'MaxSearchRadiusKm': data.get('maxSearchRadiusKm', None),  
        'PreferredSupplyType': data.get('preferredSupplyType', None),  
        'PreferredUnitOfMeasures': data.get('preferredUnitOfMeasures', None), 
        'PreferredValidFrom': datetime.strptime(data['preferredValidFrom'], date_format).isoformat() 
            if data.get('preferredValidFrom') else None,  
        'PreferredValidTo': datetime.strptime(data['preferredValidTo'], date_format).isoformat() 
            if data.get('preferredValidTo') else None  
    }

    print("Preferences:", preferences) 
    top_n = data.get('top_n')

    try:
        # Get recommendations by applying preferences and filtering based on them
        recommendations = recommender.content_based_recommendation(preferences, top_n=top_n)
        resource_names = [row['Resource Name'] for row in recommendations.to_dict('records')]

        
        return jsonify({
            'status': 'success',
            'recommendations': resource_names
        }), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

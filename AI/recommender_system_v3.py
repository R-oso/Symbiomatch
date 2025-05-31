import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import MinMaxScaler
from flask import Flask, request, jsonify
from datetime import datetime
import sqlalchemy
from sqlalchemy import create_engine, text
import os
import math
import ast
import logging
import traceback
from functools import lru_cache
import time
import threading
import re
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('recommendation_system.log')
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Database Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost') 
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'None58-DB')
DB_NAME = os.getenv('DB_NAME', 'SymbioDb')

class HybridRecommendationSystem:
    def __init__(self, engine):
        try:
            self.engine = engine
            self.keyword_weight = 0.3
            self.content_weight = 0.4
            self.collaborative_weight = 0.3
            
            self.df, self.feedback_df = self.fetch_data_from_db()
            self.prepare_data()
            logger.info("Recommendation system initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing recommendation system: {e}")
            raise

    def fetch_data_from_db(self):
        product_query = """
            SELECT 
                p.Id AS ProductId,
                p.Name AS ProductName,
                p.SupplyType AS SupplyType, 
                p.Categories AS Categories,  
                p.ValidFrom AS ValidFrom,
                p.ValidTo AS ValidTo,
                COALESCE(m.Name, '') AS MaterialName,
                COALESCE(m.Description, '') AS MaterialDescription,
                COALESCE(m.AvailableQuantity, 0) AS AvailableQuantity,
                COALESCE(m.UnitOfMeasure, '') AS UnitOfMeasure, 
                l.Longitude AS Longitude,
                l.Latitude AS Latitude
            FROM 
                Products p
            LEFT JOIN 
                Materials m ON m.ProductId = p.Id
            JOIN 
                Companies c ON c.Id = p.CompanyId
            JOIN 
                Locations l ON l.Id = c.LocationId
            WHERE 
                p.ValidTo >= CURRENT_DATE
        """

        feedback_query = """
            SELECT UserId, ProductId, IsLiked
            FROM UserFeedback
            WHERE IsLiked = 1
        """

        try:
            with self.engine.connect() as connection:
                product_result = connection.execute(text(product_query))
                feedback_result = connection.execute(text(feedback_query))
                
                df = pd.DataFrame(product_result.fetchall(), columns=product_result.keys())
                feedback_df = pd.DataFrame(feedback_result.fetchall(), columns=feedback_result.keys())

            return df, feedback_df

        except Exception as e:
            logger.error(f"Database fetch error: {e}")
            raise

    def preprocess_text(self, text):
        if isinstance(text, (pd.Series, np.ndarray)):
            return ' '.join(map(str, text))
        if pd.isna(text) or text is None:
            return ''
        if isinstance(text, (list, tuple)):
            text = ' '.join(map(str, text))
        text = str(text).lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)
        return ' '.join(text.split())

    def prepare_data(self):
        try:
            self.df['Categories'] = self.df['Categories'].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )
            
            numeric_cols = ['Latitude', 'Longitude', 'AvailableQuantity']
            for col in numeric_cols:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)

            def preprocess_text(text):
                if pd.isna(text) or text is None:
                    return ''
                if isinstance(text, (list, tuple)):
                    text = ' '.join(map(str, text))
                text = str(text).lower().strip()
                text = re.sub(r'[^\w\s]', ' ', text)
                text = ' '.join(text.split())
                return text

            self.df['processed_name'] = self.df['ProductName'].apply(preprocess_text)
            self.df['processed_material'] = self.df['MaterialName'].apply(preprocess_text)
            self.df['processed_description'] = self.df['MaterialDescription'].apply(preprocess_text)
            self.df['processed_categories'] = self.df['Categories'].apply(preprocess_text)
            self.df['processed_supply_type'] = self.df['SupplyType'].apply(preprocess_text)
            self.df['processed_unit'] = self.df['UnitOfMeasure'].apply(preprocess_text)

            self.df['content_features'] = (
                self.df['processed_name'] + ' ' + 
                self.df['processed_name'] + ' ' +  
                self.df['processed_material'] + ' ' +
                self.df['processed_description'] + ' ' +
                self.df['processed_categories'] + ' ' +
                self.df['processed_categories'] + ' ' +  
                self.df['processed_supply_type'] + ' ' +
                self.df['processed_unit']
            )

            self.tfidf = TfidfVectorizer(
                stop_words='english',
                max_df=0.95,
                min_df=2,
                ngram_range=(1, 2),
                max_features=5000,
                strip_accents='unicode',
                norm='l2'
            )

            if len(self.df) > 0:
                self.content_matrix = self.tfidf.fit_transform(self.df['content_features'])
                logger.info(f"TF-IDF matrix shape: {self.content_matrix.shape}")
            else:
                self.content_matrix = None
                logger.warning("No documents available for TF-IDF vectorization")

            self.scaler = MinMaxScaler()
            self.numerical_features_scaled = self.scaler.fit_transform(
                self.df[['AvailableQuantity', 'Latitude', 'Longitude']]
            )

        except Exception as e:
            logger.error(f"Data preparation error: {e}")
            raise

    def explain_similarity(self, query_text, product_text, score):
        try:
            query_vector = self.tfidf.transform([query_text])
            product_vector = self.tfidf.transform([product_text])
            
            feature_names = np.array(self.tfidf.get_feature_names_out())
            query_scores = query_vector.toarray()[0]
            product_scores = product_vector.toarray()[0]
            
            common_terms = []
            for term, q_score, p_score in zip(feature_names, query_scores, product_scores):
                if q_score > 0 and p_score > 0:
                    common_terms.append((term, q_score * p_score))
            
            common_terms.sort(key=lambda x: x[1], reverse=True)
            top_terms = common_terms[:5] if len(common_terms) > 5 else common_terms
            
            return {
                'overall_score': score,
                'matching_terms': [{'term': term, 'relevance': float(score)} for term, score in top_terms]
            }
        except Exception as e:
            logger.error(f"Error in explain_similarity: {e}")
            return {'overall_score': score, 'matching_terms': []}

    def get_content_based_recommendations(self, preferences, top_n, longitude, latitude):
        try:
            filtered_df = self.df.copy()
            
            if len(filtered_df) == 0:
                return []

            query_content = []
            
            if preferences.get('PreferredCategories'):
                categories = ' '.join(map(str, preferences['PreferredCategories']))
                query_content.extend([categories] * 3)
            
            if preferences.get('PreferredSupplyType'):
                supply_type = ' '.join(map(str, preferences['PreferredSupplyType']))
                query_content.append(supply_type)
            
            if preferences.get('PreferredUnitOfMeasures'):
                units = ' '.join(map(str, preferences['PreferredUnitOfMeasures']))
                query_content.append(units)
            
            if preferences.get('PreferredKeywords'):
                keywords = ' '.join(map(str, preferences['PreferredKeywords']))
                query_content.extend([keywords] * 3)
            
            query_text = ' '.join(query_content) if query_content else ''
            if not query_text:
                query_text = ' '.join(filtered_df['content_features'].iloc[0].split()[:5])
            
            query_vector = self.tfidf.transform([query_text])
            content_sim = cosine_similarity(
                query_vector, 
                self.tfidf.transform(filtered_df['content_features'])
            )[0]

            if longitude and latitude and preferences.get('MaxSearchRadiusKm'):
                max_radius = float(preferences['MaxSearchRadiusKm'])
                distances = np.array([
                    haversine(
                        float(latitude), float(longitude),
                        float(row['Latitude']), float(row['Longitude'])
                    )
                    for _, row in filtered_df.iterrows()
                ])
                distance_scores = 1 - (distances / max_radius).clip(0, 1)
                content_sim = 0.7 * content_sim + 0.3 * distance_scores

            top_indices = content_sim.argsort()[::-1][:top_n]
            
            recommendations = []
            for idx in top_indices:
                product = filtered_df.iloc[idx]
                similarity_explanation = self.explain_similarity(
                    query_text,
                    product['content_features'],
                    float(content_sim[idx])
                )
                
                recommendation = {
                    'ProductId': product['ProductId'],
                    'Score': float(content_sim[idx]),
                    'Name': product['ProductName'],
                    'Categories': product['Categories'],
                    'Explanation': {
                        'ContentSimilarity': similarity_explanation,
                        'Distance': f"{haversine(float(latitude), float(longitude), float(product['Latitude']), float(product['Longitude'])):.2f}km" if longitude and latitude else "N/A",
                        'MatchingFeatures': similarity_explanation['matching_terms']
                    }
                }
                recommendations.append(recommendation)

            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations

        except Exception as e:
            logger.error(f"Content-based recommendations error: {str(e)}")
            return []
        
    def get_collaborative_recommendations(self, user_id_of_interest):
        try:
            combined_sim_matrix = pd.read_csv("combined_user_user_similarity.csv", index_col=0)
        except Exception as e: 
            return []

        try:
            user_sims = combined_sim_matrix.loc[user_id_of_interest].sort_values(ascending=False)
        except Exception as e:
            return []


        # 2. Exclude the user_id_of_interest itself from the list 
        #    so you don't get the user as their own top similar user

        user_sims = user_sims.drop(user_id_of_interest, errors='ignore')

        # 3. Take the top 5 user IDs
        top_5_similar_users = user_sims.head(5).index.tolist()

        print("Top 5 similar users:", top_5_similar_users)



        # Build the list of placeholders for the IN clause, e.g. (:id1, :id2, ...)
        placeholders = ", ".join([f":id{i}" for i in range(len(top_5_similar_users))])

        # Build the SQL query
        sql_query = f"SELECT * FROM userfeedback"

        # Create a dictionary of params, like {'id0': 'user1', 'id1': 'user2', ...}

        # Execute the query using SQLAlchemy
        with self.engine.connect() as connection:
            result = connection.execute(text(sql_query))
            feedback_data = pd.DataFrame(result.fetchall(), columns=result.keys())


        # 1) Get products liked by the user_of_interest
        user_of_interest_likes = feedback_data[
            (feedback_data['UserId'] == user_id_of_interest) & 
            (feedback_data['IsLiked'] == 1)
        ]['ProductId'].unique()

        user_of_interest_likes_set = set(user_of_interest_likes)

        # 2) For each similar user, find their liked products 
        #    that user_of_interest does NOT like
        similar_user_recommendations = {}

        for sim_user in top_5_similar_users:
            # Products liked by sim_user
            sim_user_likes = feedback_data[
                (feedback_data['UserId'] == sim_user) & 
                (feedback_data['IsLiked'] == 1)
            ]['ProductId'].unique()
            
            # Filter out products the user_of_interest already likes
            new_products = set(sim_user_likes) - user_of_interest_likes_set
            
            similar_user_recommendations[sim_user] = list(new_products)

        # 3) If desired, combine all new products from all top-5 users into a single list
        combined_new_products = set()
        for sim_user, products in similar_user_recommendations.items():
            combined_new_products.update(products)

        # Convert to a list, if needed
        combined_new_products = list(combined_new_products)
        
        recommendations_list = [{"ProductId": pid} for pid in combined_new_products]
    
        return recommendations_list

def haversine(lat1, lon1, lat2, lon2):
    try:
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return 6371.0 * c
    except Exception as e:
        logger.error(f"Haversine calculation error: {e}")
        return float('inf')

# Initialize database engine
engine = create_engine(
    f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
    pool_pre_ping=True,
    pool_recycle=3600
)

# Initialize recommender
recommender = HybridRecommendationSystem(engine)

@app.route('/content-recommendations', methods=['POST'])
def get_content_recommendations():
    try:
        data = request.json

        print("Content Recommendation Request: ", data)

        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        required_params = ['longitude', 'latitude', 'top_n']
        for param in required_params:
            if param not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required parameter: {param}'
                }), 400
            
        # Process categories, since there is multiple preferredCategories
        preferred_categories = []
        for i in range(1, 4):
            key = f'preferredCategories{i}'
            logger.info(f"Processing {key}: {data.get(key)}")
            
            if key in data and data[key]:
                categories = data[key]
                if isinstance(categories, str):
                    preferred_categories.append(categories.strip())
                elif isinstance(categories, list):
                    preferred_categories.extend([c.strip() for c in categories if c and c.strip()])

        logger.info(f"Final processed categories: {preferred_categories}")

        # Parse preferences
        preferences = {
            'PreferredCategories': preferred_categories,
            'PreferredSupplyType': data.get('preferredSupplyType', []),
            'PreferredUnitOfMeasures': data.get('preferredUnitOfMeasures', []),
            'MinimumAvailableQuantity': data.get('minimumAvailableQuantity', 0),
            'MaximumAvailableQuantity': data.get('maximumAvailableQuantity', float('inf')),
            'MaxSearchRadiusKm': data.get('maxSearchRadiusKm', 50),
            'PreferredKeywords': data.get('preferredKeywords', []),
            'LikedProductIds': data.get('likedProductIds', []),
        }

        # Handle date parsing
        date_format = "%Y-%m-%dT%H:%M:%S"
        
        if data.get('preferredValidFrom'):
            try:
                preferences['PreferredValidFrom'] = datetime.strptime(
                    data['preferredValidFrom'], 
                    date_format
                ).isoformat()
            except ValueError as e:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid preferredValidFrom date format. Use YYYY-MM-DDThh:mm:ss'
                }), 400

        if data.get('preferredValidTo'):
            try:
                preferences['PreferredValidTo'] = datetime.strptime(
                    data['preferredValidTo'], 
                    date_format
                ).isoformat()
            except ValueError as e:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid preferredValidTo date format. Use YYYY-MM-DDThh:mm:ss'
                }), 400

        # Validate and parse numeric parameters
        try:
            top_n = int(data['top_n'])
            if top_n <= 0:
                return jsonify({
                    'status': 'error',
                    'message': 'top_n must be greater than 0'
                }), 400

            longitude = float(data['longitude'])
            latitude = float(data['latitude'])

            # Basic coordinate validation
            if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid coordinates'
                }), 400

        except ValueError as e:
            logger.error(f"Parameter parsing error: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid numeric parameters'
            }), 400

        # Validate quantity constraints
        min_qty = preferences['MinimumAvailableQuantity']
        max_qty = preferences['MaximumAvailableQuantity']
        if min_qty > max_qty:
            return jsonify({
                'status': 'error',
                'message': 'MinimumAvailableQuantity cannot be greater than MaximumAvailableQuantity'
            }), 400

        # Log the processed request
        logger.info(f"Processing recommendation request with parameters: top_n={top_n}, "
                   f"location=({latitude}, {longitude})")

        # Generate recommendations
        try:
            content_recommendation = recommender.get_content_based_recommendations(
                preferences, top_n, longitude, latitude
            )

            if not content_recommendation:
                logger.info("No recommendations found for the given criteria")
                return jsonify({
                    'status': 'success',
                    'message': 'No recommendations found',
                    'recommendations': []
                }), 200

            logger.info(f"Successfully generated {len(content_recommendation)} recommendations")
            return jsonify({
                'status': 'success',
                'recommendations': content_recommendation
            }), 200

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            logger.error(traceback.format_exc())
            return jsonify({
                'status': 'error',
                'message': 'Error generating recommendations'
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error in recommendation endpoint: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }), 500


@app.route('/collaborative-recommendations', methods=['POST'])
def get_collaborative_recommendations():
    try:
        data = request.json
        print("Collaborative Recommendation Request: ", data)
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        required_params = ['longitude', 'latitude', 'top_n']
        for param in required_params:
            if param not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required parameter: {param}'
                }), 400

        # Parse preferences
        preferences = {
            'PreferredCategories': data.get('preferredCategories', []),
            'PreferredSupplyType': data.get('preferredSupplyType', []),
            'PreferredUnitOfMeasures': data.get('preferredUnitOfMeasures', []),
            'MinimumAvailableQuantity': data.get('minimumAvailableQuantity', 0),
            'MaximumAvailableQuantity': data.get('maximumAvailableQuantity', float('inf')),
            'MaxSearchRadiusKm': data.get('maxSearchRadiusKm', 50),
            'PreferredKeywords': data.get('preferredKeywords', []),
            'LikedProductIds': data.get('likedProductIds', []),
        }

        # Handle date parsing
        date_format = "%Y-%m-%dT%H:%M:%S"
        
        if data.get('preferredValidFrom'):
            try:
                preferences['PreferredValidFrom'] = datetime.strptime(
                    data['preferredValidFrom'], 
                    date_format
                ).isoformat()
            except ValueError as e:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid preferredValidFrom date format. Use YYYY-MM-DDThh:mm:ss'
                }), 400

        if data.get('preferredValidTo'):
            try:
                preferences['PreferredValidTo'] = datetime.strptime(
                    data['preferredValidTo'], 
                    date_format
                ).isoformat()
            except ValueError as e:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid preferredValidTo date format. Use YYYY-MM-DDThh:mm:ss'
                }), 400

        # Validate and parse numeric parameters
        try:
            top_n = int(data['top_n'])
            if top_n <= 0:
                return jsonify({
                    'status': 'error',
                    'message': 'top_n must be greater than 0'
                }), 400

            longitude = float(data['longitude'])
            latitude = float(data['latitude'])

            # Basic coordinate validation
            if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid coordinates'
                }), 400

        except ValueError as e:
            logger.error(f"Parameter parsing error: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid numeric parameters'
            }), 400

        # Validate quantity constraints
        min_qty = preferences['MinimumAvailableQuantity']
        max_qty = preferences['MaximumAvailableQuantity']
        if min_qty > max_qty:
            return jsonify({
                'status': 'error',
                'message': 'MinimumAvailableQuantity cannot be greater than MaximumAvailableQuantity'
            }), 400

        # Log the processed request
        logger.info(f"Processing recommendation request with parameters: top_n={top_n}, "
                   f"location=({latitude}, {longitude})")

        # Generate recommendations
        try:
            collaborative_recommendation = recommender.get_collaborative_recommendations(data["userId"])

            if not collaborative_recommendation:
                logger.info("No recommendations found for the given criteria")
                return jsonify({
                    'status': 'success',
                    'message': 'No recommendations found',
                    'recommendations': []
                }), 200

            logger.info(f"Successfully generated {len(collaborative_recommendation)} recommendations")
            return jsonify({
                'status': 'success',
                'recommendations': collaborative_recommendation
            }), 200

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            logger.error(traceback.format_exc())
            return jsonify({
                'status': 'error',
                'message': 'Error generating recommendations'
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error in recommendation endpoint: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }), 500



def CreateUserUserMatrix():
    try:
        DB_HOST = os.getenv('DB_HOST', 'localhost') 
        DB_PORT = os.getenv('DB_PORT', '3306')
        DB_USER = os.getenv('DB_USER', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'None58-DB')
        DB_NAME = os.getenv('DB_NAME', 'SymbioDb')

        engine = create_engine(
            f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
            pool_pre_ping=True,
            pool_recycle=3600
        )


        df = pd.DataFrame()

        user_preference_query = """
            SELECT * FROM userpreferences
        """
        user_query = """
            SELECT * FROM aspnetusers
        """
        user_feedback_query = """
            SELECT * FROM userfeedback
        """
        company_query = """
            SELECT * FROM companies
        """
        merged_df = pd.DataFrame()
        user_preference_data = pd.DataFrame()
        user_data = pd.DataFrame()
        user_feedback_data = pd.DataFrame()
        company_data = pd.DataFrame()
        company_data = pd.DataFrame()

        try:
            with engine.connect() as connection:
                user_preference_result = connection.execute(text(user_preference_query))
                user_result = connection.execute(text(user_query))
                user_feedback_result = connection.execute(text(user_feedback_query))
                company_result = connection.execute(text(company_query))

                
                user_preference_data = pd.DataFrame(user_preference_result.fetchall(), columns=user_preference_result.keys())
                user_data = pd.DataFrame(user_result.fetchall(), columns=user_result.keys())
                user_feedback_data = pd.DataFrame(user_feedback_result.fetchall(), columns=user_feedback_result.keys())
                company_data = pd.DataFrame(company_result.fetchall(), columns=company_result.keys())


        except Exception as e:
            raise

        merged_df = pd.merge(user_preference_data, user_data, how='left', left_on='UserId', right_on='Id', suffixes=('', '_user'))
        merged_df = pd.merge(merged_df, company_data, how='left', left_on='CompanyId', right_on='Id', suffixes=('', '_company'))
        merged_df = pd.merge(merged_df, user_feedback_data, how='inner', left_on='UserId', right_on='UserId', suffixes=('', '_feedback'))
        merged_df['PreferredCategories2'] = merged_df['PreferredCategories2'].fillna('')
        merged_df['PreferredCategories3'] = merged_df['PreferredCategories3'].fillna('')
        merged_df['PreferredKeywords'] = merged_df['PreferredKeywords'].fillna('')

        user_feedback_matrix = pd.pivot_table(merged_df, index='UserId', columns='ProductId', values='IsLiked', aggfunc='max', fill_value=0)
        user_user_sim_matrix = pd.DataFrame(cosine_similarity(user_feedback_matrix))


        user_feedback_matrix = pd.pivot_table(
            merged_df, 
            index='UserId', 
            columns='ProductId', 
            values='IsLiked', 
            aggfunc='max', 
            fill_value=0
        )

        # Collaborative filtering similarity
        # This returns a NumPy array (n_users x n_users)
        collab_sim_array = cosine_similarity(user_feedback_matrix)

        # Make it a DataFrame, aligning rows & columns with user IDs
        user_ids = user_feedback_matrix.index
        user_user_sim_matrix = pd.DataFrame(collab_sim_array, 
                                            index=user_ids, 
                                            columns=user_ids)

        # -----------------------------------------
        # 2) Build the TF-IDF-based similarity matrix
        # -----------------------------------------
        # Ensure all columns used in "combined_text" exist and have no NaNs
        cols_to_combine = [
            "PreferredCategories1",
            "PreferredCategories2",
            "PreferredCategories3",
            "PreferredUnitOfMeasures",
            "PreferredKeywords",
            "PreferredSupplyType",
            "PreferredValidFrom",
            "PreferredValidTo",
            "NACECode"
        ]

        merged_df[cols_to_combine] = merged_df[cols_to_combine].fillna("")

        # Convert each user row into a single combined string
        def row_to_text(row):
            parts = []
            for col in cols_to_combine:
                col_value = str(row[col])  # ensure string
                parts.append(f"{col}: {col_value}")
            return ", ".join(parts)

        merged_df["combined_text"] = merged_df.apply(row_to_text, axis=1)

        print(len(merged_df))
        merged_df = merged_df.drop_duplicates(subset='UserId')
        print(len(merged_df))

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(merged_df["combined_text"])

        # Content-based similarity
        # This returns a NumPy array (n_users x n_users)
        content_sim_array = cosine_similarity(tfidf_matrix)

        # Make it a DataFrame with the same index (UserId)
        # IMPORTANT: merged_df is already indexed by 'UserId'
        content_sim_matrix = pd.DataFrame(content_sim_array, 
                                        index=merged_df['UserId'], 
                                        columns=merged_df['UserId'])

        # -----------------------------------------
        # 3) Combine the two similarity matrices
        # -----------------------------------------
        # Example approach: Weighted average
        alpha = 0.5  # you can pick any weighting (0 < alpha < 1)
        combined_sim_matrix = alpha * user_user_sim_matrix + (1 - alpha) * content_sim_matrix
        # combined_sim_matrix is now a DataFrame with user-based similarity
        # that incorporates both collaborative filtering and content-based features.

        # Exporting for later use
        combined_sim_matrix.to_csv("combined_user_user_similarity.csv", index=True)
    except Exception as e:
        print(e)


def run_scheduler():
    """ Continuously run the schedule in a separate thread. """
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('recommendation_system.log')
        ]
    )
    
    logger.info("Starting Recommendation System Server")
    
    try:
        # Test database connection
        with engine.connect() as connection:
            logger.info("Database connection successful") 
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise
    
    CreateUserUserMatrix()
    schedule.every(1).day.do(CreateUserUserMatrix)


    
    # 2) Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()


        # time.sleep(1)
    # Run the Flask application
    app.run(
        debug=False,  # Set to False in production
        host='0.0.0.0',
        port=6000,
        threaded=True
    )


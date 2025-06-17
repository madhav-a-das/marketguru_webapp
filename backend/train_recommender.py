import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from pymongo import MongoClient
import os

def create_model_artifacts_dir():
    """Create model_artifacts directory if it doesn't exist"""
    if not os.path.exists('model_artifacts'):
        os.makedirs('model_artifacts')
        print("Created model_artifacts directory")

def connect_to_mongodb():
    """Connect to MongoDB and get products"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['marketguru']
        products_collection = db['products']
        
        # Test connection
        client.admin.command('ping')
        print("Connected to MongoDB successfully")
        
        # Get products from MongoDB
        products = list(products_collection.find({}, {'_id': 0}))
        if not products:
            print("No products found in MongoDB. Using sample data.")
            return None
        
        return products
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return None

def get_sample_products():
    """Get sample products if MongoDB is not available"""
    return [
        {
            "id": 1,
            "name": "Wireless Headphones",
            "description": "High-quality over-ear wireless headphones with active noise cancellation and long battery life",
            "price": 199.99,
            "category": "Electronics",
            "brand": "AudioTech"
        },
        {
            "id": 2,
            "name": "Smart Watch",
            "description": "Waterproof smartwatch featuring heart rate monitoring, GPS tracking, and customizable watch faces",
            "price": 299.99,
            "category": "Electronics",
            "brand": "WatchPro"
        },
        {
            "id": 3,
            "name": "Running Shoes",
            "description": "Lightweight running shoes with breathable mesh upper and responsive cushioning for long-distance comfort",
            "price": 129.99,
            "category": "Sports",
            "brand": "RunFast"
        },
        {
            "id": 4,
            "name": "DSLR Camera",
            "description": "Professional-grade DSLR camera with 24.2MP sensor, 4K video recording, and interchangeable lenses",
            "price": 899.99,
            "category": "Electronics",
            "brand": "PhotoPro"
        },
        {
            "id": 5,
            "name": "Travel Backpack",
            "description": "Durable travel backpack with multiple compartments, USB charging port, and ergonomic straps",
            "price": 79.99,
            "category": "Travel",
            "brand": "AdventurePack"
        },
        {
            "id": 6,
            "name": "Gaming Laptop",
            "description": "High-performance gaming laptop with RTX graphics, 16GB RAM, and RGB keyboard for ultimate gaming experience",
            "price": 1299.99,
            "category": "Electronics",
            "brand": "GameMaster"
        },
        {
            "id": 7,
            "name": "Bluetooth Speaker",
            "description": "Portable waterproof Bluetooth speaker with 360-degree sound and 20-hour battery life",
            "price": 89.99,
            "category": "Electronics",
            "brand": "SoundWave"
        },
        {
            "id": 8,
            "name": "Fitness Tracker",
            "description": "Advanced fitness tracker with sleep monitoring, heart rate sensor, and smartphone notifications",
            "price": 149.99,
            "category": "Electronics",
            "brand": "FitLife"
        }
    ]

def train_content_based_recommender(products):
    """Train content-based recommendation system"""
    print(f"Training recommender with {len(products)} products...")
    
    # Create DataFrame
    df = pd.DataFrame(products)
    
    # Combine features for content-based filtering
    df['combined_features'] = (
        df['name'].fillna('') + ' ' +
        df['description'].fillna('') + ' ' +
        df['category'].fillna('') + ' ' +
        df['brand'].fillna('')
    )
    
    # Create TF-IDF matrix
    tfidf = TfidfVectorizer(
        stop_words='english',
        max_features=1000,
        ngram_range=(1, 2),
        lowercase=True
    )
    
    tfidf_matrix = tfidf.fit_transform(df['combined_features'])
    
    print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
    print(f"Feature names sample: {tfidf.get_feature_names_out()[:10]}")
    
    return tfidf, tfidf_matrix, df

def save_model_artifacts(tfidf, tfidf_matrix, df):
    """Save trained model artifacts"""
    try:
        # Save TF-IDF vectorizer
        joblib.dump(tfidf, 'model_artifacts/tfidf_vectorizer.pkl')
        print("✓ Saved TF-IDF vectorizer")
        
        # Save TF-IDF matrix (this is our recommender matrix)
        joblib.dump(tfidf_matrix, 'model_artifacts/recommender_matrix.pkl')
        print("✓ Saved recommender matrix")
        
        # Save a simple model file (for compatibility)
        model_info = {
            'type': 'content_based',
            'features': tfidf_matrix.shape[1],
            'products': len(df),
            'trained_at': pd.Timestamp.now().isoformat()
        }
        joblib.dump(model_info, 'model_artifacts/recommender_model.pkl')
        print("✓ Saved model metadata")
        
        # Display model statistics
        print(f"\n📊 Model Statistics:")
        print(f"   - Number of products: {len(df)}")
        print(f"   - Number of features: {tfidf_matrix.shape[1]}")
        print(f"   - Matrix density: {tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1]):.4f}")
        
    except Exception as e:
        print(f"Error saving model artifacts: {e}")

def test_recommendations(tfidf, tfidf_matrix, df):
    """Test the recommendation system"""
    print("\n🧪 Testing recommendation system...")
    
    # Test with a sample query
    test_query = "wireless noise cancelling headphones"
    query_vec = tfidf.transform([test_query])
    similarities = cosine_similarity(query_vec, tfidf_matrix)[0]
    
    # Get top recommendations
    top_indices = np.argsort(similarities)[::-1][:3]
    
    print(f"Query: '{test_query}'")
    print("Top 3 recommendations:")
    for i, idx in enumerate(top_indices, 1):
        product = df.iloc[idx]
        print(f"  {i}. {product['name']} (similarity: {similarities[idx]:.3f})")
        print(f"     {product['description'][:80]}...")

def main():
    print("🚀 Starting MarketGuru Recommendation Model Training...")
    
    # Create necessary directories
    create_model_artifacts_dir()
    
    # Get product data
    products = connect_to_mongodb()
    if not products:
        print("Using sample product data for training...")
        products = get_sample_products()
    
    # Train the model
    tfidf, tfidf_matrix, df = train_content_based_recommender(products)
    
    # Save model artifacts
    save_model_artifacts(tfidf, tfidf_matrix, df)
    
    # Test the model
    test_recommendations(tfidf, tfidf_matrix, df)
    
    print("\n✅ Training completed successfully!")
    print("Model artifacts saved in 'model_artifacts/' directory")

if __name__ == "__main__":
    main()
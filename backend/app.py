from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import requests
from bs4 import BeautifulSoup
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from pymongo import MongoClient
from bson import ObjectId
import pandas as pd
import asyncio
import aiohttp
import urllib.parse
import datetime
import re
import bcrypt
import jwt
from functools import wraps
from detect import detect_image
from enhanced_detection import EnhancedProductDetector
from product_search import ProductSearchEngine

app = Flask(__name__)
CORS(app)

# JWT Secret Key - In production, use environment variable
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'

# Initialize enhanced product detector
enhanced_detector = EnhancedProductDetector()

# Initialize product search engine
product_search_engine = ProductSearchEngine()

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['marketguru']
products_collection = db['products']
preferences_collection = db['preferences']
price_comparison_collection = db['price_comparison']
users_collection = db['users']  # Add users collection

# Enhanced HTTP headers for better scraping
SCRAPING_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
    "Accept-Language": "en-US,en;q=0.9"
}

# Authentication helper functions
def hash_password(password):
    """Hash a password for storing."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def check_password(password, hashed):
    """Check if provided password matches the hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def generate_token(user_id):
    """Generate JWT token for user."""
    payload = {
        'user_id': str(user_id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)  # Token expires in 30 days
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

def token_required(f):
    """Decorator to require authentication for protected routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            
            # Get user from database
            current_user = users_collection.find_one({'_id': ObjectId(current_user_id)})
            if not current_user:
                return jsonify({'success': False, 'error': 'Invalid token'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'success': False, 'error': 'Token validation failed'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator to require admin authentication for protected routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            
            # Get user from database
            current_user = users_collection.find_one({'_id': ObjectId(current_user_id)})
            if not current_user:
                return jsonify({'success': False, 'error': 'Invalid token'}), 401
            
            # Check if user is admin
            if current_user.get('role') != 'Admin':
                return jsonify({'success': False, 'error': 'Admin access required'}), 403
                
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'success': False, 'error': 'Token validation failed'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# Initialize or load recommender artifacts
try:
    tfidf = joblib.load('model_artifacts/tfidf_vectorizer.pkl')
    recommender_matrix = joblib.load('model_artifacts/recommender_matrix.pkl')
except FileNotFoundError:
    # Initialize with empty vectorizer if files don't exist
    tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
    recommender_matrix = None

def scrape_amazon_india(product):
    """Scrape the first product price and title from Amazon India."""
    try:
        query = urllib.parse.quote_plus(product)
        url = f"https://www.amazon.in/s?k={query}"
        resp = requests.get(url, headers=SCRAPING_HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        result = soup.select_one("div[data-component-type='s-search-result']")
        if not result:
            return {"retailer": "Amazon India", "title": "No results found", "price": None}

        title_tag = result.select_one("span.a-size-medium.a-color-base.a-text-normal")
        title = title_tag.get_text(strip=True) if title_tag else "Unknown"

        price_tag = result.select_one("span.a-price > span.a-offscreen")
        if not price_tag:
            return {"retailer": "Amazon India", "title": title, "price": None}
        
        raw = price_tag.get_text().replace("₹", "").replace(",", "")
        try:
            price = float(raw)
            return {"retailer": "Amazon India", "title": title, "price": price, "currency": "₹"}
        except ValueError:
            return {"retailer": "Amazon India", "title": title, "price": None}
    except Exception as e:
        return {"retailer": "Amazon India", "title": "Error", "price": None, "error": str(e)}

def scrape_flipkart(product):
    """Scrape the first product price and title from Flipkart India."""
    try:
        query = urllib.parse.quote_plus(product)
        url = f"https://www.flipkart.com/search?q={query}"
        resp = requests.get(url, headers=SCRAPING_HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Try multiple price selectors as Flipkart changes them frequently
        price_selectors = [
            "div.Nx9bqj._4b5DiR",
            "div._30jeq3._1_WHN1",
            "div._25b18c"
        ]
        
        price_tag = None
        for selector in price_selectors:
            price_tag = soup.select_one(selector)
            if price_tag:
                break
                
        if not price_tag:
            return {"retailer": "Flipkart", "title": "No price found", "price": None}
        
        raw = price_tag.get_text().strip().replace("₹", "").replace(",", "")
        try:
            price = float(raw)
        except ValueError:
            return {"retailer": "Flipkart", "title": "Price parse error", "price": None}

        # Try multiple title selectors
        title_selectors = [
            "div.yRaY8j.ZYYwLA",
            "div._4rR01T",
            "a.s1Q9rs"
        ]
        
        title_tag = None
        for selector in title_selectors:
            title_tag = soup.select_one(selector)
            if title_tag:
                break
                
        title = title_tag.get_text(strip=True) if title_tag else "Unknown"

        return {"retailer": "Flipkart", "title": title, "price": price, "currency": "₹"}
    except Exception as e:
        return {"retailer": "Flipkart", "title": "Error", "price": None, "error": str(e)}

def filter_by_specs(data_list, storage=None, color=None):
    """Filter results by storage and color specifications."""
    filtered = []
    for data in data_list:
        if not data or data["price"] is None:
            continue
        title = data["title"].lower()
        if storage and storage.lower() not in title:
            continue
        if color and color.lower() not in title:
            continue
        filtered.append(data)
    return filtered

# Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['email', 'password', 'fullName']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        full_name = data['fullName'].strip()
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if user already exists
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            return jsonify({'success': False, 'error': 'Email already registered'}), 400
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Create user document
        user_data = {
            'email': email,
            'password': hashed_password,
            'fullName': full_name,
            'role': 'Regular User',  # Default role
            'status': 'Active',     # Default status
            'createdAt': datetime.datetime.utcnow(),
            'preferences': {},
            'searchHistory': []
        }
        
        # Insert user into database
        result = users_collection.insert_one(user_data)
        user_id = result.inserted_id
        
        # Generate token
        token = generate_token(user_id)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': str(user_id),
                'email': email,
                'fullName': full_name,
                'role': 'Regular User',
                'status': 'Active'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Find user in database
        user = users_collection.find_one({'email': email})
        if not user:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Check if user is banned
        if user.get('status') == 'Banned':
            return jsonify({
                'success': False, 
                'error': 'Account is banned', 
                'banned': True,
                'message': 'Your account has been banned. Please contact the administrator for assistance.'
            }), 403
        
        # Check password
        if not check_password(password, user['password']):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = generate_token(user['_id'])
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'fullName': user['fullName'],
                'role': user.get('role', 'Regular User'),
                'status': user.get('status', 'Active')
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    """Verify if token is valid and return user info."""
    try:
        return jsonify({
            'success': True,
            'user': {
                'id': str(current_user['_id']),
                'email': current_user['email'],
                'fullName': current_user['fullName'],
                'role': current_user.get('role', 'Regular User'),
                'status': current_user.get('status', 'Active')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get user profile information."""
    try:
        return jsonify({
            'success': True,
            'user': {
                'id': str(current_user['_id']),
                'email': current_user['email'],
                'fullName': current_user['fullName'],
                'role': current_user.get('role', 'Regular User'),
                'status': current_user.get('status', 'Active'),
                'createdAt': current_user.get('createdAt'),
                'preferences': current_user.get('preferences', {}),
                'searchHistory': current_user.get('searchHistory', [])
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Admin Routes
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users(current_user):
    """Get all users with search and pagination."""
    try:
        # Get query parameters
        search = request.args.get('search', '').strip()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        role_filter = request.args.get('role', '')
        status_filter = request.args.get('status', '')
        
        # Build search query
        query = {}
        if search:
            query['$or'] = [
                {'email': {'$regex': search, '$options': 'i'}},
                {'fullName': {'$regex': search, '$options': 'i'}}
            ]
        
        if role_filter:
            query['role'] = role_filter
            
        if status_filter:
            query['status'] = status_filter
        
        # Calculate skip for pagination
        skip = (page - 1) * limit
        
        # Get users with pagination
        total_users = users_collection.count_documents(query)
        users = list(users_collection.find(
            query, 
            {'password': 0}  # Exclude password from results
        ).skip(skip).limit(limit).sort('createdAt', -1))
        
        # Convert ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])
        
        return jsonify({
            'success': True,
            'users': users,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_users,
                'pages': (total_users + limit - 1) // limit
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users/<user_id>', methods=['GET'])
@admin_required
def get_user_by_id(current_user, user_id):
    """Get a specific user by ID."""
    try:
        user = users_collection.find_one(
            {'_id': ObjectId(user_id)}, 
            {'password': 0}  # Exclude password
        )
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        user['_id'] = str(user['_id'])
        
        return jsonify({
            'success': True,
            'user': user
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users/<user_id>', methods=['PUT'])
@admin_required
def update_user(current_user, user_id):
    """Update user details."""
    try:
        data = request.json
        
        # Find the user
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Prepare update data
        update_data = {}
        
        if 'fullName' in data:
            update_data['fullName'] = data['fullName'].strip()
        
        if 'email' in data:
            new_email = data['email'].lower().strip()
            # Check if email is already taken by another user
            existing_user = users_collection.find_one({
                'email': new_email,
                '_id': {'$ne': ObjectId(user_id)}
            })
            if existing_user:
                return jsonify({'success': False, 'error': 'Email already taken'}), 400
            update_data['email'] = new_email
        
        if 'role' in data:
            valid_roles = ['Admin', 'Moderator', 'Regular User']
            if data['role'] not in valid_roles:
                return jsonify({'success': False, 'error': 'Invalid role'}), 400
            update_data['role'] = data['role']
        
        if 'status' in data:
            valid_statuses = ['Active', 'Banned']
            if data['status'] not in valid_statuses:
                return jsonify({'success': False, 'error': 'Invalid status'}), 400
            update_data['status'] = data['status']
        
        if not update_data:
            return jsonify({'success': False, 'error': 'No valid fields to update'}), 400
        
        # Update the user
        update_data['updatedAt'] = datetime.datetime.utcnow()
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        
        # Return updated user (exclude password)
        updated_user = users_collection.find_one(
            {'_id': ObjectId(user_id)}, 
            {'password': 0}
        )
        updated_user['_id'] = str(updated_user['_id'])
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': updated_user
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(current_user, user_id):
    """Delete a user."""
    try:
        # Prevent admin from deleting themselves
        if str(current_user['_id']) == user_id:
            return jsonify({'success': False, 'error': 'Cannot delete your own account'}), 400
        
        # Find and delete the user
        result = users_collection.delete_one({'_id': ObjectId(user_id)})
        
        if result.deleted_count == 0:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_admin_stats(current_user):
    """Get admin dashboard statistics."""
    try:
        # Get user stats
        total_users = users_collection.count_documents({})
        active_users = users_collection.count_documents({'status': 'Active'})
        banned_users = users_collection.count_documents({'status': 'Banned'})
        
        # Role distribution
        admins = users_collection.count_documents({'role': 'Admin'})
        moderators = users_collection.count_documents({'role': 'Moderator'})
        regular_users = users_collection.count_documents({'role': 'Regular User'})
        
        # Recent users (last 30 days)
        thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        recent_users = users_collection.count_documents({
            'createdAt': {'$gte': thirty_days_ago}
        })
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'active_users': active_users,
                'banned_users': banned_users,
                'recent_users': recent_users,
                'role_distribution': {
                    'Admin': admins,
                    'Moderator': moderators,
                    'Regular User': regular_users
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/detect', methods=['POST'])
def api_detect():
    try:
        file = request.files['image']
        detections = detect_image(file.read())
        return jsonify({'success': True, 'detections': detections})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/enhanced-detect', methods=['POST'])
def api_enhanced_detect():
    """Enhanced product detection with internet search"""
    try:
        file = request.files['image']
        image_bytes = file.read()
        
        # Perform enhanced detection and search
        results = enhanced_detector.analyze_and_identify_products(image_bytes)
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/upload-search', methods=['POST'])
def api_upload_search():
    """Upload image and search for products with optional search query"""
    try:
        file = request.files['image']
        search_query = request.form.get('search_query', None)
        image_bytes = file.read()
        
        # Search for products in uploaded image
        results = enhanced_detector.search_uploaded_image(image_bytes, search_query)
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/search-product', methods=['POST'])
def api_search_product():
    """Direct product search without image"""
    try:
        data = request.json
        search_query = data.get('query', '')
        
        if not search_query.strip():
            return jsonify({'success': False, 'error': 'Search query is required'}), 400
        
        # Search for products across platforms
        search_results = enhanced_detector.search_engine.search_all_platforms(
            search_query, max_results_per_platform=3
        )
        
        return jsonify({
            'success': True,
            'results': {
                'search_query': search_query,
                'search_results': search_results,
                'total_found': len(search_results)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    try:
        item_desc = request.json.get('description', '')
        print(f"Received search query: {item_desc}")
        
        if not item_desc:
            return jsonify({'success': False, 'error': 'Description required'}), 400
        
        # Search Amazon for real products based on user description
        print(f"Searching Amazon for: {item_desc}")
        amazon_products = product_search_engine.search_amazon_products(item_desc, max_results=8)
        print(f"Found {len(amazon_products)} products from Amazon")
        
        if not amazon_products:
            print("No products found from Amazon, trying fallback...")
            # Fallback to local products if Amazon search fails
            products = list(products_collection.find({}, {'_id': 0}))
            return jsonify({
                'success': True, 
                'recommendations': products[:5],
                'message': 'Amazon search failed, showing local products'
            })
        
        # Transform the data to match frontend expectations
        recommendations = []
        for i, product in enumerate(amazon_products):
            print(f"Processing product {i+1}: {product.get('title', 'Unknown')[:50]}...")
            
            # Clean up price - remove currency symbols and convert to number if possible
            price_str = product.get('price', 'N/A')
            try:
                # Extract numeric value from price string
                price_numeric = re.sub(r'[₹,]', '', price_str).strip()
                price_value = float(price_numeric) if price_numeric.replace('.', '').isdigit() else 0
            except:
                price_value = 0
            
            recommendations.append({
                'name': product.get('title', 'Unknown Product'),
                'price': price_value,
                'description': product.get('title', ''),
                'category': 'Amazon Product',
                'brand': 'Various',
                'image_url': product.get('image_url', ''),
                'product_link': product.get('product_link', ''),
                'rating': product.get('rating', 'N/A'),
                'reviews': product.get('reviews', 'N/A'),
                'retailer': product.get('retailer', 'Amazon India')
            })
        
        print(f"Returning {len(recommendations)} processed recommendations")
        return jsonify({'success': True, 'recommendations': recommendations})
    except Exception as e:
        print(f"Error in api_recommend: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test-amazon', methods=['POST'])
def test_amazon_search():
    """Test endpoint to debug Amazon search"""
    try:
        query = request.json.get('query', 'wireless headphones')
        print(f"Testing Amazon search with query: {query}")
        
        # Test the search directly
        results = product_search_engine.search_amazon_products(query, max_results=3)
        
        print(f"Raw Amazon results: {results}")
        
        return jsonify({
            'success': True,
            'query': query,
            'raw_results': results,
            'count': len(results)
        })
    except Exception as e:
        print(f"Error in test_amazon_search: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recommend-local', methods=['POST'])
def api_recommend_local():
    """Original local recommendation system (backup)"""
    global tfidf, recommender_matrix
    try:
        item_desc = request.json.get('description', '')
        if not item_desc:
            return jsonify({'success': False, 'error': 'Description required'}), 400
        
        # Get products from MongoDB
        products = list(products_collection.find({}, {'_id': 0}))
        if not products:
            return jsonify({'success': True, 'recommendations': []})
        
        if recommender_matrix is None:
            # Build recommendation matrix if not exists
            descriptions = [p.get('description', '') for p in products]
            if descriptions:
                recommender_matrix = tfidf.fit_transform(descriptions)
                joblib.dump(tfidf, 'model_artifacts/tfidf_vectorizer.pkl')
                joblib.dump(recommender_matrix, 'model_artifacts/recommender_matrix.pkl')
        
        # Find similar products
        vec = tfidf.transform([item_desc])
        sims = cosine_similarity(vec, recommender_matrix)[0]
        top_idx = np.argsort(sims)[::-1][:5]
        
        recommendations = [products[i] for i in top_idx if i < len(products)]
        return jsonify({'success': True, 'recommendations': recommendations})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/price', methods=['POST'])
def api_price():
    try:
        data = request.json
        product_name = data.get('product_name', '')
        storage = data.get('storage', None)
        color = data.get('color', None)
        sites = data.get('sites', ['amazon', 'flipkart'])
        
        if not product_name.strip():
            return jsonify({'success': False, 'error': 'Product name is required'}), 400
        
        # Build full search query
        search_parts = [product_name]
        if storage:
            search_parts.append(storage)
        if color:
            search_parts.append(color)
        full_query = " ".join(search_parts)
        
        # Scrape prices from different sites
        price_data = []
        results = {}
        
        if 'amazon' in sites:
            amazon_data = scrape_amazon_india(full_query)
            price_data.append(amazon_data)
            
            if amazon_data['price'] is not None:
                results['amazon'] = f"₹{amazon_data['price']:,.2f}"
            elif 'error' in amazon_data:
                results['amazon'] = f"Error: {amazon_data['error']}"
            else:
                results['amazon'] = "Price not found"
        
        if 'flipkart' in sites:
            flipkart_data = scrape_flipkart(full_query)
            price_data.append(flipkart_data)
            
            if flipkart_data['price'] is not None:
                results['flipkart'] = f"₹{flipkart_data['price']:,.2f}"
            elif 'error' in flipkart_data:
                results['flipkart'] = f"Error: {flipkart_data['error']}"
            else:
                results['flipkart'] = "Price not found"
        
        # Filter by specifications if provided
        if storage or color:
            filtered_data = filter_by_specs(price_data, storage, color)
            if not filtered_data:
                return jsonify({
                    'success': True, 
                    'prices': results,
                    'message': f'No products found matching specifications: {storage or ""} {color or ""}'.strip(),
                    'raw_data': price_data
                })
        
        # Store in MongoDB for analytics (optional)
        try:
            timestamp = datetime.datetime.utcnow()
            document = {
                "product": product_name,
                "storage": storage,
                "color": color,
                "full_query": full_query,
                "prices": price_data,
                "timestamp": timestamp
            }
            price_comparison_collection.insert_one(document)
        except Exception as mongo_error:
            print(f"MongoDB storage error: {mongo_error}")
        
        # Calculate price analysis
        valid_prices = [d for d in price_data if d['price'] is not None]
        analysis = {}
        
        if len(valid_prices) >= 2:
            prices_only = [d['price'] for d in valid_prices]
            min_price = min(prices_only)
            max_price = max(prices_only)
            best_retailer = next(d['retailer'] for d in valid_prices if d['price'] == min_price)
            
            analysis = {
                'best_price': min_price,
                'best_retailer': best_retailer,
                'price_range': {'min': min_price, 'max': max_price},
                'savings': max_price - min_price if max_price > min_price else 0
            }
        
        return jsonify({
            'success': True, 
            'prices': results,
            'analysis': analysis,
            'product_details': price_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        msg = request.json.get('message', '').lower()
        
        # Enhanced rule-based chatbot
        if any(word in msg for word in ['hello', 'hi', 'hey']):
            resp = 'Hi there! I\'m MarketGuru AI. How can I help you find the perfect product today?'
        elif any(word in msg for word in ['price', 'cost', 'how much']):
            resp = 'I can help you compare prices! Use the Price Comparison feature to find the best deals across multiple stores.'
        elif any(word in msg for word in ['recommend', 'suggest', 'similar']):
            resp = 'I\'d love to recommend products for you! Try the Product Detection feature to scan an item and get personalized recommendations.'
        elif any(word in msg for word in ['ar', 'try on', 'virtual']):
            resp = 'You can virtually try on products using our AR feature! Look for the AR viewer in the product details.'
        elif any(word in msg for word in ['detect', 'scan', 'identify']):
            resp = 'Use the Product Detection feature to scan any item with your camera. I\'ll identify it and provide detailed information!'
        elif any(word in msg for word in ['help', 'support']):
            resp = 'I can help you with:\n• Product detection and scanning\n• Price comparisons\n• Product recommendations\n• AR try-on features\nWhat would you like to explore?'
        elif any(word in msg for word in ['thank', 'thanks']):
            resp = 'You\'re welcome! Happy shopping with MarketGuru! 🛍️'
        else:
            resp = 'I\'m here to help with product detection, recommendations, and price comparisons. What would you like to know more about?'
            
        return jsonify({'success': True, 'reply': resp})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        products = list(products_collection.find({}, {'_id': 0}))
        return jsonify({'success': True, 'products': products})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def add_product():
    try:
        product_data = request.json
        result = products_collection.insert_one(product_data)
        return jsonify({'success': True, 'id': str(result.inserted_id)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/seed-data', methods=['POST'])
def seed_database():
    try:
        # Clear existing data
        products_collection.delete_many({})
        
        # Sample products for testing
        sample_products = [
            {
                "id": 1,
                "name": "Wireless Headphones",
                "description": "High-quality over-ear wireless headphones with active noise cancellation and long battery life",
                "price": 199.99,
                "category": "Electronics",
                "brand": "AudioTech",
                "image_url": "/images/headphones.jpg",
                "ar_model": "/models/headphones.gltf"
            },
            {
                "id": 2,
                "name": "Smart Watch",
                "description": "Waterproof smartwatch featuring heart rate monitoring, GPS tracking, and customizable watch faces",
                "price": 299.99,
                "category": "Electronics",
                "brand": "WatchPro",
                "image_url": "/images/smartwatch.jpg",
                "ar_model": "/models/AnimatedCube.gltf"
            },
            {
                "id": 3,
                "name": "Running Shoes",
                "description": "Lightweight running shoes with breathable mesh upper and responsive cushioning for long-distance comfort",
                "price": 129.99,
                "category": "Sports",
                "brand": "RunFast",
                "image_url": "/images/shoes.jpg",
                "ar_model": "/models/AnimatedCube.gltf"
            },
            {
                "id": 4,
                "name": "DSLR Camera",
                "description": "Professional-grade DSLR camera with 24.2MP sensor, 4K video recording, and interchangeable lenses",
                "price": 899.99,
                "category": "Electronics",
                "brand": "PhotoPro",
                "image_url": "/images/camera.jpg",
                "ar_model": "/models/AnimatedCube.gltf"
            },
            {
                "id": 5,
                "name": "Travel Backpack",
                "description": "Durable travel backpack with multiple compartments, USB charging port, and ergonomic straps",
                "price": 79.99,
                "category": "Travel",
                "brand": "AdventurePack",
                "image_url": "/images/backpack.jpg",
                "ar_model": "/models/AnimatedCube.gltf"
            },
            {
                "id": 6,
                "name": "Gaming Laptop",
                "description": "High-performance gaming laptop with RTX graphics, 16GB RAM, and RGB keyboard for ultimate gaming experience",
                "price": 1299.99,
                "category": "Electronics",
                "brand": "GameMaster",
                "image_url": "/images/laptop.jpg",
                "ar_model": "/models/AnimatedCube.gltf"
            }
        ]
        
        products_collection.insert_many(sample_products)
        return jsonify({'success': True, 'message': f'Seeded {len(sample_products)} products'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/setup-admin', methods=['POST'])
def setup_admin():
    """Setup initial admin user - should be used only once during setup"""
    try:
        data = request.json
        
        # Check if admin already exists
        existing_admin = users_collection.find_one({'role': 'Admin'})
        if existing_admin:
            return jsonify({'success': False, 'error': 'Admin user already exists'}), 400
        
        # Validate required fields
        required_fields = ['email', 'password', 'fullName']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        full_name = data['fullName'].strip()
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if user already exists
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            return jsonify({'success': False, 'error': 'Email already registered'}), 400
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Create admin user document
        user_data = {
            'email': email,
            'password': hashed_password,
            'fullName': full_name,
            'role': 'Admin',  # Set as Admin
            'status': 'Active',
            'createdAt': datetime.datetime.utcnow(),
            'preferences': {},
            'searchHistory': []
        }
        
        # Insert user into database
        result = users_collection.insert_one(user_data)
        user_id = result.inserted_id
        
        return jsonify({
            'success': True,
            'message': 'Admin user created successfully',
            'user': {
                'id': str(user_id),
                'email': email,
                'fullName': full_name,
                'role': 'Admin'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database on startup
    print("Starting MarketGuru Backend...")
    print("MongoDB connection:", "✓" if client.admin.command('ping') else "✗")
    app.run(host='0.0.0.0', port=5000, debug=True)
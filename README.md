# MarketGuru - AI-Powered Shopping Assistant

A complete AI-powered shopping web application with product detection, recommendations, AR try-on, price comparison, and chatbot features.

## ✨ Features

🔍 **Product Detection** - Detect products using webcam with YOLOv5  
🎯 **Smart Recommendations** - Content-based product recommendations using Scikit-learn  
🥽 **AR Try-On** - Virtual try-on using model-viewer and WebXR  
💰 **Price Comparison** - Compare prices across multiple online stores  
💬 **AI Chatbot** - Rule-based shopping assistant  
🗃️ **MongoDB Database** - Store product details and preferences  

## 🛠️ Tech Stack

**Frontend:** React.js + Tailwind CSS  
**Backend:** Flask (Python)  
**ML Models:** YOLOv5, Scikit-learn  
**AR Module:** @google/model-viewer  
**Database:** MongoDB  

## 📦 Prerequisites

Before starting, make sure you have installed:

- **Python 3.8+** ([Download here](https://www.python.org/downloads/))
- **Node.js 16+** ([Download here](https://nodejs.org/))
- **MongoDB Community** ([Download here](https://www.mongodb.com/try/download/community))
- **Git** ([Download here](https://git-scm.com/downloads))

## 🚀 Quick Start

### 1. Clone and Setup Project

```powershell
# Clone the repository (if from Git)
# git clone <your-repo-url>
# cd marketguru-webapp

# Or navigate to your existing project folder
cd "E:\A Work\AR app\webApp final\marketguru-webapp"
```

### 2. Backend Setup (Flask + Python)

```powershell
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Train the ML model (this creates the model files)
python train_recommender.py
```

### 3. Start MongoDB

```powershell
# Start MongoDB service (Windows)
net start MongoDB

# Or start MongoDB manually
mongod --dbpath "C:\data\db"
```

### 4. Frontend Setup (React)

```powershell
# Open a new PowerShell window and navigate to frontend folder
cd frontend

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

### 5. Start Backend Server

```powershell
# In the backend folder (with virtual environment activated)
python app.py
```

## 🔧 Detailed Setup Guide

### MongoDB Setup

1. **Install MongoDB Community Edition**
   - Download from [MongoDB official website](https://www.mongodb.com/try/download/community)
   - Follow installation instructions for Windows
   - Add MongoDB to your system PATH

2. **Start MongoDB Service**
   ```powershell
   # Option 1: As Windows Service
   net start MongoDB
   
   # Option 2: Manual start
   mongod --dbpath "C:\data\db"
   ```

3. **Verify MongoDB is Running**
   - Open MongoDB Compass
   - Connect to `mongodb://localhost:27017`
   - You should see an empty database

### Backend Configuration

1. **Virtual Environment Setup**
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Train ML Models**
   ```powershell
   # This creates the recommendation model
   python train_recommender.py
   ```

4. **Seed Database** (After starting the backend)
   ```powershell
   # Make a POST request to seed the database
   curl -X POST http://localhost:5000/api/seed-data
   ```

### Frontend Configuration

1. **Install Dependencies**
   ```powershell
   cd frontend
   npm install
   ```

2. **Environment Setup**
   ```powershell
   # Create .env file in frontend folder (optional)
   echo "REACT_APP_API_URL=http://localhost:5000" > .env
   ```

## 🏃‍♂️ Running the Application

### Start All Services

1. **MongoDB** (Terminal 1)
   ```powershell
   mongod --dbpath "C:\data\db"
   ```

2. **Backend Server** (Terminal 2)
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   python app.py
   ```

3. **Frontend Server** (Terminal 3)
   ```powershell
   cd frontend
   npm start
   ```

### Access the Application

- **Web App:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **MongoDB Compass:** mongodb://localhost:27017

## 📱 Using the Application

### 1. Product Detection
- Click on "Product Detection" tab
- Allow camera permissions
- Point camera at products and click "Detect Product"
- View detection results with confidence scores

### 2. Smart Recommendations
- Click on "Recommendations" tab
- Enter a product description
- Get AI-powered product suggestions
- Browse recommended products

### 3. AR Try-On
- Click on "AR Try-On" tab
- Select a product from the list
- Click "View in AR" to see 3D model
- Point phone camera at flat surface to place model

### 4. Price Comparison
- Click on "Price Compare" tab
- Enter product name
- Select stores (Amazon, eBay)
- View price comparison results

### 5. AI Assistant
- Click on "AI Assistant" tab
- Chat with the AI about products and features
- Get help with navigation and recommendations

## 🗃️ Database Structure

### Products Collection
```json
{
  "id": 1,
  "name": "Wireless Headphones",
  "description": "High-quality over-ear wireless headphones...",
  "price": 199.99,
  "category": "Electronics",
  "brand": "AudioTech",
  "image_url": "/images/headphones.jpg",
  "ar_model": "/models/headphones.gltf"
}
```

## 🔌 API Endpoints

### Product Management
- `GET /api/products` - Get all products
- `POST /api/products` - Add new product
- `POST /api/seed-data` - Seed database with sample data

### AI Features
- `POST /api/detect` - Detect products in image
- `POST /api/recommend` - Get product recommendations
- `POST /api/price` - Compare product prices
- `POST /api/chat` - Chat with AI assistant

## 📁 Project Structure

```
marketguru-webapp/
├── frontend/                 # React.js frontend
│   ├── public/
│   │   └── models/          # 3D models for AR
│   │   └── src/
│   │   │   ├── components/      # React components
│   │   │   └── App.js          # Main app component
│   │   └── package.json
│   ├── backend/                 # Flask backend
│   │   ├── model_artifacts/    # Trained ML models
│   │   ├── app.py             # Main Flask app
│   │   ├── detect.py          # YOLO detection
│   │   ├── train_recommender.py # ML training
│   │   └── requirements.txt
│   └── README.md
```

## 🐛 Troubleshooting

### Common Issues

1. **Camera not working**
   - Allow camera permissions in browser
   - Use HTTPS for camera access (or localhost)

2. **MongoDB connection failed**
   - Ensure MongoDB service is running
   - Check if port 27017 is available

3. **CORS errors**
   - Backend includes CORS headers
   - Frontend proxy is configured

4. **Model files missing**
   - Run `python train_recommender.py` in backend folder
   - Check if model_artifacts folder is created

5. **Dependencies issues**
   - Delete node_modules and run `npm install` again
   - Recreate Python virtual environment

## 🔮 Advanced Configuration

### Add New Products
```python
# Via API
import requests
data = {
    "name": "New Product",
    "description": "Product description",
    "price": 99.99,
    "category": "Electronics",
    "brand": "BrandName"
}
requests.post("http://localhost:5000/api/products", json=data)
```

### Retrain ML Model
```powershell
cd backend
python train_recommender.py
```

### Add New 3D Models
1. Add .gltf files to `frontend/public/models/`
2. Update product records with ar_model path
3. Test in AR viewer

## 📈 Performance Tips

- **MongoDB:** Create indexes for better query performance
- **Frontend:** Enable React production build for deployment
- **Backend:** Use caching for frequently accessed data
- **AR Models:** Optimize GLTF files for faster loading

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- YOLOv5 by Ultralytics
- React.js community
- MongoDB team
- Google Model Viewer
- Tailwind CSS

---

**Happy Shopping with MarketGuru! 🛒✨** 
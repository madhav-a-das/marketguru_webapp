# Quick Start Guide - Enhanced Product Detection System

## Issues Resolved
- Fixed missing `seaborn` dependency
- Fixed Windows encoding issues  
- Created working startup scripts
- AI models download automatically when needed

## Prerequisites
1. **Python 3.8+** installed and in PATH
2. **Node.js 14+** installed and in PATH  
3. **MongoDB** - Download from: https://www.mongodb.com/try/download/community
4. **Chrome browser** for web scraping

## Quick Start (3 Steps)

### Step 1: Install MongoDB
Download and install MongoDB Community Edition
Windows: net start MongoDB

### Step 2: Start the System
EASIEST: Double-click start_all.bat
This will start both backend and frontend automatically

### Step 3: Open Browser
Go to: http://localhost:3000

## Features Available

### Camera Detection
1. Click "Camera Capture" tab
2. Allow camera permissions
3. Point camera at product
4. Click "Detect & Search Online"
5. Get real-time shopping results!

### Image Upload
1. Click "Upload Image" tab
2. Optionally enter search query
3. Choose image file
4. Get comprehensive shopping results!

## Access URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- MongoDB: mongodb://localhost:27017

## What's Working Now
- All Python dependencies installed
- AI models (YOLOv5, BLIP, EasyOCR) working
- Enhanced product detection system
- Real-time shopping search
- Modern React frontend
- Windows-compatible startup scripts

## Troubleshooting
- Camera not working: Check browser permissions
- Slow first run: AI models downloading (normal)
- No shopping results: Check internet connection
- MongoDB errors: Run net start MongoDB

Your Enhanced Product Detection System is Ready!
Just run start_all.bat and open http://localhost:3000 
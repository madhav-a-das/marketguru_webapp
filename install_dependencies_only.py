#!/usr/bin/env python3
"""
Simple dependency installer for Enhanced Product Detection System
Only installs required packages without downloading large AI models
"""

import subprocess
import sys
import os

def install_pip_package(package):
    """Install a single pip package"""
    try:
        print(f"Installing {package}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package}: {e}")
        return False

def main():
    print("Installing dependencies for Enhanced Product Detection System...")
    print("=" * 60)
    
    # Essential packages only
    packages = [
        "flask",
        "flask-cors", 
        "requests",
        "beautifulsoup4",
        "pymongo",
        "numpy",
        "pandas",
        "scikit-learn",
        "joblib",
        "pillow",
        "opencv-python",
        "aiohttp",
        "lxml",
        "seaborn",
        "matplotlib",
        "torch",
        "torchvision", 
        "ultralytics",
        "transformers",
        "easyocr",
        "selenium",
        "webdriver-manager"
    ]
    
    successful = 0
    total = len(packages)
    
    for package in packages:
        if install_pip_package(package):
            successful += 1
    
    print("\n" + "=" * 60)
    print(f"Installation complete: {successful}/{total} packages installed")
    
    if successful == total:
        print("✓ All dependencies installed successfully!")
    else:
        print("⚠ Some packages failed to install. The system may still work.")
    
    print("\nNext steps:")
    print("1. Install MongoDB from: https://www.mongodb.com/try/download/community")
    print("2. Start MongoDB: net start MongoDB")
    print("3. Run the backend: cd backend && python app.py")
    print("4. Run the frontend: cd frontend && npm start")
    print("5. Open: http://localhost:3000")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Enhanced Product Detection System Setup
Installs all dependencies and configures the system for optimal performance.
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors gracefully"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def install_python_dependencies():
    """Install Python backend dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    dependencies = [
        "torch torchvision",
        "ultralytics",
        "opencv-python",
        "scikit-learn",
        "pandas",
        "joblib",
        "requests",
        "beautifulsoup4",
        "pymongo",
        "numpy",
        "aiohttp",
        "lxml",
        "pillow",
        "easyocr",
        "transformers",
        "flask",
        "flask-cors"
    ]
    
    # Install Chrome driver dependencies for web scraping
    if platform.system() == "Windows":
        chrome_deps = ["selenium", "webdriver-manager"]
    else:
        chrome_deps = ["selenium", "webdriver-manager", "chromium-browser"]
    
    dependencies.extend(chrome_deps)
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"⚠️ Failed to install {dep}, but continuing...")

def setup_mongodb():
    """Setup MongoDB (instructions)"""
    print("\n🗄️ MongoDB Setup Instructions:")
    print("1. Install MongoDB Community Edition from: https://www.mongodb.com/try/download/community")
    print("2. Start MongoDB service:")
    
    if platform.system() == "Windows":
        print("   - Run: net start MongoDB")
    else:
        print("   - Run: sudo systemctl start mongod")
    
    print("3. MongoDB will be accessible at: mongodb://localhost:27017/")

def install_node_dependencies():
    """Install Node.js frontend dependencies"""
    print("\n🌐 Installing Node.js dependencies...")
    
    frontend_dir = "frontend"
    if os.path.exists(frontend_dir):
        os.chdir(frontend_dir)
        
        # Install dependencies
        run_command("npm install", "Installing frontend dependencies")
        
        # Install additional dependencies for enhanced features
        additional_deps = [
            "axios",
            "@tailwindcss/aspect-ratio",
            "@tailwindcss/forms"
        ]
        
        for dep in additional_deps:
            run_command(f"npm install {dep}", f"Installing {dep}")
        
        os.chdir("..")
    else:
        print("❌ Frontend directory not found!")

def create_model_artifacts_directory():
    """Create directory for ML model artifacts"""
    backend_dir = "backend"
    if os.path.exists(backend_dir):
        model_dir = os.path.join(backend_dir, "model_artifacts")
        os.makedirs(model_dir, exist_ok=True)
        print(f"✅ Created model artifacts directory: {model_dir}")

def download_initial_models():
    """Download required AI models"""
    print("\n🤖 Downloading AI models (this may take a few minutes)...")
    
    model_downloads = [
        "python -c \"import torch; torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)\"",
        "python -c \"from transformers import BlipProcessor, BlipForConditionalGeneration; BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base'); BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')\"",
        "python -c \"import easyocr; easyocr.Reader(['en'])\""
    ]
    
    for cmd in model_downloads:
        run_command(cmd, "Downloading AI models")

def create_startup_scripts():
    """Create convenient startup scripts"""
    print("\n📜 Creating startup scripts...")
    
    # Backend startup script
    backend_script = """#!/bin/bash
echo "🚀 Starting MarketGuru Backend..."
cd backend
python app.py
"""
    
    # Frontend startup script  
    frontend_script = """#!/bin/bash
echo "🌐 Starting MarketGuru Frontend..."
cd frontend
npm start
"""
    
    # Combined startup script
    combined_script = """#!/bin/bash
echo "🚀 Starting MarketGuru - Enhanced Product Detection System"
echo "Starting backend..."
cd backend && python app.py &
BACKEND_PID=$!

echo "Starting frontend..."
cd ../frontend && npm start &
FRONTEND_PID=$!

echo "✅ System started!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for interrupt
trap 'kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
"""
    
    with open("start_backend.sh", "w") as f:
        f.write(backend_script)
    
    with open("start_frontend.sh", "w") as f:
        f.write(frontend_script)
        
    with open("start_all.sh", "w") as f:
        f.write(combined_script)
    
    # Make scripts executable on Unix systems
    if platform.system() != "Windows":
        os.chmod("start_backend.sh", 0o755)
        os.chmod("start_frontend.sh", 0o755) 
        os.chmod("start_all.sh", 0o755)
    
    print("✅ Created startup scripts: start_backend.sh, start_frontend.sh, start_all.sh")

def print_final_instructions():
    """Print final setup instructions"""
    print("\n" + "="*60)
    print("🎉 ENHANCED PRODUCT DETECTION SYSTEM SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Start MongoDB service")
    print("2. Run the system:")
    
    if platform.system() == "Windows":
        print("   Backend: cd backend && python app.py")
        print("   Frontend: cd frontend && npm start")
    else:
        print("   All services: ./start_all.sh")
        print("   Or separately:")
        print("   Backend: ./start_backend.sh")
        print("   Frontend: ./start_frontend.sh")
    
    print("\n🌐 Access URLs:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:5000")
    
    print("\n✨ Features Available:")
    print("   📷 Camera product detection with online search")
    print("   📤 Image upload with AI-powered product recognition")
    print("   🛒 Real-time shopping results from Amazon, Flipkart, Google")
    print("   🔗 Direct purchase links and price comparisons")
    print("   🤖 Advanced AI with YOLO, BLIP, and OCR models")
    
    print("\n⚠️ Important Notes:")
    print("   - First run may take longer due to AI model downloads")
    print("   - Ensure stable internet connection for shopping search")
    print("   - Camera permissions required for detection")
    print("   - MongoDB must be running for full functionality")

def main():
    """Main setup function"""
    print("🚀 Enhanced Product Detection System Setup")
    print("==========================================")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    
    print(f"✅ Python {sys.version} detected")
    
    # Create directories
    create_model_artifacts_directory()
    
    # Install dependencies
    install_python_dependencies()
    install_node_dependencies()
    
    # Setup MongoDB (instructions only)
    setup_mongodb()
    
    # Download AI models
    download_initial_models()
    
    # Create startup scripts
    create_startup_scripts()
    
    # Final instructions
    print_final_instructions()

if __name__ == "__main__":
    main() 
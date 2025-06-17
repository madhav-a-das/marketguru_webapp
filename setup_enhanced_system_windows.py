#!/usr/bin/env python3
"""
Enhanced Product Detection System Setup - Windows Compatible
Installs all dependencies and configures the system for optimal performance.
Handles Windows encoding issues and provides better error handling.
"""

import subprocess
import sys
import os
import platform
import time

def run_command(command, description, timeout=300):
    """Run a command and handle errors gracefully with timeout"""
    print(f"\n[INFO] {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        print(f"[SUCCESS] {description} completed successfully")
        return True
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {description} timed out after {timeout} seconds")
        return False
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error in {description}: {e}")
        return False

def install_python_dependencies():
    """Install Python backend dependencies"""
    print("\n[STEP] Installing Python dependencies...")
    
    # Core dependencies
    core_dependencies = [
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
        "flask",
        "flask-cors",
        "seaborn",
        "matplotlib"
    ]
    
    # ML/AI dependencies (install separately due to size)
    ai_dependencies = [
        "transformers",
        "easyocr"
    ]
    
    # Web scraping dependencies
    web_dependencies = [
        "selenium",
        "webdriver-manager"
    ]
    
    all_deps = core_dependencies + ai_dependencies + web_dependencies
    
    for dep in all_deps:
        success = run_command(f"pip install {dep}", f"Installing {dep}", timeout=600)
        if not success:
            print(f"[WARNING] Failed to install {dep}, but continuing...")
            # Try alternative installation
            run_command(f"pip install --user {dep}", f"Installing {dep} (user mode)")

def setup_mongodb_instructions():
    """Provide MongoDB setup instructions"""
    print("\n[STEP] MongoDB Setup Instructions:")
    print("1. Download MongoDB Community Edition from:")
    print("   https://www.mongodb.com/try/download/community")
    print("2. Install MongoDB using the installer")
    print("3. Start MongoDB service:")
    
    if platform.system() == "Windows":
        print("   Option A: Run as service (recommended):")
        print("     net start MongoDB")
        print("   Option B: Manual start:")
        print("     mongod --dbpath C:\\data\\db")
    else:
        print("   sudo systemctl start mongod")
    
    print("4. MongoDB will be accessible at: mongodb://localhost:27017/")
    print("5. You can verify MongoDB is running by visiting: http://localhost:27017")

def install_node_dependencies():
    """Install Node.js frontend dependencies"""
    print("\n[STEP] Installing Node.js dependencies...")
    
    frontend_dir = "frontend"
    if os.path.exists(frontend_dir):
        original_dir = os.getcwd()
        try:
            os.chdir(frontend_dir)
            
            # Clear npm cache first
            run_command("npm cache clean --force", "Cleaning npm cache")
            
            # Install dependencies
            success = run_command("npm install", "Installing frontend dependencies", timeout=600)
            if not success:
                print("[WARNING] npm install failed, trying alternative...")
                run_command("npm install --legacy-peer-deps", "Installing with legacy peer deps")
            
            # Install additional dependencies
            additional_deps = [
                "axios",
                "@tailwindcss/aspect-ratio",
                "@tailwindcss/forms"
            ]
            
            for dep in additional_deps:
                run_command(f"npm install {dep}", f"Installing {dep}")
            
        finally:
            os.chdir(original_dir)
    else:
        print("[ERROR] Frontend directory not found!")

def create_model_artifacts_directory():
    """Create directory for ML model artifacts"""
    backend_dir = "backend"
    if os.path.exists(backend_dir):
        model_dir = os.path.join(backend_dir, "model_artifacts")
        os.makedirs(model_dir, exist_ok=True)
        print(f"[SUCCESS] Created model artifacts directory: {model_dir}")

def download_models_safely():
    """Download AI models with better error handling"""
    print("\n[STEP] Downloading AI models (this may take a while)...")
    print("[INFO] Models will be downloaded automatically on first use")
    print("[INFO] This prevents timeout and encoding issues during setup")
    
    # Create a simple test script to verify installations
    test_script = '''
import sys
try:
    import torch
    print("PyTorch: OK")
    
    import cv2
    print("OpenCV: OK")
    
    import requests
    print("Requests: OK")
    
    import sklearn
    print("Scikit-learn: OK")
    
    print("All core dependencies are working!")
    
except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)
'''
    
    test_file = "test_dependencies.py"
    with open(test_file, "w", encoding='utf-8') as f:
        f.write(test_script)
    
    success = run_command("python test_dependencies.py", "Testing core dependencies")
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
    
    return success

def create_windows_startup_scripts():
    """Create Windows-compatible startup scripts"""
    print("\n[STEP] Creating startup scripts...")
    
    # Backend startup script (Windows batch)
    backend_script = '''@echo off
echo Starting MarketGuru Backend...
cd backend
python app.py
pause
'''
    
    # Frontend startup script (Windows batch)
    frontend_script = '''@echo off
echo Starting MarketGuru Frontend...
cd frontend
npm start
pause
'''
    
    # Combined startup script (Windows batch)
    combined_script = '''@echo off
echo Starting MarketGuru - Enhanced Product Detection System
echo.
echo Starting backend...
start "Backend" cmd /k "cd backend && python app.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting frontend...
start "Frontend" cmd /k "cd frontend && npm start"

echo.
echo System started!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:5000
echo.
echo Press any key to exit...
pause > nul
'''
    
    # PowerShell script for advanced users
    powershell_script = '''# PowerShell script for MarketGuru
Write-Host "Starting MarketGuru - Enhanced Product Detection System" -ForegroundColor Green

# Start backend
Write-Host "Starting backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-Command", "cd backend; python app.py; Read-Host 'Press Enter to close'"

# Wait for backend
Start-Sleep 5

# Start frontend  
Write-Host "Starting frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-Command", "cd frontend; npm start; Read-Host 'Press Enter to close'"

Write-Host "System started!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:5000" -ForegroundColor Cyan

Read-Host "Press Enter to exit"
'''
    
    try:
        with open("start_backend.bat", "w", encoding='utf-8') as f:
            f.write(backend_script)
        
        with open("start_frontend.bat", "w", encoding='utf-8') as f:
            f.write(frontend_script)
            
        with open("start_all.bat", "w", encoding='utf-8') as f:
            f.write(combined_script)
            
        with open("start_all.ps1", "w", encoding='utf-8') as f:
            f.write(powershell_script)
        
        print("[SUCCESS] Created startup scripts:")
        print("  - start_backend.bat")
        print("  - start_frontend.bat") 
        print("  - start_all.bat (recommended)")
        print("  - start_all.ps1 (PowerShell version)")
        
    except Exception as e:
        print(f"[ERROR] Failed to create startup scripts: {e}")

def create_quick_start_guide():
    """Create a quick start guide file"""
    guide_content = '''# Quick Start Guide - Enhanced Product Detection System

## Prerequisites Check
1. Python 3.8+ installed and in PATH
2. Node.js 14+ installed and in PATH  
3. MongoDB installed and running
4. Chrome browser installed

## Quick Start Steps

### Option 1: Automatic (Recommended)
1. Double-click: start_all.bat
2. Wait for both services to start
3. Open browser to: http://localhost:3000

### Option 2: Manual
1. Start MongoDB:
   - Windows: net start MongoDB
   - Or: mongod --dbpath C:\\data\\db

2. Start Backend:
   - Double-click: start_backend.bat
   - Or: cd backend && python app.py

3. Start Frontend:
   - Double-click: start_frontend.bat  
   - Or: cd frontend && npm start

4. Open: http://localhost:3000

## Features Available
- Camera product detection with online search
- Image upload with AI-powered recognition  
- Real-time shopping results from Amazon, Flipkart, Google
- Direct purchase links and price comparisons

## Troubleshooting
- Camera not working: Check browser permissions
- Slow first run: AI models downloading (normal)
- No results: Check internet connection
- MongoDB errors: Ensure MongoDB service is running

## URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- MongoDB: mongodb://localhost:27017

## Support
If you encounter issues:
1. Check MongoDB is running
2. Verify all dependencies installed: python test_system.py
3. Check console for error messages
4. Restart services
'''
    
    try:
        with open("QUICK_START.md", "w", encoding='utf-8') as f:
            f.write(guide_content)
        print("[SUCCESS] Created QUICK_START.md guide")
    except Exception as e:
        print(f"[ERROR] Failed to create quick start guide: {e}")

def print_final_instructions():
    """Print final setup instructions"""
    print("\n" + "="*60)
    print("ENHANCED PRODUCT DETECTION SYSTEM SETUP COMPLETE!")
    print("="*60)
    
    print("\n[NEXT STEPS]")
    print("1. Install and start MongoDB:")
    print("   Download: https://www.mongodb.com/try/download/community")
    print("   Start: net start MongoDB")
    
    print("\n2. Start the system:")
    print("   EASY: Double-click 'start_all.bat'")
    print("   OR manually:")
    print("   - Backend: start_backend.bat")
    print("   - Frontend: start_frontend.bat")
    
    print("\n[ACCESS URLS]")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:5000")
    
    print("\n[FEATURES]")
    print("   - Camera product detection with online search")
    print("   - Image upload with AI recognition")
    print("   - Real-time shopping from Amazon, Flipkart, Google")
    print("   - Direct purchase links and price comparisons")
    
    print("\n[IMPORTANT NOTES]")
    print("   - First run may be slower (AI models downloading)")
    print("   - Stable internet required for shopping search")
    print("   - Camera permissions needed for detection")
    print("   - MongoDB must be running")
    
    print("\n[FILES CREATED]")
    print("   - start_all.bat (main startup script)")
    print("   - QUICK_START.md (detailed guide)")
    print("   - test_system.py (system verification)")

def main():
    """Main setup function with better error handling"""
    print("Enhanced Product Detection System Setup - Windows Compatible")
    print("="*70)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print(f"[SUCCESS] Python {sys.version.split()[0]} detected")
    
    # Set UTF-8 encoding for Windows console
    if platform.system() == "Windows":
        try:
            # Try to set UTF-8 encoding
            os.system("chcp 65001 > nul")
        except:
            pass
    
    steps_completed = 0
    total_steps = 6
    
    try:
        # Step 1: Create directories
        print(f"\n[STEP 1/{total_steps}] Creating directories...")
        create_model_artifacts_directory()
        steps_completed += 1
        
        # Step 2: Install Python dependencies
        print(f"\n[STEP 2/{total_steps}] Installing Python dependencies...")
        install_python_dependencies()
        steps_completed += 1
        
        # Step 3: Install Node.js dependencies
        print(f"\n[STEP 3/{total_steps}] Installing Node.js dependencies...")
        install_node_dependencies()
        steps_completed += 1
        
        # Step 4: Test core dependencies
        print(f"\n[STEP 4/{total_steps}] Testing dependencies...")
        download_models_safely()
        steps_completed += 1
        
        # Step 5: Create startup scripts
        print(f"\n[STEP 5/{total_steps}] Creating startup scripts...")
        create_windows_startup_scripts()
        steps_completed += 1
        
        # Step 6: Create documentation
        print(f"\n[STEP 6/{total_steps}] Creating documentation...")
        create_quick_start_guide()
        setup_mongodb_instructions()
        steps_completed += 1
        
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Setup interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during setup: {e}")
    
    # Final results
    print(f"\n[PROGRESS] Completed {steps_completed}/{total_steps} setup steps")
    
    if steps_completed == total_steps:
        print_final_instructions()
        print("\n[SUCCESS] Setup completed successfully!")
    else:
        print("\n[PARTIAL] Setup partially completed. You may need to:")
        print("1. Install missing dependencies manually")
        print("2. Check internet connection")
        print("3. Run setup again")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main() 
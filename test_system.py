#!/usr/bin/env python3
"""
Test script for Enhanced Product Detection System
Verifies that all components are working correctly.
"""

import requests
import time
import sys
import json
from PIL import Image
import io
import base64

def test_backend_connection():
    """Test if backend server is running"""
    try:
        response = requests.get('http://localhost:5000/api/products', timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            return True
        else:
            print(f"❌ Backend server returned status {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Backend server is not running")
        return False
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        return False

def test_product_search():
    """Test direct product search functionality"""
    try:
        search_data = {"query": "iPhone 15"}
        response = requests.post(
            'http://localhost:5000/api/search-product',
            json=search_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and len(data.get('results', {}).get('search_results', [])) > 0:
                print("✅ Product search is working")
                print(f"   Found {len(data['results']['search_results'])} results for iPhone 15")
                return True
            else:
                print("❌ Product search returned no results")
                return False
        else:
            print(f"❌ Product search failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing product search: {e}")
        return False

def create_test_image():
    """Create a simple test image"""
    # Create a simple colored rectangle as test image
    img = Image.new('RGB', (300, 200), color='blue')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_enhanced_detection():
    """Test enhanced detection with a simple image"""
    try:
        test_img = create_test_image()
        
        files = {'image': ('test.png', test_img, 'image/png')}
        response = requests.post(
            'http://localhost:5000/api/enhanced-detect',
            files=files,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Enhanced detection API is working")
                results = data.get('results', {})
                if results.get('yolo_detections'):
                    print(f"   YOLO detected {len(results['yolo_detections'])} objects")
                if results.get('image_caption'):
                    print(f"   Image caption: {results['image_caption'][:50]}...")
                return True
            else:
                print("❌ Enhanced detection failed")
                return False
        else:
            print(f"❌ Enhanced detection API failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing enhanced detection: {e}")
        return False

def test_upload_search():
    """Test upload search functionality"""
    try:
        test_img = create_test_image()
        
        files = {'image': ('test.png', test_img, 'image/png')}
        data = {'search_query': 'smartphone'}
        
        response = requests.post(
            'http://localhost:5000/api/upload-search',
            files=files,
            data=data,
            timeout=60
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('success'):
                print("✅ Upload search API is working")
                results = response_data.get('results', {})
                if results.get('search_results'):
                    print(f"   Found {len(results['search_results'])} search results")
                return True
            else:
                print("❌ Upload search failed")
                return False
        else:
            print(f"❌ Upload search API failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing upload search: {e}")
        return False

def check_ai_models():
    """Check if AI models can be loaded"""
    try:
        import torch
        print("✅ PyTorch is available")
        
        # Test YOLO model
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        print("✅ YOLOv5 model loaded successfully")
        
        # Test BLIP model
        from transformers import BlipProcessor, BlipForConditionalGeneration
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        print("✅ BLIP model loaded successfully")
        
        # Test EasyOCR
        import easyocr
        reader = easyocr.Reader(['en'])
        print("✅ EasyOCR initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading AI models: {e}")
        return False

def test_frontend_connection():
    """Test if frontend is accessible"""
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend returned status {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Frontend is not running (expected if not started)")
        return False
    except Exception as e:
        print(f"❌ Error connecting to frontend: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Enhanced Product Detection System")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: AI Models
    print("\n1. Testing AI Models...")
    if check_ai_models():
        tests_passed += 1
    total_tests += 1
    
    # Test 2: Backend Connection
    print("\n2. Testing Backend Connection...")
    if test_backend_connection():
        tests_passed += 1
    total_tests += 1
    
    # Test 3: Product Search
    print("\n3. Testing Product Search...")
    if test_product_search():
        tests_passed += 1
    total_tests += 1
    
    # Test 4: Enhanced Detection
    print("\n4. Testing Enhanced Detection...")
    if test_enhanced_detection():
        tests_passed += 1
    total_tests += 1
    
    # Test 5: Upload Search
    print("\n5. Testing Upload Search...")
    if test_upload_search():
        tests_passed += 1
    total_tests += 1
    
    # Test 6: Frontend Connection
    print("\n6. Testing Frontend Connection...")
    if test_frontend_connection():
        tests_passed += 1
    total_tests += 1
    
    # Results
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! System is working correctly.")
        return 0
    elif tests_passed >= total_tests - 1:
        print("✅ System is mostly working. Minor issues detected.")
        return 0
    else:
        print("❌ System has significant issues. Please check the setup.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
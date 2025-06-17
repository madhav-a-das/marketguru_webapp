import torch
from PIL import Image
import io   
import base64
import easyocr
import re
from transformers import BlipProcessor, BlipForConditionalGeneration
import numpy as np
import requests
import json
from product_search import ProductSearchEngine

class EnhancedProductDetector:
    def __init__(self):
        # Check for GPU availability
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"🚀 Using device: {self.device}")
        if torch.cuda.is_available():
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        
        # Initialize YOLO model with GPU support
        self.yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        self.yolo_model.to(self.device)
        
        # Initialize BLIP model for image captioning with GPU support
        try:
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            if torch.cuda.is_available():
                self.blip_model = self.blip_model.to(self.device)
                print("✅ BLIP model loaded on GPU")
        except Exception as e:
            print(f"Error loading BLIP model: {e}")
            self.blip_processor = None
            self.blip_model = None
        
        # Initialize OCR reader
        try:
            self.ocr_reader = easyocr.Reader(['en'])
        except Exception as e:
            print(f"Error initializing OCR: {e}")
            self.ocr_reader = None
            
        # Initialize product search engine
        self.search_engine = ProductSearchEngine()
        
        # Common product categories and keywords
        self.product_categories = {
            'electronics': ['phone', 'smartphone', 'laptop', 'computer', 'tablet', 'camera', 'headphones', 'speaker', 'watch', 'smartwatch', 'tv', 'monitor'],
            'clothing': ['shirt', 't-shirt', 'dress', 'pants', 'jeans', 'jacket', 'coat', 'shoes', 'sneakers', 'boots', 'hat', 'cap'],
            'home': ['chair', 'table', 'sofa', 'bed', 'lamp', 'cushion', 'pillow', 'curtain', 'rug', 'vase', 'clock'],
            'kitchen': ['bottle', 'cup', 'mug', 'plate', 'bowl', 'spoon', 'fork', 'knife', 'pot', 'pan'],
            'sports': ['ball', 'football', 'basketball', 'tennis', 'racket', 'bike', 'bicycle', 'weights', 'dumbbells'],
            'books': ['book', 'notebook', 'journal', 'magazine', 'newspaper'],
            'toys': ['toy', 'doll', 'car', 'truck', 'puzzle', 'game'],
            'beauty': ['perfume', 'lipstick', 'makeup', 'brush', 'mirror', 'cream', 'lotion']
        }

    def detect_with_yolo(self, image_bytes):
        """Basic YOLO detection"""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            results = self.yolo_model(img)
            detections = results.pandas().xyxy[0].to_dict(orient="records")
            return detections
        except Exception as e:
            print(f"YOLO detection error: {e}")
            return []

    def generate_image_caption(self, image_bytes):
        """Generate descriptive caption using BLIP model with GPU acceleration"""
        try:
            if not self.blip_processor or not self.blip_model:
                return ""
                
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            inputs = self.blip_processor(img, return_tensors="pt")
            
            # Move inputs to GPU if available
            if torch.cuda.is_available():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():  # Save GPU memory during inference
                out = self.blip_model.generate(**inputs, max_length=50)
            
            caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
            
            return caption
        except Exception as e:
            print(f"Caption generation error: {e}")
            return ""

    def extract_text_from_image(self, image_bytes):
        """Extract text using OCR"""
        try:
            if not self.ocr_reader:
                return []
                
            img = Image.open(io.BytesIO(image_bytes))
            img_array = np.array(img)
            
            results = self.ocr_reader.readtext(img_array)
            texts = [result[1] for result in results if result[2] > 0.5]  # Confidence > 0.5
            
            return texts
        except Exception as e:
            print(f"OCR error: {e}")
            return []

    def analyze_and_identify_products(self, image_bytes):
        """Comprehensive product analysis using multiple AI techniques"""
        try:
            # 1. YOLO Detection
            yolo_detections = self.detect_with_yolo(image_bytes)
            
            # 2. Image Caption Generation
            caption = self.generate_image_caption(image_bytes)
            
            # 3. OCR Text Extraction
            extracted_texts = self.extract_text_from_image(image_bytes)
            
            # 4. Combine all information to identify products
            identified_products = self.combine_detection_results(
                yolo_detections, caption, extracted_texts
            )
            
            # 5. Search for each identified product online
            enhanced_results = []
            for product in identified_products:
                search_results = self.search_engine.search_all_platforms(
                    product['name'], max_results_per_platform=2
                )
                
                enhanced_results.append({
                    'detected_name': product['name'],
                    'confidence': product['confidence'],
                    'category': product['category'],
                    'detection_method': product['detection_method'],
                    'search_results': search_results,
                    'total_found': len(search_results)
                })
            
            return {
                'yolo_detections': yolo_detections,
                'image_caption': caption,
                'extracted_text': extracted_texts,
                'identified_products': enhanced_results,
                'analysis_summary': self.generate_analysis_summary(enhanced_results)
            }
            
        except Exception as e:
            print(f"Product analysis error: {e}")
            return {
                'error': str(e),
                'yolo_detections': [],
                'image_caption': '',
                'extracted_text': [],
                'identified_products': []
            }

    def combine_detection_results(self, yolo_detections, caption, extracted_texts):
        """Intelligently combine detection results from multiple sources"""
        identified_products = []
        seen_products = set()
        
        # Process YOLO detections
        for detection in yolo_detections:
            product_name = detection.get('name', '').lower()
            confidence = detection.get('confidence', 0)
            
            if confidence > 0.3 and product_name not in seen_products:
                category = self.categorize_product(product_name)
                enhanced_name = self.enhance_product_name(product_name, extracted_texts)
                
                identified_products.append({
                    'name': enhanced_name,
                    'confidence': confidence,
                    'category': category,
                    'detection_method': 'YOLO'
                })
                seen_products.add(product_name)
        
        # Process caption for additional products
        if caption:
            caption_products = self.extract_products_from_caption(caption)
            for product in caption_products:
                if product.lower() not in seen_products:
                    category = self.categorize_product(product)
                    enhanced_name = self.enhance_product_name(product, extracted_texts)
                    
                    identified_products.append({
                        'name': enhanced_name,
                        'confidence': 0.7,  # Medium confidence for caption-based detection
                        'category': category,
                        'detection_method': 'Image Caption'
                    })
                    seen_products.add(product.lower())
        
        # Process OCR text for brand names and product details
        brand_info = self.extract_brand_info(extracted_texts)
        if brand_info:
            # Enhance existing products with brand information
            for product in identified_products:
                if brand_info['brand']:
                    product['name'] = f"{brand_info['brand']} {product['name']}"
                if brand_info['model']:
                    product['name'] = f"{product['name']} {brand_info['model']}"
        
        return identified_products

    def enhance_product_name(self, base_name, extracted_texts):
        """Enhance product name with information from OCR text"""
        enhanced_name = base_name
        
        # Look for brand names, model numbers, etc. in OCR text
        for text in extracted_texts:
            text_words = text.split()
            for word in text_words:
                # Check if word looks like a model number or important identifier
                if re.match(r'^[A-Z0-9]{2,}$', word) and len(word) <= 10:
                    if word.lower() not in enhanced_name.lower():
                        enhanced_name += f" {word}"
                        
        return enhanced_name.strip()

    def extract_products_from_caption(self, caption):
        """Extract potential product names from image caption"""
        products = []
        caption_words = caption.lower().split()
        
        # Check against known product categories
        for category, keywords in self.product_categories.items():
            for keyword in keywords:
                if keyword in caption_words:
                    products.append(keyword)
                    
        return list(set(products))  # Remove duplicates

    def categorize_product(self, product_name):
        """Categorize product based on name"""
        product_name = product_name.lower()
        
        for category, keywords in self.product_categories.items():
            for keyword in keywords:
                if keyword in product_name:
                    return category
                    
        return 'general'

    def extract_brand_info(self, extracted_texts):
        """Extract brand and model information from OCR text"""
        brand_info = {'brand': '', 'model': ''}
        
        # Common brand patterns
        known_brands = [
            'apple', 'samsung', 'sony', 'lg', 'nike', 'adidas', 'canon', 'nikon',
            'hp', 'dell', 'lenovo', 'asus', 'acer', 'microsoft', 'google', 'amazon',
            'xiaomi', 'oppo', 'vivo', 'oneplus', 'huawei', 'realme', 'nokia'
        ]
        
        for text in extracted_texts:
            text_lower = text.lower()
            
            # Check for known brands
            for brand in known_brands:
                if brand in text_lower:
                    brand_info['brand'] = brand.title()
                    break
            
            # Look for model numbers (alphanumeric patterns)
            model_match = re.search(r'\b[A-Z0-9]{3,10}\b', text.upper())
            if model_match and not brand_info['model']:
                brand_info['model'] = model_match.group()
                
        return brand_info

    def generate_analysis_summary(self, enhanced_results):
        """Generate a summary of the analysis"""
        if not enhanced_results:
            return "No products detected in the image."
        
        total_products = len(enhanced_results)
        total_search_results = sum(result['total_found'] for result in enhanced_results)
        
        product_names = [result['detected_name'] for result in enhanced_results]
        
        summary = f"Detected {total_products} product(s): {', '.join(product_names)}. "
        summary += f"Found {total_search_results} online shopping results across multiple platforms."
        
        return summary

    def search_uploaded_image(self, image_bytes, search_query=None):
        """Search for products in uploaded image with optional search query"""
        try:
            if search_query:
                # Direct search with user-provided query
                search_results = self.search_engine.search_all_platforms(search_query, max_results_per_platform=3)
                return {
                    'search_query': search_query,
                    'search_results': search_results,
                    'total_found': len(search_results),
                    'analysis_summary': f"Found {len(search_results)} results for '{search_query}'"
                }
            else:
                # Analyze image and search for detected products
                return self.analyze_and_identify_products(image_bytes)
                
        except Exception as e:
            return {
                'error': str(e),
                'search_results': [],
                'total_found': 0
            } 
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json

class ProductSearchEngine:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
    def setup_driver(self):
        """Setup Chrome driver for dynamic content scraping"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
            return driver
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            return None

    def search_amazon_products(self, product_name, max_results=5):
        """Search Amazon for products and return detailed info"""
        try:
            query = urllib.parse.quote_plus(product_name)
            url = f"https://www.amazon.in/s?k={query}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            products = []
            search_results = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            for result in search_results[:max_results]:
                try:
                    # Extract product title - try multiple selectors
                    title = "N/A"
                    title_selectors = [
                        'span.a-size-medium.a-color-base.a-text-normal',
                        'span.a-size-base-plus.a-color-base.a-text-normal',
                        'h2.a-size-mini span',
                        'h2 span.a-color-base',
                        '[data-cy="title-recipe-label"]',
                        'h2 a span'
                    ]
                    
                    for selector in title_selectors:
                        title_elem = result.select_one(selector)
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            break
                    
                    # Extract price - try multiple selectors
                    price = "N/A"
                    price_selectors = [
                        'span.a-price-whole',
                        'span.a-offscreen',
                        '.a-price .a-offscreen',
                        '.a-price-range .a-offscreen'
                    ]
                    
                    for selector in price_selectors:
                        price_elem = result.select_one(selector)
                        if price_elem:
                            price = price_elem.get_text(strip=True)
                            break
                    
                    # Extract image
                    img_elem = result.find('img')
                    image_url = ""
                    if img_elem:
                        image_url = img_elem.get('src') or img_elem.get('data-src') or ""
                    
                    # Extract product link - try multiple selectors
                    product_link = ""
                    link_selectors = [
                        'h2 a',
                        'a.a-link-normal',
                        '.s-link-style a'
                    ]
                    
                    for selector in link_selectors:
                        link_elem = result.select_one(selector)
                        if link_elem and link_elem.get('href'):
                            href = link_elem.get('href')
                            product_link = f"https://www.amazon.in{href}" if href.startswith('/') else href
                            break
                    
                    # Extract rating
                    rating = "N/A"
                    rating_elem = result.find('span', class_='a-icon-alt')
                    if rating_elem:
                        rating_text = rating_elem.get_text()
                        rating = rating_text.split()[0] if rating_text else "N/A"
                    
                    # Extract number of reviews
                    reviews = "N/A"
                    reviews_elem = result.find('span', class_='a-size-base')
                    if reviews_elem:
                        reviews = reviews_elem.get_text()
                    
                    # Add product if we have at least a title or image
                    if title != "N/A" or image_url:
                        products.append({
                            'title': title if title != "N/A" else "Amazon Product",
                            'price': price,
                            'image_url': image_url,
                            'product_link': product_link,
                            'rating': rating,
                            'reviews': reviews,
                            'retailer': 'Amazon India'
                        })
                        
                except Exception as e:
                    print(f"Error processing Amazon result: {e}")
                    continue
                    
            return products
            
        except Exception as e:
            print(f"Error searching Amazon: {e}")
            return []

    def search_flipkart_products(self, product_name, max_results=5):
        """Search Flipkart for products and return detailed info"""
        try:
            query = urllib.parse.quote_plus(product_name)
            url = f"https://www.flipkart.com/search?q={query}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            products = []
            
            # Multiple selectors as Flipkart changes structure frequently
            product_containers = soup.find_all('div', class_='_1AtVbE') or soup.find_all('div', class_='_13oc-S')
            
            for container in product_containers[:max_results]:
                try:
                    # Extract title
                    title_elem = container.find('div', class_='_4rR01T') or container.find('a', class_='s1Q9rs')
                    title = title_elem.get_text(strip=True) if title_elem else "N/A"
                    
                    # Extract price
                    price_elem = container.find('div', class_='_30jeq3') or container.find('div', class_='_25b18c')
                    price = price_elem.get_text(strip=True) if price_elem else "N/A"
                    
                    # Extract image
                    img_elem = container.find('img', class_='_396cs4')
                    image_url = img_elem.get('src') if img_elem else ""
                    
                    # Extract product link
                    link_elem = container.find('a', class_='_1fQZEK') or container.find('a', class_='s1Q9rs')
                    product_link = f"https://www.flipkart.com{link_elem.get('href')}" if link_elem else ""
                    
                    # Extract rating
                    rating_elem = container.find('div', class_='_3LWZlK')
                    rating = rating_elem.get_text() if rating_elem else "N/A"
                    
                    if title != "N/A" and image_url:
                        products.append({
                            'title': title,
                            'price': price,
                            'image_url': image_url,
                            'product_link': product_link,
                            'rating': rating,
                            'reviews': "N/A",
                            'retailer': 'Flipkart'
                        })
                        
                except Exception as e:
                    continue
                    
            return products
            
        except Exception as e:
            print(f"Error searching Flipkart: {e}")
            return []

    def search_google_shopping(self, product_name, max_results=5):
        """Search Google Shopping for products"""
        try:
            driver = self.setup_driver()
            if not driver:
                return []
                
            query = urllib.parse.quote_plus(product_name)
            url = f"https://www.google.com/search?q={query}&tbm=shop"
            
            driver.get(url)
            time.sleep(3)
            
            products = []
            product_elements = driver.find_elements(By.CSS_SELECTOR, '.sh-dgr__content')
            
            for element in product_elements[:max_results]:
                try:
                    # Extract title
                    title_elem = element.find_element(By.CSS_SELECTOR, '.Xjkr3b')
                    title = title_elem.text if title_elem else "N/A"
                    
                    # Extract price
                    price_elem = element.find_element(By.CSS_SELECTOR, '.a8Pemb')
                    price = price_elem.text if price_elem else "N/A"
                    
                    # Extract image
                    img_elem = element.find_element(By.CSS_SELECTOR, '.ArOc1c img')
                    image_url = img_elem.get_attribute('src') if img_elem else ""
                    
                    # Extract link
                    link_elem = element.find_element(By.CSS_SELECTOR, 'a')
                    product_link = link_elem.get_attribute('href') if link_elem else ""
                    
                    if title != "N/A" and image_url:
                        products.append({
                            'title': title,
                            'price': price,
                            'image_url': image_url,
                            'product_link': product_link,
                            'rating': "N/A",
                            'reviews': "N/A",
                            'retailer': 'Google Shopping'
                        })
                        
                except Exception as e:
                    continue
            
            driver.quit()
            return products
            
        except Exception as e:
            print(f"Error searching Google Shopping: {e}")
            return []

    def search_all_platforms(self, product_name, max_results_per_platform=3):
        """Search all platforms and combine results"""
        all_products = []
        
        # Search Amazon
        amazon_products = self.search_amazon_products(product_name, max_results_per_platform)
        all_products.extend(amazon_products)
        
        # Search Flipkart  
        flipkart_products = self.search_flipkart_products(product_name, max_results_per_platform)
        all_products.extend(flipkart_products)
        
        # Search Google Shopping
        google_products = self.search_google_shopping(product_name, max_results_per_platform)
        all_products.extend(google_products)
        
        # Remove duplicates based on title similarity
        unique_products = self.remove_duplicates(all_products)
        
        return unique_products

    def remove_duplicates(self, products):
        """Remove duplicate products based on title similarity"""
        unique_products = []
        seen_titles = set()
        
        for product in products:
            # Create a normalized title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', product['title'].lower())
            title_words = set(normalized_title.split())
            
            # Check if this product is too similar to any we've already seen
            is_duplicate = False
            for seen_title in seen_titles:
                seen_words = set(seen_title.split())
                # If more than 60% of words match, consider it a duplicate
                if len(title_words.intersection(seen_words)) / max(len(title_words), 1) > 0.6:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_products.append(product)
                seen_titles.add(normalized_title)
                
        return unique_products

    def get_product_details_from_url(self, url):
        """Extract detailed product information from a product URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {
                'description': '',
                'specifications': {},
                'additional_images': []
            }
            
            # Extract based on the domain
            if 'amazon' in url:
                # Amazon-specific extraction
                desc_elem = soup.find('div', {'id': 'feature-bullets'})
                if desc_elem:
                    details['description'] = desc_elem.get_text(strip=True)
                    
                # Extract additional images
                img_elements = soup.find_all('img', class_='a-dynamic-image')
                for img in img_elements[:5]:  # Limit to 5 images
                    img_url = img.get('src')
                    if img_url and img_url not in details['additional_images']:
                        details['additional_images'].append(img_url)
                        
            elif 'flipkart' in url:
                # Flipkart-specific extraction
                desc_elem = soup.find('div', class_='_1mXcCf')
                if desc_elem:
                    details['description'] = desc_elem.get_text(strip=True)
                    
            return details
            
        except Exception as e:
            print(f"Error extracting product details: {e}")
            return {} 
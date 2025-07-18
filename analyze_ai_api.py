#!/usr/bin/env python3
"""
Script untuk menganalisis struktur data yang diterima AI API
dan menyesuaikan dengan data yang dikirim dari frontend
"""
import requests
import json
from pprint import pprint

# Test URLs
SCRAPER_URL = "http://localhost:8000"
AI_URL = "http://localhost:8001"

# Test product URL
TEST_PRODUCT_URL = "https://www.tokopedia.com/huawei/huawei-matepad-11-5-s-papermatte-edition-tablet-8-256gb-nearlink-accessories-gopaint-pc-level-wps-space-grey-94e22/review"

def get_scraper_data():
    """Get actual data from scraper"""
    print("=== Getting Scraper Data ===")
    
    try:
        response = requests.post(f"{SCRAPER_URL}/scrape-with-details", 
                               json={
                                   "url": TEST_PRODUCT_URL,
                                   "target_ratings": [5],
                                   "max_reviews_per_rating": 5,
                                   "headless": True
                               },
                               timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            product_details = data.get("product_details", {})
            
            print("✅ Scraper data received:")
            print("📊 Product details keys:", list(product_details.keys()))
            
            # Show actual values
            print("\n=== Actual Product Details ===")
            for key, value in product_details.items():
                print(f"{key}: {value}")
            
            return product_details
        else:
            print(f"❌ Scraper error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting scraper data: {e}")
        return None

def test_ai_with_actual_data(product_data):
    """Test AI API with actual scraper data"""
    print("\n=== Testing AI API with Actual Data ===")
    
    if not product_data:
        print("❌ No product data to test")
        return
    
    # Map data exactly as frontend does
    request_data = {
        "product_data": {
            "name": product_data.get("product_name", "Tidak tersedia"),
            "price": product_data.get("price", "Tidak tersedia"),
            "rating": product_data.get("rating", 0),
            "total_ratings": product_data.get("rating_count", 0),
            "sold_count": product_data.get("sold_count", "Tidak tersedia"),
            "store_type": product_data.get("store_name", "Tidak tersedia"),
            "store_rating": product_data.get("store_rating", 0),
            "store_reviews": product_data.get("store_reviews", 0),
            "processing_time": product_data.get("processing_time", "Tidak tersedia"),
            "description": product_data.get("description", "Tidak tersedia"),
            "url": product_data.get("product_url", product_data.get("review_url", ""))
        }
    }
    
    print("📤 Request data for AI:")
    pprint(request_data)
    
    try:
        response = requests.post(f"{AI_URL}/ai-consultant", 
                               json=request_data,
                               timeout=30)
        
        print(f"📥 AI response status: {response.status_code}")
        
        if response.status_code == 200:
            ai_result = response.json()
            print("✅ AI analysis successful!")
            print("📊 AI response keys:", list(ai_result.keys()))
            print("🎯 Recommendation:", ai_result.get("recommendation"))
            print("📊 Confidence:", ai_result.get("confidence_score"))
            return True
        else:
            print(f"❌ AI error: {response.status_code}")
            error_text = response.text
            print("📊 Error response:", error_text)
            
            # Try to parse error details
            try:
                error_data = response.json()
                print("📊 Error details:", error_data)
            except:
                print("📊 Raw error text:", error_text)
            return False
            
    except Exception as e:
        print(f"❌ Error testing AI: {e}")
        return False

def analyze_ai_api_structure():
    """Analyze what AI API expects"""
    print("\n=== Analyzing AI API Structure ===")
    
    # Test with minimal data
    minimal_data = {
        "product_data": {
            "name": "Test Product",
            "price": "Rp 1.000.000",
            "rating": 4.5,
            "total_ratings": 100,
            "sold_count": "10+ terjual",
            "store_type": "Test Store",
            "store_rating": 4.8,
            "store_reviews": 500,
            "processing_time": "1-2 hari",
            "description": "Test description",
            "url": "https://example.com"
        }
    }
    
    print("📤 Testing with minimal data:")
    pprint(minimal_data)
    
    try:
        response = requests.post(f"{AI_URL}/ai-consultant", 
                               json=minimal_data,
                               timeout=30)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Minimal data works!")
            result = response.json()
            print("📊 Response keys:", list(result.keys()))
        else:
            print(f"❌ Minimal data failed: {response.status_code}")
            print("📊 Error:", response.text)
            
    except Exception as e:
        print(f"❌ Error with minimal data: {e}")

def check_ai_api_health():
    """Check if AI API is running"""
    print("\n=== Checking AI API Health ===")
    
    try:
        # Try different endpoints
        endpoints = [
            f"{AI_URL}/",
            f"{AI_URL}/health",
            f"{AI_URL}/docs"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                print(f"✅ {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
                
    except Exception as e:
        print(f"❌ AI API health check failed: {e}")

def main():
    """Main function"""
    print("🔍 Analyzing AI API Data Structure...")
    print("=" * 60)
    
    # Check AI API health
    check_ai_api_health()
    
    # Get actual scraper data
    product_data = get_scraper_data()
    
    # Test AI with actual data
    if product_data:
        test_ai_with_actual_data(product_data)
    
    # Analyze AI API structure
    analyze_ai_api_structure()

if __name__ == "__main__":
    main()

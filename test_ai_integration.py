#!/usr/bin/env python3
"""
Complete test script for the AI API integration
"""
import requests
import json
from pprint import pprint
import time

# Configuration
SCRAPER_URL = "http://localhost:8000"
AI_URL = "http://localhost:8001"
TEST_PRODUCT_URL = "https://www.tokopedia.com/huawei/huawei-matepad-11-5-s-papermatte-edition-tablet-8-256gb-nearlink-accessories-gopaint-pc-level-wps-space-grey-94e22/review"

def test_ai_health():
    """Test AI API health"""
    print("=== Testing AI API Health ===")
    try:
        response = requests.get(f"{AI_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ AI API is healthy")
            print(f"📊 Status: {data.get('status')}")
            print(f"📊 Gemini API: {data.get('gemini_api')}")
            return True
        else:
            print(f"❌ AI API unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach AI API: {e}")
        return False

def get_test_product_data():
    """Get product data from scraper"""
    print("\n=== Getting Test Product Data ===")
    try:
        response = requests.post(f"{SCRAPER_URL}/scrape-with-details", 
                               json={
                                   "url": TEST_PRODUCT_URL,
                                   "target_ratings": [5],
                                   "max_reviews_per_rating": 3,
                                   "headless": True
                               },
                               timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            product_details = data.get("product_details", {})
            print("✅ Product data retrieved")
            print(f"📊 Product: {product_details.get('product_name', 'Unknown')}")
            print(f"📊 Price: {product_details.get('price', 'Unknown')}")
            print(f"📊 Rating: {product_details.get('rating', 'Unknown')}")
            return product_details
        else:
            print(f"❌ Failed to get product data: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting product data: {e}")
        return None

def test_ai_debug_endpoint(product_data):
    """Test AI debug endpoint"""
    print("\n=== Testing AI Debug Endpoint ===")
    
    if not product_data:
        print("❌ No product data to test")
        return False
    
    # Prepare request data exactly like frontend
    request_data = {
        "product_data": {
            "name": product_data.get("product_name", "Tidak tersedia"),
            "price": product_data.get("price", "Tidak tersedia"),
            "rating": str(product_data.get("rating", 0)),
            "total_ratings": str(product_data.get("rating_count", 0)),
            "sold_count": product_data.get("sold_count", "Tidak tersedia"),
            "store_type": product_data.get("store_name", "Tidak tersedia"),
            "store_rating": str(product_data.get("store_rating", 0)),
            "store_reviews": str(product_data.get("store_reviews", 0)),
            "processing_time": product_data.get("processing_time", "Tidak tersedia"),
            "description": product_data.get("description", "Tidak tersedia"),
            "url": product_data.get("product_url", product_data.get("review_url", ""))
        },
        "user_budget": 8000000,
        "user_preferences": "Tablet untuk produktivitas dan kreativitas"
    }
    
    try:
        response = requests.post(f"{AI_URL}/debug-request", 
                               json=request_data,
                               timeout=30)
        
        if response.status_code == 200:
            debug_data = response.json()
            print("✅ Debug endpoint works")
            print("📊 Request data validated successfully")
            return True
        else:
            print(f"❌ Debug endpoint failed: {response.status_code}")
            print(f"📊 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing debug endpoint: {e}")
        return False

def test_ai_consultation(product_data):
    """Test full AI consultation"""
    print("\n=== Testing AI Consultation ===")
    
    if not product_data:
        print("❌ No product data to test")
        return False
    
    # Prepare request data exactly like frontend
    request_data = {
        "product_data": {
            "name": product_data.get("product_name", "Tidak tersedia"),
            "price": product_data.get("price", "Tidak tersedia"),
            "rating": str(product_data.get("rating", 0)),
            "total_ratings": str(product_data.get("rating_count", 0)),
            "sold_count": product_data.get("sold_count", "Tidak tersedia"),
            "store_type": product_data.get("store_name", "Tidak tersedia"),
            "store_rating": str(product_data.get("store_rating", 0)),
            "store_reviews": str(product_data.get("store_reviews", 0)),
            "processing_time": product_data.get("processing_time", "Tidak tersedia"),
            "description": product_data.get("description", "Tidak tersedia"),
            "url": product_data.get("product_url", product_data.get("review_url", ""))
        },
        "user_budget": 8000000,
        "user_preferences": "Tablet untuk produktivitas dan kreativitas"
    }
    
    print("📤 Sending consultation request...")
    print("📊 Request data:")
    pprint(request_data)
    
    try:
        response = requests.post(f"{AI_URL}/ai-consultant", 
                               json=request_data,
                               timeout=60)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            ai_result = response.json()
            print("✅ AI consultation successful!")
            print(f"📊 Recommendation: {ai_result.get('recommendation')}")
            print(f"📊 Confidence: {ai_result.get('confidence_score')}")
            print(f"📊 Analysis: {ai_result.get('analysis', '')[:200]}...")
            print(f"📊 Pros: {len(ai_result.get('pros', []))} items")
            print(f"📊 Cons: {len(ai_result.get('cons', []))} items")
            return True
        else:
            print(f"❌ AI consultation failed: {response.status_code}")
            print(f"📊 Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during AI consultation: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 Complete AI API Integration Test")
    print("=" * 60)
    
    # Test AI API health
    if not test_ai_health():
        print("\n❌ AI API is not healthy. Please check:")
        print("1. AI API server is running: python ai_consultant_api.py")
        print("2. .env file exists with GEMINI_API_KEY")
        print("3. Gemini API key is valid")
        return
    
    # Get product data
    product_data = get_test_product_data()
    if not product_data:
        print("\n❌ Cannot get product data. Please check:")
        print("1. Scraper API is running: python tokopedia_scraper_api.py")
        print("2. Network connection is working")
        return
    
    # Test debug endpoint
    if not test_ai_debug_endpoint(product_data):
        print("\n❌ Debug endpoint failed")
        return
    
    # Test full AI consultation
    if not test_ai_consultation(product_data):
        print("\n❌ AI consultation failed")
        return
    
    print("\n✅ All tests passed!")
    print("🎉 The AI API integration is working correctly!")
    print("\nYou can now test the frontend at: http://localhost:3000")

if __name__ == "__main__":
    main()

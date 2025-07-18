#!/usr/bin/env python3
"""
Test script to verify data mapping between scraper and AI consultant
"""
import requests
import json
from pprint import pprint

# Test URLs
SCRAPER_URL = "http://localhost:8000"
AI_URL = "http://localhost:8001"

# Test product URL (using a simple Tokopedia product)
TEST_PRODUCT_URL = "https://www.tokopedia.com/huawei-official/huawei-matepad-11-5s-8gb-256gb-original-garansi-resmi-1-tahun"

def test_scraper_response():
    """Test the scraper API response format"""
    print("=== Testing Scraper API ===")
    try:
        response = requests.post(f"{SCRAPER_URL}/scrape-with-details", 
                               json={
                                   "url": TEST_PRODUCT_URL,
                                   "target_ratings": [1, 2, 3, 4, 5],
                                   "max_reviews_per_rating": 15,
                                   "headless": False
                               })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Scraper API working!")
            print("Response keys:", list(data.keys()))
            
            if "product_details" in data:
                product_details = data["product_details"]
                print("Product details keys:", list(product_details.keys()))
                
                # Show the structure we'll use for AI consultant
                print("\n=== Product Details Structure ===")
                important_fields = [
                    "product_name", "price", "rating", "rating_count", 
                    "sold_count", "store_name", "store_rating", 
                    "store_reviews", "description", "product_url", "review_url"
                ]
                
                for field in important_fields:
                    value = product_details.get(field, "NOT FOUND")
                    print(f"{field}: {value}")
                
                return product_details
            else:
                print("❌ No product_details in response")
                print("Available keys:", list(data.keys()))
                return None
        else:
            print(f"❌ Scraper API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing scraper: {e}")
        return None

def test_ai_mapping(product_data):
    """Test the AI consultant with properly mapped data"""
    print("\n=== Testing AI Consultant Mapping ===")
    try:
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
        
        print("Mapped data for AI consultant:")
        pprint(request_data)
        
        response = requests.post(f"{AI_URL}/ai-consultant", json=request_data)
        
        if response.status_code == 200:
            ai_result = response.json()
            print("✅ AI Consultant working!")
            print("AI Response keys:", list(ai_result.keys()))
            print("Recommendation:", ai_result.get("recommendation"))
            print("Confidence:", ai_result.get("confidence_score"))
            return True
        else:
            print(f"❌ AI Consultant error: {response.status_code}")
            print("Response:", response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error testing AI consultant: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 Testing Data Mapping Fix...")
    print("=" * 50)
    
    # Test scraper first
    product_data = test_scraper_response()
    
    if product_data:
        # Test AI consultant mapping
        ai_success = test_ai_mapping(product_data)
        
        if ai_success:
            print("\n✅ All tests passed! Data mapping is correct.")
        else:
            print("\n❌ AI consultant test failed.")
    else:
        print("\n❌ Scraper test failed.")

if __name__ == "__main__":
    main()

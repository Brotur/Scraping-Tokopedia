#!/usr/bin/env python3
"""
Debug script to check the actual response structure from the scraper API
"""
import requests
import json
from pprint import pprint

# Test URLs
SCRAPER_URL = "http://localhost:8000"
TEST_PRODUCT_URL = "https://www.tokopedia.com/huawei-official/huawei-matepad-11-5s-8gb-256gb-original-garansi-resmi-1-tahun"

def debug_scraper_response():
    """Debug the actual scraper response structure"""
    print("=== DEBUGGING SCRAPER RESPONSE ===")
    
    try:
        print(f"Making request to: {SCRAPER_URL}/scrape-with-details")
        print(f"With URL: {TEST_PRODUCT_URL}")
        
        response = requests.post(f"{SCRAPER_URL}/scrape-with-details", 
                               json={
                                   "url": TEST_PRODUCT_URL,
                                   "target_ratings": [1, 2, 3, 4, 5],
                                   "max_reviews_per_rating": 5,  # Smaller number for testing
                                   "headless": True
                               })
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print("\n=== TOP LEVEL KEYS ===")
            print(list(data.keys()))
            
            if "product_details" in data:
                print("\n=== PRODUCT DETAILS KEYS ===")
                product_details = data["product_details"]
                print(list(product_details.keys()))
                
                print("\n=== PRODUCT DETAILS VALUES ===")
                for key, value in product_details.items():
                    print(f"{key}: {value}")
                
                # Test the exact mapping that frontend will use
                print("\n=== FRONTEND MAPPING TEST ===")
                mapped_data = {
                    "name": product_details.get("product_name", "NOT FOUND"),
                    "price": product_details.get("price", "NOT FOUND"),
                    "rating": product_details.get("rating", "NOT FOUND"),
                    "total_ratings": product_details.get("rating_count", "NOT FOUND"),
                    "sold_count": product_details.get("sold_count", "NOT FOUND"),
                    "store_type": product_details.get("store_name", "NOT FOUND"),
                    "store_rating": product_details.get("store_rating", "NOT FOUND"),
                    "store_reviews": product_details.get("store_reviews", "NOT FOUND"),
                    "description": product_details.get("description", "NOT FOUND"),
                    "url": product_details.get("product_url", product_details.get("review_url", "NOT FOUND"))
                }
                
                print("Mapped data for AI consultant:")
                for key, value in mapped_data.items():
                    print(f"  {key}: {value}")
                
                # Check for missing fields
                missing_fields = [k for k, v in mapped_data.items() if v == "NOT FOUND"]
                if missing_fields:
                    print(f"\n❌ Missing fields: {missing_fields}")
                else:
                    print("\n✅ All fields found!")
                
                return product_details
            else:
                print("❌ No product_details in response")
                print("Full response:")
                pprint(data)
                return None
        else:
            print(f"❌ Error: {response.status_code}")
            print("Response text:", response.text)
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_scraper_response()

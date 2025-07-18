#!/usr/bin/env python3
"""
Simple test script to check if servers are running and responding
"""
import requests
import json
import time

def test_server_health():
    """Test if servers are running"""
    print("=== Testing Server Health ===")
    
    # Test scraper API
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        print("✅ Scraper API server is running")
        print(f"   Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Scraper API server is NOT running")
        return False
    except Exception as e:
        print(f"⚠️ Scraper API server issue: {e}")
        return False
    
    # Test AI API
    try:
        response = requests.get("http://localhost:8001", timeout=5)
        print("✅ AI API server is running")
        print(f"   Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ AI API server is NOT running")
        return False
    except Exception as e:
        print(f"⚠️ AI API server issue: {e}")
        return False
    
    return True

def test_scraper_simple():
    """Test simple scraper endpoint"""
    print("\n=== Testing Simple Scraper ===")
    
    # Use a simpler product URL
    simple_url = "https://www.tokopedia.com/toko-komputer/laptop-gaming-asus-tuf-15-i5-12450h-rtx4050-6gb-512gb-ssd-win11-original"
    
    try:
        print(f"📤 Testing with URL: {simple_url}")
        
        response = requests.post("http://localhost:8000/scrape-with-details", 
                               json={
                                   "url": simple_url,
                                   "target_ratings": [5],
                                   "max_reviews_per_rating": 5,
                                   "headless": True
                               },
                               timeout=60)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Simple test passed")
            print("📊 Response keys:", list(data.keys()))
            
            if "product_details" in data:
                pd = data["product_details"]
                print("📊 Product name:", pd.get("product_name", "NOT FOUND"))
                print("📊 Price:", pd.get("price", "NOT FOUND"))
                print("📊 Rating:", pd.get("rating", "NOT FOUND"))
                print("📊 Rating count:", pd.get("rating_count", "NOT FOUND"))
                print("📊 Store name:", pd.get("store_name", "NOT FOUND"))
                return True
            else:
                print("❌ No product_details in response")
                return False
            
        else:
            print(f"❌ Simple test failed: {response.status_code}")
            print("📊 Response text:", response.text[:500])
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return False
    except Exception as e:
        print(f"❌ Simple test error: {e}")
        return False

def test_frontend_api_config():
    """Test frontend API configuration"""
    print("\n=== Testing Frontend API Config ===")
    
    # Check if frontend can reach API
    try:
        # Test CORS
        response = requests.options("http://localhost:8000/scrape-with-details", 
                                  headers={
                                      "Origin": "http://localhost:3000",
                                      "Access-Control-Request-Method": "POST",
                                      "Access-Control-Request-Headers": "Content-Type"
                                  })
        
        print(f"📥 CORS preflight status: {response.status_code}")
        print(f"📥 CORS headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ CORS configured correctly")
            return True
        else:
            print("⚠️ CORS might have issues")
            return False
            
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 Testing System Health...")
    print("=" * 60)
    
    # Test server health
    if not test_server_health():
        print("\n❌ Server health check failed. Please start the servers:")
        print("   1. python tokopedia_scraper_api.py")
        print("   2. python ai_consultant_api.py")
        return
    
    # Test scraper functionality
    if not test_scraper_simple():
        print("\n❌ Scraper test failed")
        return
    
    # Test CORS for frontend
    if not test_frontend_api_config():
        print("\n⚠️ Frontend API config might have issues")
    
    print("\n✅ All basic tests passed!")
    print("🎉 You can now test the frontend at: http://localhost:3000")

if __name__ == "__main__":
    main()

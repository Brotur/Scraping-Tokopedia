#!/usr/bin/env python3
"""
Test AI Consultant dengan struktur data lengkap seperti yang diberikan user
"""

import json
import requests
import time
from datetime import datetime

# Sample data structure seperti yang diberikan user
SAMPLE_DATA = {
    "product_details": {
        "product_name": "HUAWEI MatePad 11.5\"S PaperMatte Edition Tablet [8+256GB] | NearLink Accessories | GoPaint | PC Level WPS - Space Grey",
        "store_name": "Huawei Indonesia",
        "product_url": "https://www.tokopedia.com/huawei/huawei-matepad-11-5-s-papermatte-edition-tablet-8-256gb-nearlink-accessories-gopaint-pc-level-wps-space-grey-94e22",
        "review_url": "https://www.tokopedia.com/huawei/huawei-matepad-11-5-s-papermatte-edition-tablet-8-256gb-nearlink-accessories-gopaint-pc-level-wps-space-grey-94e22/review",
        "scraped_at": "2025-07-18T16:28:23.086006",
        "price": "Rp6.999.000",
        "rating": "4.9",
        "rating_count": "(1.066 rating)",
        "sold_count": "Terjual 2 rb+",
        "description": "HUAWEI MatePad 11.5\"S PaperMatte Edition Tablet [8+256GB] | NearLink Accessories | GoPaint | PC Level WPS"
    },
    "reviews": [
        {
            "rating": 5,
            "reviewer_name": "Dimas",
            "reviewer_name_normalized": "Dimas",
            "review_text": "Barang sesuai pesanan, dapat bonus Mpencil dan keyboard sesuai di foto, pengiriman cepat, berfungsi dengan baik, desain keren dan fitur sangat keren, tab terbaik dengan harga yg oke. dapat diskon lumayan waktu 10.10, mantap",
            "review_text_normalized": "barang sesuai pesanan dapat bonus mpencil dan keyboard sesuai di foto pengiriman cepat berfungsi dengan baik desain keren dan fitur sangat keren tab terbaik dengan harga yg oke dapat diskon lumayan waktu mantap",
            "review_date": "9 bulan lalu",
            "review_date_normalized": "9 bulan lalu",
            "variant": "Violet",
            "variant_normalized": "Violet",
            "rating_filter": 5,
            "scraped_at": "2025-07-18 16:34:35"
        },
        {
            "rating": 1,
            "reviewer_name": "iqwan",
            "reviewer_name_normalized": "iqwan",
            "review_text": "Pengiriman sangat lama. Walaupun diluar pihak penjual, tetapi ini mempengaruhi pelayanan terjadap konsumen, sehingga saya merasa kurang puas belanja disini. Meskipun barang bagus.",
            "review_text_normalized": "pengiriman sangat lama walaupun diluar pihak penjual tetapi ini mempengaruhi pelayanan terjadap konsumen sehingga saya merasa kurang puas belanja disini meskipun barang bagus",
            "review_date": "9 bulan lalu",
            "review_date_normalized": "9 bulan lalu",
            "variant": "Space Grey",
            "variant_normalized": "Space Grey",
            "rating_filter": 1,
            "scraped_at": "2025-07-18 16:29:15"
        }
    ],
    "summary": {
        "total_reviews_scraped": 62,
        "target_ratings": [1, 2, 3, 4, 5],
        "max_reviews_per_rating": 15,
        "scraped_at": "2025-07-18T16:35:37.971693"
    }
}

def test_ai_consultant_flexible():
    """Test AI consultant dengan format baru yang fleksibel"""
    print("🧪 Testing AI Consultant dengan struktur data lengkap...")
    
    # URL API
    ai_api_url = "http://localhost:8001/ai-consultant-flexible"
    
    # Prepare request data
    request_data = {
        "product_details": SAMPLE_DATA["product_details"],
        "reviews": SAMPLE_DATA["reviews"],
        "summary": SAMPLE_DATA["summary"],
        "user_budget": 7000000,  # 7 juta rupiah
        "user_preferences": "Tablet untuk drawing dan produktivitas"
    }
    
    print(f"📤 Sending request to {ai_api_url}")
    print(f"📊 Product: {request_data['product_details']['product_name']}")
    print(f"📊 Reviews: {len(request_data['reviews'])} reviews")
    print(f"💰 Budget: Rp {request_data['user_budget']:,}")
    print(f"📝 Preferences: {request_data['user_preferences']}")
    
    try:
        # Send request
        response = requests.post(
            ai_api_url,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI Analysis Result:")
            print(f"   🎯 Recommendation: {result['recommendation']}")
            print(f"   📊 Confidence: {result['confidence_score']:.2f}")
            print(f"   📝 Analysis: {result['analysis'][:200]}...")
            print(f"   ✅ Pros: {len(result['pros'])} items")
            print(f"   ❌ Cons: {len(result['cons'])} items")
            print(f"   💡 Insights: {len(result['key_insights'])} items")
            
            if result.get('budget_analysis'):
                print(f"   💰 Budget Analysis: {result['budget_analysis'][:100]}...")
            
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"❌ Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - AI API tidak berjalan di port 8001")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_ai_consultant_old_format():
    """Test AI consultant dengan format lama untuk kompatibilitas"""
    print("\n🧪 Testing AI Consultant dengan format lama...")
    
    # URL API
    ai_api_url = "http://localhost:8001/ai-consultant-flexible"
    
    # Convert to old format
    product_details = SAMPLE_DATA["product_details"]
    request_data = {
        "product_data": {
            "name": product_details["product_name"],
            "price": product_details["price"],
            "rating": product_details["rating"],
            "total_ratings": product_details["rating_count"],
            "sold_count": product_details["sold_count"],
            "store_type": product_details["store_name"],
            "store_rating": "4.5",
            "store_reviews": "1000",
            "processing_time": "1-2 hari",
            "description": product_details["description"],
            "url": product_details["product_url"]
        },
        "user_budget": 7000000,
        "user_preferences": "Tablet untuk drawing dan produktivitas"
    }
    
    print(f"📤 Sending request to {ai_api_url}")
    print(f"📊 Product: {request_data['product_data']['name']}")
    print(f"💰 Budget: Rp {request_data['user_budget']:,}")
    
    try:
        # Send request
        response = requests.post(
            ai_api_url,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI Analysis Result (Old Format):")
            print(f"   🎯 Recommendation: {result['recommendation']}")
            print(f"   📊 Confidence: {result['confidence_score']:.2f}")
            print(f"   📝 Analysis: {result['analysis'][:200]}...")
            
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health_check():
    """Test health check endpoint"""
    print("\n🧪 Testing Health Check...")
    
    try:
        response = requests.get("http://localhost:8001/health", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health Check: {result['status']}")
            print(f"   🤖 Gemini API: {result['gemini_api']}")
            print(f"   🔧 Model: {result['model']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing AI Consultant API dengan berbagai format data")
    print("=" * 60)
    
    # Test health check first
    health_ok = test_health_check()
    
    if not health_ok:
        print("❌ Health check failed - stopping tests")
        return
    
    # Test new format with reviews
    test1_ok = test_ai_consultant_flexible()
    
    # Test old format for compatibility
    test2_ok = test_ai_consultant_old_format()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   🏥 Health Check: {'✅' if health_ok else '❌'}")
    print(f"   🆕 New Format: {'✅' if test1_ok else '❌'}")
    print(f"   🔄 Old Format: {'✅' if test2_ok else '❌'}")
    
    if test1_ok and test2_ok:
        print("\n🎉 All tests passed! AI Consultant dapat menangani kedua format data.")
    else:
        print("\n⚠️  Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()

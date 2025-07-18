"""
Test script untuk AI Shopping Consultant
Menguji berbagai skenario rekomendasi dengan contoh produk Tokopedia
"""

import requests
import json
import time
from typing import Dict, Any

# API Configuration
SCRAPER_API_URL = "http://localhost:8000"
AI_API_URL = "http://localhost:8001"

def test_api_connection():
    """Test koneksi ke kedua API"""
    print("🔍 Testing API connections...")
    
    try:
        # Test scraper API
        response = requests.get(f"{SCRAPER_API_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Scraper API connected")
        else:
            print(f"❌ Scraper API error: {response.status_code}")
    except Exception as e:
        print(f"❌ Scraper API connection failed: {e}")
    
    try:
        # Test AI API
        response = requests.get(f"{AI_API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ AI API connected")
        else:
            print(f"❌ AI API error: {response.status_code}")
    except Exception as e:
        print(f"❌ AI API connection failed: {e}")

def get_product_details(url: str) -> Dict[str, Any]:
    """Ekstrak detail produk dari URL Tokopedia"""
    try:
        response = requests.post(
            f"{SCRAPER_API_URL}/product-details",
            json={"url": url},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data["product_details"]
        
        raise Exception(f"Failed to extract product details: {response.text}")
        
    except Exception as e:
        print(f"❌ Error extracting product details: {e}")
        return {}

def get_ai_consultation(product_data: Dict[str, Any], budget: float = None, preferences: str = None) -> Dict[str, Any]:
    """Mendapatkan konsultasi AI untuk produk"""
    try:
        request_data = {
            "product_data": {
                "name": product_data.get("name", "Unknown Product"),
                "price": product_data.get("price", "Unknown"),
                "rating": product_data.get("rating"),
                "total_ratings": product_data.get("total_ratings"),
                "sold_count": product_data.get("sold_count"),
                "store_type": product_data.get("store_type"),
                "store_rating": product_data.get("store_rating"),
                "store_reviews": product_data.get("store_reviews"),
                "processing_time": product_data.get("processing_time"),
                "description": product_data.get("description"),
                "url": product_data.get("url", "")
            }
        }
        
        if budget:
            request_data["user_budget"] = budget
        if preferences:
            request_data["user_preferences"] = preferences
        
        response = requests.post(
            f"{AI_API_URL}/ai-consultant",
            json=request_data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        
        raise Exception(f"AI consultation failed: {response.text}")
        
    except Exception as e:
        print(f"❌ Error getting AI consultation: {e}")
        return {}

def print_analysis_result(product_data: Dict[str, Any], ai_result: Dict[str, Any]):
    """Print hasil analisis dengan format yang rapi"""
    print("\n" + "="*60)
    print("📦 HASIL ANALISIS PRODUK")
    print("="*60)
    
    # Product Info
    print(f"📝 Nama: {product_data.get('name', 'N/A')}")
    print(f"💰 Harga: {product_data.get('price', 'N/A')}")
    print(f"⭐ Rating: {product_data.get('rating', 'N/A')}")
    print(f"👥 Jumlah Rating: {product_data.get('total_ratings', 'N/A')}")
    print(f"🛒 Terjual: {product_data.get('sold_count', 'N/A')}")
    print(f"🏪 Toko: {product_data.get('store_type', 'N/A')}")
    
    if ai_result:
        print("\n" + "-"*40)
        print("🤖 REKOMENDASI AI")
        print("-"*40)
        
        # Recommendation
        recommendation = ai_result.get("recommendation", "N/A")
        confidence = ai_result.get("confidence_score", 0) * 100
        
        if recommendation == "LAYAK_BELI":
            emoji = "✅"
        elif recommendation == "TIDAK_LAYAK_BELI":
            emoji = "❌"
        else:
            emoji = "⚠️"
        
        print(f"{emoji} Rekomendasi: {recommendation}")
        print(f"🎯 Confidence: {confidence:.1f}%")
        print(f"📋 Analisis: {ai_result.get('analysis', 'N/A')}")
        
        # Pros
        print(f"\n✅ Keunggulan:")
        for pro in ai_result.get("pros", []):
            print(f"   • {pro}")
        
        # Cons
        print(f"\n❌ Kekurangan:")
        for con in ai_result.get("cons", []):
            print(f"   • {con}")
        
        # Key Insights
        print(f"\n💡 Insight Penting:")
        for insight in ai_result.get("key_insights", []):
            print(f"   • {insight}")
        
        # Budget Analysis
        if ai_result.get("budget_analysis"):
            print(f"\n💳 Analisis Budget: {ai_result['budget_analysis']}")

def test_case_layak_beli():
    """Test case untuk produk yang diharapkan LAYAK_BELI"""
    print("\n🧪 TEST CASE 1: LAYAK_BELI")
    print("Testing dengan produk yang memiliki rating tinggi dan toko terpercaya...")
    
    # Contoh URL produk populer (ganti dengan URL aktual)
    test_url = "https://www.tokopedia.com/xiaomiofficial/xiaomi-redmi-note-12-pro-5g-8-256gb-garansi-resmi"
    
    product_data = get_product_details(test_url)
    if product_data:
        ai_result = get_ai_consultation(
            product_data, 
            budget=3000000,  # 3 juta
            preferences="Brand terkenal, garansi resmi"
        )
        print_analysis_result(product_data, ai_result)
    else:
        print("❌ Gagal mengambil data produk untuk test case 1")

def test_case_tidak_layak_beli():
    """Test case untuk produk yang diharapkan TIDAK_LAYAK_BELI"""
    print("\n🧪 TEST CASE 2: TIDAK_LAYAK_BELI")
    print("Testing dengan produk yang memiliki rating rendah atau toko tidak terpercaya...")
    
    # Simulasi data produk dengan rating rendah
    mock_product_data = {
        "name": "Smartphone Murah No Brand",
        "price": "Rp 500.000",
        "rating": "3.2",
        "total_ratings": "15",
        "sold_count": "3",
        "store_type": "Power Merchant",
        "store_rating": "3.5",
        "store_reviews": "25",
        "processing_time": "2-3 hari",
        "description": "Smartphone murah dengan spesifikasi standar",
        "url": "https://www.tokopedia.com/example"
    }
    
    ai_result = get_ai_consultation(
        mock_product_data,
        budget=1000000,  # 1 juta
        preferences="Kualitas bagus, tahan lama"
    )
    print_analysis_result(mock_product_data, ai_result)

def test_case_layak_beli_dengan_catatan():
    """Test case untuk produk yang diharapkan LAYAK_BELI_DENGAN_CATATAN"""
    print("\n🧪 TEST CASE 3: LAYAK_BELI_DENGAN_CATATAN")
    print("Testing dengan produk yang memiliki rating sedang dengan pertimbangan khusus...")
    
    # Simulasi data produk dengan rating sedang
    mock_product_data = {
        "name": "Laptop Gaming Menengah",
        "price": "Rp 8.500.000",
        "rating": "4.2",
        "total_ratings": "87",
        "sold_count": "156",
        "store_type": "Official Store",
        "store_rating": "4.6",
        "store_reviews": "1,250",
        "processing_time": "1-2 hari",
        "description": "Laptop gaming dengan performa menengah, cocok untuk gaming casual dan kerja",
        "url": "https://www.tokopedia.com/example"
    }
    
    ai_result = get_ai_consultation(
        mock_product_data,
        budget=10000000,  # 10 juta
        preferences="Gaming, editing video, budget terbatas"
    )
    print_analysis_result(mock_product_data, ai_result)

def test_budget_analysis():
    """Test analisis budget dengan berbagai skenario"""
    print("\n🧪 TEST CASE 4: BUDGET ANALYSIS")
    print("Testing analisis budget dengan berbagai skenario...")
    
    mock_product_data = {
        "name": "iPhone 15 Pro Max 256GB",
        "price": "Rp 22.999.000",
        "rating": "4.9",
        "total_ratings": "1,245",
        "sold_count": "3,567",
        "store_type": "Official Store",
        "store_rating": "4.9",
        "store_reviews": "45,678",
        "processing_time": "1 hari",
        "description": "iPhone terbaru dengan fitur Pro Max",
        "url": "https://www.tokopedia.com/example"
    }
    
    # Test dengan budget pas
    print("\n--- Budget Pas ---")
    ai_result = get_ai_consultation(
        mock_product_data,
        budget=23000000,  # 23 juta (pas)
        preferences="Premium, brand terkenal"
    )
    if ai_result.get("budget_analysis"):
        print(f"💳 Budget Analysis: {ai_result['budget_analysis']}")
    
    # Test dengan budget kurang
    print("\n--- Budget Kurang ---")
    ai_result = get_ai_consultation(
        mock_product_data,
        budget=15000000,  # 15 juta (kurang)
        preferences="Premium, brand terkenal"
    )
    if ai_result.get("budget_analysis"):
        print(f"💳 Budget Analysis: {ai_result['budget_analysis']}")

def run_all_tests():
    """Jalankan semua test cases"""
    print("🚀 MEMULAI TEST AI SHOPPING CONSULTANT")
    print("="*60)
    
    # Test koneksi API
    test_api_connection()
    
    # Test cases
    test_case_layak_beli()
    time.sleep(2)  # Delay antar test
    
    test_case_tidak_layak_beli()
    time.sleep(2)
    
    test_case_layak_beli_dengan_catatan()
    time.sleep(2)
    
    test_budget_analysis()
    
    print("\n" + "="*60)
    print("✅ SEMUA TEST SELESAI")
    print("="*60)

if __name__ == "__main__":
    print("🤖 AI Shopping Consultant - Test Suite")
    print("Pastikan kedua API berjalan:")
    print("- Scraper API: http://localhost:8000")
    print("- AI API: http://localhost:8001")
    print("\nTekan Enter untuk melanjutkan...")
    input()
    
    run_all_tests()

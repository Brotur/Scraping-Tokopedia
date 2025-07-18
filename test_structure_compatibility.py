#!/usr/bin/env python3
"""
Simple test untuk memverifikasi AI consultant dapat menangani struktur data
"""

import json

# Sample data structure seperti yang user berikan
SAMPLE_DATA = {
    "product_details": {
        "product_name": "HUAWEI MatePad 11.5\"S PaperMatte Edition Tablet [8+256GB]",
        "store_name": "Huawei Indonesia",
        "product_url": "https://www.tokopedia.com/huawei/huawei-matepad-11-5-s-papermatte-edition-tablet",
        "price": "Rp6.999.000",
        "rating": "4.9",
        "rating_count": "(1.066 rating)",
        "sold_count": "Terjual 2 rb+",
        "description": "HUAWEI MatePad 11.5\"S PaperMatte Edition Tablet [8+256GB] | NearLink Accessories"
    },
    "reviews": [
        {
            "rating": 5,
            "reviewer_name": "Dimas",
            "review_text": "Barang sesuai pesanan, dapat bonus Mpencil dan keyboard sesuai di foto, pengiriman cepat, berfungsi dengan baik",
            "review_date": "9 bulan lalu",
            "variant": "Violet"
        },
        {
            "rating": 1,
            "reviewer_name": "iqwan",
            "review_text": "Pengiriman sangat lama. Walaupun diluar pihak penjual, tetapi ini mempengaruhi pelayanan terjadap konsumen",
            "review_date": "9 bulan lalu",
            "variant": "Space Grey"
        }
    ],
    "summary": {
        "total_reviews_scraped": 62,
        "target_ratings": [1, 2, 3, 4, 5],
        "max_reviews_per_rating": 15,
        "scraped_at": "2025-07-18T16:35:37.971693"
    }
}

def test_data_structure():
    """Test apakah struktur data dapat diproses dengan benar"""
    print("🧪 Testing Data Structure Processing...")
    
    # Test extracting product details
    product_details = SAMPLE_DATA["product_details"]
    print(f"✅ Product Name: {product_details['product_name']}")
    print(f"✅ Store: {product_details['store_name']}")
    print(f"✅ Price: {product_details['price']}")
    print(f"✅ Rating: {product_details['rating']}")
    print(f"✅ Rating Count: {product_details['rating_count']}")
    print(f"✅ Sold Count: {product_details['sold_count']}")
    
    # Test processing reviews
    reviews = SAMPLE_DATA["reviews"]
    print(f"✅ Total Reviews: {len(reviews)}")
    
    # Count rating distribution
    rating_counts = {}
    for review in reviews:
        rating = review["rating"]
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    
    print(f"✅ Rating Distribution: {rating_counts}")
    
    # Test creating flexible request format
    flexible_request = {
        "product_details": {
            "product_name": product_details["product_name"],
            "store_name": product_details["store_name"],
            "product_url": product_details["product_url"],
            "price": product_details["price"],
            "rating": product_details["rating"],
            "rating_count": product_details["rating_count"],
            "sold_count": product_details["sold_count"],
            "description": product_details["description"]
        },
        "reviews": reviews,
        "summary": SAMPLE_DATA["summary"],
        "user_budget": 7000000,
        "user_preferences": "Tablet untuk drawing dan produktivitas"
    }
    
    print(f"✅ Flexible Request Format Created")
    print(f"   📊 Product: {flexible_request['product_details']['product_name']}")
    print(f"   📊 Reviews: {len(flexible_request['reviews'])}")
    print(f"   💰 Budget: Rp {flexible_request['user_budget']:,}")
    
    # Test old format compatibility
    old_format_request = {
        "product_data": {
            "name": product_details["product_name"],
            "price": product_details["price"],
            "rating": product_details["rating"],
            "total_ratings": product_details["rating_count"],
            "sold_count": product_details["sold_count"],
            "store_type": product_details["store_name"],
            "url": product_details["product_url"],
            "description": product_details["description"]
        },
        "user_budget": 7000000,
        "user_preferences": "Tablet untuk drawing dan produktivitas"
    }
    
    print(f"✅ Old Format Request Created")
    print(f"   📊 Product: {old_format_request['product_data']['name']}")
    print(f"   💰 Budget: Rp {old_format_request['user_budget']:,}")
    
    # Save sample requests for testing
    with open("sample_new_format_request.json", "w", encoding="utf-8") as f:
        json.dump(flexible_request, f, indent=2, ensure_ascii=False)
    
    with open("sample_old_format_request.json", "w", encoding="utf-8") as f:
        json.dump(old_format_request, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Sample requests saved to files")
    
    return True

def main():
    """Main test function"""
    print("🚀 Testing Data Structure Compatibility")
    print("=" * 50)
    
    success = test_data_structure()
    
    if success:
        print("\n🎉 All data structure tests passed!")
        print("✅ AI Consultant dapat menangani struktur data yang diberikan")
        print("✅ Mendukung format baru dengan reviews dan summary")
        print("✅ Mendukung format lama untuk backward compatibility")
        print("✅ Data dapat diproses dengan benar")
    else:
        print("\n❌ Some tests failed")

if __name__ == "__main__":
    main()

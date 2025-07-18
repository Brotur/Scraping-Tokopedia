# Correct API Request Format

## POST Request to `/scrape-with-details`

### Request Format
```json
{
    "url": "https://www.tokopedia.com/huawei/huawei-matepad-11-5-s-papermatte-edition-tablet-8-256gb-nearlink-accessories-gopaint-pc-level-wps-space-grey-94e22/review",
    "target_ratings": [1, 2, 3, 4, 5],
    "max_reviews_per_rating": 15,
    "headless": false
}
```

### Parameters Explanation
- `url`: Full Tokopedia product URL (can be product page or review page)
- `target_ratings`: Array of rating values to scrape (1-5)
- `max_reviews_per_rating`: Maximum reviews to collect per rating level
- `headless`: Whether to run browser in headless mode (false for debugging)

### Expected Response
```json
{
    "success": true,
    "product_details": {
        "product_name": "Huawei MatePad 11.5S",
        "price": "Rp 7.999.000",
        "rating": 4.8,
        "rating_count": 150,
        "sold_count": "50+ terjual",
        "store_name": "Huawei Official Store",
        "store_rating": 4.9,
        "store_reviews": 12500,
        "description": "...",
        "product_url": "https://...",
        "processing_time": "2-3 hari"
    },
    "reviews": [
        {
            "rating": 5,
            "comment": "Produk bagus!",
            "date": "2025-01-15",
            "reviewer": "user123"
        }
    ],
    "scraping_stats": {
        "total_reviews": 45,
        "ratings_distribution": {
            "1": 2,
            "2": 3,
            "3": 5,
            "4": 10,
            "5": 25
        }
    }
}
```

## Frontend JavaScript (Corrected)
```javascript
async function extractProductDetails(productUrl) {
    const response = await fetch(`${API_BASE_URL}/scrape-with-details`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            url: productUrl,
            target_ratings: [1, 2, 3, 4, 5],
            max_reviews_per_rating: 15,
            headless: false
        })
    });
    
    const data = await response.json();
    return data.product_details;
}
```

## Test with curl
```bash
curl -X POST "http://localhost:8000/scrape-with-details" \
     -H "Content-Type: application/json" \
     -d '{
         "url": "https://www.tokopedia.com/huawei/huawei-matepad-11-5-s-papermatte-edition-tablet-8-256gb-nearlink-accessories-gopaint-pc-level-wps-space-grey-94e22/review",
         "target_ratings": [1, 2, 3, 4, 5],
         "max_reviews_per_rating": 15,
         "headless": false
     }'
```

## Notes
- ✅ Parameter name is `url` (not `product_url`)
- ✅ Include all required parameters for proper scraping
- ✅ Response contains `product_details` object with all needed fields
- ✅ Frontend maps correctly to AI consultant format

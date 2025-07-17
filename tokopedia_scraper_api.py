from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import List, Optional
import time
import re
import urllib.parse
from datetime import datetime

# Import scraper class yang sudah ada
from tokopedia_scraper_improved import TokopediaReviewScraperImproved

app = FastAPI(title="Tokopedia Review Scraper Simple API", version="1.0.0")

# Pydantic model untuk request
class ScrapeRequest(BaseModel):
    url: str
    target_ratings: Optional[List[int]] = [1, 2, 3, 4, 5]
    max_reviews_per_rating: Optional[int] = 15
    headless: Optional[bool] = True
    
    @field_validator('target_ratings')
    def validate_ratings(cls, v):
        for rating in v:
            if rating not in [1, 2, 3, 4, 5]:
                raise ValueError('Ratings must be between 1 and 5')
        return v
    
    @field_validator('url')
    def validate_url(cls, v):
        if 'tokopedia.com' not in v:
            raise ValueError('URL must be from tokopedia.com')
        return v

def extract_product_name_from_url(url):
    """Extract product name from Tokopedia URL - FAST and SIMPLE"""
    try:
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        
        # Remove /review suffix if present
        if path.endswith('/review'):
            path = path[:-7]
        
        # Split path and get product slug
        path_parts = path.split('/')
        
        # Find product slug (usually the last part)
        product_slug = ""
        for part in reversed(path_parts):
            if part and part != "review":
                product_slug = part
                break
        
        if not product_slug:
            return "Unknown Product"
        
        # Clean and format product name
        product_name = product_slug.replace('-', ' ')
        
        # Remove common suffixes
        suffixes_to_remove = [
            r'-\w+$',  # Remove single word suffix like -12345
            r'\d+gb$',  # Remove storage info
            r'\d+mb$',  # Remove storage info
            r'review$',  # Remove review
        ]
        
        for suffix in suffixes_to_remove:
            product_name = re.sub(suffix, '', product_name, flags=re.IGNORECASE)
        
        # Capitalize words
        product_name = ' '.join(word.capitalize() for word in product_name.split())
        
        # Clean up multiple spaces
        product_name = re.sub(r'\s+', ' ', product_name).strip()
        
        return product_name if product_name else "Unknown Product"
        
    except Exception as e:
        print(f"Error extracting product name from URL: {e}")
        return "Unknown Product"

def extract_store_name_from_url(url):
    """Extract store name from Tokopedia URL"""
    try:
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        
        # Split path and get store name (usually second part)
        path_parts = path.split('/')
        
        if len(path_parts) >= 2:
            store_slug = path_parts[1]
            # Clean store name
            store_name = store_slug.replace('-', ' ').title()
            return store_name
        
        return "Unknown Store"
        
    except Exception as e:
        print(f"Error extracting store name from URL: {e}")
        return "Unknown Store"

@app.post("/scrape")
async def scrape_reviews(request: ScrapeRequest):
    """Scrape reviews and return results directly"""
    try:
        print(f"Starting scraping for URL: {request.url}")
        
        # FAST: Extract product info from URL first
        product_name_from_url = extract_product_name_from_url(request.url)
        store_name_from_url = extract_store_name_from_url(request.url)
        
        print(f"Product name from URL: {product_name_from_url}")
        print(f"Store name from URL: {store_name_from_url}")
        
        # Initialize scraper
        scraper = TokopediaReviewScraperImproved(headless=request.headless)
        
        try:
            # Jalankan scraping
            scraper.get_reviews_by_rating(
                product_url=request.url,
                target_ratings=request.target_ratings,
                max_reviews_per_rating=request.max_reviews_per_rating
            )
            
            # Format data sesuai format yang diinginkan (array of objects)
            formatted_reviews = []
            for review in scraper.reviews_data:
                formatted_review = {
                    "rating": review.get("rating", 0),
                    "reviewer_name": review.get("reviewer_name", ""),
                    "reviewer_name_normalized": review.get("reviewer_name_normalized", ""),
                    "review_text": review.get("review_text", ""),
                    "review_text_normalized": review.get("review_text_normalized", ""),
                    "review_date": review.get("review_date", ""),
                    "review_date_normalized": review.get("review_date_normalized", ""),
                    "variant": review.get("variant", ""),
                    "variant_normalized": review.get("variant_normalized", ""),
                    "rating_filter": review.get("rating_filter", 0),
                    "scraped_at": review.get("scraped_at", ""),
                    # Fast product info from URL
                    "product_name": product_name_from_url,
                    "store_name": store_name_from_url,
                    "product_url": request.url.replace('/review', '') if '/review' in request.url else request.url
                }
                
                # Add scraped product info if available (optional, slower)
                if hasattr(scraper, 'product_info') and scraper.product_info:
                    formatted_review["product_name_scraped"] = scraper.product_info.get("product_name", "")
                    formatted_review["product_price"] = scraper.product_info.get("product_price", "")
                    formatted_review["product_description"] = scraper.product_info.get("product_description", "")
                
                formatted_reviews.append(formatted_review)
            
            # Return direct JSON array
            return formatted_reviews
            
        finally:
            scraper.close()
            
    except Exception as e:
        print(f"Error during scraping: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/extract-product-info")
async def extract_product_info(url: str):
    """Extract product info from URL only (very fast)"""
    try:
        if 'tokopedia.com' not in url:
            raise HTTPException(status_code=400, detail="URL must be from tokopedia.com")
        
        product_name = extract_product_name_from_url(url)
        store_name = extract_store_name_from_url(url)
        
        return {
            "product_name": product_name,
            "store_name": store_name,
            "product_url": url.replace('/review', '') if '/review' in url else url,
            "review_url": url if '/review' in url else url + '/review',
            "extracted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@app.get("/")
async def root():
    """API Info"""
    return {
        "message": "Tokopedia Review Scraper Simple API",
        "version": "1.0.0",
        "description": "Send URL and get reviews directly with fast product name extraction",
        "endpoints": {
            "POST /scrape": "Scrape reviews with fast product info from URL",
            "GET /extract-product-info": "Extract product info from URL only (very fast)"
        },
        "example_request": {
            "url": "https://www.tokopedia.com/store/product-name-12345/review",
            "target_ratings": [1, 2, 3, 4, 5],
            "max_reviews_per_rating": 15,
            "headless": True
        },
        "example_response": [
            {
                "rating": 2,
                "reviewer_name": "R***i",
                "reviewer_name_normalized": "R i",
                "review_text": "percuma PO benefits yg didapet...",
                "review_text_normalized": "percuma po benefits yg didapet...",
                "review_date": "Lebih dari 1 tahun lalu",
                "review_date_normalized": "Lebih dari 1 tahun lalu",
                "variant": "Grey+Proteksi",
                "variant_normalized": "Grey Proteksi",
                "rating_filter": 2,
                "scraped_at": "2025-07-17 09:45:21",
                "product_name": "Huawei Matepad 11 5 S Papermatte Edition Tablet 8 256Gb",
                "store_name": "Huawei",
                "product_url": "https://www.tokopedia.com/huawei/product-name"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
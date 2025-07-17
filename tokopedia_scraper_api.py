from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import List, Optional
import time
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

@app.post("/scrape")
async def scrape_reviews(request: ScrapeRequest):
    """Scrape reviews and return results directly"""
    try:
        print(f"Starting scraping for URL: {request.url}")
        
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
                    "scraped_at": review.get("scraped_at", "")
                }
                
                # Add product info if available
                if hasattr(scraper, 'product_info') and scraper.product_info:
                    formatted_review["product_name"] = scraper.product_info.get("product_name", "")
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

@app.get("/")
async def root():
    """API Info"""
    return {
        "message": "Tokopedia Review Scraper Simple API",
        "version": "1.0.0",
        "description": "Send URL and get reviews directly",
        "endpoint": "POST /scrape",
        "example_request": {
            "url": "https://www.tokopedia.com/product/review",
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
                "scraped_at": "2025-07-17 09:45:21"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
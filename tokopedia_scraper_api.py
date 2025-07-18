from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Add this import
from pydantic import BaseModel, field_validator
from typing import List, Optional
import time
import re
import urllib.parse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import scraper class yang sudah ada
from tokopedia_scraper_improved import TokopediaReviewScraperImproved

app = FastAPI(title="Tokopedia Review Scraper API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

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

class ProductDetailsRequest(BaseModel):
    url: str
    headless: Optional[bool] = True
    
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

def setup_driver(headless=True):
    """Setup Chrome driver dengan konfigurasi optimal"""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def extract_product_details(url, headless=True):
    """Extract comprehensive product details from Tokopedia product page"""
    driver = setup_driver(headless)
    product_details = {}
    
    try:
        # Clean URL (remove /review if present)
        clean_url = url.replace('/review', '') if '/review' in url else url
        
        print(f"Loading product page: {clean_url}")
        driver.get(clean_url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 15)
        
        # Extract basic product info
        try:
            # Product name - try multiple selectors
            product_name = ""
            selectors = [
                '[data-testid="lblPDPDetailProductName"]',
                'h1[data-testid="lblPDPDetailProductName"]',
                '.css-1os9jjn',
                'h1'
            ]
            
            for selector in selectors:
                try:
                    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    product_name = element.text.strip()
                    if product_name:
                        break
                except:
                    continue
            
            product_details['product_name'] = product_name if product_name else extract_product_name_from_url(url)
        except:
            product_details['product_name'] = extract_product_name_from_url(url)
        
        # Extract price
        try:
            price_selectors = [
                '[data-testid="lblPDPDetailProductPrice"]',
                '.price',
                '[data-testid="lblPDPDetailProductPrice"] span',
                '.css-1ksb19c',
                '.css-o5uqvq'
            ]
            
            price = ""
            for selector in price_selectors:
                try:
                    price_element = driver.find_element(By.CSS_SELECTOR, selector)
                    price = price_element.text.strip()
                    if price and 'Rp' in price:
                        break
                except:
                    continue
            
            product_details['price'] = price
        except:
            product_details['price'] = ""
        
        # Extract rating - focus on main span only
        try:
            rating = ""
            try:
                rating_element = driver.find_element(By.CSS_SELECTOR, 'span.main[data-testid="lblPDPDetailProductRatingNumber"]')
                rating = rating_element.text.strip()
            except:
                try:
                    rating_element = driver.find_element(By.CSS_SELECTOR, '[data-testid="lblPDPDetailProductRatingNumber"]')
                    rating = rating_element.text.strip()
                except:
                    pass
            
            product_details['rating'] = rating
        except:
            product_details['rating'] = ""
        
        # Extract rating count - look for exact pattern
        try:
            rating_count = ""
            try:
                rating_count_element = driver.find_element(By.CSS_SELECTOR, 'span[data-testid="lblPDPDetailProductRatingCounter"]')
                rating_count = rating_count_element.text.strip()
            except:
                pass
            
            product_details['rating_count'] = rating_count
        except:
            product_details['rating_count'] = ""
        
        # Extract sold count - look for exact pattern and exclude "Subtotal"
        try:
            sold_count = ""
            try:
                sold_element = driver.find_element(By.CSS_SELECTOR, 'p[data-testid="lblPDPDetailProductSoldCounter"]')
                sold_text = sold_element.text.strip()
                # Filter out "Subtotal" and only get text with "Terjual"
                if 'terjual' in sold_text.lower() and 'subtotal' not in sold_text.lower():
                    sold_count = sold_text
            except:
                pass
            
            product_details['sold_count'] = sold_count
        except:
            product_details['sold_count'] = ""
        
        # Extract store information
        try:
            store_selectors = [
                '[data-testid="llbPDPFooterShopName"]',
                '[data-testid="lblPDPFooterShopName"]',
                '.shop-name',
                '.css-1rn0irl'
            ]
            
            store_name = ""
            for selector in store_selectors:
                try:
                    store_name_element = driver.find_element(By.CSS_SELECTOR, selector)
                    store_name = store_name_element.text.strip()
                    if store_name:
                        break
                except:
                    continue
            
            product_details['store_name'] = store_name if store_name else extract_store_name_from_url(url)
        except:
            product_details['store_name'] = extract_store_name_from_url(url)
        
        # Extract product description
        try:
            # Try to click "Selengkapnya" button if it exists
            try:
                selengkapnya_selectors = [
                    '[data-testid="btnPDPDescriptionSeeMore"]',
                    '.see-more',
                    '.selengkapnya',
                    'button[data-testid="btnPDPDescriptionSeeMore"]'
                ]
                
                for selector in selengkapnya_selectors:
                    try:
                        selengkapnya_button = driver.find_element(By.CSS_SELECTOR, selector)
                        if selengkapnya_button.is_displayed():
                            driver.execute_script("arguments[0].click();", selengkapnya_button)
                            time.sleep(1)
                            break
                    except:
                        continue
            except:
                pass
            
            # Extract full description
            description_selectors = [
                '[data-testid="lblPDPDescriptionProduk"]',
                '.product-description',
                '.css-175oi2r',
                '.description'
            ]
            
            description = ""
            for selector in description_selectors:
                try:
                    description_element = driver.find_element(By.CSS_SELECTOR, selector)
                    description = description_element.text.strip()
                    if description and len(description) > 50:
                        break
                except:
                    continue
            
            product_details['description'] = description
        except:
            product_details['description'] = ""
        
        # Add metadata
        product_details['scraped_at'] = datetime.now().isoformat()
        product_details['product_url'] = clean_url
        
        # Remove empty fields - only keep fields with actual data
        cleaned_product_details = {}
        for key, value in product_details.items():
            if value and str(value).strip():  # Only keep non-empty values
                cleaned_product_details[key] = value
        
        # Log what we found
        print(f"[OK] Product Name: {cleaned_product_details.get('product_name', 'Not found')}")
        print(f"[OK] Price: {cleaned_product_details.get('price', 'Not found')}")
        print(f"[OK] Rating: {cleaned_product_details.get('rating', 'Not found')}")
        print(f"[OK] Rating Count: {cleaned_product_details.get('rating_count', 'Not found')}")
        print(f"[OK] Sold Count: {cleaned_product_details.get('sold_count', 'Not found')}")
        print(f"[OK] Store Name: {cleaned_product_details.get('store_name', 'Not found')}")
        print(f"[OK] Description Length: {len(cleaned_product_details.get('description', ''))}")
        
        return cleaned_product_details
        
    except Exception as e:
        print(f"[ERROR] Error extracting product details: {e}")
        # Return only essential fields when error occurs
        return {
            'error': str(e),
            'product_name': extract_product_name_from_url(url),
            'store_name': extract_store_name_from_url(url),
            'product_url': url.replace('/review', '') if '/review' in url else url,
            'scraped_at': datetime.now().isoformat()
        }
    
    finally:
        driver.quit()

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

@app.post("/product-details")
async def get_product_details(request: ProductDetailsRequest):
    """Extract comprehensive product details including price, rating, store info, and description"""
    try:
        print(f"Extracting product details for URL: {request.url}")
        
        # Extract detailed product information
        product_details = extract_product_details(request.url, request.headless)
        
        return product_details
        
    except Exception as e:
        print(f"Error extracting product details: {e}")
        raise HTTPException(status_code=500, detail=f"Product details extraction failed: {str(e)}")

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
        "description": "Send URL and get reviews or product details",
        "endpoints": {
            "POST /scrape": "Scrape reviews with fast product info from URL",
            "POST /scrape-with-details": "Scrape reviews + comprehensive product details (NEW)",
            "POST /product-details": "Get comprehensive product details only",
            "GET /extract-product-info": "Extract product info from URL only (very fast)"
        },
        "scrape_example": {
            "url": "https://www.tokopedia.com/store/product-name-12345/review",
            "target_ratings": [1, 2, 3, 4, 5],
            "max_reviews_per_rating": 15,
            "headless": True
        },
        "scrape_with_details_example": {
            "url": "https://www.tokopedia.com/store/product-name-12345/review",
            "target_ratings": [1, 2, 3, 4, 5],
            "max_reviews_per_rating": 15,
            "headless": True
        },
        "scrape_with_details_response": {
            "product_details": {
                "product_name": "Nintendo Switch OLED Model",
                "price": "Rp5.349.000",
                "rating": "5.0",
                "rating_count": "1.405 rating",
                "sold_count": "2 rb+",
                "description": "Nintendo Switch OLED Model merupakan konsol gaming...",
                "store_name": "Butikgames",
                "store_rating": "4.9",
                "store_review_count": "135 rb",
                "processing_time": "± 2 jam pesanan diproses",
                "shipped_from": "Kota Administrasi Jakarta Pusat",
                "product_url": "https://www.tokopedia.com/store/product-name",
                "review_url": "https://www.tokopedia.com/store/product-name/review",
                "scraped_at": "2025-07-17T10:30:00"
            },
            "reviews": [
                {
                    "rating": 5,
                    "reviewer_name": "J***n",
                    "reviewer_name_normalized": "J n",
                    "review_text": "Produk bagus, pengiriman cepat",
                    "review_text_normalized": "produk bagus pengiriman cepat",
                    "review_date": "1 minggu lalu",
                    "review_date_normalized": "1 minggu lalu",
                    "variant": "Neon, 128GB",
                    "variant_normalized": "Neon 128GB",
                    "rating_filter": 5,
                    "scraped_at": "2025-07-17 10:30:00"
                }
            ],
            "summary": {
                "total_reviews_scraped": 75,
                "target_ratings": [1, 2, 3, 4, 5],
                "max_reviews_per_rating": 15,
                "scraped_at": "2025-07-17T10:30:00"
            }
        },
        "product_details_example": {
            "url": "https://www.tokopedia.com/store/product-name-12345",
            "headless": True
        },
        "old_scrape_response": [
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

@app.post("/scrape-with-details")
async def scrape_with_details(request: ScrapeRequest):
    """Scrape reviews AND product details - Details shown once, reviews in array"""
    try:
        print(f"Starting comprehensive scraping for URL: {request.url}")
        
        # 1. Extract basic info from URL (fast)
        product_name_from_url = extract_product_name_from_url(request.url)
        store_name_from_url = extract_store_name_from_url(request.url)
        
        print(f"Product name from URL: {product_name_from_url}")
        print(f"Store name from URL: {store_name_from_url}")
        
        # 2. Extract detailed product info (slower but comprehensive)
        product_url = request.url.replace('/review', '') if '/review' in request.url else request.url
        product_details = extract_product_details(product_url, request.headless)
        
        # 3. Initialize scraper for reviews
        scraper = TokopediaReviewScraperImproved(headless=request.headless)
        
        try:
            # 4. Scrape reviews
            scraper.get_reviews_by_rating(
                product_url=request.url,
                target_ratings=request.target_ratings,
                max_reviews_per_rating=request.max_reviews_per_rating
            )
            
            # 5. Format reviews (NO PRODUCT DETAILS in each review)
            formatted_reviews = []
            for review in scraper.reviews_data:
                formatted_review = {
                    # Review data only
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
                formatted_reviews.append(formatted_review)
            
            # 6. Prepare clean product details (only fields with data)
            clean_product_details = {}
            
            # Essential fields (always include)
            clean_product_details["product_name"] = product_details.get("product_name", product_name_from_url)
            clean_product_details["store_name"] = product_details.get("store_name", store_name_from_url)
            clean_product_details["product_url"] = product_url
            clean_product_details["review_url"] = request.url
            clean_product_details["scraped_at"] = product_details.get("scraped_at", datetime.now().isoformat())
            
            # Optional fields (only if they have data)
            if product_details.get("price"):
                clean_product_details["price"] = product_details["price"]
            
            if product_details.get("rating"):
                clean_product_details["rating"] = product_details["rating"]
            
            if product_details.get("rating_count"):
                clean_product_details["rating_count"] = product_details["rating_count"]
            
            if product_details.get("sold_count"):
                clean_product_details["sold_count"] = product_details["sold_count"]
            
            if product_details.get("description"):
                clean_product_details["description"] = product_details["description"]
            
            # 7. Return clean structured data
            return {
                "product_details": clean_product_details,
                "reviews": formatted_reviews,
                "summary": {
                    "total_reviews_scraped": len(formatted_reviews),
                    "target_ratings": request.target_ratings,
                    "max_reviews_per_rating": request.max_reviews_per_rating,
                    "scraped_at": datetime.now().isoformat()
                }
            }
            
        finally:
            scraper.close()
            
    except Exception as e:
        print(f"Error during comprehensive scraping: {e}")
        raise HTTPException(status_code=500, detail=f"Comprehensive scraping failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
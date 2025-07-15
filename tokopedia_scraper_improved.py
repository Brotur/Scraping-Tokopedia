import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import json
import random
import re

class TokopediaReviewScraperImproved:
    def __init__(self, headless=False):
        self.setup_driver(headless)
        self.reviews_data = []
        self.current_page = 1
        
    def setup_driver(self, headless):
        """Setup Chrome driver dengan konfigurasi optimal"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        
        # Enhanced user agent and stealth options
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        
        self.wait = WebDriverWait(self.driver, 15)
        self.actions = ActionChains(self.driver)
        
    def wait_for_page_load(self):
        """Wait for page to fully load"""
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        # Wait for specific elements to load
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.css-15m2bcr")))
        except TimeoutException:
            pass
        time.sleep(2)
        
    def scroll_to_element(self, element):
        """Scroll to element smoothly"""
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(1)
        
    def get_reviews_by_rating(self, product_url, target_ratings=[1, 2, 3, 4, 5], max_reviews_per_rating=15):
        """Scrape ulasan berdasarkan rating tertentu dengan batasan maksimal review per rating"""
        try:
            print(f"Loading page: {product_url}")
            self.driver.get(product_url)
            self.wait_for_page_load()
            
            # Scrape by specific ratings only (no "all reviews" filter)
            for rating in target_ratings:
                print(f"\n=== Scraping ulasan {rating} bintang (max {max_reviews_per_rating} reviews) ===")
                if self.apply_rating_filter(rating):
                    self.scrape_filtered_reviews(rating, max_reviews_per_rating)
                    self.remove_rating_filter()
                    time.sleep(2)
                else:
                    print(f"Failed to apply filter for rating {rating}")
                    
        except Exception as e:
            print(f"Error in get_reviews_by_rating: {e}")
            import traceback
            traceback.print_exc()
            
    def apply_rating_filter(self, rating):
        """Apply rating filter on the page (exclusive - only one filter active at a time)"""
        try:
            # Close any overlays first
            self.close_overlays()
            
            # First, clear all existing rating filters to ensure exclusivity
            print(f"Clearing all existing rating filters before applying rating {rating}")
            self.clear_all_rating_filters()
            time.sleep(2)
            
            # Expand the Rating accordion if collapsed
            try:
                rating_header = self.driver.find_element(By.XPATH, "//button[contains(@aria-controls, 'Rating') or contains(text(), 'Rating')]")
                if rating_header.get_attribute('aria-expanded') == 'false':
                    self.scroll_to_element(rating_header)
                    rating_header.click()
                    time.sleep(2)
            except:
                print("Rating accordion not found or already expanded")
            
            # Method 1: Find by label containing rating number
            applied = False
            try:
                labels = self.driver.find_elements(By.CSS_SELECTOR, "label.checkbox")
                for label in labels:
                    try:
                        # Look for rating number in various possible locations
                        rating_elements = label.find_elements(By.CSS_SELECTOR, "span, p")
                        for elem in rating_elements:
                            if elem.text.strip() == str(rating):
                                checkbox = label.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                                if not checkbox.is_selected():
                                    self.scroll_to_element(label)
                                    label.click()
                                    time.sleep(3)
                                    applied = True
                                    print(f"Successfully applied filter for rating {rating}")
                                    break
                        if applied:
                            break
                    except:
                        continue
            except Exception as e:
                print(f"Method 1 failed: {e}")
            
            # Method 2: Find by specific rating filter structure
            if not applied:
                try:
                    rating_filters = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='ratingFilter']")
                    for i, filter_elem in enumerate(rating_filters):
                        try:
                            # Check if this filter corresponds to our target rating
                            # The filters are usually ordered 5, 4, 3, 2, 1
                            expected_rating = 5 - i  # Convert index to rating
                            if expected_rating == rating:
                                checkbox = filter_elem.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                                if not checkbox.is_selected():
                                    self.scroll_to_element(checkbox)
                                    checkbox.click()
                                    time.sleep(3)
                                    applied = True
                                    print(f"Successfully applied filter for rating {rating} (method 2)")
                                    break
                        except:
                            continue
                except Exception as e:
                    print(f"Method 2 failed: {e}")
            
            # Method 3: Try XPath approach
            if not applied:
                try:
                    xpath = f"//label[contains(@class, 'checkbox')]//span[text()='{rating}']"
                    rating_span = self.driver.find_element(By.XPATH, xpath)
                    label = rating_span.find_element(By.XPATH, "./ancestor::label")
                    checkbox = label.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                    if not checkbox.is_selected():
                        self.scroll_to_element(label)
                        label.click()
                        time.sleep(3)
                        applied = True
                        print(f"Successfully applied filter for rating {rating} (method 3)")
                except Exception as e:
                    print(f"Method 3 failed: {e}")
            
            # Verify that only the target rating filter is active
            if applied:
                self.verify_exclusive_filter(rating)
                
            if not applied:
                print(f"All methods failed for rating {rating}")
                
            return applied
            
        except Exception as e:
            print(f"Error applying rating filter {rating}: {e}")
            return False
            
    def verify_exclusive_filter(self, target_rating):
        """Verify that only the target rating filter is active"""
        try:
            active_filters = []
            
            # Check all rating filters
            rating_filters = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='ratingFilter']")
            for i, filter_elem in enumerate(rating_filters):
                try:
                    checkbox = filter_elem.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                    if checkbox.is_selected():
                        expected_rating = 5 - i  # Convert index to rating
                        active_filters.append(expected_rating)
                except:
                    continue
            
            # Also check by label structure
            labels = self.driver.find_elements(By.CSS_SELECTOR, "label.checkbox")
            for label in labels:
                try:
                    checkbox = label.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                    if checkbox.is_selected():
                        spans = label.find_elements(By.CSS_SELECTOR, "span")
                        for span in spans:
                            if span.text.strip() in ['1', '2', '3', '4', '5']:
                                rating_num = int(span.text.strip())
                                if rating_num not in active_filters:
                                    active_filters.append(rating_num)
                                break
                except:
                    continue
            
            print(f"Active filters detected: {active_filters}")
            
            # If more than one filter is active, clear others
            if len(active_filters) > 1:
                print(f"⚠️  Multiple filters active: {active_filters}. Clearing unwanted filters...")
                self.clear_unwanted_filters(target_rating)
            elif len(active_filters) == 1 and active_filters[0] == target_rating:
                print(f"✅ Only target filter {target_rating} is active")
            else:
                print(f"⚠️  Unexpected filter state: {active_filters}")
                
        except Exception as e:
            print(f"Error verifying exclusive filter: {e}")
            
    def clear_unwanted_filters(self, target_rating):
        """Clear all filters except the target rating"""
        try:
            # Clear all rating filters that are not the target
            rating_filters = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='ratingFilter']")
            for i, filter_elem in enumerate(rating_filters):
                try:
                    expected_rating = 5 - i  # Convert index to rating
                    if expected_rating != target_rating:
                        checkbox = filter_elem.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                        if checkbox.is_selected():
                            self.scroll_to_element(checkbox)
                            checkbox.click()
                            time.sleep(1)
                            print(f"Cleared unwanted filter: {expected_rating}")
                except:
                    continue
                    
        except Exception as e:
            print(f"Error clearing unwanted filters: {e}")
            
    def clear_all_rating_filters(self):
        """Clear all rating filters to ensure exclusivity"""
        try:
            print("Attempting to clear all rating filters...")
            
            # Wait a moment for page to stabilize
            time.sleep(1)
            
            # Method 1: Direct approach - find all checked rating filters
            cleared_count = 0
            try:
                # Find all rating filter checkboxes that are checked
                rating_filters = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='ratingFilter']")
                
                for filter_div in rating_filters:
                    try:
                        checkbox = filter_div.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                        
                        # Check if checkbox is actually checked
                        if checkbox.is_selected():
                            # Get rating number for logging
                            try:
                                rating_text = filter_div.find_element(By.CSS_SELECTOR, "span").text.strip()
                                print(f"Found checked filter for rating {rating_text}")
                            except:
                                rating_text = "unknown"
                            
                            # Scroll to element and click
                            self.scroll_to_element(checkbox)
                            time.sleep(0.5)
                            
                            # Try different click methods
                            try:
                                checkbox.click()
                                cleared_count += 1
                                print(f"Cleared rating filter {rating_text} (method: direct click)")
                            except:
                                try:
                                    self.driver.execute_script("arguments[0].click();", checkbox)
                                    cleared_count += 1
                                    print(f"Cleared rating filter {rating_text} (method: javascript click)")
                                except:
                                    try:
                                        self.actions.move_to_element(checkbox).click().perform()
                                        cleared_count += 1
                                        print(f"Cleared rating filter {rating_text} (method: action chain)")
                                    except:
                                        print(f"Failed to clear rating filter {rating_text}")
                            
                            time.sleep(1)
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"Method 1 failed: {e}")
            
            # Method 2: Find by label structure
            if cleared_count == 0:
                try:
                    labels = self.driver.find_elements(By.CSS_SELECTOR, "label.checkbox")
                    for label in labels:
                        try:
                            checkbox = label.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                            if checkbox.is_selected():
                                # Check if this is a rating filter
                                spans = label.find_elements(By.CSS_SELECTOR, "span")
                                for span in spans:
                                    if span.text.strip() in ['1', '2', '3', '4', '5']:
                                        print(f"Found checked rating filter: {span.text.strip()}")
                                        
                                        self.scroll_to_element(checkbox)
                                        time.sleep(0.5)
                                        
                                        try:
                                            checkbox.click()
                                            cleared_count += 1
                                            print(f"Cleared rating filter {span.text.strip()} (method 2)")
                                        except:
                                            try:
                                                self.driver.execute_script("arguments[0].click();", checkbox)
                                                cleared_count += 1
                                                print(f"Cleared rating filter {span.text.strip()} (method 2 - JS)")
                                            except:
                                                print(f"Failed to clear rating filter {span.text.strip()}")
                                        
                                        time.sleep(1)
                                        break
                        except:
                            continue
                except Exception as e:
                    print(f"Method 2 failed: {e}")
            
            # Method 3: JavaScript approach as last resort
            if cleared_count == 0:
                try:
                    js_script = """
                    var cleared = 0;
                    var filters = document.querySelectorAll('div[data-testid="ratingFilter"] input[type="checkbox"]:checked');
                    console.log('Found ' + filters.length + ' checked filters');
                    
                    for(var i = 0; i < filters.length; i++) {
                        if(filters[i].checked) {
                            filters[i].click();
                            cleared++;
                            console.log('Cleared filter ' + (i+1));
                        }
                    }
                    
                    return cleared;
                    """
                    
                    js_cleared = self.driver.execute_script(js_script)
                    if js_cleared > 0:
                        cleared_count += js_cleared
                        print(f"Cleared {js_cleared} filters using JavaScript (method 3)")
                        
                except Exception as e:
                    print(f"Method 3 failed: {e}")
            
            print(f"Total filters cleared: {cleared_count}")
            
            # Wait for changes to take effect
            time.sleep(2)
            
        except Exception as e:
            print(f"Error clearing all rating filters: {e}")
            
    def remove_rating_filter(self):
        """Remove all rating filters (same as clear_all_rating_filters)"""
        try:
            self.clear_all_rating_filters()
        except Exception as e:
            print(f"Error removing rating filters: {e}")
            
    def scrape_filtered_reviews(self, rating, max_reviews=15):
        """Scrape reviews after applying rating filter with maximum limit"""
        try:
            page = 1
            reviews_collected = 0
            
            while reviews_collected < max_reviews:
                print(f"Scraping page {page} for rating {rating} (collected: {reviews_collected}/{max_reviews})")
                
                # Scrape current page
                reviews = self.scrape_current_page_reviews(rating, max_reviews - reviews_collected)
                if not reviews:
                    print(f"No more reviews found for rating {rating}")
                    break
                
                reviews_collected += len(reviews)
                print(f"Collected {len(reviews)} reviews from page {page}, total: {reviews_collected}")
                
                # Stop if we've reached the limit
                if reviews_collected >= max_reviews:
                    print(f"Reached maximum limit of {max_reviews} reviews for rating {rating}")
                    break
                
                # Try to go to next page
                if not self.go_to_next_page():
                    print(f"No more pages available for rating {rating}")
                    break
                    
                page += 1
                if page > 10:  # Safety limit to prevent infinite loop
                    break
                    
        except Exception as e:
            print(f"Error scraping filtered reviews for rating {rating}: {e}")
            
    def scrape_current_page_reviews(self, rating_filter, max_reviews=None):
        """Scrape reviews on current page with optional limit"""
        try:
            # Wait for reviews to load
            self.wait_for_page_load()
            
            # Scroll down to load more content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Find all review articles with multiple selectors
            review_selectors = [
                "article.css-15m2bcr",
                "article[class*='css-15m2bcr']",
                "section#review-feed article",
                "div[class*='review'] article"
            ]
            
            review_articles = []
            for selector in review_selectors:
                try:
                    articles = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if articles:
                        review_articles = articles
                        print(f"Found {len(articles)} articles using selector: {selector}")
                        break
                except:
                    continue
            
            if not review_articles:
                print("No review articles found on this page")
                return []
            
            scraped_reviews = []
            
            # Apply limit if specified
            articles_to_process = review_articles
            if max_reviews:
                articles_to_process = review_articles[:max_reviews]
            
            for i, article in enumerate(articles_to_process):
                try:
                    print(f"Processing article {i+1}/{len(articles_to_process)}")
                    review_data = self.extract_review_from_article(article, rating_filter)
                    if review_data:
                        # Check for duplicates
                        is_duplicate = False
                        for existing_review in self.reviews_data:
                            if (existing_review['reviewer_name'] == review_data['reviewer_name'] and 
                                existing_review['review_text'] == review_data['review_text']):
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            self.reviews_data.append(review_data)
                            scraped_reviews.append(review_data)
                            print(f"  ✓ Added review from {review_data['reviewer_name']}")
                        else:
                            print(f"  ⚠ Duplicate review from {review_data['reviewer_name']}")
                    else:
                        print(f"  ✗ Failed to extract review from article {i+1}")
                        
                    # Stop if we've reached the limit
                    if max_reviews and len(scraped_reviews) >= max_reviews:
                        print(f"Reached limit of {max_reviews} reviews for this page")
                        break
                        
                except Exception as e:
                    print(f"  ✗ Error extracting review from article {i+1}: {e}")
                    continue
            
            print(f"Scraped {len(scraped_reviews)} new reviews from current page")
            return scraped_reviews
            
        except Exception as e:
            print(f"Error scraping current page: {e}")
            return []
            
    def extract_review_from_article(self, article, rating_filter):
        """Extract review data from article element"""
        try:
            # Extract star rating
            star_rating = self.extract_star_rating(article)
            
            # Extract reviewer name
            reviewer_name = self.safe_find_text(article, [
                "span.name",
                ".css-k4rf3m span.name",
                ".name"
            ])
            
            # Extract review text
            review_text = self.safe_find_text(article, [
                "span[data-testid='lblItemUlasan']",
                ".css-34x6j7-unf-heading span",
                "p[data-testid='lblItemUlasan']"
            ])
            
            # Extract review date
            review_date = self.safe_find_text(article, [
                "p.css-1rpz5os-unf-heading",
                ".css-6ce5r8 p.css-1rpz5os-unf-heading"
            ])
            
            # Extract variant
            variant = self.safe_find_text(article, [
                "p[data-testid='lblVarian']",
                ".css-5amcmn-unf-heading"
            ])
            
            # Clean variant text
            if variant and "Varian:" in variant:
                variant = variant.replace("Varian:", "").strip()
            
            return {
                'rating': star_rating,
                'reviewer_name': reviewer_name,
                'review_text': review_text,
                'review_date': review_date,
                'variant': variant,
                'rating_filter': rating_filter,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error extracting review data: {e}")
            return None
            
    def extract_star_rating(self, article):
        """Extract star rating from article"""
        try:
            # Look for star rating element
            star_elem = article.find_element(By.CSS_SELECTOR, "div[data-testid='icnStarRating']")
            aria_label = star_elem.get_attribute('aria-label')
            
            if aria_label:
                # Extract number from "bintang 5" format
                match = re.search(r'bintang (\d+)', aria_label)
                if match:
                    return int(match.group(1))
            
            # Alternative: count filled stars
            filled_stars = article.find_elements(By.CSS_SELECTOR, "div[data-testid='icnStarRating'] svg[fill*='FFD45F']")
            if filled_stars:
                return len(filled_stars)
                
            return 0
            
        except Exception as e:
            print(f"Error extracting star rating: {e}")
            return 0
            
    def safe_find_text(self, element, selectors):
        """Safely find text with multiple selectors"""
        for selector in selectors:
            try:
                found = element.find_element(By.CSS_SELECTOR, selector)
                text = found.text.strip()
                if text:
                    return text
            except:
                continue
        return ""
        
    def go_to_next_page(self):
        """Navigate to next page"""
        try:
            # Close any overlays first
            self.close_overlays()
            
            # Look for pagination buttons with multiple approaches
            pagination_selectors = [
                "button[aria-label*='Laman berikutnya']",
                "button[aria-label*='next']",
                "button.css-dzvl4q-unf-pagination-item",
                "button.css-5p3bh2-unf-pagination-item"
            ]
            
            next_button = None
            for selector in pagination_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_enabled() and button.is_displayed():
                            next_button = button
                            break
                    if next_button:
                        break
                except:
                    continue
            
            if next_button:
                # Try multiple click methods
                try:
                    self.scroll_to_element(next_button)
                    self.actions.move_to_element(next_button).click().perform()
                except:
                    try:
                        self.driver.execute_script("arguments[0].click();", next_button)
                    except:
                        try:
                            next_button.click()
                        except:
                            return False
                
                time.sleep(3)
                self.wait_for_page_load()
                return True
                
            return False
            
        except Exception as e:
            print(f"Error navigating to next page: {e}")
            return False
            
    def close_overlays(self):
        """Close any overlays that might be blocking clicks"""
        try:
            # Look for common overlay elements
            overlay_selectors = [
                "div[data-unify='Overlay']",
                ".css-1b94wk9-unf-overlay",
                "div[aria-label='unf-overlay']",
                "button[aria-label*='close']",
                "button[aria-label*='tutup']"
            ]
            
            for selector in overlay_selectors:
                try:
                    overlays = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for overlay in overlays:
                        if overlay.is_displayed():
                            # Try to click close button or ESC key
                            try:
                                overlay.click()
                            except:
                                self.driver.execute_script("arguments[0].style.display = 'none';", overlay)
                except:
                    continue
                    
            # Press ESC to close any modal
            try:
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            except:
                pass
                
        except Exception as e:
            print(f"Error closing overlays: {e}")
            
    def save_to_csv(self, filename='tokopedia_reviews_improved.csv'):
        """Save data to CSV"""
        if self.reviews_data:
            df = pd.DataFrame(self.reviews_data)
            
            # Remove duplicates based on reviewer name and review text
            df = df.drop_duplicates(subset=['reviewer_name', 'review_text', 'review_date'])
            
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Data saved to {filename}")
            print(f"Total unique reviews scraped: {len(df)}")
            
            # Print summary by rating
            if not df.empty:
                summary = df.groupby('rating').size()
                print("\nSummary by rating:")
                for rating, count in summary.items():
                    print(f"Rating {rating}: {count} reviews")
                    
                # Print summary by filter applied
                filter_summary = df.groupby('rating_filter').size()
                print("\nSummary by filter applied:")
                for filter_type, count in filter_summary.items():
                    print(f"Filter {filter_type}: {count} reviews")
        else:
            print("No data to save")
            
    def save_to_json(self, filename='tokopedia_reviews_improved.json'):
        """Save data to JSON"""
        if self.reviews_data:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.reviews_data, f, ensure_ascii=False, indent=2)
            print(f"Data also saved to {filename}")
            
    def close(self):
        """Close browser"""
        self.driver.quit()

# Usage example
if __name__ == "__main__":
    # URL produk Samsung Galaxy A16 5G
    product_url = "https://www.tokopedia.com/huawei/huawei-matepad-11-5-s-papermatte-edition-tablet-8-256gb-nearlink-accessories-gopaint-pc-level-wps-space-grey-94e22/review"
    
    # Initialize scraper
    scraper = TokopediaReviewScraperImproved(headless=False)
    
    try:
        # Scrape reviews for specific ratings with max 15 reviews per rating
        scraper.get_reviews_by_rating(product_url, target_ratings=[1, 2, 3, 4, 5], max_reviews_per_rating=15)
        
        # Save to CSV and JSON
        scraper.save_to_csv('huawei_matepad_reviews_improved.csv')
        scraper.save_to_json('huawei_matepad_reviews_improved.json')
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        scraper.close()

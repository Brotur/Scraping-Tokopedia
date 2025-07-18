# 🔧 Debugging Guide - Tokopedia AI Consultant

## Common Issues & Solutions

### 1. "Gagal mengekstrak data produk" Error

**Penyebab:**
- Server scraper tidak berjalan
- Response tidak mengandung `product_details`
- Network/connection issues

**Solusi:**
1. **Cek server status:**
   ```bash
   python test_health.py
   ```

2. **Debug response structure:**
   ```bash
   python test_mapping.py
   ```

3. **Cek browser console:**
   - Buka Developer Tools (F12)
   - Lihat tab Console untuk error details
   - Cek tab Network untuk API calls

### 2. Server Connection Issues

**Pastikan server berjalan:**
```bash
# Terminal 1 - Scraper API
python tokopedia_scraper_api.py

# Terminal 2 - AI Consultant
python ai_consultant_api.py

# Terminal 3 - Frontend
python -m http.server 3000 --directory frontend
```

### 3. CORS Issues

**Gejala:** Frontend tidak bisa connect ke API
**Solusi:** Pastikan CORS middleware aktif di `tokopedia_scraper_api.py`

### 4. Response Structure Issues

**Debug steps:**
1. Test langsung API dengan curl:
   ```bash
   curl -X POST http://localhost:8000/scrape-with-details \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.tokopedia.com/toko-komputer/laptop-gaming-asus-tuf-15", "target_ratings": [5], "max_reviews_per_rating": 5, "headless": true}'
   ```

2. Cek response format:
   ```json
   {
     "product_details": {
       "product_name": "...",
       "price": "...",
       "rating": "...",
       "rating_count": "...",
       "sold_count": "...",
       "store_name": "...",
       "description": "...",
       "product_url": "...",
       "review_url": "..."
     },
     "reviews": [...],
     "summary": {...}
   }
   ```

## Debug Console Commands

**Frontend Debug (Browser Console):**
```javascript
// Test API connection
fetch('http://localhost:8000')
  .then(r => r.text())
  .then(console.log);

// Test scraper endpoint
fetch('http://localhost:8000/scrape-with-details', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    url: 'https://www.tokopedia.com/toko-komputer/laptop-gaming-asus-tuf-15',
    target_ratings: [5],
    max_reviews_per_rating: 5,
    headless: true
  })
})
.then(r => r.json())
.then(console.log);
```

## Log Locations

**Frontend Logs:** Browser Developer Tools > Console
**Backend Logs:** Terminal where you ran the Python scripts

## Test Scripts

```bash
# Quick health check
python test_health.py

# Full mapping test
python test_mapping.py

# Debug response structure
python debug_response.py

# All tests
test_system.bat
```

## Expected Response Structure

**Scraper API (`/scrape-with-details`):**
```json
{
  "product_details": {
    "product_name": "Product Name",
    "price": "Rp X.XXX.XXX",
    "rating": "4.5",
    "rating_count": "(123 rating)",
    "sold_count": "Terjual 50+",
    "store_name": "Store Name",
    "description": "...",
    "product_url": "https://...",
    "review_url": "https://..."
  },
  "reviews": [...],
  "summary": {...}
}
```

**AI Consultant Input:**
```json
{
  "product_data": {
    "name": "Product Name",
    "price": "Rp X.XXX.XXX",
    "rating": "4.5",
    "total_ratings": "(123 rating)",
    "sold_count": "Terjual 50+",
    "store_type": "Store Name",
    "description": "...",
    "url": "https://..."
  }
}
```

## Port Configuration

- **Scraper API:** http://localhost:8000
- **AI Consultant:** http://localhost:8001
- **Frontend:** http://localhost:3000

## Environment Variables

Create `.env` file:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

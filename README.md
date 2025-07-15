# Tokopedia Review Scraper dengan Normalisasi Data untuk Analisis Sentiment

## 📋 Deskripsi
Script Python untuk scraping review produk Tokopedia dengan fitur normalisasi data yang mempersiapkan teks untuk analisis sentiment. Script ini menggunakan Selenium untuk web scraping dan TextBlob untuk analisis sentiment.

## 🚀 Fitur Utama

### 1. **Web Scraping**
- Scraping review berdasarkan rating tertentu (1-5 bintang)
- Pagination otomatis untuk mengambil lebih banyak review
- Handling filter rating yang eksklusif
- Anti-detection dengan user agent dan stealth options

### 2. **Normalisasi Data**
- **Pembersihan teks**: Menghapus emoji, URL, mention, hashtag
- **Normalisasi karakter**: Konversi ke lowercase, hapus tanda baca
- **Standarisasi spasi**: Menghapus spasi berlebih
- **Siap untuk analisis**: Format alfanumerikal yang konsisten

### 3. **Analisis Sentiment**
- Klasifikasi sentiment (Positive, Negative, Neutral)
- Polarity score (-1 hingga 1)
- Korelasi rating dengan sentiment
- Export hasil analisis

## 📁 Struktur File

```
Scraping-Tokopedia/
├── tokopedia_scraper_improved.py      # Script utama scraping
├── simple_sentiment_analysis.py       # Analisis sentiment sederhana
├── sentiment_analysis_example.py      # Contoh analisis lengkap
├── requirements.txt                   # Dependencies
├── NORMALIZATION_GUIDE.md             # Panduan normalisasi
├── README.md                         # File ini
└── Output Files:
    ├── huawei_matepad_reviews_improved.csv           # Data lengkap
    ├── huawei_matepad_reviews_improved.json          # Data JSON
    ├── huawei_matepad_sentiment_ready.csv            # Data siap sentiment
    ├── huawei_matepad_sentiment_ready.json           # Data sentiment JSON
    └── huawei_matepad_sentiment_analysis_results.csv # Hasil analisis
```

## 🛠️ Instalasi

1. **Clone atau download repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Download ChromeDriver** dan pastikan sudah di PATH
4. **Install NLTK data untuk TextBlob:**
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('brown')
   ```

## 📊 Cara Penggunaan

### 1. Scraping Review
```python
from tokopedia_scraper_improved import TokopediaReviewScraperImproved

# URL produk Tokopedia
product_url = "https://www.tokopedia.com/huawei/huawei-matepad-11-5-s-papermatte-edition-tablet-8-256gb-nearlink-accessories-gopaint-pc-level-wps-space-grey-94e22/review"

# Initialize scraper
scraper = TokopediaReviewScraperImproved(headless=False)

# Scrape reviews dengan maksimal 15 review per rating
scraper.get_reviews_by_rating(product_url, target_ratings=[1, 2, 3, 4, 5], max_reviews_per_rating=15)

# Validasi dan simpan data
scraper.validate_normalized_data()
scraper.save_to_csv('reviews.csv')
scraper.save_sentiment_ready_data('sentiment_ready.json')

scraper.close()
```

### 2. Analisis Sentiment
```python
# Jalankan analisis sentiment sederhana
python simple_sentiment_analysis.py
```

## 📈 Hasil Scraping

### Data yang Dihasilkan:
- **Total reviews**: 61 review
- **Success rate normalisasi**: 90.2%
- **Distribusi rating**: 
  - 1★: 12 reviews
  - 2★: 5 reviews  
  - 3★: 14 reviews
  - 4★: 15 reviews
  - 5★: 15 reviews

### Hasil Analisis Sentiment:
- **Neutral**: 46 reviews (83.6%)
- **Positive**: 8 reviews (14.5%)
- **Negative**: 1 review (1.8%)
- **Korelasi rating-sentiment**: 0.375 (korelasi positif yang kuat)

## 🔧 Normalisasi Data

### Proses Normalisasi:
1. **Konversi ke lowercase**
2. **Hapus emoji dan karakter unicode khusus**
3. **Hapus URL, mention (@username), hashtag (#hashtag)**
4. **Hapus tanda baca (kecuali spasi)**
5. **Hapus angka yang berdiri sendiri**
6. **Normalisasi spasi berlebih**

### Contoh Normalisasi:
**Sebelum:**
```
"Pengiriman sangat lama. Walaupun diluar pihak penjual, tetapi ini mempengaruhi pelayanan terjadap konsumen, sehingga saya merasa kurang puas belanja disini. Meskipun bara..."
```

**Setelah:**
```
"pengiriman sangat lama walaupun diluar pihak penjual tetapi ini mempengaruhi pelayanan terjadap konsumen sehingga saya merasa kurang puas belanja disini meskipun bara"
```

## 📋 Format Output

### CSV Utama (`huawei_matepad_reviews_improved.csv`)
| Column | Description |
|--------|-------------|
| rating | Rating bintang (1-5) |
| reviewer_name | Nama reviewer asli |
| reviewer_name_normalized | Nama reviewer yang dibersihkan |
| review_text | Teks review asli |
| review_text_normalized | Teks review yang dinormalisasi |
| review_date | Tanggal review asli |
| review_date_normalized | Tanggal yang dibersihkan |
| variant | Varian produk asli |
| variant_normalized | Varian yang dibersihkan |
| rating_filter | Filter rating yang digunakan |
| scraped_at | Waktu scraping |

### CSV Sentiment Ready (`huawei_matepad_sentiment_ready.csv`)
| Column | Description |
|--------|-------------|
| rating | Rating bintang |
| text | Teks yang dinormalisasi |
| reviewer | Nama reviewer yang dibersihkan |
| variant | Varian yang dibersihkan |
| date | Tanggal yang dibersihkan |
| original_text | Teks asli |

### CSV Hasil Analisis (`huawei_matepad_sentiment_analysis_results.csv`)
| Column | Description |
|--------|-------------|
| ... | Semua kolom dari sentiment ready |
| sentiment | Klasifikasi sentiment (Positive/Negative/Neutral) |
| polarity | Skor polarity (-1 hingga 1) |

## 🔍 Validasi Data

Script menyediakan validasi untuk:
- ✅ Tingkat keberhasilan normalisasi
- ✅ Contoh perbandingan teks asli vs normalisasi
- ✅ Statistik panjang teks sebelum dan sesudah
- ✅ Deteksi duplikasi review

## 📊 Analisis Sentiment

### Metrik yang Dihasilkan:
- **Distribusi sentiment** per rating
- **Polarity score** rata-rata per rating
- **Korelasi** antara rating dan sentiment
- **Review paling positif** dan **paling negatif**
- **Statistik** polarity (mean, std, min, max)

### Interpretasi Polarity:
- **> 0.1**: Positive sentiment
- **< -0.1**: Negative sentiment
- **-0.1 to 0.1**: Neutral sentiment

## 🎯 Kegunaan

1. **Analisis Produk**: Memahami sentiment konsumen terhadap produk
2. **Market Research**: Mengidentifikasi kelebihan dan kekurangan produk
3. **Quality Control**: Monitoring feedback dan complaint
4. **Competitor Analysis**: Membandingkan sentiment produk sejenis
5. **Machine Learning**: Data yang siap untuk training model sentiment

## ⚙️ Konfigurasi

### Customize Scraping:
```python
# Ubah jumlah maximum review per rating
max_reviews_per_rating = 20

# Pilih rating spesifik
target_ratings = [1, 2, 5]  # Hanya rating 1, 2, dan 5

# Mode headless
scraper = TokopediaReviewScraperImproved(headless=True)
```

### Customize Sentiment Analysis:
```python
# Ubah threshold sentiment
if polarity > 0.2:      # Lebih ketat untuk positive
    sentiment = 'Positive'
elif polarity < -0.2:   # Lebih ketat untuk negative
    sentiment = 'Negative'
```

## 🚨 Catatan Penting

1. **Rate Limiting**: Gunakan delay yang wajar untuk menghindari IP blocking
2. **Legal Compliance**: Pastikan scraping sesuai dengan terms of service
3. **Data Privacy**: Jaga privasi data reviewer
4. **Browser Driver**: Update ChromeDriver secara berkala
5. **Dependencies**: Install semua package yang diperlukan

## 🔄 Troubleshooting

### Common Issues:
1. **ChromeDriver tidak ditemukan**: Download dan tambahkan ke PATH
2. **Timeout**: Increase wait time atau check internet connection
3. **Element not found**: Website structure mungkin berubah
4. **Memory error**: Kurangi jumlah review per batch

### Error Handling:
Script sudah dilengkapi dengan:
- Exception handling untuk setiap fungsi
- Retry mechanism untuk elemen yang tidak ditemukan
- Logging untuk debugging
- Validasi data untuk memastikan kualitas

## 📝 Lisensi

Script ini dibuat untuk keperluan edukasi dan penelitian. Gunakan dengan bijak dan sesuai dengan terms of service website yang di-scrape.

## 🤝 Kontribusi

Silakan fork repository ini dan buat pull request untuk improvement atau bug fixes.

---

**Happy Scraping & Analyzing! 🎉**

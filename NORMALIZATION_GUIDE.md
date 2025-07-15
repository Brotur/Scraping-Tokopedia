# Panduan Normalisasi Data untuk Analisis Sentiment

## Fitur Normalisasi Data yang Ditambahkan

Script `tokopedia_scraper_improved.py` telah dilengkapi dengan fitur normalisasi data yang akan mempersiapkan teks review untuk analisis sentiment.

## Fungsi Normalisasi

### 1. `normalize_text(text)`
Fungsi utama untuk menormalisasi teks review dengan tahapan:
- **Konversi ke lowercase** - Semua huruf menjadi kecil
- **Hapus emoji dan karakter unicode khusus** - Menghapus emoji dan simbol khusus
- **Hapus URL** - Menghapus link yang mungkin ada di review
- **Hapus mention (@username)** - Menghapus mention pengguna
- **Hapus hashtag (#hashtag)** - Menghapus hashtag
- **Hapus tanda baca** - Kecuali spasi, semua tanda baca dihapus
- **Hapus angka yang berdiri sendiri** - Menghapus angka yang tidak berguna
- **Normalisasi spasi** - Menghapus spasi berlebih

### 2. `clean_reviewer_name(name)`
Membersihkan nama reviewer dari karakter khusus dan emoji.

### 3. `clean_variant(variant)`
Membersihkan informasi variant produk.

### 4. `clean_date(date)`
Membersihkan format tanggal dari karakter khusus.

## Output Data

### Data Asli vs Normalisasi
Setiap review akan memiliki kolom:
- `review_text` - Teks asli
- `review_text_normalized` - Teks yang sudah dinormalisasi
- `reviewer_name` - Nama asli
- `reviewer_name_normalized` - Nama yang sudah dibersihkan
- `variant` - Variant asli
- `variant_normalized` - Variant yang sudah dibersihkan
- `review_date` - Tanggal asli
- `review_date_normalized` - Tanggal yang sudah dibersihkan

### File Output

1. **`huawei_matepad_reviews_improved.csv`** - Data lengkap dengan kolom asli dan normalisasi
2. **`huawei_matepad_reviews_improved.json`** - Data lengkap dalam format JSON
3. **`huawei_matepad_sentiment_ready.csv`** - Data yang siap untuk analisis sentiment
4. **`huawei_matepad_sentiment_ready.json`** - Data sentiment dalam format JSON

## Contoh Hasil Normalisasi

### Sebelum Normalisasi:
```
"Pengiriman sangat lama. Walaupun diluar pihak penjual, tetapi ini mempengaruhi pelayanan terjadap konsumen, sehingga saya merasa kurang puas belanja disini. Meskipun bara..."
```

### Setelah Normalisasi:
```
"pengiriman sangat lama walaupun diluar pihak penjual tetapi ini mempengaruhi pelayanan terjadap konsumen sehingga saya merasa kurang puas belanja disini meskipun bara"
```

## Validasi dan Statistik

Script akan menampilkan:
- Total reviews yang berhasil dinormalisasi
- Success rate normalisasi
- Contoh perbandingan teks asli vs normalisasi
- Perbandingan panjang teks sebelum dan sesudah normalisasi

## Penggunaan untuk Analisis Sentiment

File `huawei_matepad_sentiment_ready.csv` atau `huawei_matepad_sentiment_ready.json` sudah siap untuk digunakan dengan library analisis sentiment seperti:
- **TextBlob**
- **VADER Sentiment**
- **Transformers (BERT, RoBERTa)**
- **spaCy**

### Contoh Struktur Data Sentiment-Ready:
```json
{
  "rating": 1,
  "text": "pengiriman sangat lama walaupun diluar pihak penjual tetapi ini mempengaruhi pelayanan terjadap konsumen sehingga saya merasa kurang puas belanja disini",
  "reviewer": "iqwan",
  "variant": "Space Grey",
  "date": "9 bulan lalu",
  "original_text": "Pengiriman sangat lama. Walaupun diluar pihak penjual, tetapi ini mempengaruhi pelayanan terjadap konsumen..."
}
```

## Kelebihan Normalisasi

1. **Konsistensi Data** - Semua teks dalam format yang sama
2. **Mengurangi Noise** - Menghapus karakter yang tidak perlu
3. **Meningkatkan Akurasi** - Analisis sentiment menjadi lebih akurat
4. **Standarisasi** - Format yang seragam untuk semua teks
5. **Siap Analisis** - Dapat langsung digunakan untuk machine learning

## Statistik Hasil Scraping

Dari contoh yang dijalankan:
- **Total reviews**: 61
- **Reviews dengan teks normalisasi**: 55
- **Success rate**: 90.2%
- **Distribusi rating**: 1★(12), 2★(5), 3★(14), 4★(15), 5★(15)

Data sudah siap untuk analisis sentiment dan dapat digunakan untuk berbagai keperluan analisis teks.

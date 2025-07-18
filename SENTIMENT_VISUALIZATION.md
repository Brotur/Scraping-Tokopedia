# Sentiment Visualization dengan Pie Chart

## Fitur Baru: Visualisasi Sentimen Review

### 🎯 Tujuan
Membuat visualisasi sentimen review yang menarik dan informatif menggunakan pie chart untuk memberikan insight yang mudah dipahami tentang pengalaman pelanggan.

### 🎨 Komponen Visualisasi

#### 1. **Pie Chart Interaktif**
- **Library**: Chart.js (CDN)
- **Tipe**: Doughnut chart dengan animasi
- **Warna**: 
  - Positif: #48bb78 (hijau)
  - Netral: #ed8936 (oranye)
  - Negatif: #f56565 (merah)
- **Fitur**: Hover effects, tooltips, animasi rotation

#### 2. **Sentiment Statistics Cards**
- **Positif**: 😊 dengan persentase dan warna hijau
- **Netral**: 😐 dengan persentase dan warna oranye
- **Negatif**: 😞 dengan persentase dan warna merah
- **Animasi**: Hover effects dan scaling

#### 3. **Insight Text**
- Analisis komprehensif berdasarkan data sentimen
- Highlight untuk insight penting
- Peringatan jika sentiment negatif tinggi

### 📊 Contoh Data
```
Berdasarkan 56 review:
- Positif: 30 review (53.6%)
- Netral: 15 review (26.8%)
- Negatif: 11 review (19.6%)
```

### 🔧 Implementasi Teknis

#### HTML Structure
```html
<div id="sentimentAnalysis" class="sentiment-chart-container">
    <h4><i class="fas fa-chart-pie"></i> Analisis Sentimen Review</h4>
    <div class="sentiment-chart-wrapper">
        <canvas id="sentimentChart"></canvas>
    </div>
    <div class="sentiment-summary">
        <div class="sentiment-stats">
            <!-- Sentiment cards -->
        </div>
        <div class="sentiment-insight">
            <!-- Insight text -->
        </div>
    </div>
</div>
```

#### CSS Features
- **Responsive Design**: Grid layout yang menyesuaikan ukuran layar
- **Gradient Backgrounds**: Linear gradients untuk visual appeal
- **Box Shadows**: Depth effects untuk cards
- **Hover Effects**: Transform dan shadow changes
- **Animations**: Smooth transitions dan scaling

#### JavaScript Functions
- `displaySentimentChart(reviews)`: Main function untuk render chart
- `analyzeSentiment(reviews)`: Analisis rating menjadi sentimen
- `updateSentimentInsight(data)`: Generate insight text

### 📱 Responsive Design
- **Desktop**: 3 kolom grid untuk statistics
- **Mobile**: Optimized layout dengan chart yang lebih kecil
- **Chart Height**: 300px desktop, 250px mobile

### 🎭 Animasi dan Interaksi
1. **Chart Animation**: Rotate dan scale saat load
2. **Hover Effects**: Offset pada pie segments
3. **Card Animations**: Scale effects pada hover
4. **Tooltip**: Custom styling dengan informasi detail

### 🔍 Analisis Sentiment Logic
```javascript
Rating >= 4: Positif
Rating = 3: Netral  
Rating < 3: Negatif
```

### 📈 Insight Generation
- Automatic insight berdasarkan distribusi sentimen
- Warning jika sentiment negatif > 30%
- Highlight jika sentiment netral > 25%
- Rekomendasi berdasarkan pola sentimen

### 🧪 Testing
File test: `sentiment-test.html`
- Preview pie chart dengan data sample
- Test responsive design
- Validasi animasi dan interaksi

### 🚀 Integrasi
Chart otomatis muncul ketika:
1. Ada data review tersedia
2. Setelah product info ditampilkan
3. Dalam section yang sama dengan rating distribution

### 📊 Positioning
Visualisasi sentimen ditempatkan di:
- Setelah rating distribution
- Sebelum AI recommendation
- Dalam card product information
- Dengan styling yang konsisten

### 🎯 Value Proposition
- **Visual Appeal**: Pie chart yang menarik dan profesional
- **Quick Insight**: Persentase sentiment yang jelas
- **Comprehensive Analysis**: Text insight yang informatif
- **Interactive Experience**: Hover effects dan tooltips
- **Mobile Friendly**: Responsive design yang optimal

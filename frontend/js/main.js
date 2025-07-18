// API Configuration
const API_BASE_URL = 'http://localhost:8000'; // Main scraper API
const AI_API_BASE_URL = 'http://localhost:8001'; // AI consultant API

// DOM Elements
const productForm = document.getElementById('productForm');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingState = document.getElementById('loadingState');
const errorMessage = document.getElementById('errorMessage');
const resultsSection = document.getElementById('resultsSection');

// Loading steps
const loadingSteps = {
    step1: document.getElementById('step1'),
    step2: document.getElementById('step2'),
    step3: document.getElementById('step3')
};

// Form submission handler
productForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const productUrl = document.getElementById('productUrl').value.trim();
    const userBudget = document.getElementById('userBudget').value;
    const userPreferences = document.getElementById('userPreferences').value.trim();
    
    if (!productUrl) {
        showError('URL produk harus diisi');
        return;
    }
    
    if (!isValidTokopediaUrl(productUrl)) {
        showError('URL harus dari Tokopedia (tokopedia.com)');
        return;
    }
    
    await analyzeProduct(productUrl, userBudget, userPreferences);
});

// Validate Tokopedia URL
function isValidTokopediaUrl(url) {
    try {
        const urlObj = new URL(url);
        return urlObj.hostname.includes('tokopedia.com');
    } catch {
        return false;
    }
}

// Show loading state
function showLoading() {
    hideError();
    hideResults();
    loadingState.style.display = 'block';
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Menganalisis...';
    
    // Reset steps
    Object.values(loadingSteps).forEach(step => step.classList.remove('active'));
}

// Hide loading state
function hideLoading() {
    loadingState.style.display = 'none';
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analisis Produk';
    
    // Reset steps
    Object.values(loadingSteps).forEach(step => step.classList.remove('active'));
}

// Activate loading step
function activateLoadingStep(stepNumber) {
    const step = loadingSteps[`step${stepNumber}`];
    if (step) {
        step.classList.add('active');
    }
}

// Show error message
function showError(message) {
    hideLoading();
    hideResults();
    document.getElementById('errorText').textContent = message;
    errorMessage.style.display = 'block';
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

// Hide error message
function hideError() {
    errorMessage.style.display = 'none';
}

// Show results
function showResults() {
    hideLoading();
    hideError();
    resultsSection.style.display = 'block';
    
    // Smooth scroll to results
    resultsSection.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

// Hide results
function hideResults() {
    resultsSection.style.display = 'none';
}

// Main analysis function
async function analyzeProduct(productUrl, userBudget, userPreferences) {
    try {
        showLoading();
        
        // Step 1: Extract product details
        activateLoadingStep(1);
        console.log('🔍 Step 1: Extracting product details...');
        
        const productData = await extractProductDetails(productUrl);
        console.log('✅ Step 1 completed:', productData);
        
        // Step 2: Get AI analysis
        activateLoadingStep(2);
        console.log('🤖 Step 2: Getting AI analysis...');
        
        const aiAnalysis = await getAIAnalysis(productData, userBudget, userPreferences);
        console.log('✅ Step 2 completed:', aiAnalysis);
        
        // Step 3: Display results
        activateLoadingStep(3);
        console.log('📋 Step 3: Displaying results...');
        
        displayResults(productData, aiAnalysis);
        console.log('✅ All steps completed successfully');
        
        showResults();
        
    } catch (error) {
        console.error('❌ Analysis error:', error);
        showError(error.message || 'Terjadi kesalahan saat menganalisis produk');
    } finally {
        hideLoading();
    }
}

// Extract product details from Tokopedia
async function extractProductDetails(productUrl) {
    try {
        console.log('🔍 Extracting product details from:', productUrl);
        
        const requestPayload = {
            url: productUrl,
            target_ratings: [1, 2, 3, 4, 5],
            max_reviews_per_rating: 15,
            headless: false
        };
        
        console.log('📤 Request payload:', requestPayload);
        
        const response = await fetch(`${API_BASE_URL}/scrape-with-details`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestPayload)
        });
        
        console.log('📥 Response status:', response.status);
        console.log('📥 Response ok:', response.ok);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Response error:', errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('📊 Full response data:', data);
        console.log('📊 Response keys:', Object.keys(data));
        
        // Check if we have product_details
        if (!data.product_details) {
            console.error('❌ No product_details in response');
            console.log('Available keys:', Object.keys(data));
            throw new Error('Response tidak mengandung product_details');
        }
        
        const productDetails = data.product_details;
        console.log('✅ Product details found:', productDetails);
        console.log('✅ Product details keys:', Object.keys(productDetails));
        
        // Also include reviews and summary for enhanced AI analysis
        const fullData = {
            product_details: productDetails,
            reviews: data.reviews || [],
            summary: data.summary || {}
        };
        
        console.log('✅ Full scraping data:', {
            product_details: 'included',
            reviews: fullData.reviews.length,
            summary: fullData.summary ? 'included' : 'not available'
        });
        
        // Validate essential fields
        const essentialFields = ['product_name', 'price', 'rating'];
        const missingFields = essentialFields.filter(field => !productDetails[field]);
        
        if (missingFields.length > 0) {
            console.warn('⚠️ Missing essential fields:', missingFields);
            // But don't throw error, just warn
        }
        
        return fullData;
        
    } catch (error) {
        console.error('❌ Error in extractProductDetails:', error);
        
        // Provide more detailed error information
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Tidak dapat terhubung ke server scraper. Pastikan server berjalan di http://localhost:8000');
        }
        
        if (error.message.includes('HTTP')) {
            throw new Error(`Server error: ${error.message}`);
        }
        
        throw new Error(`Gagal mengekstrak data produk: ${error.message}`);
    }
}

// Get AI analysis
async function getAIAnalysis(scrapingData, userBudget, userPreferences) {
    try {
        console.log('🔍 Preparing AI analysis request...');
        console.log('📊 Scraping data received:', scrapingData);
        
        // Extract product details
        const productDetails = scrapingData.product_details || scrapingData;
        
        // Check if we have the new format with full scraping data
        const hasFullData = scrapingData.product_details && scrapingData.reviews;
        
        let requestData;
        
        if (hasFullData) {
            // New format - use full scraping response with reviews
            console.log('📊 Using enhanced format with reviews');
            console.log('📊 Reviews count:', scrapingData.reviews.length);
            
            requestData = {
                product_details: {
                    product_name: productDetails.product_name,
                    store_name: productDetails.store_name,
                    product_url: productDetails.product_url || '',
                    price: productDetails.price,
                    rating: productDetails.rating || 0,
                    rating_count: productDetails.rating_count || 0,
                    sold_count: productDetails.sold_count || 'Tidak tersedia',
                    description: productDetails.description || 'Tidak tersedia'
                },
                reviews: scrapingData.reviews,
                summary: scrapingData.summary
            };
        } else {
            // Fallback format
            console.log('📊 Using fallback format');
            const hasProductDetails = productDetails.product_name && productDetails.store_name;
            
            if (hasProductDetails) {
                requestData = {
                    product_details: {
                        product_name: productDetails.product_name,
                        store_name: productDetails.store_name,
                        product_url: productDetails.product_url || '',
                        price: productDetails.price,
                        rating: productDetails.rating || 0,
                        rating_count: productDetails.rating_count || 0,
                        sold_count: productDetails.sold_count || 'Tidak tersedia',
                        description: productDetails.description || 'Tidak tersedia'
                    }
                };
            } else {
                requestData = {
                    product_data: {
                        name: productDetails.product_name || 'Tidak tersedia',
                        price: productDetails.price || 'Tidak tersedia',
                        rating: productDetails.rating || 0,
                        total_ratings: productDetails.rating_count || 0,
                        sold_count: productDetails.sold_count || 'Tidak tersedia',
                        store_type: productDetails.store_name || 'Tidak tersedia',
                        store_rating: productDetails.store_rating || 0,
                        store_reviews: productDetails.store_reviews || 0,
                        processing_time: productDetails.processing_time || 'Tidak tersedia',
                        description: productDetails.description || 'Tidak tersedia',
                        url: productDetails.product_url || productDetails.review_url || ''
                    }
                };
            }
        }
        
        // Add optional fields if provided
        if (userBudget && !isNaN(parseFloat(userBudget.replace(/\D/g, '')))) {
            requestData.user_budget = parseFloat(userBudget.replace(/\D/g, ''));
        }
        
        if (userPreferences) {
            requestData.user_preferences = userPreferences;
        }
        
        console.log('📤 AI request data:', requestData);
        
        // Use the flexible endpoint that can handle both formats
        const response = await fetch(`${AI_API_BASE_URL}/ai-consultant-flexible`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        console.log('📥 AI response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ AI API error response:', errorText);
            
            try {
                const errorData = JSON.parse(errorText);
                throw new Error(errorData.detail || `HTTP ${response.status}: ${errorText}`);
            } catch (parseError) {
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
        }
        
        const aiResult = await response.json();
        console.log('✅ AI analysis completed:', aiResult);
        
        return aiResult;
        
    } catch (error) {
        console.error('❌ Error in getAIAnalysis:', error);
        
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Tidak dapat terhubung ke AI consultant. Pastikan AI API berjalan di port 8001');
        }
        throw error;
    }
}

// Display results in the UI
function displayResults(productData, aiAnalysis) {
    // Product information
    displayProductInfo(productData);
    
    // AI recommendation
    displayAIRecommendation(aiAnalysis);
    
    // Analysis details
    displayAnalysisDetails(aiAnalysis);
    
    // Display sentiment analysis from AI if available
    if (aiAnalysis.sentiment_analysis) {
        displayAISentimentAnalysis(aiAnalysis.sentiment_analysis);
    } else if (productData.reviews && productData.reviews.length > 0) {
        // Fallback to frontend sentiment analysis
        sentimentAnalyzer.displayChart(productData.reviews);
    }
}

// Initialize sentiment analyzer
const sentimentAnalyzer = new SentimentAnalyzer();

// Display product information
function displayProductInfo(scrapingData) {
    console.log('📊 Displaying product info:', scrapingData);
    
    // Extract product details from the scraping data
    const productData = scrapingData.product_details || scrapingData;
    
    // Product name dengan fallback
    const productName = productData.product_name || 'Nama produk tidak tersedia';
    document.getElementById('productName').textContent = productName;
    
    // Price dengan fallback
    const price = productData.price || 'Harga tidak tersedia';
    document.getElementById('productPrice').textContent = price;
    
    // Rating dengan fallback
    const rating = productData.rating ? `${productData.rating} ⭐` : 'Rating tidak tersedia';
    document.getElementById('productRating').textContent = rating;
    
    // Reviews dengan fallback
    const reviews = productData.rating_count || 'Ulasan tidak tersedia';
    document.getElementById('productReviews').textContent = reviews;
    
    // Sold count dengan fallback
    const sold = productData.sold_count || 'Data penjualan tidak tersedia';
    document.getElementById('productSold').textContent = sold;
    
    // Store info dengan fallback
    const storeName = productData.store_name || 'Info toko tidak tersedia';
    document.getElementById('storeInfo').textContent = storeName;
    
    // Add review analysis info if available
    if (scrapingData.reviews && scrapingData.reviews.length > 0) {
        const reviewAnalysisElement = document.getElementById('reviewAnalysis');
        if (reviewAnalysisElement) {
            const reviewCount = scrapingData.reviews.length;
            const ratingDistribution = {};
            
            scrapingData.reviews.forEach(review => {
                ratingDistribution[review.rating] = (ratingDistribution[review.rating] || 0) + 1;
            });
            
            reviewAnalysisElement.innerHTML = `
                <div class="review-analysis">
                    <h4>📊 Analisis Review (${reviewCount} ulasan)</h4>
                    <div class="rating-distribution">
                        ${Object.entries(ratingDistribution).map(([rating, count]) => 
                            `<span class="rating-item">★${rating}: ${count}</span>`
                        ).join(' ')}
                    </div>
                </div>
            `;
        }
    }
    
    console.log('✅ Product info displayed successfully');
}

// Display AI-powered sentiment analysis
function displayAISentimentAnalysis(sentimentData) {
    console.log('🤖 Displaying AI sentiment analysis:', sentimentData);
    
    const sentimentContainer = document.getElementById('sentimentChart');
    if (!sentimentContainer) return;
    
    // Create enhanced sentiment display
    sentimentContainer.innerHTML = `
        <div class="sentiment-ai-analysis">
            <h3>🤖 AI Sentiment Analysis</h3>
            
            <div class="sentiment-summary">
                <div class="sentiment-percentages">
                    <div class="sentiment-item positive">
                        <div class="sentiment-icon">😊</div>
                        <div class="sentiment-data">
                            <span class="sentiment-label">Positif</span>
                            <span class="sentiment-value">${sentimentData.positive_percentage}%</span>
                            <span class="sentiment-count">(${sentimentData.positive_count} ulasan)</span>
                        </div>
                    </div>
                    <div class="sentiment-item neutral">
                        <div class="sentiment-icon">😐</div>
                        <div class="sentiment-data">
                            <span class="sentiment-label">Netral</span>
                            <span class="sentiment-value">${sentimentData.neutral_percentage}%</span>
                            <span class="sentiment-count">(${sentimentData.neutral_count} ulasan)</span>
                        </div>
                    </div>
                    <div class="sentiment-item negative">
                        <div class="sentiment-icon">😞</div>
                        <div class="sentiment-data">
                            <span class="sentiment-label">Negatif</span>
                            <span class="sentiment-value">${sentimentData.negative_percentage}%</span>
                            <span class="sentiment-count">(${sentimentData.negative_count} ulasan)</span>
                        </div>
                    </div>
                </div>
                
                <div class="sentiment-insights">
                    <div class="sentiment-summary-text">
                        <h4>📊 Ringkasan Sentiment</h4>
                        <p>${sentimentData.sentiment_summary}</p>
                    </div>
                    
                    ${sentimentData.key_themes && sentimentData.key_themes.length > 0 ? `
                        <div class="sentiment-themes">
                            <h4>🔍 Tema Utama</h4>
                            <div class="theme-tags">
                                ${sentimentData.key_themes.map(theme => `
                                    <span class="theme-tag">${theme}</span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${sentimentData.emotional_indicators && sentimentData.emotional_indicators.length > 0 ? `
                        <div class="sentiment-emotions">
                            <h4>💭 Indikator Emosional</h4>
                            <div class="emotion-tags">
                                ${sentimentData.emotional_indicators.map(emotion => `
                                    <span class="emotion-tag">${emotion}</span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
            
            <div class="sentiment-chart-container">
                <canvas id="aiSentimentChart" width="400" height="200"></canvas>
            </div>
        </div>
    `;
    
    // Create chart using Chart.js
    const ctx = document.getElementById('aiSentimentChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positif', 'Netral', 'Negatif'],
            datasets: [{
                data: [
                    sentimentData.positive_percentage,
                    sentimentData.neutral_percentage,
                    sentimentData.negative_percentage
                ],
                backgroundColor: [
                    '#4CAF50',
                    '#FFC107',
                    '#F44336'
                ],
                borderColor: [
                    '#45a049',
                    '#ffb300',
                    '#da190b'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 20,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const counts = [
                                sentimentData.positive_count,
                                sentimentData.neutral_count,
                                sentimentData.negative_count
                            ];
                            return `${label}: ${value}% (${counts[context.dataIndex]} ulasan)`;
                        }
                    }
                }
            },
            animation: {
                animateScale: true,
                duration: 1500
            }
        }
    });
    
    console.log('✅ AI sentiment analysis displayed successfully');
}

// Display AI recommendation with enhanced confidence visualization
function displayAIRecommendation(aiAnalysis) {
    const recommendationBadge = document.getElementById('recommendationBadge');
    const confidenceFill = document.getElementById('confidenceFill');
    const confidenceText = document.getElementById('confidenceText');
    const analysisText = document.getElementById('analysisText');
    
    // Recommendation badge
    recommendationBadge.textContent = formatRecommendation(aiAnalysis.recommendation);
    recommendationBadge.className = `recommendation-badge ${aiAnalysis.recommendation.toLowerCase().replace(/_/g, '-')}`;
    
    // Enhanced confidence score visualization
    const confidencePercent = Math.round(aiAnalysis.confidence_score * 100);
    const confidenceContainer = document.getElementById('confidenceContainer');
    
    // Create enhanced confidence display
    if (confidenceContainer) {
        confidenceContainer.innerHTML = `
            <div class="confidence-display">
                <div class="confidence-header">
                    <h3>🎯 Tingkat Kepercayaan AI</h3>
                    <div class="confidence-score ${getConfidenceClass(confidencePercent)}">
                        ${confidencePercent}%
                    </div>
                </div>
                
                <div class="confidence-bar-container">
                    <div class="confidence-bar">
                        <div class="confidence-fill ${getConfidenceClass(confidencePercent)}" 
                             style="width: ${confidencePercent}%; transition: width 1.5s ease-out;">
                        </div>
                        <div class="confidence-markers">
                            <div class="marker" style="left: 25%">25%</div>
                            <div class="marker" style="left: 50%">50%</div>
                            <div class="marker" style="left: 75%">75%</div>
                        </div>
                    </div>
                </div>
                
                <div class="confidence-interpretation">
                    <div class="confidence-label">
                        <span class="confidence-icon">${getConfidenceIcon(confidencePercent)}</span>
                        <span class="confidence-text">${getConfidenceText(confidencePercent)}</span>
                    </div>
                    <div class="confidence-description">
                        ${getConfidenceDescription(confidencePercent)}
                    </div>
                </div>
                
                <div class="confidence-metrics">
                    <div class="metric">
                        <span class="metric-label">Akurasi Prediksi</span>
                        <span class="metric-value">${confidencePercent}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Basis Analisis</span>
                        <span class="metric-value">AI + Review Data</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Tingkat Risiko</span>
                        <span class="metric-value">${getRiskLevel(confidencePercent)}</span>
                    </div>
                </div>
            </div>
        `;
    } else {
        // Fallback for existing elements
        confidenceFill.style.width = `${confidencePercent}%`;
        confidenceText.textContent = `${confidencePercent}%`;
    }
    
    // Analysis text
    analysisText.textContent = aiAnalysis.analysis;
    
    // Add confidence animation
    setTimeout(() => {
        const fill = document.querySelector('.confidence-fill');
        if (fill) {
            fill.style.width = `${confidencePercent}%`;
        }
    }, 500);
}

// Helper functions for confidence display
function getConfidenceClass(percentage) {
    if (percentage >= 85) return 'confidence-very-high';
    if (percentage >= 70) return 'confidence-high';
    if (percentage >= 55) return 'confidence-medium';
    if (percentage >= 40) return 'confidence-low';
    return 'confidence-very-low';
}

function getConfidenceIcon(percentage) {
    if (percentage >= 85) return '🚀';
    if (percentage >= 70) return '✅';
    if (percentage >= 55) return '⚖️';
    if (percentage >= 40) return '⚠️';
    return '❌';
}

function getConfidenceText(percentage) {
    if (percentage >= 85) return 'Sangat Tinggi';
    if (percentage >= 70) return 'Tinggi';
    if (percentage >= 55) return 'Sedang';
    if (percentage >= 40) return 'Rendah';
    return 'Sangat Rendah';
}

function getConfidenceDescription(percentage) {
    if (percentage >= 85) return 'AI sangat yakin dengan rekomendasi ini berdasarkan analisis mendalam data produk dan review pelanggan.';
    if (percentage >= 70) return 'AI cukup yakin dengan rekomendasi ini berdasarkan data yang tersedia dan pola review positif.';
    if (percentage >= 55) return 'AI memberikan rekomendasi dengan tingkat kepercayaan moderat. Pertimbangkan faktor tambahan.';
    if (percentage >= 40) return 'AI memiliki keraguan dalam rekomendasi ini. Disarankan untuk riset lebih lanjut.';
    return 'AI tidak yakin dengan rekomendasi ini. Sebaiknya cari alternatif produk lain.';
}

function getRiskLevel(percentage) {
    if (percentage >= 85) return 'Sangat Rendah';
    if (percentage >= 70) return 'Rendah';
    if (percentage >= 55) return 'Sedang';
    if (percentage >= 40) return 'Tinggi';
    return 'Sangat Tinggi';
}

// Display analysis details
function displayAnalysisDetails(aiAnalysis) {
    // Pros
    const prosList = document.getElementById('prosList');
    prosList.innerHTML = '';
    if (aiAnalysis.pros && aiAnalysis.pros.length > 0) {
        aiAnalysis.pros.forEach(pro => {
            const li = document.createElement('li');
            li.textContent = pro;
            prosList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'Tidak ada keunggulan yang diidentifikasi';
        prosList.appendChild(li);
    }
    
    // Cons
    const consList = document.getElementById('consList');
    consList.innerHTML = '';
    if (aiAnalysis.cons && aiAnalysis.cons.length > 0) {
        aiAnalysis.cons.forEach(con => {
            const li = document.createElement('li');
            li.textContent = con;
            consList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'Tidak ada kekurangan yang diidentifikasi';
        consList.appendChild(li);
    }
    
    // Key insights
    const insightsList = document.getElementById('insightsList');
    insightsList.innerHTML = '';
    if (aiAnalysis.key_insights && aiAnalysis.key_insights.length > 0) {
        aiAnalysis.key_insights.forEach(insight => {
            const li = document.createElement('li');
            li.textContent = insight;
            insightsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'Tidak ada insight khusus';
        insightsList.appendChild(li);
    }
    
    // Budget analysis (if available)
    const budgetCard = document.getElementById('budgetCard');
    const budgetAnalysis = document.getElementById('budgetAnalysis');
    
    if (aiAnalysis.budget_analysis) {
        budgetAnalysis.textContent = aiAnalysis.budget_analysis;
        budgetCard.style.display = 'block';
    } else {
        budgetCard.style.display = 'none';
    }
}

// Format recommendation text
function formatRecommendation(recommendation) {
    switch (recommendation) {
        case 'LAYAK_BELI':
            return 'Layak Beli';
        case 'TIDAK_LAYAK_BELI':
            return 'Tidak Layak Beli';
        case 'LAYAK_BELI_DENGAN_CATATAN':
            return 'Layak Beli dengan Catatan';
        default:
            return recommendation;
    }
}

// Format currency (Indonesian Rupiah)
function formatCurrency(amount) {
    if (!amount || isNaN(amount)) return amount;
    
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// Utility function to truncate text
function truncateText(text, maxLength = 100) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Add smooth scrolling for all anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add input validation feedback
document.getElementById('productUrl').addEventListener('input', function() {
    const url = this.value.trim();
    
    if (url && !isValidTokopediaUrl(url)) {
        this.style.borderColor = '#e53e3e';
        this.style.boxShadow = '0 0 0 3px rgba(229, 62, 62, 0.1)';
    } else {
        this.style.borderColor = '#e2e8f0';
        this.style.boxShadow = 'none';
    }
});

// Add number formatting for budget input
document.getElementById('userBudget').addEventListener('input', function() {
    let value = this.value.replace(/\D/g, ''); // Remove non-digits
    
    if (value) {
        // Add thousand separators
        value = parseInt(value).toLocaleString('id-ID');
        this.value = value;
    }
});

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Shopping Consultant initialized');
    
    // Check if APIs are available
    checkAPIStatus();
});

// Check API status
async function checkAPIStatus() {
    try {
        // Check main scraper API
        const scraperResponse = await fetch(`${API_BASE_URL}/`, { 
            method: 'GET',
            signal: AbortSignal.timeout(5000)
        });
        
        // Check AI consultant API
        const aiResponse = await fetch(`${AI_API_BASE_URL}/health`, { 
            method: 'GET',
            signal: AbortSignal.timeout(5000)
        });
        
        if (!scraperResponse.ok || !aiResponse.ok) {
            console.warn('Some APIs may not be available');
        } else {
            console.log('All APIs are available');
        }
        
    } catch (error) {
        console.warn('API status check failed:', error.message);
    }
}

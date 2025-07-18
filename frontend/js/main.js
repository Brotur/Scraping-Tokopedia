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
        const productData = await extractProductDetails(productUrl);
        
        // Step 2: Get AI analysis
        activateLoadingStep(2);
        const aiAnalysis = await getAIAnalysis(productData, userBudget, userPreferences);
        
        // Step 3: Display results
        activateLoadingStep(3);
        displayResults(productData, aiAnalysis);
        
        showResults();
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Terjadi kesalahan saat menganalisis produk');
    }
}

// Extract product details from Tokopedia
async function extractProductDetails(productUrl) {
    try {
        // Use scrape-with-details endpoint to get comprehensive data
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
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}: Gagal mengambil data produk`);
        }
        
        const data = await response.json();
        
        // Check if we have product_details in the response
        if (!data.product_details) {
            throw new Error('Data produk tidak ditemukan dalam response');
        }
        
        // Return the product_details from scrape-with-details response
        return data.product_details;
        
    } catch (error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Tidak dapat terhubung ke server. Pastikan API scraper berjalan di port 8000');
        }
        throw error;
    }
}

// Get AI analysis
async function getAIAnalysis(productData, userBudget, userPreferences) {
    try {
        const requestData = {
            product_data: {
                name: productData.product_name || 'Tidak tersedia',
                price: productData.price || 'Tidak tersedia',
                rating: productData.rating || 0,
                total_ratings: productData.rating_count || 0,
                sold_count: productData.sold_count || 'Tidak tersedia',
                store_type: productData.store_name || 'Tidak tersedia',
                store_rating: productData.store_rating || 0,
                store_reviews: productData.store_reviews || 0,
                processing_time: productData.processing_time || 'Tidak tersedia',
                description: productData.description || 'Tidak tersedia',
                url: productData.product_url || productData.review_url || ''
            }
        };
        
        // Add optional fields if provided
        if (userBudget && !isNaN(parseFloat(userBudget))) {
            requestData.user_budget = parseFloat(userBudget);
        }
        
        if (userPreferences) {
            requestData.user_preferences = userPreferences;
        }
        
        const response = await fetch(`${AI_API_BASE_URL}/ai-consultant`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}: Gagal mendapatkan analisis AI`);
        }
        
        return await response.json();
        
    } catch (error) {
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
}

// Display product information
function displayProductInfo(productData) {
    // Map fields from scrape-with-details response
    document.getElementById('productName').textContent = 
        productData.product_name || 'Nama produk tidak tersedia';
    
    document.getElementById('productPrice').textContent = 
        productData.price || 'Harga tidak tersedia';
    
    // Product stats
    document.getElementById('productRating').textContent = 
        productData.rating ? `${productData.rating} ⭐` : 'Rating tidak tersedia';
    
    document.getElementById('productReviews').textContent = 
        productData.rating_count ? `${productData.rating_count}` : 'Ulasan tidak tersedia';
    
    document.getElementById('productSold').textContent = 
        productData.sold_count ? `${productData.sold_count}` : 'Data penjualan tidak tersedia';
    
    // Store information
    document.getElementById('storeInfo').textContent = 
        productData.store_name || 'Info toko tidak tersedia';
}

// Display AI recommendation
function displayAIRecommendation(aiAnalysis) {
    const recommendationBadge = document.getElementById('recommendationBadge');
    const confidenceFill = document.getElementById('confidenceFill');
    const confidenceText = document.getElementById('confidenceText');
    const analysisText = document.getElementById('analysisText');
    
    // Recommendation badge
    recommendationBadge.textContent = formatRecommendation(aiAnalysis.recommendation);
    recommendationBadge.className = `recommendation-badge ${aiAnalysis.recommendation.toLowerCase().replace(/_/g, '-')}`;
    
    // Confidence score
    const confidencePercent = Math.round(aiAnalysis.confidence_score * 100);
    confidenceFill.style.width = `${confidencePercent}%`;
    confidenceText.textContent = `${confidencePercent}%`;
    
    // Analysis text
    analysisText.textContent = aiAnalysis.analysis;
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

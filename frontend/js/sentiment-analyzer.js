// Sentiment Analysis Module
class SentimentAnalyzer {
    constructor() {
        this.chart = null;
        this.colors = {
            positive: {
                background: '#48bb78',
                border: '#38a169',
                hover: '#68d391'
            },
            neutral: {
                background: '#ed8936',
                border: '#dd6b20',
                hover: '#f6ad55'
            },
            negative: {
                background: '#f56565',
                border: '#e53e3e',
                hover: '#fc8181'
            }
        };
    }

    // Analyze sentiment from reviews
    analyzeSentiment(reviews) {
        if (!reviews || reviews.length === 0) {
            return null;
        }

        let positive = 0;
        let neutral = 0;
        let negative = 0;

        reviews.forEach(review => {
            const rating = parseFloat(review.rating);
            
            if (rating >= 4) {
                positive++;
            } else if (rating >= 3) {
                neutral++;
            } else {
                negative++;
            }
        });

        const total = reviews.length;

        return {
            positive: positive,
            neutral: neutral,
            negative: negative,
            total: total,
            positivePercent: Math.round((positive / total) * 100),
            neutralPercent: Math.round((neutral / total) * 100),
            negativePercent: Math.round((negative / total) * 100)
        };
    }

    // Create and display sentiment chart
    displayChart(reviews, containerId = 'sentimentAnalysis') {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('Sentiment container not found');
            return;
        }

        const sentimentData = this.analyzeSentiment(reviews);
        if (!sentimentData) {
            container.style.display = 'none';
            return;
        }

        // Show container
        container.style.display = 'block';

        // Update percentage displays
        this.updatePercentageDisplays(sentimentData);

        // Create chart
        this.createChart(sentimentData);

        // Update insight
        this.updateInsight(sentimentData);

        // Add animations
        this.addAnimations();
    }

    // Update percentage displays
    updatePercentageDisplays(data) {
        const elements = {
            positive: document.getElementById('positivePercent'),
            neutral: document.getElementById('neutralPercent'),
            negative: document.getElementById('negativePercent')
        };

        if (elements.positive) elements.positive.textContent = `${data.positivePercent}%`;
        if (elements.neutral) elements.neutral.textContent = `${data.neutralPercent}%`;
        if (elements.negative) elements.negative.textContent = `${data.negativePercent}%`;
    }

    // Create pie chart
    createChart(data) {
        const ctx = document.getElementById('sentimentChart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.chart) {
            this.chart.destroy();
        }

        // Create new chart
        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Positif', 'Netral', 'Negatif'],
                datasets: [{
                    data: [data.positive, data.neutral, data.negative],
                    backgroundColor: [
                        this.colors.positive.background,
                        this.colors.neutral.background,
                        this.colors.negative.background
                    ],
                    borderColor: [
                        this.colors.positive.border,
                        this.colors.neutral.border,
                        this.colors.negative.border
                    ],
                    borderWidth: 3,
                    hoverBackgroundColor: [
                        this.colors.positive.hover,
                        this.colors.neutral.hover,
                        this.colors.negative.hover
                    ],
                    hoverBorderWidth: 4,
                    hoverOffset: 20
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 25,
                            font: {
                                size: 14,
                                weight: 'bold'
                            },
                            color: '#2d3748',
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} review (${percentage}%)`;
                            }
                        },
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#667eea',
                        borderWidth: 2,
                        cornerRadius: 8,
                        displayColors: true
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 2000,
                    easing: 'easeOutBounce'
                }
            }
        });
    }

    // Update sentiment insight
    updateInsight(data) {
        const insightElement = document.getElementById('sentimentInsight');
        if (!insightElement) return;

        let insight = `<strong>Analisis komprehensif berdasarkan ${data.total} review pelanggan:</strong> `;

        // Main sentiment analysis
        if (data.positivePercent > 60) {
            insight += `<strong style="color: #48bb78;">Sentimen sangat positif</strong> (${data.positivePercent}%) mendominasi. Mayoritas pelanggan sangat puas dengan produk ini.`;
        } else if (data.positivePercent > 40) {
            insight += `<strong style="color: #48bb78;">Sentimen positif</strong> (${data.positivePercent}%) cukup dominan. Sebagian besar pelanggan memiliki pengalaman yang baik.`;
        } else {
            insight += `<strong style="color: #ed8936;">Sentimen beragam</strong> dengan distribusi yang perlu diperhatikan.`;
        }

        // Neutral sentiment analysis
        if (data.neutralPercent > 25) {
            insight += ` Persentase review <strong style="color: #ed8936;">netral (${data.neutralPercent}%)</strong> cukup signifikan, menunjukkan adanya area yang bisa diperbaiki.`;
        }

        // Negative sentiment warning
        if (data.negativePercent > 30) {
            insight += ` <strong style="color: #f56565;">⚠️ Perhatian:</strong> Review negatif (${data.negativePercent}%) cukup tinggi. Disarankan untuk membaca detail keluhan pelanggan sebelum membeli.`;
        } else if (data.negativePercent > 20) {
            insight += ` Review negatif (${data.negativePercent}%) masih dalam batas wajar namun tetap perlu dipertimbangkan.`;
        }

        // Recommendation based on sentiment
        if (data.positivePercent > 60 && data.negativePercent < 20) {
            insight += ` <strong style="color: #48bb78;">✅ Rekomendasi:</strong> Produk ini memiliki tingkat kepuasan pelanggan yang tinggi.`;
        } else if (data.negativePercent > 30) {
            insight += ` <strong style="color: #f56565;">❌ Perhatian:</strong> Sebaiknya pertimbangkan alternatif lain atau riset lebih mendalam.`;
        } else {
            insight += ` <strong style="color: #ed8936;">⚖️ Pertimbangan:</strong> Analisis review secara detail sebelum memutuskan pembelian.`;
        }

        insightElement.innerHTML = insight;
    }

    // Add animations to sentiment cards
    addAnimations() {
        setTimeout(() => {
            const stats = document.querySelectorAll('.sentiment-stat');
            stats.forEach((stat, index) => {
                setTimeout(() => {
                    stat.style.animation = 'pulse 0.6s ease-in-out';
                }, index * 300);
            });
        }, 1000);
    }

    // Get sentiment distribution summary
    getSentimentSummary(reviews) {
        const data = this.analyzeSentiment(reviews);
        if (!data) return null;

        return {
            dominant: data.positivePercent > data.neutralPercent && data.positivePercent > data.negativePercent ? 'positive' :
                     data.neutralPercent > data.positivePercent && data.neutralPercent > data.negativePercent ? 'neutral' : 'negative',
            distribution: data,
            recommendation: this.getRecommendationLevel(data)
        };
    }

    // Get recommendation level based on sentiment
    getRecommendationLevel(data) {
        if (data.positivePercent > 70 && data.negativePercent < 15) {
            return 'highly_recommended';
        } else if (data.positivePercent > 50 && data.negativePercent < 25) {
            return 'recommended';
        } else if (data.negativePercent > 40) {
            return 'not_recommended';
        } else {
            return 'neutral';
        }
    }

    // Destroy chart when needed
    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// Export for use in main application
window.SentimentAnalyzer = SentimentAnalyzer;

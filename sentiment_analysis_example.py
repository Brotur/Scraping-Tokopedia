import pandas as pd
import json
from textblob import TextBlob
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re
from collections import Counter

class SentimentAnalyzer:
    def __init__(self, data_file):
        """Initialize dengan file data yang sudah dinormalisasi"""
        self.data_file = data_file
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Load data dari CSV atau JSON"""
        if self.data_file.endswith('.csv'):
            self.df = pd.read_csv(self.data_file)
        elif self.data_file.endswith('.json'):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.df = pd.DataFrame(data)
        
        print(f"Loaded {len(self.df)} reviews for sentiment analysis")
        
    def analyze_sentiment(self):
        """Analisis sentiment menggunakan TextBlob"""
        if self.df is None:
            print("No data loaded")
            return
            
        sentiments = []
        polarities = []
        subjectivities = []
        
        for text in self.df['text']:
            try:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                subjectivity = blob.sentiment.subjectivity
                
                # Klasifikasi sentiment
                if polarity > 0.1:
                    sentiment = 'Positive'
                elif polarity < -0.1:
                    sentiment = 'Negative'
                else:
                    sentiment = 'Neutral'
                    
                sentiments.append(sentiment)
                polarities.append(polarity)
                subjectivities.append(subjectivity)
                
            except Exception as e:
                print(f"Error analyzing text: {e}")
                sentiments.append('Neutral')
                polarities.append(0)
                subjectivities.append(0)
        
        # Tambahkan ke dataframe
        self.df['sentiment'] = sentiments
        self.df['polarity'] = polarities
        self.df['subjectivity'] = subjectivities
        
        print("Sentiment analysis completed!")
        
    def sentiment_summary(self):
        """Ringkasan hasil analisis sentiment"""
        if 'sentiment' not in self.df.columns:
            print("Please run analyze_sentiment() first")
            return
            
        print("\n=== SENTIMENT ANALYSIS SUMMARY ===")
        
        # Overall sentiment distribution
        sentiment_counts = self.df['sentiment'].value_counts()
        print(f"\nOverall Sentiment Distribution:")
        for sentiment, count in sentiment_counts.items():
            percentage = (count / len(self.df)) * 100
            print(f"{sentiment}: {count} reviews ({percentage:.1f}%)")
        
        # Sentiment by rating
        print(f"\nSentiment by Rating:")
        rating_sentiment = pd.crosstab(self.df['rating'], self.df['sentiment'])
        print(rating_sentiment)
        
        # Average polarity by rating
        print(f"\nAverage Polarity by Rating:")
        avg_polarity = self.df.groupby('rating')['polarity'].mean()
        for rating, polarity in avg_polarity.items():
            print(f"Rating {rating}: {polarity:.3f}")
        
        # Most positive and negative reviews
        print(f"\nMost Positive Review (polarity: {self.df['polarity'].max():.3f}):")
        most_positive = self.df.loc[self.df['polarity'].idxmax()]
        print(f"Text: {most_positive['text'][:100]}...")
        print(f"Rating: {most_positive['rating']}")
        
        print(f"\nMost Negative Review (polarity: {self.df['polarity'].min():.3f}):")
        most_negative = self.df.loc[self.df['polarity'].idxmin()]
        print(f"Text: {most_negative['text'][:100]}...")
        print(f"Rating: {most_negative['rating']}")
        
    def extract_common_words(self, sentiment_type='all', top_n=20):
        """Extract kata-kata yang paling sering muncul"""
        if sentiment_type == 'all':
            texts = self.df['text']
        else:
            texts = self.df[self.df['sentiment'] == sentiment_type]['text']
        
        # Gabungkan semua teks
        all_text = ' '.join(texts)
        
        # Tokenize dan hitung frekuensi
        words = re.findall(r'\b\w+\b', all_text.lower())
        
        # Filter kata-kata yang terlalu pendek
        words = [word for word in words if len(word) > 2]
        
        # Hitung frekuensi
        word_freq = Counter(words)
        
        print(f"\nTop {top_n} words in {sentiment_type} sentiment:")
        for word, count in word_freq.most_common(top_n):
            print(f"{word}: {count}")
        
        return word_freq
    
    def create_wordcloud(self, sentiment_type='all', save_path=None):
        """Buat word cloud untuk sentiment tertentu"""
        try:
            if sentiment_type == 'all':
                texts = self.df['text']
            else:
                texts = self.df[self.df['sentiment'] == sentiment_type]['text']
            
            all_text = ' '.join(texts)
            
            # Buat word cloud
            wordcloud = WordCloud(width=800, height=400, 
                                background_color='white',
                                max_words=100,
                                colormap='viridis').generate(all_text)
            
            # Plot
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title(f'Word Cloud - {sentiment_type} Sentiment')
            
            if save_path:
                plt.savefig(save_path, bbox_inches='tight')
                print(f"Word cloud saved to {save_path}")
            
            plt.show()
            
        except Exception as e:
            print(f"Error creating word cloud: {e}")
            print("Make sure you have wordcloud installed: pip install wordcloud")
    
    def plot_sentiment_distribution(self, save_path=None):
        """Plot distribusi sentiment"""
        try:
            plt.figure(figsize=(12, 8))
            
            # Subplot 1: Overall sentiment distribution
            plt.subplot(2, 2, 1)
            sentiment_counts = self.df['sentiment'].value_counts()
            plt.pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%')
            plt.title('Overall Sentiment Distribution')
            
            # Subplot 2: Sentiment by rating
            plt.subplot(2, 2, 2)
            rating_sentiment = pd.crosstab(self.df['rating'], self.df['sentiment'])
            rating_sentiment.plot(kind='bar', stacked=True)
            plt.title('Sentiment by Rating')
            plt.xlabel('Rating')
            plt.ylabel('Count')
            plt.legend(title='Sentiment')
            plt.xticks(rotation=0)
            
            # Subplot 3: Polarity distribution
            plt.subplot(2, 2, 3)
            plt.hist(self.df['polarity'], bins=20, alpha=0.7, color='skyblue')
            plt.title('Polarity Distribution')
            plt.xlabel('Polarity Score')
            plt.ylabel('Frequency')
            
            # Subplot 4: Average polarity by rating
            plt.subplot(2, 2, 4)
            avg_polarity = self.df.groupby('rating')['polarity'].mean()
            plt.bar(avg_polarity.index, avg_polarity.values, color='lightgreen')
            plt.title('Average Polarity by Rating')
            plt.xlabel('Rating')
            plt.ylabel('Average Polarity')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, bbox_inches='tight')
                print(f"Plots saved to {save_path}")
            
            plt.show()
            
        except Exception as e:
            print(f"Error creating plots: {e}")
            print("Make sure you have matplotlib and seaborn installed")
    
    def save_results(self, filename='sentiment_analysis_results.csv'):
        """Simpan hasil analisis sentiment"""
        if 'sentiment' not in self.df.columns:
            print("Please run analyze_sentiment() first")
            return
            
        self.df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Results saved to {filename}")
        
        # Simpan summary
        summary_filename = filename.replace('.csv', '_summary.txt')
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("SENTIMENT ANALYSIS SUMMARY\n")
            f.write("="*50 + "\n\n")
            
            # Overall sentiment distribution
            sentiment_counts = self.df['sentiment'].value_counts()
            f.write("Overall Sentiment Distribution:\n")
            for sentiment, count in sentiment_counts.items():
                percentage = (count / len(self.df)) * 100
                f.write(f"{sentiment}: {count} reviews ({percentage:.1f}%)\n")
            
            f.write("\n" + "="*50 + "\n")
            
            # Sentiment by rating
            f.write("Sentiment by Rating:\n")
            rating_sentiment = pd.crosstab(self.df['rating'], self.df['sentiment'])
            f.write(rating_sentiment.to_string())
            
            f.write("\n\n" + "="*50 + "\n")
            
            # Average polarity by rating
            f.write("Average Polarity by Rating:\n")
            avg_polarity = self.df.groupby('rating')['polarity'].mean()
            for rating, polarity in avg_polarity.items():
                f.write(f"Rating {rating}: {polarity:.3f}\n")
        
        print(f"Summary saved to {summary_filename}")

# Contoh penggunaan
if __name__ == "__main__":
    # Gunakan data yang sudah dinormalisasi
    analyzer = SentimentAnalyzer('huawei_matepad_sentiment_ready.csv')
    
    # Jalankan analisis sentiment
    analyzer.analyze_sentiment()
    
    # Tampilkan summary
    analyzer.sentiment_summary()
    
    # Extract kata-kata yang sering muncul
    analyzer.extract_common_words('Negative', top_n=15)
    analyzer.extract_common_words('Positive', top_n=15)
    
    # Buat visualisasi (uncomment jika ingin menggunakan)
    # analyzer.plot_sentiment_distribution('sentiment_plots.png')
    # analyzer.create_wordcloud('Negative', 'negative_wordcloud.png')
    # analyzer.create_wordcloud('Positive', 'positive_wordcloud.png')
    
    # Simpan hasil
    analyzer.save_results('huawei_matepad_sentiment_analysis.csv')

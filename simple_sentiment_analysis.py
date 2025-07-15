import pandas as pd
import json
from textblob import TextBlob

def simple_sentiment_analysis():
    """Analisis sentiment sederhana menggunakan data yang sudah dinormalisasi"""
    
    # Load data
    try:
        df = pd.read_csv('huawei_matepad_sentiment_ready.csv')
        print(f"Loaded {len(df)} reviews for sentiment analysis")
    except FileNotFoundError:
        print("File 'huawei_matepad_sentiment_ready.csv' not found!")
        print("Please run the scraper first.")
        return
    
    # Analyze sentiment
    print("\n=== ANALYZING SENTIMENT ===")
    sentiments = []
    polarities = []
    
    for i, text in enumerate(df['text']):
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment = 'Positive'
            elif polarity < -0.1:
                sentiment = 'Negative'
            else:
                sentiment = 'Neutral'
                
            sentiments.append(sentiment)
            polarities.append(polarity)
            
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(df)} reviews...")
                
        except Exception as e:
            print(f"Error analyzing text {i+1}: {e}")
            sentiments.append('Neutral')
            polarities.append(0)
    
    # Add results to dataframe
    df['sentiment'] = sentiments
    df['polarity'] = polarities
    
    # Display results
    print("\n=== SENTIMENT ANALYSIS RESULTS ===")
    
    # Overall sentiment distribution
    sentiment_counts = df['sentiment'].value_counts()
    print(f"\nOverall Sentiment Distribution:")
    for sentiment, count in sentiment_counts.items():
        percentage = (count / len(df)) * 100
        print(f"{sentiment}: {count} reviews ({percentage:.1f}%)")
    
    # Sentiment by rating
    print(f"\nSentiment by Rating:")
    rating_sentiment = pd.crosstab(df['rating'], df['sentiment'])
    print(rating_sentiment)
    
    # Average polarity by rating
    print(f"\nAverage Polarity by Rating:")
    avg_polarity = df.groupby('rating')['polarity'].mean()
    for rating, polarity in avg_polarity.items():
        print(f"Rating {rating}: {polarity:.3f}")
    
    # Examples of different sentiments
    print(f"\n=== EXAMPLES ===")
    
    # Most positive review
    most_positive_idx = df['polarity'].idxmax()
    most_positive = df.loc[most_positive_idx]
    print(f"\nMost Positive Review (polarity: {most_positive['polarity']:.3f}):")
    print(f"Rating: {most_positive['rating']} stars")
    print(f"Text: {most_positive['text']}")
    
    # Most negative review
    most_negative_idx = df['polarity'].idxmin()
    most_negative = df.loc[most_negative_idx]
    print(f"\nMost Negative Review (polarity: {most_negative['polarity']:.3f}):")
    print(f"Rating: {most_negative['rating']} stars")
    print(f"Text: {most_negative['text']}")
    
    # Save results
    df.to_csv('huawei_matepad_sentiment_analysis_results.csv', index=False, encoding='utf-8')
    print(f"\nResults saved to 'huawei_matepad_sentiment_analysis_results.csv'")
    
    # Summary statistics
    print(f"\n=== SUMMARY STATISTICS ===")
    print(f"Total reviews analyzed: {len(df)}")
    print(f"Average polarity: {df['polarity'].mean():.3f}")
    print(f"Polarity standard deviation: {df['polarity'].std():.3f}")
    print(f"Most positive polarity: {df['polarity'].max():.3f}")
    print(f"Most negative polarity: {df['polarity'].min():.3f}")
    
    # Analysis by rating correlation
    print(f"\n=== RATING vs SENTIMENT CORRELATION ===")
    correlation = df['rating'].corr(df['polarity'])
    print(f"Correlation between rating and sentiment polarity: {correlation:.3f}")
    
    if correlation > 0.3:
        print("Strong positive correlation - higher ratings tend to have more positive sentiment")
    elif correlation < -0.3:
        print("Strong negative correlation - higher ratings tend to have more negative sentiment")
    else:
        print("Weak correlation between rating and sentiment")

if __name__ == "__main__":
    simple_sentiment_analysis()

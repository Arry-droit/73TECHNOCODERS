import schedule
import time
from crawler import YahooFinanceScraper
from keyword_extract import extract_keywords, summarize_article
import json
import os
from datetime import datetime

def process_articles(articles):
    """Process articles with keyword extraction and summarization."""
    processed_articles = []
    for article in articles:
        content = article.get("content", "")
        if not content:
            continue
            
        try:
            # Get summary and keywords
            summary = summarize_article(content)
            keywords = extract_keywords(content)
            
            if summary and keywords:
                article.update({
                    "summary": summary,
                    "keywords": keywords
                })
                processed_articles.append(article)
        except Exception as e:
            print(f"Error processing article: {e}")
            continue
            
    return processed_articles

def run_crawler():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduled crawl...")
    
    # Initialize and run the scraper
    scraper = YahooFinanceScraper(keywords=["stock", "market"])
    scraper.scrape_yahoo_finance(max_articles=5)
    scraper.scrape_cnbc(max_articles=5)
    
    # Get articles and process them
    articles = scraper.get_articles()
    if articles:
        processed_articles = process_articles(articles)
        
        # Save processed results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_path = f"finance_data/finance_articles_{timestamp}.json"
        
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(processed_articles, f, ensure_ascii=False, indent=4)
            print(f"Processed results saved to: {json_path}")
        except Exception as e:
            print(f"Error saving processed results: {e}")
    else:
        print("No articles to process")

def main():
    print("Starting scheduler...")
    print("Crawler will run every 6 hours")
    
    # Schedule the job to run every 6 hours
    schedule.every(6).hours.do(run_crawler)
    
    # Run immediately on startup
    run_crawler()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main() 
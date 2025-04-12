import json
import os
from crawler import YahooFinanceScraper
from keyword_extract import extract_keywords, summarize_article
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY not found in environment variables. Please check your .env file.")
        return

    try:
        # Step 1: Scrape Data
        scraper = YahooFinanceScraper(keywords=["stock", "market"])
        scraper.scrape_yahoo_finance(max_articles=5)
        scraper.scrape_cnbc(max_articles=5)
        
        # Save results and get the saved file path
        saved_file = scraper.save_results()
        if not saved_file:
            print("⚠️ Failed to save scraped results.")
            return
        print(f"Results saved to: {saved_file}")

        # Step 2: Load Articles from Scraped Data
        try:
            with open(saved_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
        except FileNotFoundError:
            print("⚠️ File not found. Ensure the file was saved correctly.")
            return
        except json.JSONDecodeError:
            print("⚠️ Error reading the JSON file. The file might be corrupted.")
            return

        if not articles:
            print("⚠️ No articles found in the saved file.")
            return

        # Step 3: Process each article (keywords and summary)
        print("\n📰 FINANCIAL NEWS ANALYSIS\n")
        
        for i, article in enumerate(articles, 1):
            content = article.get("content", "")
            title = article.get("title", "Unknown Title")
            url = article.get("url", "No URL provided")
            
            if not content:
                print(f"⚠️ Content not found in article: {title}")
                continue

            print(f"\n[Article {i}]")
            print(f"Title: {title}")
            print(f"Source: {url}")
            
            try:
                # Get keywords and sentiment
                analysis = extract_keywords(content)
                if analysis:
                    print("\n📊 Analysis:")
                    print(analysis)
                
                # Get summary
                summary = summarize_article(content)
                if summary:
                    print("\n📝 Summary:")
                    print(summary)
                
                print("\n" + "="*80 + "\n")
            
            except Exception as e:
                print(f"⚠️ Error processing article '{title}': {str(e)}")
                continue

    except Exception as e:
        print(f"⚠️ An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()

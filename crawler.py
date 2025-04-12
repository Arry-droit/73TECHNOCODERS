import os
import requests
import time
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

class YahooFinanceScraper:
    def __init__(self, output_dir="finance_data", keywords=None):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.output_dir = output_dir
        self.yahoo_url = 'https://finance.yahoo.com/news'
        self.cnbc_url = 'https://www.cnbc.com/finance/'
        self.articles = []
        self.keywords = keywords or []

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def scrape_yahoo_finance(self, max_articles=5, debug=False):
        print(f"Scraping Yahoo Finance news listings...")
        try:
            response = requests.get(self.yahoo_url, headers=self.headers)
            if response.status_code == 200:
                if debug:
                    with open("yahoo_debug.html", "w", encoding="utf-8") as f:
                        f.write(response.text)

                soup = BeautifulSoup(response.text, 'html.parser')
                article_links = []

                for article in soup.find_all('a', href=True):
                    href = article['href']
                    if href.startswith('/'):
                        href = "https://finance.yahoo.com" + href
                    title = article.get_text(strip=True)
                    if title and len(title) > 10:
                        if not self.keywords or any(keyword.lower() in title.lower() for keyword in self.keywords):
                            article_links.append((title, href))

                seen_urls = set()
                unique_articles = []
                for title, url in article_links:
                    if url not in seen_urls:
                        seen_urls.add(url)
                        unique_articles.append((title, url))

                print(f"Found {len(unique_articles)} unique Yahoo Finance articles")
                articles_to_process = unique_articles[:max_articles]

                for i, (title, url) in enumerate(articles_to_process):
                    print(f"Processing Yahoo article {i+1}/{len(articles_to_process)}: {title}")
                    article_data = self.scrape_article_content(url, title)
                    if article_data:
                        self.articles.append(article_data)
                    time.sleep(2)
            else:
                print(f"Failed to fetch Yahoo Finance. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error scraping Yahoo Finance: {e}")
    def get_articles(self):
        """Return the list of scraped articles."""
        return self.articles

    def scrape_cnbc(self, max_articles=5, debug=False):
        print(f"Scraping CNBC Finance news listings...")
        try:
            response = requests.get(self.cnbc_url, headers=self.headers)
            if response.status_code == 200:
                if debug:
                    with open("cnbc_debug.html", "w", encoding="utf-8") as f:
                        f.write(response.text)

                soup = BeautifulSoup(response.text, 'html.parser')
                article_links = []

                for article in soup.find_all('a', href=True):
                    href = article['href']
                    if href.startswith('/'):
                        href = urljoin(self.cnbc_url, href)
                    title = article.get_text(strip=True)
                    if title and len(title) > 10:
                        if not self.keywords or any(keyword.lower() in title.lower() for keyword in self.keywords):
                            article_links.append((title, href))

                seen_urls = set()
                unique_articles = []
                for title, url in article_links:
                    if url not in seen_urls and 'video' not in url and 'live-updates' not in url:
                        seen_urls.add(url)
                        unique_articles.append((title, url))

                print(f"Found {len(unique_articles)} unique CNBC articles")
                articles_to_process = unique_articles[:max_articles]

                for i, (title, url) in enumerate(articles_to_process):
                    print(f"Processing CNBC article {i+1}/{len(articles_to_process)}: {title}")
                    article_data = self.scrape_article_content(url, title)
                    if article_data:
                        self.articles.append(article_data)
                    time.sleep(2)
            else:
                print(f"Failed to fetch CNBC. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error scraping CNBC: {e}")

    def scrape_article_content(self, url, title=None):
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"Failed to fetch article at {url}. Status code: {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            if not title:
                title_element = soup.find('h1')
                title = title_element.text.strip() if title_element else "Unknown Title"

            timestamp = None
            time_element = soup.find('time')
            if time_element:
                timestamp = time_element.get('datetime') or time_element.text.strip()

            author = "Unknown"
            author_element = soup.find('span', class_=lambda c: c and 'author' in c.lower())
            if author_element:
                author = author_element.text.strip()

            content = ""
            content_selectors = [
                'div.caas-body',               # Yahoo
                'article',                     # General
                'div.ArticleBody-articleBody', # CNBC
                'div.article-body__content',
                'section.ArticleBodyContainer',
            ]

            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    paragraphs = content_element.find_all('p')[:2]
                    content = "\n\n".join([p.text.strip() for p in paragraphs])
                    if content:
                        break

            if not content:
                paragraphs = soup.find_all('p')[:2]
                content = "\n\n".join([p.text.strip() for p in paragraphs])

            tickers = self.extract_tickers(response.text)

            return {
                'title': title,
                'url': url,
                'author': author,
                'published_date': timestamp,
                'content': content,
                'mentioned_tickers': tickers
            }
        except Exception as e:
            print(f"Error processing article at {url}: {e}")
            return None

    def extract_tickers(self, text):
        ticker_pattern = r'\(([A-Z]{1,5}(?:\.[A-Z]{1,2})?)\)'
        tickers_raw = re.findall(ticker_pattern, text)
        false_positives = {'A', 'I', 'AM', 'PM', 'CEO', 'CFO', 'THE', 'FOR', 'ON', 'BY'}
        filtered_tickers = [ticker for ticker in tickers_raw if ticker not in false_positives]
        return list(set(filtered_tickers))

    def save_results(self, output_format="json"):
        if not self.articles:
            print("No articles to save.")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_path = f"{self.output_dir}/finance_articles_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=4)
        print(f"Articles saved to JSON: {os.path.abspath(json_path)}")
        return json_path


if __name__ == "__main__":
    scraper = YahooFinanceScraper(keywords=["stock", "market", "ETF", "fund"])
    
    print("Scraping Yahoo Finance...")
    scraper.scrape_yahoo_finance(max_articles=5)
    time.sleep(2)  # Delay between Yahoo and CNBC scraping
    
    print("Scraping CNBC...")
    scraper.scrape_cnbc(max_articles=5)
    time.sleep(2)  # Delay before saving results
    
    print("Saving results...")
    scraper.save_results()
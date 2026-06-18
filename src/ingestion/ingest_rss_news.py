import os
import json
import logging
import feedparser
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def fetch_rss_news():
    # Example target URL
    rss_url = "https://www.suarasurabaya.net/feed/"
    
    logging.info(f"Fetching RSS feed from: {rss_url}")
    feed = feedparser.parse(rss_url)
    
    if feed.bozo:
        logging.error(f"Error parsing feed: {feed.bozo_exception}")
        return

    entries = feed.entries
    if not entries:
        logging.info("No entries found in the RSS feed.")
        return

    # Extract required fields
    extracted_data = []
    for entry in entries:
        extracted_data.append({
            'title': entry.get('title', ''),
            'summary': clean_html(entry.get('summary', '')),
            'link': entry.get('link', ''),
            'published_date': entry.get('published', '')
        })

    # Define relative path to bronze directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    bronze_dir = os.path.join(base_dir, 'data', 'bronze')
    os.makedirs(bronze_dir, exist_ok=True)
    
    output_file = os.path.join(bronze_dir, 'rss_news_raw.jsonl')
    
    # Save as JSON Lines
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in extracted_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        logging.info(f"Successfully saved {len(extracted_data)} RSS entries to {output_file}")
    except Exception as e:
        logging.error(f"Failed to write to file: {e}")

if __name__ == "__main__":
    fetch_rss_news()

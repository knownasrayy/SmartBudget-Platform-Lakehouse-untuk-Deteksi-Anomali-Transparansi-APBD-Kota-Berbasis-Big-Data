import os
import requests
import pandas as pd
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_gnews():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GNEWS_API_KEY')
    
    if not api_key:
        logging.error("GNEWS_API_KEY not found in environment variables.")
        return

    endpoint = "https://gnews.io/api/v4/search"
    query = "Surabaya AND (APBD OR anggaran OR walikota OR DPRD OR pembangunan)"
    
    params = {
        'q': query,
        'lang': 'id',
        'apikey': api_key,
        'max': 100
    }

    try:
        logging.info(f"Fetching news from GNews API with query: '{query}'")
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            logging.info("No articles found.")
            return

        # Extract required fields
        extracted_data = []
        for article in articles:
            extracted_data.append({
                'title': article.get('title'),
                'description': article.get('description'),
                'publishedAt': article.get('publishedAt'),
                'source_name': article.get('source', {}).get('name')
            })

        # Save to CSV
        df = pd.DataFrame(extracted_data)
        
        # Define relative path to bronze directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bronze_dir = os.path.join(base_dir, 'data', 'bronze')
        os.makedirs(bronze_dir, exist_ok=True)
        
        output_file = os.path.join(bronze_dir, 'gnews_raw.csv')
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        logging.info(f"Successfully saved {len(extracted_data)} articles to {output_file}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error or HTTP issue occurred: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fetch_gnews()

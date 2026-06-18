import os
import pandas as pd
import logging
from apify_client import ApifyClient
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_twitter_apify():
    # Load environment variables
    load_dotenv()
    api_token = os.getenv('APIFY_TOKEN')
    
    if not api_token:
        logging.error("APIFY_TOKEN not found in environment variables.")
        return

    # Initialize the ApifyClient
    client = ApifyClient(api_token)

    # Actor input configuration based on user snippet
    run_input = {
        "searchTerms": [
            "jalan rusak surabaya",
            "macet pdam",
            "apbd surabaya"
        ],
        "maxItems": 50,
        "sort": "Latest",
        "tweetLanguage": "id",
        "customMapFunction": "(object) => { return {...object} }",
    }

    try:
        logging.info("Starting Apify Twitter Scraper (apidojo/tweet-scraper) actor...")
        # Run the Actor and wait for it to finish
        run = client.actor("apidojo/tweet-scraper").call(run_input=run_input)
        
        logging.info("Actor finished. Fetching results from dataset...")
        # Fetch results from the actor's dataset
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
        
        if not dataset_items:
            logging.info("No tweets found.")
            return
            
        # Process and convert to DataFrame
        extracted_data = []
        for item in dataset_items:
            extracted_data.append({
                'full_text': item.get('full_text', ''),
                'created_at': item.get('created_at', ''),
                'retweet_count': item.get('retweet_count', 0),
                'user.screen_name': item.get('user', {}).get('screen_name', '')
            })
            
        df = pd.DataFrame(extracted_data)
        
        # Define relative path to bronze directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bronze_dir = os.path.join(base_dir, 'data', 'bronze')
        os.makedirs(bronze_dir, exist_ok=True)
        
        output_file = os.path.join(bronze_dir, 'tweets_raw.csv')
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        logging.info(f"Successfully saved {len(extracted_data)} tweets to {output_file}")

    except Exception as e:
        logging.error(f"An error occurred during Apify execution: {e}")

if __name__ == "__main__":
    fetch_twitter_apify()

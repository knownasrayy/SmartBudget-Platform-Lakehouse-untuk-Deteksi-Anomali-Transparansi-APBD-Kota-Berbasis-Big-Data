import os
import json
import logging
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_youtube_comments():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        logging.error("YOUTUBE_API_KEY not found in environment variables.")
        return

    # Relevant video IDs regarding APBD Surabaya specifically
    video_ids = ["BJ2DZ6tSU7A", "wIcJzKTNJm0", "Ed6RcTcNEo4"] 
    
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        extracted_data = []
        
        for video_id in video_ids:
            logging.info(f"Fetching comments for video_id: {video_id}")
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                textFormat="plainText"
            )
            response = request.execute()
            
            items = response.get("items", [])
            for item in items:
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                extracted_data.append({
                    'authorDisplayName': snippet.get('authorDisplayName'),
                    'textOriginal': snippet.get('textOriginal'),
                    'likeCount': snippet.get('likeCount', 0),
                    'publishedAt': snippet.get('publishedAt')
                })
            
        # Define relative path to bronze directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bronze_dir = os.path.join(base_dir, 'data', 'bronze')
        os.makedirs(bronze_dir, exist_ok=True)
        
        output_file = os.path.join(bronze_dir, 'yt_comments_raw.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=4)
            
        logging.info(f"Successfully saved {len(extracted_data)} comments to {output_file}")
        
    except Exception as e:
        logging.error(f"An error occurred while fetching YouTube comments: {e}")

if __name__ == "__main__":
    fetch_youtube_comments()

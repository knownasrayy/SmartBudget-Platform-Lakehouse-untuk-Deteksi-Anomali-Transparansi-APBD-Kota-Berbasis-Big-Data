import os
import sys
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
api_key = os.getenv("YOUTUBE_API_KEY")
if not api_key:
    sys.exit("No API key")

youtube = build('youtube', 'v3', developerKey=api_key)
request = youtube.search().list(q="apbd surabaya banjir", part="snippet", type="video", maxResults=5)
response = request.execute()
for item in response.get('items', []):
    print(f"ID: {item['id']['videoId']}, Title: {item['snippet']['title']}")

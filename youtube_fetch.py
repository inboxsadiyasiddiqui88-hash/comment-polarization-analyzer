import os
from googleapiclient.discovery import build
import re
from googleapiclient.discovery import build

def extract_video_id(youtube_url):
    """
    Extract video ID from full YouTube URL
    """
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"shorts/([a-zA-Z0-9_-]{11})"
    ]

    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)

    raise ValueError("Invalid YouTube URL")

def get_youtube_comments(video_id, max_comments=100):
    api_key = os.getenv("YOUTUBE_API_KEY")
    
    if not api_key:
        raise ValueError("YouTube API key not found in environment variables")
    """
    Fetch top-level YouTube comments for a given video ID.
    """
    youtube = build(
        serviceName="youtube", 
        version="v3", 
        developerKey=api_key,
        cache_discovery=False
        )
    
    comments = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=min(100, max_comments),
        textFormat="plainText"
    )

    response = request.execute()

    for item in response["items"]:
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)

        """if len(comments) >= max_comments:
            break"""

    return comments

   




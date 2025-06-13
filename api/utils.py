# api/utils.py

import os
import praw
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime

# Initialize and return a PRAW Reddit client
def get_reddit_client():
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'reddit-sentiment-app')
    if not client_id or not client_secret:
        raise RuntimeError("Missing Reddit credentials in environment variables.")
    # PRAW requires check_for_async=False in some contexts to avoid warnings
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        check_for_async=False
    )
    return reddit

# Initialize VADER sentiment analyzer once
sia = SentimentIntensityAnalyzer()

def fetch_and_analyze(subreddit=None, keyword=None, limit=100):
    """
    Fetch recent posts from Reddit via PRAW and analyze sentiment with VADER.
    Returns a list of dicts: [{ "timestamp": ISO8601_str, "sentiment": float }, ...]
    """
    reddit = get_reddit_client()
    items = []

    if subreddit:
        sub = subreddit.strip()
        # Fetch 'new' posts from the subreddit
        try:
            for post in reddit.subreddit(sub).new(limit=limit):
                text = (post.title or "") + " " + (post.selftext or "")
                ts = datetime.utcfromtimestamp(post.created_utc).isoformat() + 'Z'
                score = sia.polarity_scores(text)['compound']
                items.append({"timestamp": ts, "sentiment": score})
        except Exception as e:
            # Propagate exception with a clear message
            raise RuntimeError(f"Error fetching from subreddit '{sub}': {e}")

    elif keyword:
        kw = keyword.strip()
        # Search across all subreddits
        try:
            for post in reddit.subreddit('all').search(kw, limit=limit):
                text = (post.title or "") + " " + (post.selftext or "")
                ts = datetime.utcfromtimestamp(post.created_utc).isoformat() + 'Z'
                score = sia.polarity_scores(text)['compound']
                items.append({"timestamp": ts, "sentiment": score})
        except Exception as e:
            raise RuntimeError(f"Error searching keyword '{kw}': {e}")

    else:
        raise ValueError("Either 'subreddit' or 'keyword' must be provided.")

    # Sort by timestamp ascending
    items.sort(key=lambda x: x["timestamp"])
    return items

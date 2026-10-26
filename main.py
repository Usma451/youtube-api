from fastapi import FastAPI, HTTPException
from yt_dlp import YoutubeDL
import textblob

app = FastAPI(title="YouTube Sentiment Analysis API")

def analyze_sentiment(text):
    if not text:
        return "Neutral"
    analysis = textblob.TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.05:
        return "Positive"
    elif polarity < -0.05:
        return "Negative"
    else:
        return "Neutral"

@app.get("/analyze-comments/")
def scrape_and_analyze(video_url: str, max_comments: int = 50):
    try:
        ydl_opts = {
            'extract_flat': False,
            'getcomments': True,
            'max_comments': max_comments,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            comments_data = info.get('comments', [])
            
            formatted_comments = []
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for comment in comments_data:
                text = comment.get("text", "")
                sentiment = analyze_sentiment(text)
                
                if sentiment == "Positive":
                    positive_count += 1
                elif sentiment == "Negative":
                    negative_count += 1
                else:
                    neutral_count += 1
                
                formatted_comments.append({
                    "author": comment.get("author"),
                    "text": text,
                    "likes": comment.get("like_count"),
                    "sentiment": sentiment
                })
                
            return {
                "video_title": info.get("title"),
                "total_analyzed": len(formatted_comments),
                "summary": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count
                },
                "comments": formatted_comments
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import feedparser
import os
from datetime import datetime
from livekit.agents import function_tool

TOOL = {
    "name": "news_provider",
    "description": "Get latest news headlines from RSS feeds for different countries and topics. Use when the user wants to hear current news from India, USA, UK, technology, business, sports, or entertainment.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "country": {"type": "STRING", "description": "Country or topic: 'india', 'usa', 'uk', 'australia', 'canada', 'technology', 'business', 'sports', 'entertainment'"}
        },
        "required": []
    },
    "handler": "get_top_news",
}

@function_tool()
async def get_top_news(country: str = "india") -> str:
    """
    Gets latest news from RSS feeds for different countries.
    
    Args:
        country: Country for news (india, usa, uk, australia, canada, technology, business, sports, entertainment)
    
    Returns:
        str: Latest news headlines with links
    """
    try:
        print(f"[NEWS] Fetching for: {country}")
        
        rss_feeds = {
            "india": "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
            "usa": "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml", 
            "uk": "https://feeds.bbci.co.uk/news/uk/rss.xml",
            "australia": "https://feeds.bbci.co.uk/news/world/australia/rss.xml",
            "canada": "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
            "technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
            "business": "https://feeds.bbci.co.uk/news/business/rss.xml",
            "sports": "https://feeds.bbci.co.uk/news/sport/rss.xml",
            "entertainment": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"
        }
        
        country_codes = {
            "in": "india", "us": "usa", "uk": "uk", "au": "australia",
            "ca": "canada", "tech": "technology", "biz": "business",
            "sports": "sports", "ent": "entertainment",
        }
        
        country_lower = country.lower()
        country_lower = country_codes.get(country_lower, country_lower)
        print(f"[NEWS] Country: {country_lower}")
        
        if country_lower not in rss_feeds:
            available_countries = ", ".join(rss_feeds.keys())
            return f"Country '{country}' not found. Available: {available_countries}"
        
        feed_url = rss_feeds[country_lower]
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:
            return f"RSS feed error: {feed.bozo_exception}"
        
        if not feed.entries:
            return "No news entries found."
        
        news_output = f"Latest {country.upper()} News:\n\n"
        
        for i, entry in enumerate(feed.entries[:3], 1):
            title = entry.get('title', 'No title')
            news_output += f"{i}. {title}\n"
        
        return news_output
        
    except Exception as e:
        return f"News error: {str(e)
}"

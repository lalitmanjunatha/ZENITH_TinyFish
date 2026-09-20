"""YouTube playback without embedding an API credential in source code."""
from __future__ import annotations

import asyncio
import os
import webbrowser
from typing import Literal
from urllib.parse import quote_plus

import aiohttp
from livekit.agents import function_tool

TOOL = {
    "name": "youtube_videos",
    "description": "Search and play a song or video on YouTube.",
    "parameters": {"type": "OBJECT", "properties": {
        "media_name": {"type": "STRING", "description": "Song or video to play"},
        "media_type": {"type": "STRING", "description": "song or video"}},
        "required": ["media_name"]},
    "handler": "play_media",
}


def _search_url(query: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"


@function_tool()
async def play_media(media_name: str, media_type: Literal["song", "video"] = "song") -> str:
    query = media_name.strip()
    if not query:
        return "I need a song or video title."
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    try:
        if api_key:
            params = {"part": "snippet", "q": query, "type": "video", "maxResults": 1, "key": api_key}
            async with aiohttp.ClientSession() as session:
                async with session.get("https://www.googleapis.com/youtube/v3/search", params=params,
                                       timeout=aiohttp.ClientTimeout(total=10)) as response:
                    data = await response.json() if response.status == 200 else {}
            items = data.get("items", [])
            if items:
                item = items[0]
                await asyncio.to_thread(webbrowser.open, f"https://www.youtube.com/watch?v={item['id']['videoId']}")
                return f"Playing {item['snippet']['title']} on YouTube."
        await asyncio.to_thread(webbrowser.open, _search_url(query))
        return f"Opened YouTube results for {query}."
    except Exception as exc:
        return f"Could not open YouTube for '{query}': {exc}"

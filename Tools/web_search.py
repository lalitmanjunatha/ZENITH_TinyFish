#web_search.py
"""Web search and news tools for ZENITH.

Provides web search functionality using TinyFish Search API with DuckDuckGo fallbacks.
Also provides news search via DuckDuckGo.

TTM: All function return types preserved from original Gemini-based implementation.
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


# Base directory & config paths 

def _base_dir() -> Path:
    import sys
    if getattr(sys, "_MEIPASS", False):  # pyinstaller freeze
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR        = _base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"


# TinyFish Search API 

_TF_SEARCH_URL = "https://api.search.tinyfish.ai"
_TF_TIMEOUT    = 15        # seconds  connection + read timeout combined
_TF_MAX_RETRIES = 0        # no retries per spec: "Avoid retries that could cause excessive API usage"


def _get_tinyfish_api_key() -> Optional[str]:
    """Return the TinyFish API key from the environment, if configured.

    Reads ``TINYFISH_API_KEY``.  Falls back to the legacy ``gemini_api_key``
    in ``config/api_keys.json`` for backward compatibility, but only if the
    TinyFish key is missing  the preferred flow is the dedicated key.
    """
    # Preferred: dedicated TinyFish key
    key = os.getenv("TINYFISH_API_KEY")
    if key and key.strip():
        return key.strip()

    # Legacy fallback: read from api_keys.json (Gemini key)
    try:
        api_data = json.loads(
            BASE_DIR.joinpath("config", "api_keys.json").read_text(encoding="utf-8")
        )
        legacy = api_data.get("gemini_api_key")
        if legacy and legacy.strip():
            # Return legacy key so existing callers still work, but mark it.
            return f"LEGACY:{legacy.strip()}"
    except Exception:
        pass

    return None


def _tinyfish_search(
    query: str,
    *,
    location: Optional[str] = None,
    language: Optional[str] = None,
    domain_type: str = "web",
    purpose: Optional[str] = None,
) -> Dict[str, Any]:
    """Call the TinyFish Search API and return the parsed JSON payload.

    Parameters
    ----------
    query: str
        The search query string.
    location: Optional[str]
        Geo-targeting location (e.g. "city:London").
    language: Optional[str]
        Two-letter language code (e.g. "en").
    domain_type: str
        One of ``"web"``, ``"news"``, ``"research_paper"``.
    purpose: Optional[str]
        Free-text statement of the search intent/goal (max 2000 chars).

    Returns
    -------
    dict
        Parsed JSON response from TinyFish Search API with keys
        ``query``, ``results``, ``total_results``, ``page``.

    Raises
    ------
    RuntimeError
        If the API key is missing, the HTTP request fails, or the response
        cannot be parsed.
    """
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("TINYFISH_API_KEY")
    if not api_key:
        raise RuntimeError(
            "TinyFish API key not configured. Set TINYFISH_API_KEY environment "
            "variable, or ensure gemini_api_key exists in config/api_keys.json "
            "for legacy fallback."
        )

    # Strip legacy prefix if present
    actual_key = api_key.split(":", 1)[1] if api_key.startswith("LEGACY:") else api_key

    # Build query string
    params = ["query=" + query]
    if location:
        params.append("location=" + location)
    if language:
        params.append("language=" + language)
    if domain_type:
        params.append("domain_type=" + domain_type)
    if purpose:
        params.append("purpose=" + purpose)

    url = _TF_SEARCH_URL + "?" + "&".join(params)
    headers = {
        "X-API-Key": actual_key,
        "Accept": "application/json",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=_TF_TIMEOUT)
    except requests.exceptions.Timeout:
        raise RuntimeError(f"TinyFish Search request timed out after {_TF_TIMEOUT} seconds")
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"TinyFish Search request failed: {exc}") from exc

    # HTTP error handling  never silently swallow non-2xx
    if not resp.ok:
        try:
            err_detail = resp.json()
        except Exception:
            err_detail = {"status_code": resp.status_code, "text": resp.text}
        raise RuntimeError(
            f"TinyFish Search API returned HTTP {resp.status_code}: {json.dumps(err_detail)}"
        )

    # Parse JSON body
    try:
        data = resp.json()
    except ValueError as exc:
        raise RuntimeError("TinyFish Search API returned invalid JSON") from exc

    # Validate minimal shape
    if not isinstance(data, dict):
        raise RuntimeError("TinyFish Search API response is not a JSON object")

    if "results" not in data:
        raise RuntimeError("TinyFish Search API response missing 'results' key")

    return data


# Public: high-level search wrappers 

def search_web(query: str) -> str:
    """Search the web using TinyFish Search API with DuckDuckGo fallback.

    This is the primary entry point that replaces the former Gemini-powered
    web search.  It attempts TinyFish first; if the API key is missing or the
    call fails, it falls back to DuckDuckGo.

    Parameters
    ----------
    query: str
        The search query or question.

    Returns
    -------
    str
        Formatted search results suitable for presentation to the user.
        Includes titles, snippets, and URLs from the selected source.
    """
    # Attempt TinyFish first
    try:
        result = _tinyfish_search(query, domain_type="web")
        results = result.get("results", [])
        if results:
            lines = [f"Search results for: {query}"]
            for r in results:
                pos = r.get("position", "")
                title = r.get("title", "")
                snippet = r.get("snippet", "")
                url = r.get("url", "")
                parts = []
                if pos:
                    parts.append(f"#{pos}")
                if title:
                    parts.append(title)
                if snippet:
                    parts.append(snippet)
                if url:
                    parts.append(f"Source: {url}")
                lines.append("  " + "  ".join(parts))
            lines.append(
                f"\nTotal results: {result.get('total_results', '?')}")
            return "\n".join(lines).strip()
    except RuntimeError:
        # Missing API key or HTTP error ? fall through to DDG
        pass

    # DuckDuckGo fallback 
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        from ddgs import DDGS

    results: List[Dict[str, str]] = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=8):
            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "url": r.get("href", ""),
            })

    if results:
        lines = [f"Search results for: {query}"]
        for i, r in enumerate(results, 1):
            if r.get("title"):
                lines.append(f"{i}. {r["title"]}")
            if r.get("snippet"):
                lines.append(f"   {r["snippet"]}")
            if r.get("url"):
                lines.append(f"   Source: {r["url"]}")
            lines.append("")
        return "\n".join(lines).strip()

    # No results from either source 
    return f"No search results found for: {query}"


def search_news(query: str) -> str:
    """Search for news using DuckDuckGo (TinyFish does not provide a free news
    endpoint in the open Search API; this keeps the original behaviour).

    Parameters
    ----------
    query: str
        The news search query.

    Returns
    -------
    str
        Formatted news results.

    """
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS

    results: List[Dict[str, str]] = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.news(query, max_results=8):
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("url", ""),
                    "source": r.get("source", ""),
                })
    except Exception:
        pass

    if results:
        lines = [f"Latest news: {query}"]
        for i, r in enumerate(results, 1):
            if r.get("title"):
                lines.append(f"{i}. {r["title"]}")
            if r.get("snippet"):
                lines.append(f"   {r["snippet"]}")
            if r.get("url"):
                lines.append(f"   Source: {r["url"]}")
            if r.get("source"):
                lines.append(f"   Publisher: {r["source"]}")
            lines.append("")
        return "\n".join(lines).strip()

    return f"No news found for: {query}"


# Backward-compatibility alias: GUI imports _news from this module
_news = search_news
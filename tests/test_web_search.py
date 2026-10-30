"""Unit tests for Tools/web_search.py — TinyFish migration."""

import sys
from unittest.mock import patch, MagicMock, PropertyMock

import pytest

sys.path.insert(0, "C:/Users/Lalit Manjunatha/Desktop/ZENITH_V-")

from Tools.web_search import search_web, search_news


# ── Helper: TinyFish response structure ───────────────────────────────────────

def _tf_response(results=None, total_results=10, page=1, query="test query"):
    return {
        "query": query,
        "results": results or [],
        "total_results": total_results,
        "page": page,
    }


# ── Test: search_web with valid TinyFish results ─────────────────────────────

@patch("Tools.web_search._tinyfish_search")
def test_search_web_tinyfish_results(mock_tinyfish):
    mock_tinyfish.return_value = _tf_response(
        results=[
            {
                "position": 1,
                "site_name": "Example",
                "title": "Example Title",
                "snippet": "This is an example snippet.",
                "url": "https://example.com",
            }
        ],
        total_results=1,
        query="test query",
    )

    result = search_web("test query")
    assert "test query" in result
    assert "Example Title" in result
    assert "Example" in result
    assert "This is an example snippet." in result
    assert "https://example.com" in result
    assert "Total results: 1" in result


# ── Test: search_web falls through to DDG when TinyFish returns empty results ─

@patch("Tools.web_search._tinyfish_search")
def test_search_web_tinyfish_empty_falls_to_ddg(mock_tinyfish):
    mock_tinyfish.return_value = _tf_response(results=[], total_results=0)

    with patch("duckduckgo_search.DDGS") as mock_ddgs_class:
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = [
            {"title": "DDG Result", "body": "DDG snippet text.", "href": "https://duckduckgo.com"}
        ]
        mock_ddgs_class.return_value.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs_class.return_value.__exit__ = MagicMock(return_value=None)

        result = search_web("test query")
        assert "DDG Result" in result
        assert "DDG snippet text." in result


# ── Test: search_web falls through to DDG when TinyFish key is missing ───────

@patch("Tools.web_search._tinyfish_search", side_effect=RuntimeError("No API key"))
def test_search_web_missing_api_key_falls_to_ddg(mock_tinyfish):
    with patch("duckduckgo_search.DDGS") as mock_ddgs_class:
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = []
        mock_ddgs_class.return_value.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs_class.return_value.__exit__ = MagicMock(return_value=None)

        result = search_web("test query")
        assert "No search results found for: test query" in result


# ── Test: search_web falls through to DDG on TinyFish HTTP error ─────────────

@patch("Tools.web_search._tinyfish_search", side_effect=RuntimeError("HTTP 403"))
def test_search_web_http_error_falls_to_ddg(mock_tinyfish):
    with patch("duckduckgo_search.DDGS") as mock_ddgs_class:
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = [
            {"title": "Fallback Result", "body": "fallback snippet", "href": "https://duck.co"}
        ]
        mock_ddgs_class.return_value.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs_class.return_value.__exit__ = MagicMock(return_value=None)

        result = search_web("test query")
        assert "Fallback Result" in result


# ── Test: search_web falls through to DDG on TinyFish timeout ────────────────

@patch("Tools.web_search._tinyfish_search", side_effect=RuntimeError("Timed out"))
def test_search_web_timeout_falls_to_ddg(mock_tinyfish):
    with patch("duckduckgo_search.DDGS") as mock_ddgs_class:
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = [
            {"title": "Timeout Fallback", "body": "timed out fallback", "href": "https://fallback.co"}
        ]
        mock_ddgs_class.return_value.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs_class.return_value.__exit__ = MagicMock(return_value=None)

        result = search_web("test query")
        assert "Timeout Fallback" in result


# ── Test: search_web with invalid JSON from TinyFish ──────────────────────────

@patch("Tools.web_search.requests.get")
def test_search_web_invalid_json_from_tinyfish(mock_get):
    mock_resp = MagicMock()
    mock_resp.is_successful = True
    mock_resp.json.side_effect = ValueError("bad JSON")
    mock_get.return_value = mock_resp

    with patch("duckduckgo_search.DDGS") as mock_ddgs_class:
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = [
            {"title": "JSON Fallback", "body": "json error fallback", "href": "https://jsonfallback.co"}
        ]
        mock_ddgs_class.return_value.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs_class.return_value.__exit__ = MagicMock(return_value=None)

        result = search_web("test query")
        assert "JSON Fallback" in result


# ── Test: search_web no results from either source ───────────────────────────

@patch("Tools.web_search._tinyfish_search", return_value=_tf_response(results=[], total_results=0))
def test_search_web_no_results_from_either_source(mock_tinyfish):
    with patch("duckduckgo_search.DDGS") as mock_ddgs_class:
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = []
        mock_ddgs_class.return_value.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs_class.return_value.__exit__ = MagicMock(return_value=None)

        result = search_web("very obscure query xyz123")
        assert "No search results found for: very obscure query xyz123" == result


# ── Test: search_news returns formatted news ───────────────────────────────────

@patch("ddgs.DDGS")
def test_search_news_with_results(mock_ddgs_class):
    mock_ddgs = MagicMock()
    mock_ddgs.news.return_value = [
        {
            "title": "Breaking News",
            "body": "Important development today.",
            "url": "https://news.example.com",
            "source": "Example Daily",
        }
    ]
    mock_ddgs_class.return_value.__enter__ = MagicMock(return_value=mock_ddgs)
    mock_ddgs_class.return_value.__exit__ = MagicMock(return_value=None)

    result = search_news("climate change")
    assert "Breaking News" in result
    assert "Important development today." in result
    assert "Example Daily" in result


# ── Test: search_news with no results ──────────────────────────────────────────

@patch("ddgs.DDGS")
def test_search_news_no_results(mock_ddgs_class):
    mock_ddgs = MagicMock()
    mock_ddgs.news.return_value = []
    mock_ddgs_class.return_value.__enter__ = MagicMock(return_value=mock_ddgs)
    mock_ddgs_class.return_value.__exit__ = MagicMock(return_value=None)

    result = search_news("completely unrelated stuff xyz")
    assert "No news found for: completely unrelated stuff xyz" == result
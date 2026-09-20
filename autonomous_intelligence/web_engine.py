"""
Web Research Engine for autonomous Internet research.
Uses programmatic search and content extraction.
"""
import re
import time
import hashlib
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Dict, List, Optional, Tuple
from html.parser import HTMLParser

from .models import Source, SourceType, BrowserTab
from .events import EventBus, EventType, create_event
from .config import ResearchConfig
from .permissions import PermissionManager


class HTMLTextExtractor(HTMLParser):
    """Extract readable text from HTML."""

    def __init__(self):
        super().__init__()
        self._text = []
        self._skip = False
        self._skip_tags = {"script", "style", "nav", "footer", "header", "noscript", "iframe", "svg"}
        self._current_tag = ""
        self._in_article = False
        self._in_main = False
        self._in_code = False
        self._code_block = []

    def handle_starttag(self, tag, attrs):
        self._current_tag = tag
        if tag in self._skip_tags:
            self._skip = True
        if tag in ("article", "main", "section", "div"):
            for attr, val in attrs:
                if attr == "class" and val:
                    classes = val.lower()
                    if any(x in classes for x in ["article", "content", "main", "post", "entry", "text"]):
                        self._in_article = True
                    if "code" in classes or "pre" in classes:
                        self._in_code = True
        if tag == "pre":
            self._in_code = True
            self._code_block = []

    def handle_endtag(self, tag):
        if tag in self._skip_tags:
            self._skip = False
        if tag in ("article", "main", "section"):
            self._in_article = False
        if tag == "pre" and self._in_code:
            self._in_code = False
            if self._code_block:
                self._text.append("[CODE]: " + " ".join(self._code_block))
                self._code_block = []

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text and len(text) > 2:
                if self._in_code:
                    self._code_block.append(text)
                else:
                    self._text.append(text)

    def get_text(self) -> str:
        return "\n".join(self._text)


class LinkExtractor(HTMLParser):
    """Extract links from HTML."""

    def __init__(self, base_url: str = ""):
        super().__init__()
        self.links = []
        self.base_url = base_url

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr, val in attrs:
                if attr == "href" and val:
                    self.links.append(val)


class WebResearchEngine:
    """Handles all web research operations."""

    def __init__(
        self,
        config: ResearchConfig,
        event_bus: EventBus,
        permissions: PermissionManager,
    ):
        self.config = config
        self.events = event_bus
        self.permissions = permissions
        self._tabs: Dict[str, BrowserTab] = {}
        self._visited_urls: set = set()
        self._cache: Dict[str, str] = {}

    def search(self, query: str, num_results: int = 8) -> List[Dict[str, str]]:
        """Search the web and return results."""
        if not self.permissions.can_access_web():
            return []

        self.events.emit(create_event(
            EventType.SEARCH_STARTED,
            query=query, num_results=num_results
        ))

        results = self._duckduckgo_search(query, num_results)

        self.events.emit(create_event(
            EventType.SEARCH_COMPLETED,
            query=query, results_count=len(results)
        ))

        return results

    def _duckduckgo_search(self, query: str, num_results: int = 8) -> List[Dict[str, str]]:
        """Search using DuckDuckGo HTML."""
        try:
            encoded = urllib.parse.quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded}"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response = urllib.request.urlopen(req, timeout=self.config.request_timeout)
            html = response.read().decode("utf-8", errors="ignore")

            results = []
            # Extract search results from DuckDuckGo HTML
            # Pattern: <a rel="nofollow" class="result__a" href="URL">TITLE</a>
            links = re.findall(
                r'class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
                html, re.DOTALL
            )
            snippets = re.findall(
                r'class="result__snippet"[^>]*>(.*?)</(?:a|span|div)',
                html, re.DOTALL
            )

            for i, (url, title) in enumerate(links[:num_results]):
                title_clean = re.sub(r'<[^>]+>', '', title).strip()
                snippet = ""
                if i < len(snippets):
                    snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()

                # Decode DuckDuckGo redirect URL
                if "uddg=" in url:
                    url = urllib.parse.unquote(url.split("uddg=")[1].split("&")[0])

                if url.startswith("http"):
                    results.append({
                        "url": url,
                        "title": title_clean,
                        "snippet": snippet,
                        "domain": urllib.parse.urlparse(url).netloc,
                    })

            return results

        except Exception as e:
            self.events.emit(create_event(
                EventType.ERROR_OCCURRED,
                error=f"Search failed: {str(e)[:100]}"
            ))
            return []

    def open_page(self, url: str) -> Optional[BrowserTab]:
        """Open and read a web page."""
        if not self.permissions.check_url_access(url):
            return None

        if url in self._visited_urls:
            return None

        tab = BrowserTab(
            url=url,
            domain=urllib.parse.urlparse(url).netloc,
            status="loading",
            action="opening",
        )
        self._tabs[tab.id] = tab

        self.events.emit(create_event(
            EventType.TAB_OPENED,
            tab_id=tab.id, url=url, domain=tab.domain
        ))

        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response = urllib.request.urlopen(req, timeout=self.config.request_timeout)
            html = response.read().decode("utf-8", errors="ignore")

            tab.status = "loaded"
            tab.action = "reading"

            self.events.emit(create_event(
                EventType.PAGE_OPENED,
                tab_id=tab.id, url=url, size=len(html)
            ))

            # Extract text with site-specific parsing
            text = self._extract_structured_content(url, html)
            title = self._extract_title(html)

            tab.title = title or url
            tab.status = "read"
            tab.action = "extracted"
            self._visited_urls.add(url)

            # Cache content
            self._cache[url] = text[:50000]

            self.events.emit(create_event(
                EventType.PAGE_READ,
                tab_id=tab.id, url=url, title=title,
                text_length=len(text)
            ))

            return tab

        except Exception as e:
            tab.status = "error"
            tab.action = str(e)[:100]
            self.events.emit(create_event(
                EventType.ERROR_OCCURRED,
                tab_id=tab.id, error=str(e)[:100]
            ))
            return tab

    def read_page(self, url: str) -> str:
        """Read and return the text content of a page."""
        if url in self._cache:
            return self._cache[url]

        tab = self.open_page(url)
        if tab and tab.url in self._cache:
            return self._cache[tab.url]

        return ""

    def extract_links(self, url: str, html: str = "") -> List[str]:
        """Extract links from a page."""
        if not html and url in self._cache:
            # Re-fetch minimal HTML for link extraction
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                })
                response = urllib.request.urlopen(req, timeout=self.config.request_timeout)
                html = response.read().decode("utf-8", errors="ignore")
            except Exception:
                return []

        extractor = LinkExtractor(url)
        try:
            extractor.feed(html)
        except Exception:
            pass

        # Normalize and filter links
        base_domain = urllib.parse.urlparse(url).netloc
        links = []
        for link in extractor.links:
            if link.startswith("/"):
                link = f"https://{base_domain}{link}"
            elif not link.startswith("http"):
                continue

            link_domain = urllib.parse.urlparse(link).netloc
            if link_domain and link_domain != base_domain:
                continue  # Skip external links

            if link not in self._visited_urls:
                links.append(link)

        return links[:10]

    def close_tab(self, tab_id: str):
        """Close a browser tab."""
        if tab_id in self._tabs:
            self._tabs[tab_id].status = "closed"
            self.events.emit(create_event(EventType.TAB_CLOSED, tab_id=tab_id))
            del self._tabs[tab_id]

    def get_open_tabs(self) -> List[Dict]:
        """Get info about open tabs."""
        return [
            {
                "id": tab.id,
                "url": tab.url,
                "title": tab.title,
                "domain": tab.domain,
                "status": tab.status,
                "action": tab.action,
                "relevance": tab.relevance,
            }
            for tab in self._tabs.values()
            if tab.status != "closed"
        ]

    def get_cached_content(self, url: str) -> str:
        return self._cache.get(url, "")

    def clear_cache(self):
        self._cache.clear()
        self._visited_urls.clear()

    def _extract_text(self, html: str) -> str:
        extractor = HTMLTextExtractor()
        try:
            extractor.feed(html)
        except Exception:
            pass
        return extractor.get_text()

    def _extract_title(self, html: str) -> str:
        match = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _extract_structured_content(self, url: str, html: str) -> str:
        """Extract structured content based on site type."""
        domain = urllib.parse.urlparse(url).netloc.lower()

        # Wikipedia
        if "wikipedia.org" in domain:
            return self._extract_wikipedia(html)

        # GitHub
        if "github.com" in domain:
            return self._extract_github(html)

        # arXiv
        if "arxiv.org" in domain:
            return self._extract_arxiv(html)

        # Documentation sites
        if any(x in domain for x in ["readthedocs.io", "docs.python.org", "developer.mozilla.org"]):
            return self._extract_documentation(html)

        # Stack Overflow
        if "stackoverflow.com" in domain:
            return self._extract_stackoverflow(html)

        # Default: extract main content
        return self._extract_main_content(html)

    def _extract_wikipedia(self, html: str) -> str:
        """Extract Wikipedia article content."""
        # Get the main article body
        match = re.search(r'<div[^>]*id="mw-content-text"[^>]*>(.*?)</div>\s*<div', html, re.DOTALL)
        if not match:
            # Try alternative pattern
            match = re.search(r'<div[^>]*class="mw-parser-output"[^>]*>(.*?)</div>\s*<div[^>]*class="', html, re.DOTALL)

        if match:
            content = match.group(1)
            # Remove references, edit links, etc.
            content = re.sub(r'<ref[^>]*>.*?</ref>', '', content, flags=re.DOTALL)
            content = re.sub(r'<sup[^>]*>.*?</sup>', '', content, flags=re.DOTALL)
            content = re.sub(r'<span class="mw-editsection">.*?</span>', '', content, flags=re.DOTALL)
            content = re.sub(r'<div[^>]*class="[^"]*infobox[^"]*"[^>]*>.*?</div>', '', content, flags=re.DOTALL)
            content = re.sub(r'<div[^>]*class="[^"]*sidebar[^"]*"[^>]*>.*?</div>', '', content, flags=re.DOTALL)
            content = re.sub(r'<table[^>]*>.*?</table>', '', content, flags=re.DOTALL)
            text = self._extract_text(content)
            if len(text) > 500:
                return text[:10000]

        # Fallback: try to get first few paragraphs
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
        texts = []
        for p in paragraphs[:15]:
            text = self._extract_text(p)
            if len(text) > 50:
                texts.append(text)

        if texts:
            return "\n\n".join(texts)[:10000]

        return self._extract_text(html)[:5000]

    def _extract_github(self, html: str) -> str:
        """Extract GitHub README content."""
        # Look for README - try multiple patterns
        patterns = [
            r'<article[^>]*class="markdown-body[^"]*"[^>]*>(.*?)</article>',
            r'<div[^>]*class="[^"]*readme[^"]*"[^>]*>(.*?)</div>\s*</div>',
            r'<div[^>]*id="readme"[^>]*>(.*?)</div>\s*</div>',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                text = self._extract_text(match.group(1))
                if len(text) > 200:
                    return text[:10000]

        # Try to get repository description
        desc_match = re.search(r'<p[^>]*class="[^"]*f4[^"]*"[^>]*>(.*?)</p>', html, re.DOTALL)
        if desc_match:
            desc = self._extract_text(desc_match.group(1))
        else:
            desc = ""

        # Get file listing
        files = re.findall(r'<a[^>]*class="[^"]*js-navigation-open[^"]*"[^>]*title="([^"]*)"[^>]*>', html)
        if not files:
            files = re.findall(r'<a[^>]*class="[^"]*js-navigation-open[^"]*"[^>]*>(.*?)</a>', html, re.DOTALL)
            files = [self._extract_text(f) for f in files if self._extract_text(f)]

        parts = []
        if desc:
            parts.append(f"DESCRIPTION: {desc}")
        if files:
            # Filter out common navigation items
            filtered = [f for f in files if f not in ("..", ".", "LICENSE", "LICENSE.txt")]
            if filtered:
                parts.append(f"FILES: {', '.join(filtered[:20])}")

        if parts:
            return "\n\n".join(parts)[:10000]

        return self._extract_text(html)[:5000]

    def _extract_arxiv(self, html: str) -> str:
        """Extract arXiv abstract and metadata."""
        # Get title
        title_match = re.search(r'<h1 class="title[^"]*">(.*?)</h1>', html, re.DOTALL)
        title = self._extract_text(title_match.group(1)) if title_match else ""

        # Get abstract
        abstract_match = re.search(r'<blockquote class="abstract[^"]*">(.*?)</blockquote>', html, re.DOTALL)
        abstract = self._extract_text(abstract_match.group(1)) if abstract_match else ""

        # Get authors
        authors_match = re.search(r'<div class="authors">(.*?)</div>', html, re.DOTALL)
        authors = self._extract_text(authors_match.group(1)) if authors_match else ""

        parts = []
        if title:
            parts.append(f"TITLE: {title}")
        if authors:
            parts.append(f"AUTHORS: {authors}")
        if abstract:
            parts.append(f"ABSTRACT: {abstract}")

        return "\n\n".join(parts) if parts else self._extract_text(html)[:5000]

    def _extract_documentation(self, html: str) -> str:
        """Extract documentation content."""
        # Look for main content area
        match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
        if not match:
            match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
        if not match:
            match = re.search(r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)

        if match:
            text = self._extract_text(match.group(1))
            return text[:8000]

        return self._extract_text(html)[:5000]

    def _extract_stackoverflow(self, html: str) -> str:
        """Extract Stack Overflow question and answers."""
        parts = []

        # Question
        q_match = re.search(r'<div class="question[^"]*"[^>]*>(.*?)</div>\s*<div class="answer', html, re.DOTALL)
        if q_match:
            question = self._extract_text(q_match.group(1))
            parts.append(f"QUESTION:\n{question[:3000]}")

        # Answers
        answers = re.findall(r'<div class="answer[^"]*"[^>]*>(.*?)</div>\s*(?=<div class="answer|<div class="post-layout")', html, re.DOTALL)
        for i, answer in enumerate(answers[:3]):
            answer_text = self._extract_text(answer)
            parts.append(f"ANSWER {i+1}:\n{answer_text[:2000]}")

        return "\n\n".join(parts) if parts else self._extract_text(html)[:5000]

    def _extract_main_content(self, html: str) -> str:
        """Extract main content from any page."""
        # Try common content selectors
        selectors = [
            r'<main[^>]*>(.*?)</main>',
            r'<article[^>]*>(.*?)</article>',
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*post[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*entry[^"]*"[^>]*>(.*?)</div>',
        ]

        for pattern in selectors:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                text = self._extract_text(match.group(1))
                if len(text) > 200:  # Found meaningful content
                    return text[:8000]

        # Fallback to full text extraction
        return self._extract_text(html)[:5000]

    def _make_source(self, url: str, title: str = "") -> Source:
        domain = urllib.parse.urlparse(url).netloc
        return Source(
            source_type=SourceType.WEB_PAGE,
            url=url,
            title=title,
            domain=domain,
        )

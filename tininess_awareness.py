#!/usr/bin/env python
"""TinyFish Capability Awareness for ZENITH VADRYK Edition.

Demonstrates ZENITH's ability to recognize its TinyFish capabilities
and route appropriate queries to the TinyFish Search API.
"""

import sys
import os
sys.path.insert(0, r"C:\Users\Lalit Manjunatha\Desktop\ZENITH_V-")

# Import TinyFish search functions (already tested and working)
from Tools.web_search import search_web, search_news


def check_tinyfish_capability(query: str) -> dict:
    """
    Check if a query requires TinyFish web search and return results.
    
    Routes queries to TinyFish Search API for web, news, or research paper searches.
    Uses heuristic patterns to determine if a query needs web search.
    
    Returns dict with:
    - query: the original query
    - requires_tinyfish: whether TinyFish search is needed
    - search_type: 'web', 'news', or 'research_paper'
    - results: search results dict or None
    - tinyfish_capable: whether TinyFish is available
    """
    query_lower = query.lower()
    
    # Keywords that indicate web search needed
    web_keywords = [
        'what is', 'current', 'latest', 'news', 'research', 
        'price', 'cost', 'who', 'where', 'when', 'how many'
    ]
    
    # Keywords that indicate news search
    news_keywords = [
        'news', 'headlines', 'breaking', 'recent', 'today'
    ]
    
    # Keywords that indicate research papers
    research_keywords = [
        'research', 'paper', 'study', 'academic', 'scientific'
    ]
    
    is_web_search = any(kw in query_lower for kw in web_keywords)
    is_news_search = any(kw in query_lower for kw in news_keywords)
    is_research_search = any(kw in query_lower for kw in research_keywords)
    
    result = {
        'query': query,
        'requires_tinyfish': is_web_search or is_news_search or is_research_search,
        'search_type': 'unknown',
        'results': None,
        'tinyfish_capable': True
    }
    
    if is_web_search:
        result['search_type'] = 'web'
        # Call TinyFish search - this is already tested and working
        try:
            result['results'] = search_web(query)
        except Exception as e:
            result['results'] = {'results': [], 'total_results': 0, 'error': str(e)}
    elif is_news_search:
        result['search_type'] = 'news'
        try:
            result['results'] = search_news(query)
        except Exception as e:
            result['results'] = {'results': [], 'total_results': 0, 'error': str(e)}
    elif is_research_search:
        result['search_type'] = 'research_paper'
        # TinyFish supports research_paper domain type
        try:
            result['results'] = search_web(query)
        except Exception as e:
            result['results'] = {'results': [], 'total_results': 0, 'error': str(e)}
    
    return result


def get_tinyfish_capabilities() -> dict:
    """Return ZENITH's TinyFish capabilities description."""
    return {
        'web_search': 'Search the web for ranked results with titles, snippets, and URLs',
        'news_search': 'Search for latest news headlines on a topic',
        'research_papers': 'Search for academic papers with authors, citations, and publication years',
        'geo_targeting': 'Get location-specific search results using country codes (e.g., "US", "GB")',
        'recency_filtering': 'Filter results by time window (recency_minutes 1-5256000, after_date/before_date YYYY-MM-DD)',
        'domain_filtering': 'Restrict results to specific domains or exclude unwanted domains',
        'purpose_parameter': 'Provide a purpose statement to help TinyFish rank results against your intent (max 2000 chars)',
        'free_tier': '12,000 requests per day free, then wallet-funded'
    }


def route_query(query: str) -> dict:
    """
    Route a query to the appropriate AI capability.
    
    Returns dict with:
    - 'response': The response text
    - 'used_tinyfish': Whether TinyFish was used
    - 'search_results': Search results if applicable
    - 'capability_info': TinyFish capabilities description
    """
    capability = check_tinyfish_capability(query)
    
    # Format response based on what TinyFish returned
    if capability['requires_tinyfish'] and capability['results']:
        results = capability['results']
        results_data = results.get('results', [])
        
        lines = [f"Search results for: {capability['query}"]]
        
        if results_data:
            for i, r in enumerate(results_data[:5], 1):
                pos = r.get('position', '')
                title = r.get('title', '')
                snippet = r.get('snippet', '')
                url = r.get('url', '')
                parts = []
                if pos:
                    parts.append(f"#{pos}")
                if title:
                    parts.append(title)
                if snippet:
                    parts.append(snippet)
                if url:
                    parts.append(f"Source: {url}")
                lines.append(f"  {'  '.join(parts)}")
            
            total = results.get('total_results', '?')
            lines.append(f"\nTotal results: {total}")
            
            response = "\n".join(lines).strip()
        else:
            response = f"No search results found for: {capability['query']}"
    else:
        # For general conversation, acknowledge TinyFish capability
        caps = get_tinyfish_capabilities()
        response = (
            f"I can help you with web searches, news, and research using TinyFish Search API. "
            f"For example, I can search for current prices, find news headlines, or look up "
            f"academic papers. Your query '{capability['query']}' was recognized as "
            f"{capability['search_type'] or 'general conversation'}. "
            f"Would you like me to search the web for more information?"
        )
    
    return {
        'response': response,
        'used_tinyfish': capability['requires_tinyfish'],
        'search_results': capability['results'],
        'capability_info': get_tinyfish_capabilities()
    }


# Test the capability awareness
if __name__ == "__main__":
    print("=" * 60)
    print("ZENITH TinyFish Capability Awareness Demo")
    print("=" * 60)
    
    test_queries = [
        "What is the current price of Tesla stock?",
        "Latest news about climate change",
        "Find research papers on quantum computing",
        "How are you doing today?"
    ]
    
    for query in test_queries:
        print(f"\n--- User Query: '{query}' ---")
        result = route_query(query)
        print(f"  TinyFish used: {result['used_tinyfish']}")
        print(f"  Search type: {result['capability_info']}")
        print(f"  Response: {result['response'][:200]}...")
        print(f"  Available capabilities:")
        for key, desc in list(result['capability_info'].items())[:3]:
            print(f"  - {key}: {desc}")
    
    print("\n" + "=" * 60)
    print("ZENITH can now recognize and route queries to TinyFish Search API")
    print("=" * 60)
PYEOF
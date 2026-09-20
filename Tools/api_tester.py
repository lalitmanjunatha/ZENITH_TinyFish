"""
ZENITH API Tester Tool
Provides: api_test
"""

import json
import time
from typing import Optional
from livekit.agents import function_tool

import aiohttp

TOOL = {
    "name": "api_tester",
    "description": "Test a REST API endpoint. Returns HTTP status, headers, and response body. Use when the user wants to test or debug an API endpoint with any HTTP method.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "url": {"type": "STRING", "description": "Full API URL (e.g. 'https://jsonplaceholder.typicode.com/posts/1')"},
            "method": {"type": "STRING", "description": "HTTP method: GET, POST, PUT, DELETE, PATCH (default: GET)"},
            "headers": {"type": "STRING", "description": "JSON string of headers (e.g. '{\"Authorization\": \"Bearer xxx\"}')"},
            "body": {"type": "STRING", "description": "JSON string of request body (for POST/PUT/PATCH)"},
            "timeout": {"type": "INTEGER", "description": "Request timeout in seconds (default: 10)"}
        },
        "required": ["url"]
    },
    "handler": "api_test",
}


@function_tool()
async def api_test(
    url: str,
    method: str = "GET",
    headers: Optional[str] = None,
    body: Optional[str] = None,
    timeout: int = 10,
) -> str:
    """
    Test a REST API endpoint. Returns status, headers, and response body.

    Args:
        url: Full API URL (e.g. 'https://jsonplaceholder.typicode.com/posts/1')
        method: HTTP method — 'GET', 'POST', 'PUT', 'DELETE', 'PATCH' (default: 'GET')
        headers: JSON string of headers (e.g. '{"Authorization": "Bearer xxx"}')
        body: JSON string of request body (for POST/PUT/PATCH)
        timeout: Request timeout in seconds (default: 10)

    Example: api_test("https://jsonplaceholder.typicode.com/posts/1", "GET")
    """
    try:
        parsed_headers = {}
        if headers:
            try:
                parsed_headers = json.loads(headers)
            except json.JSONDecodeError:
                return f"Invalid headers JSON: {headers}"

        parsed_body = None
        if body:
            try:
                parsed_body = json.loads(body)
            except json.JSONDecodeError:
                parsed_body = body

        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            kwargs = {
                "headers": parsed_headers,
                "timeout": aiohttp.ClientTimeout(total=timeout),
            }

            if parsed_body and method.upper() in ("POST", "PUT", "PATCH"):
                kwargs["json"] = parsed_body

            async with session.request(method.upper(), url, **kwargs) as resp:
                elapsed = (time.time() - start_time) * 1000

                response_text = await resp.text()
                try:
                    response_json = json.loads(response_text)
                    response_body = json.dumps(response_json, indent=2, ensure_ascii=False)
                except json.JSONDecodeError:
                    response_body = response_text

                response_headers = dict(resp.headers)

                lines = [
                    f"HTTP {resp.status} {resp.reason} — {elapsed:.0f}ms",
                    f"\nRequest:",
                    f"  {method.upper()} {url}",
                ]

                if parsed_headers:
                    lines.append(f"  Headers: {json.dumps(parsed_headers)}")
                if parsed_body:
                    lines.append(f"  Body: {json.dumps(parsed_body)}")

                lines.append(f"\nResponse Headers:")
                for key, val in list(response_headers.items())[:10]:
                    lines.append(f"  {key}: {val}")

                lines.append(f"\nResponse Body ({len(response_text)} chars):")
                if len(response_body) > 2000:
                    lines.append(response_body[:2000] + "\n... (truncated)")
                else:
                    lines.append(response_body)

                return "\n".join(lines)

    except aiohttp.ClientError as e:
        return f"Connection error: {str(e)}"
    except asyncio.TimeoutError:
        return f"Request timed out after {timeout}s"
    except Exception as e:
        return f"API test error: {str(e)
}"

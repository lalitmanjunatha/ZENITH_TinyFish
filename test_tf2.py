import os
os.chdir(r"C:\Users\Lalit Manjunatha\Desktop\ZENITH_V-")
from Tools.web_search import _tinyfish_search

try:
    result = _tinyfish_search("AI small language models", domain_type="web")
    print("Success!")
    print("Type of result:", type(result))
    print("Result keys:", list(result.keys()) if isinstance(result, dict) else "N/A")
    print("results key exists:", "results" in result if isinstance(result, dict) else "N/A")
    print("results value:", result.get("results", "N/A"))
    if "results" in result and result["results"]:
        r = result["results"][0]
        print("First result keys:", list(r.keys()) if isinstance(r, dict) else "N/A")
        print("First result:", r)
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])
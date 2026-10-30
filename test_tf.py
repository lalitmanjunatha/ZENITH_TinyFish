import os
os.chdir(r"C:\Users\Lalit Manjunatha\Desktop\ZENITH_V-")
from Tools.web_search import _tinyfish_search

try:
    result = _tinyfish_search("AI small language models")
    print("Success!")
    print("Query:", result.get("query"))
    print("Results count:", len(result.get("results", [])))
    print("Total results:", result.get("total_results"))
    print("Page:", result.get("page"))
    if result.get("results"):
        r = result["results"][0]
        print("First result position:", r.get("position"))
        print("First result title:", r.get("title"))
        print("First result snippet:", r.get("snippet"))
        print("First result URL:", r.get("url"))
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:200])
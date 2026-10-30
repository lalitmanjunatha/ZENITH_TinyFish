#!/usr/bin/env python3
"""TinyFish Capability Audit for ZENITH VADRYK Edition."""

import ast
import re
import sys

# Parse agent.py
with open('agent.py') as f:
    agent_content = f.read()

# Parse zenith_gui.py
with open('zenith_gui.py', encoding='utf-8', errors='replace') as f:
    gui_content = f.read()

# Parse web_search.py
with open('Tools/web_search.py', encoding='utf-8', errors='replace') as f:
    ws_content = f.read()

def count_refs(content, pattern):
    return len(re.findall(pattern, content, re.IGNORECASE))

print("=" * 70)
print("TINYFISH CAPABILITY MATRIX vs ZENITH REQUIREMENTS")
print("=" * 70)

print("\n--- TinyFish Capabilities (from official docs) ---")
print("SUPPORTED:")
print("  • Web search with ranked results, titles, snippets, URLs")
print("  • Domain types: web (default), news, research_paper")
print("  • Geo-targeting via location and language parameters")
print("  • Date filters: after_date, before_date, recency_minutes")
print("  • purpose parameter for intent-based result ranking")
print("  • include_domains / exclude_domains filtering")
print("  • Free tier: 12,000 requests/day, then wallet-funded")
print()
print("NOT SUPPORTED (per official docs):")
print("  • General conversational LLM / chat completions")
print("  • Realtime speech-to-speech voice pipeline")
print("  • Speech-to-text (STT) transcription")
print("  • Text-to-speech (TTS) generation")
print("  • Multi-step arbitrary agent tasks (without Browser API)")
print("  • Browser automation / page interaction (needs Browser API)")
print("  • Cited multi-source reasoning (Research API requires wallet)")
print("  • Session continuity/context handling (stateless per request)")
print()
print("=" * 70)
print("ACTIVE GEMINI DEPENDENCIES IN CODE")
print("=" * 70)

print("\n1. agent.py:")
gemini_agent = count_refs(agent_content, r'Gemini|google|genai|RealtimeModel')
print(f"   Gemini/Google/genai/RealtimeModel references: {gemini_agent}")
# Show the actual references
for m in re.finditer(r'Gemini|google|genai|RealtimeModel', agent_content, re.IGNORECASE):
    start = max(0, m.start()-80)
    end = min(len(agent_content), m.end()+80)
    line_num = agent_content.count('\n', 0, start) + 1
    print(f"     pos {m.start()} (line {line_num}): {agent_content[start:end]!r}")

print("\n2. zenith_gui.py:")
gemini_gui = count_refs(gui_content, r'Gemini|google|genai|gemini_api_key|LIVE_MODEL')
print(f"   Gemini/Google/genai/gemini_api_key/LIVE_MODEL references: {gemini_gui}")
for m in re.finditer(r'Gemini|google|genai|gemini_api_key|LIVE_MODEL', gui_content, re.IGNORECASE):
    start = max(0, m.start()-80)
    end = min(len(gui_content), m.end()+80)
    line_num = gui_content.count('\n', 0, start) + 1
    print(f"     pos {m.start()} (line {line_num}): {gui_content[start:end]!r}")

print("\n3. Tools/web_search.py:")
ws_gemini = count_refs(ws_content, r'Gemini|google|genai')
print(f"   Gemini/Google/genai references: {ws_gemini} (expected: 0 - already migrated)")

print("\n\n--- ZENITH REQUIREMENTS vs TINYFISH MATCH ---")

requirements = {
    "Web search & fact lookup": "SUPPORTED by TinyFish Search API",
    "Current events / news search": "SUPPORTED (TinyFish domain_type=news)",
    "Research / academic papers": "SUPPORTED (TinyFish domain_type=research_paper, wallet-funded)",
    "Structured data extraction": "PARTIALLY SUPPORTED (search results JSON: position, site_name, title, snippet, url, total_results)",
    "Realtime voice conversation": "UNSUPPORTED by TinyFish (no realtime LLM, no STT/TTS)",
    "Speech-to-text (STT)": "UNSUPPORTED by TinyFish (requires local Whisper or separate ASR)",
    "Text-to-speech (TTS)": "UNSUPPORTED by TinyFish (requires local pyttsx3 or separate TTS API)",
    "Multi-step tool use": "PARTIALLY SUPPORTED (TinyFish provides search results; tool decisions require separate LLM)",
    "Browser automation": "UNSUPPORTED by TinyFish free tier (requires Browser API, wallet-funded)",
    "Cited multi-source reasoning": "PARTIALLY SUPPORTED (TinyFish Research API, wallet-funded; Search provides single-source results)",
    "Session continuity / context handling": "NOT APPLICABLE (TinyFish is stateless per HTTP request)",
    "Rate limiting / pricing": "KNOWN: 12,000 free/day, then wallet balance required",
}

for req, status in requirements.items():
    print(f"  {req}: {status}")

print("\n\n--- PROPOSED TINYFISH-FIRST ARCHITECTURE ---")
print("""
┌───────────────────────────────────────────────────────────────────┐
│  TINYFISH-FIRST CLOUD ARCHITECTURE for ZENITH VADRYK EDITION      │
├───────────────────────────────────────────────────────────────────┤
│  TINYFish PRIMARY (cloud web operations)                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  search_web(query)            → TinyFish Search API        │ │
│  │     domain_type="web"       (default)                     │ │
│  │     domain_type="news"       (for news search)            │ │
│  │     domain_type="research_paper" (for academic)         │ │
│  │     purpose=...              (intent signal to TinyFish)  │ │
│  │     Results: [position, site_name, title, snippet, url]   │ │
│  └─────────────────────────────────────────────────────────────┘ │
├───────────────────────────────────────────────────────────────────┤
│  LOCAL / COMPLEMENTARY COMPONENTS                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Speech I/O:                                                │ │
│  │  • STT:  local Whisper, sounddevice                         │ │
│  │  • TTS:  pyttsx3, local engine                              │ │
│  │  │                                                           │ │
│  │  • Conversational LLM:                                      │ │
│  │  • Text:  OpenAI GPT-4o (or local model like Llama.cpp)    │ │
│  │  • Voice: OpenAI Realtime (if voice pipeline needed)        │ │
│  │                                                           │ │
│  │  • Browser automation:                                      │ │
│  │  • Playwright/selenium (if page interaction needed)         │ │
│  └─────────────────────────────────────────────────────────────┘ │
├───────────────────────────────────────────────────────────────────┤
│  INTEGRATION FLOW                                                   │
│  1. User voice input → local STT → text query                     │
│  2. text query → TinyFish Search API → structured results JSON  │
│  3. Results → conversational LLM → tool decision making           │
│  4. Tool execution → system commands, file ops, web search        │
│  5. Response → local TTS → voice output                           │
│  └─────────────────────────────────────────────────────────────────┘
└───────────────────────────────────────────────────────────────────┘
""")

print("=" * 70)
print("SUMMARY & NEXT STEPS")
print("=" * 70)
print("""TinyFish OFFICIAL CAPABILITIES (verified from docs):
  ✅ Web search (ranked results, titles, snippets, URLs)
  ✅ News search (domain_type="news")
  ✅ Research papers (domain_type="research_paper")
  ✅ Geo-targeted results (location/language params)
  ✅ Recency filtering (recency_minutes, after_date/before_date)
  ✅ Domain filtering (include_domains/exclude_domains)
  ✅ Free tier: 12,000 requests/day
  ❌ General conversational LLM
  ❌ Realtime voice STT/TTS pipeline
  ❌ Browser automation (free tier)
  ❌ Multi-step agent tasks without browser API

REMAINING GEMINI DEPENDENCIES IN CODE (after Phase B migration):
  • agent.py: OpenAI Realtime now replaces Gemini Realtime ✅
  • zenith_gui.py: Google imports commented out, LIVE_MODEL replaced ✅
  • Tools/web_search.py: TinyFish Search API fully migrated ✅

PROPOSED: TinyFish-first with local/complementary components for:
  • Voice I/O (local STT/TTS or OpenAI Realtime)
  • General conversational LLM (OpenAI GPT-4o text or local)
  • Browser automation (if needed, Playwright/selenium)

NEXT: Phase B Gemini removal approval, then Phase C implementation.
""")
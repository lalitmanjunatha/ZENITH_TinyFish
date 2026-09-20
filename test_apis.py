"""
ZENITH 5.0 — Pre-Demo Health Check
Run this BEFORE your presentation to verify everything works.
Usage: python test_apis.py
"""

import os
import sys
import socket
import time
from dotenv import load_dotenv

load_dotenv()

# Colors
G = "\033[92m"  # Green
Y = "\033[93m"  # Yellow
R = "\033[91m"  # Red
C = "\033[96m"  # Cyan
W = "\033[0m"   # Reset
B = "\033[1m"   # Bold

passed = 0
failed = 0
warned = 0

def check(name, condition, detail=""):
    global passed, failed, warned
    if condition is True:
        print(f"  {G}[PASS]{W} {name}")
        passed += 1
    elif condition == "warn":
        print(f"  {Y}[WARN]{W} {name} — {detail}")
        warned += 1
    else:
        print(f"  {R}[FAIL]{W} {name} — {detail}")
        failed += 1

def banner(text):
    print(f"\n{C}{B}{'=' * 50}{W}")
    print(f"{C}{B}  {text}{W}")
    print(f"{C}{B}{'=' * 50}{W}")

# =========================
banner("ZENITH 5.0 — PRE-DEMO HEALTH CHECK")
# =========================

# 1. Network
banner("1. NETWORK")
try:
    socket.create_connection(("8.8.8.8", 53), timeout=5)
    check("Internet connection", True)
except Exception:
    check("Internet connection", False, "No internet access")

# 2. Environment Variables
banner("2. API KEYS")
keys = {
    "GOOGLE_API_KEY": "Google Gemini (required for voice + vision)",
    "LIVEKIT_URL": "LiveKit cloud URL",
    "LIVEKIT_API_KEY": "LiveKit API key",
    "LIVEKIT_API_SECRET": "LiveKit API secret",
    "GROQ_API_KEY": "Groq (code generation)",
    "OPENAI_API_KEY": "OpenAI (backup LLM)",
}
for key, desc in keys.items():
    val = os.getenv(key, "")
    if val:
        check(f"{key}", True)
    else:
        check(f"{key}", False, f"{desc} — not set in .env")

# 3. Python Dependencies
banner("3. PYTHON PACKAGES")
deps = [
    ("livekit.agents", "livekit-agents"),
    ("livekit.plugins.google", "livekit-plugins-google"),
    ("pyautogui", "pyautogui"),
    ("aiohttp", "aiohttp"),
    ("psutil", "psutil"),
    ("PIL", "Pillow"),
    ("numpy", "numpy"),
    ("cv2", "opencv-python"),
    ("pytesseract", "pytesseract"),
    ("pygetwindow", "pygetwindow"),
    ("screen_brightness_control", "screen-brightness-control"),
    ("pycaw", "pycaw"),
]
for module, package in deps:
    try:
        __import__(module)
        check(f"pip install {package}", True)
    except ImportError:
        check(f"pip install {package}", False, f"Missing: {module}")

# 4. Tesseract OCR
banner("4. SYSTEM TOOLS")
tess_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(tess_path):
    check("Tesseract OCR installed", True)
else:
    check("Tesseract OCR installed", False, f"Not found at {tess_path}")

# 5. Tools directory
banner("5. TOOL MODULES")
tools_dir = os.path.join(os.path.dirname(__file__), "Tools")
expected_tools = [
    "manage_windows.py", "search_web.py", "send_whatsapp_message.py",
    "system_power_action.py", "open_app.py", "spotify.py",
    "generate_ai_image.py", "screen_analyzer.py", "code_generator.py",
    "excel_data_entery.py", "reminder.py", "youtube_videos.py",
]
for tool_file in expected_tools:
    tool_path = os.path.join(tools_dir, tool_file)
    if os.path.exists(tool_path):
        check(f"Tools/{tool_file}", True)
    else:
        check(f"Tools/{tool_file}", False, "File missing")

# 6. Assets
banner("6. ASSETS")
assets_dir = os.path.join(os.path.dirname(__file__), "assets")
for asset in ["icon_nova.ico", "notification.mp3"]:
    path = os.path.join(assets_dir, asset)
    if os.path.exists(path):
        check(f"assets/{asset}", True)
    else:
        check(f"assets/{asset}", False, "File missing")

# =========================
banner("SUMMARY")
# =========================
total = passed + failed + warned
print(f"\n  {G}{passed} passed{W}  |  {R}{failed} failed{W}  |  {Y}{warned} warnings{W}  |  {total} total\n")

if failed == 0:
    print(f"  {G}{B}READY FOR DEMO!{W}")
    print(f"  {G}All critical checks passed.{W}\n")
else:
    print(f"  {R}{B}FIX ISSUES BEFORE DEMO{W}")
    print(f"  {R}Fix the {failed} failed check(s) above.{W}\n")
    sys.exit(1)

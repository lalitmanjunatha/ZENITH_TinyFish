# ZENITH 5.0 — Demo Script & Cheat Sheet

## Pre-Demo Checklist

```
[ ] Run: python test_apis.py (all checks pass?)
[ ] Close unnecessary apps (reduce noise for voice)
[ ] Open Spotify (logged in, playlist ready)
[ ] Open a browser window with some content (for screen analysis)
[ ] Have a sample Excel file ready (for data entry demo)
[ ] Test microphone in a quiet corner first
[ ] Have phone ready to show WhatsApp message delivery
```

---

## Demo Flow (20-30 minutes)

### PART 1: Introduction (2 min)

**Say to class:**
> "Today I'll show you ZENITH 5.0 — a voice-controlled AI assistant I built using LiveKit and Google Gemini. It can control my entire computer, search the web, generate AI images, analyze screens, and much more — all through natural voice commands."

**Run the app:**
```bash
python agent.py
```

**Show the terminal** — audience will see the startup animation and status indicators loading.

---

### PART 2: Basic Commands (5 min)

| # | Say This (voice) | Expected Result | Backup Text |
|---|-----------------|-----------------|-------------|
| 1 | "What time is it?" | Current date, time, day | Type the command |
| 2 | "What's the weather in Tokyo?" | Live weather data | Type the command |
| 3 | "Who is the Prime Minister of India?" | Web search result | Type the command |

**Talking point:** "ZENITH uses Wikipedia, DuckDuckGo, and Open-Meteo APIs for real-time information."

---

### PART 3: System Control (5 min)

| # | Say This | Expected Result |
|---|----------|-----------------|
| 1 | "Open Notepad" | Notepad opens |
| 2 | "Open Chrome" | Chrome opens |
| 3 | "Set volume to 50%" | System volume changes |
| 4 | "Set brightness to 80%" | Screen brightness changes |
| 5 | "Minimize the window" | Active window minimizes |

**Talking point:** "ZENITH can control any application on the system using desktop automation."

---

### PART 4: AI Magic — Biggest Wow (8 min)

| # | Say This | Expected Result | Wow Factor |
|---|----------|-----------------|------------|
| 1 | "Take a screenshot and tell me what you see" | Gemini analyzes the screen | AI VISION |
| 2 | "Generate an AI image of a futuristic city at sunset" | Image generated + opens | AI CREATION |
| 3 | "Open Spotify and play a song" | Spotify opens, plays music | MULTI-APP |
| 4 | "What's on my screen right now?" | Another screen analysis | CONSISTENCY |

**Talking point:** "This uses Google Gemini's vision model to understand what's on screen in real-time."

---

### PART 5: Real-World Use (5 min)

| # | Say This | Expected Result |
|---|----------|-----------------|
| 1 | "Create an Excel file called Students" | Excel file created |
| 2 | "Write a letter about AI in Notepad" | Notepad opens with formatted letter |
| 3 | "Send WhatsApp message to [friend] saying Hello" | WhatsApp automation runs |

**Talking point:** "ZENITH automates real workflows — messaging, document creation, data entry."

---

### PART 6: Architecture Overview (3 min)

**Show this slide or say:**

```
ZENITH 5.0 Architecture:
├── Voice Engine: Google Gemini 2.5 Flash (Realtime)
├── Framework: LiveKit Agents
├── Tools: 100+ modular Python tools
├── VADRYK Framework:
│   ├── V - Veda (Knowledge)
│   ├── A - Artha (System Flow)
│   ├── D - Dhwani (Voice/Sound)
│   ├── R - Rachna (Creation)
│   ├── Y - Yukt (Communication)
│   └── K - Kriya (Action)
├── Autonomous Intelligence Engine:
│   ├── Web Research (DuckDuckGo + page reading)
│   ├── Local Intelligence (file search + code analysis)
│   ├── Knowledge Engine (evidence, verification, contradictions)
│   ├── Research Planner (auto-generates research plans)
│   └── Event System (35 real-time event types)
└── Platform: Windows + Python
```

---

## Backup Plan: Voice Fails

If voice recognition doesn't work in the noisy classroom:

1. **Option A:** Use the web interface to type commands
2. **Option B:** Have a second laptop/phone ready to demonstrate via screen share
3. **Option C:** Run pre-recorded video clips of each demo

**Quick fallback commands (type these in the web interface):**
```
What time is it?
What's the weather in Tokyo?
Open Notepad
Generate an AI image of a robot in a city
Take a screenshot and tell me what you see
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Network issue" message | Check WiFi, restart router |
| Voice not recognized | Move closer to mic, speak clearly |
| Tool fails | Say "Try again" — ZENITH retries |
| Slow response | Gemini API may be busy, wait 5s |
| Spotify doesn't open | Pre-open it before demo |

---

## Key Phrases to Use

- "Let me show you the power of voice-controlled AI"
- "ZENITH uses 53 tools I built from scratch"
- "This is running on Google Gemini's latest model"
- "All of this happens in real-time"
- "The entire system is built on Python and LiveKit"

---

## PART 7: Presentation Mode (5 min) — KILLER FEATURE!

**This is the killer feature — ZENITH helps you present LIVE!**

### Setup
```bash
# Have a PPT file ready
# Example: demo_presentation.pptx in the Nova 5.0 folder
```

### Voice Commands for Presentation

| # | Say This | Expected Result |
|---|----------|-----------------|
| 1 | "Load my presentation" | PPT opens in memory |
| 2 | "Start slideshow" | Full-screen presentation mode |
| 3 | "Next slide" | Goes to next slide |
| 4 | "Previous slide" | Goes to previous slide |
| 5 | "Read this slide" | ZENITH narrates slide content via TTS |
| 6 | "Stop slideshow" | Returns to normal view |

### Creating Presentations Live

| # | Say This | Expected Result |
|---|----------|-----------------|
| 1 | "Create a presentation about Artificial Intelligence" | New PPT generated |
| 2 | "Add a slide about machine learning" | New slide added |
| 3 | "Add a title slide with title 'AI Revolution'" | Title slide created |

### Simulations & Visualizations

| # | Say This | Expected Result |
|---|----------|-----------------|
| 1 | "Show me a pendulum simulation" | Physics sim with 4-panel plot |
| 2 | "Graph sin(x)" | 2D function graph |
| 3 | "Show me the derivative of x^2 at x=1" | Derivative + tangent line |
| 4 | "Show the integral of sin(x) from 0 to pi" | Area under curve |
| 5 | "Show me a Mandelbrot fractal" | Fractal image |
| 6 | "Show me a neural network" | NN architecture diagram |
| 7 | "Run gradient descent on rosenbrock" | Optimization path |
| 8 | "Simulate an RC circuit" | Charging/discharging curves |
| 9 | "Simulate an AND gate" | Truth table + waveform |
| 10 | "Show me projectile motion" | Trajectory + speed profile |

### Webcam Overlay

| # | Say This | Expected Result |
|---|----------|-----------------|
| 1 | "Start webcam overlay" | Webcam feed in corner |
| 2 | "Stop webcam overlay" | Webcam feed stops |

**Talking point:** "ZENITH doesn't just control the computer — it helps you present. I can load any PowerPoint, narrate slides, run physics simulations live, and even show my webcam feed in the corner."

---

## PART 8: Autonomous Intelligence Engine (5 min) — BREAKTHROUGH FEATURE!

**This is the crown jewel — ZENITH can think and research independently!**

### What It Does

ZENITH can autonomously:
1. Search the Internet for information
2. Read and analyze web pages
3. Search local files and code
4. Extract knowledge and detect contradictions
5. Verify claims across sources
6. Generate a cited intelligence report

### Voice Commands for Autonomous Research

| # | Say This | Expected Result |
|---|----------|-----------------|
| 1 | "Research AI agent memory architectures" | ZENITH starts independent research |
| 2 | "Check research status" | Shows progress, tasks completed, evidence found |
| 3 | "Show research activity" | Live feed of what ZENITH is doing |
| 4 | "Get research report" | Final cited intelligence report |
| 5 | "Get research summary" | Executive summary with key findings |
| 6 | "Show knowledge summary" | Evidence count, claims, contradictions |
| 7 | "Stop research" | Pauses the research session |
| 8 | "Search local files for agent" | Searches your codebase |
| 9 | "Analyze codebase at C:\path" | Full codebase analysis |
| 10 | "Research [topic] and determine how ZENITH can improve" | Goal-oriented research |

### Demo Flow

**Start the research:**
```
"Research AI agent memory architectures and determine how ZENITH can improve"
```

**While it runs (30-60 seconds), explain:**
> "ZENITH is now independently searching the web, reading pages, searching local files, extracting knowledge, and building an intelligence report. It's tracking 35 different event types in real-time."

**Check progress:**
```
"Check research status"
"Show research activity"
```

**Get the results:**
```
"Get research report"
"Get research summary"
```

### What the Report Contains

- Executive summary
- Key findings with citations
- Knowledge gaps identified
- Contradictions detected
- Recommendations
- Sources used

**Talking point:** "This is real autonomous intelligence — ZENITH isn't just answering questions, it's thinking independently, researching, verifying information, and producing actionable intelligence reports."

---

## Updated Backup Plan

If voice recognition fails in the noisy classroom:

1. **Option A:** Use the web interface to type commands
2. **Option B:** Have a second laptop/phone ready to demonstrate via screen share
3. **Option C:** Run pre-recorded video clips of each demo
4. **Option D:** Use Presentation Mode — type commands to control slides

**Quick fallback commands (type these in the web interface):**
```
Load my presentation
Start slideshow
Next slide
Create a bar chart of quarterly sales
Show me a pendulum simulation
```

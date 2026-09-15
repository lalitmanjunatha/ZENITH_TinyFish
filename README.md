# ZENITH VADRYK Edition (Mark LIII)

**ZENITH** — An autonomous, voice-first AI companion built on LiveKit Agents, Gemini 2.5 Flash Native Audio, PyQt6 Reactive HUD, and an Action Registry with 76 active tool modules.

> *"A companion who thinks with you, not just executes commands."*

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [The VADRYK Framework](#the-vadryk-framework)
- [Core Algorithm: Adaptive Voice-Action Dispatch](#core-algorithm-adaptive-voice-action-dispatch)
- [Memory Brain System](#memory-brain-system)
- [Personality Engine](#personality-engine)
- [Autonomous Intelligence Engine](#autonomous-intelligence-engine)
- [Simulation Engine (v2)](#simulation-engine-v2)
- [Action Registry & Tool Modules](#action-registry--tool-modules)
- [Algorithms Reference](#algorithms-reference)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Technical Specifications](#technical-specifications)
- [File Structure](#file-structure)

---

## Overview

ZENITH is a **voice-first AI desktop assistant** running on Windows, created by Lalit Manjunatha. Built with a dual entrypoint architecture (PyQt6 Reactive HUD UI + LiveKit Realtime Voice Agent), ZENITH operates as an autonomous desktop companion that remembers user preferences, tracks mood trends over time, speaks fluent Hinglish, and executes complex system actions via auto-discovered tools.

### Key Differentiators

| Feature | ZENITH | Traditional Assistants |
|---------|--------|----------------------|
| **Voice Model** | Gemini 2.5 Flash Native Audio (Real-time bidirectional) | Text-to-speech overlay |
| **Interface** | PyQt6 Reactive HUD UI (Mark LIII) + System Tray + Sound | Static chat window / web UI |
| **Personality** | Living personality with wit, sarcasm, and opinions | Flat, corporate tone |
| **Memory** | Persistent profiling + mood tracking (`MemoryBrain`) | Session-only context |
| **Language** | Hinglish (Hindi + English natural mix) | English-only |
| **Tool Count** | 76 active Action Modules (296+ functions) | 10-20 basic skills |
| **Autonomy** | Autonomous Intelligence Engine (self-directed web/local research) | Reactive only |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      ZENITH VADRYK Edition (Mark LIII)                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────────┐  │
│  │   PyQt6 HUD GUI    │  │   LiveKit Agent    │  │   Action Loader  │  │
│  │   (zenith_gui.py / │  │   (agent.py /      │  │   (76 modules in │  │
│  │    ui.py)          │  │    Aoede Voice)    │  │    Tools/)       │  │
│  └─────────┬──────────┘  └─────────┬──────────┘  └────────┬─────────┘  │
│            │                       │                      │             │
│  ┌─────────▼───────────────────────▼──────────────────────▼──────────┐ │
│  │                     Unified Execution Layer                       │ │
│  │  - Real-time bidirectional Gemini native audio streaming          │ │
│  │  - Dynamic Action Registry (76 active modules auto-discovered)    │ │
│  │  - State management (idle → listening → thinking → speaking)      │ │
│  └─────────────────────────────┬────────────────────────────────────┘ │
│                                │                                      │
│  ┌─────────────────────────────▼────────────────────────────────────┐ │
│  │                    Memory Brain System                            │ │
│  │  ┌──────────────┐    ┌──────────────┐    ┌─────────────────────┐ │ │
│  │  │ User Profile │    │ Mood Tracker │    │  Response Adapter   │ │ │
│  │  │  Extractor   │    │  (5 states)  │    │  & Greeting Engine  │ │ │
│  │  └──────────────┘    └──────────────┘    └─────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                 Autonomous Intelligence Engine                   │ │
│  │  Director → Planner → Web/Local Engine → Knowledge               │ │
│  │  → Cited Report Generator (`autonomous_research` tool)            │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                 Simulation Engine (v2)                           │ │
│  │  9 Domains · 44+ Simulations (`simulation_engine` tool)          │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Voice Input / UI Input → LiveKit Agent / PyQt6 Event Loop → Gemini Realtime Model
      ↓                                                          ↓
VAD (Silero) detects speech                  Gemini processes + decides:
      ↓                                      1. Direct voice response
User turn completed                          2. Tool call(s)
      ↓                                      3. Hybrid response
Agent generates reply                                    ↓
      ↓                                      Action Registry Dispatcher
Audio response streamed back                             ↓
      ↓                                      Tool execution (sync/async)
Speaker output / HUD update                              ↓
                                             Combined into final response
                                                         ↓
                                             Audio streamed back to user
```

---

## The VADRYK Framework

ZENITH's capabilities are categorized under the **VADRYK** mnemonic:

| Letter | Sanskrit | Category | Domain Scope | Active Tools |
|--------|----------|----------|--------------|--------------|
| **V** | Veda | Knowledge | Web search, data analysis, deep system info, weather, news | 8 |
| **A** | Artha | Logic & System | System power, multi-tasking, window management, app launching, processes | 12 |
| **D** | Dhwani | Sound & Vision | Volume, brightness, Spotify, camera analysis, screen reading, webcam overlay | 10 |
| **R** | Rachna | Creation | AI image generation, code generation, Excel suite, PDF converters, presentation creator | 18 |
| **Y** | Yukt | Connectivity | WhatsApp, email, Discord, smart clipboard, cross-app workflows | 12 |
| **K** | Kriya | Action | Keyboard automation, desktop control, OCR text clicking, virus scan | 15 |
| **I** | Intelligence | Research | Autonomous web & local research, codebase analysis, knowledge graphs | 16 |

---

## Core Algorithm: Adaptive Voice-Action Dispatch

The core execution engine uses **Adaptive Voice-Action Dispatch (AVAD)** to route natural speech and UI interactions into validated tool execution calls.

### Algorithm Pseudocode

```
ALGORITHM AdaptiveVoiceActionDispatch
INPUT: raw_audio_stream (PCM 16-bit, 16kHz) OR ui_text_prompt
OUTPUT: audio_response_stream + UI_updates

1. VOICE ACTIVITY DETECTION (Silero VAD)
   ├── Extract audio features (MFCC, spectral)
   ├── Classify: speech / silence / noise
   └── IF silence_duration > min_endpointing_delay (0.4s) → trigger turn_complete

2. SPEECH-TO-TEXT & INTENT MATCHING (Gemini Realtime)
   ├── Stream audio chunks via WebSocket
   ├── LLM evaluates prompt against 76 registered Action Declarations
   └── Classify: DIRECT_RESPONSE | TOOL_INVOCATION | HYBRID

3. ACTION REGISTRY DISPATCH
   ├── Look up tool name in ActionRegistry (e.g. "autonomous_research", "desktop_show")
   ├── Validate arguments against parameter schema
   ├── Execute handler via ThreadPoolExecutor / asyncio loop
   └── Return output payload to Gemini

4. RESPONSE GENERATION & MEMORY ADAPTATION
   ├── Format tool results into system instructions
   ├── Inject user profile, mood score, and response guidelines
   └── Stream audio back via Gemini Native Audio (Aoede Voice)
```

---

## Memory Brain System

The Memory Brain (`Tools/memory_brain.py`) manages user profiling and mood adaptation.

```python
# Key exports & handler
TOOL = {
    "name": "memory_brain",
    "description": "Manage AI memory system: store facts, recall information, track user preferences.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "store | recall | get_profile | get_mood | clear"},
            "key": {"type": "STRING"},
            "value": {"type": "STRING"},
            "category": {"type": "STRING"}
        },
        "required": ["action"]
    },
    "handler": "handle_memory_brain"
}
```

- **UserProfileExtractor**: Scans conversation history for names, language mix, habits, and preferences.
- **MoodTracker**: Performs sentiment scoring (-1.0 to +1.0) with negation and intensifier handling.
- **ResponseAdapter**: Injects real-time tone guidelines into system instructions based on mood trends.

---

## Personality Engine

Defined in `prompts.py`, ZENITH's personality parameters include:
- **Sharp & Wit**: Warm, sarcastic when appropriate, non-robotic.
- **Hinglish Native**: Seamless mixing of Hindi and English.
- **Dynamic Confirmations**: Rotated response phrases ("Bas ho gaya!", "All set!", "Boom!").
- **Mood Sensitivity**: Adapts conciseness and tone when the user is frustrated or tired.

---

## Autonomous Intelligence Engine

The Autonomous Intelligence Engine (`autonomous_intelligence/`) is integrated into the action registry via [`Tools/autonomous_research.py`](file:///C:/Users/Lalit%20Manjunatha/Desktop/ZENITH/Tools/autonomous_research.py).

### Architecture

```
Director ──► Planner ──► Web Engine (DuckDuckGo + Scraping)
   │                       │
   ├──► Knowledge Engine ◄─┘
   │       (Verification, Contradictions, Claim Graphs)
   │
   └──► Report Generator ──► Cited Markdown Report
```

### Action Controls (`autonomous_research`)
- `start` (with `objective`): Spawns self-directed research thread.
- `status` / `activity`: Monitors active phase, completed tasks, and open tabs.
- `report` / `report_summary`: Generates cited intelligence summaries.
- `search_local` / `analyze_codebase`: Scans local files and codebase structure.

---

## Simulation Engine (v2)

The modular simulation platform (`Tools/simulation/`) features **9 domains** and **44+ simulation types**:
- **Physics**: Pendulum, Projectile, Spring-Mass, Standing Wave.
- **Mathematics**: Function Graphs, Derivatives, Integrals, Fractals (Mandelbrot).
- **AI/ML**: Neural Networks, Gradient Descent, K-Means Clustering.
- **Electronics**: RC Circuits, Rectifiers, Digital Logic Gates.
- **Biology**: SIR Epidemic Models, Lotka-Volterra Predator-Prey.
- **Robotics**: PID Controllers, Robot Arm Kinematics, A* Pathfinding.
- **Computer Science**: Sorting Visualizations, CPU Scheduling, BST Operations.
- **3D Visualization**: Surface Plots, Vector Fields.
- **Signal Processing**: Fourier Transforms, Filter Design.

---

## Action Registry & Tool Modules

ZENITH automatically discovers and validates all `*.py` files in `Tools/` containing a `TOOL` definition. Currently, **76 active actions** are registered:

| Domain | Key Action Modules |
|--------|-------------------|
| **System & Desktop** | `desktop_show`, `manage_windows`, `open_app`, `press_key`, `scroll_content`, `system_power_action`, `system_security_tools`, `scan_system_for_viruses`, `terminal_exec` |
| **Research & AI** | `autonomous_research`, `code_handler`, `code_generator`, `code_helper`, `dev_agent`, `image_analysis`, `camera_analysis`, `read_screen_text` |
| **Media & Audio** | `spotify`, `webcam_overlay`, `youtube_video`, `time_volume_brightness`, `screen_processor` |
| **Communication** | `send_whatsapp_message`, `send_media_whatsapp`, `email_tool`, `communication_tools` |
| **Document & Data** | `excel_data_entry`, `word_to_pdf`, `pdf_reader`, `data_processor`, `database_tools`, `file_controller`, `file_processor`, `file_searching` |
| **Productivity & Utilities** | `calendar_tools`, `reminder`, `schedule_task`, `study_tools`, `mindmap`, `qr_generator`, `iot_blynk_tools`, `api_tester`, `git_integration` |

---

## Setup & Installation

### Prerequisites
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.10+
- **Hardware**: Working microphone and speakers

### Installation

```bash
# Clone the repository
git clone https://github.com/lalitmanjunatha/zenith.git
cd ZENITH

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup (`.env`)

```env
# === LiveKit Cloud ===
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# === Google Gemini API ===
GOOGLE_API_KEY=your_google_api_key

# === User Defaults ===
USER_NAME=Lalit
LAN=Hindi
```

### Launching ZENITH

```bash
# Launch PyQt6 HUD GUI (Default)
python agent.py

# Launch CLI / LiveKit Worker Mode
python agent.py dev
```

---

## Technical Specifications

| Parameter | Specification |
|-----------|---------------|
| **Core Voice Model** | Gemini 2.5 Flash Native Audio Preview (`Aoede` voice) |
| **VAD Engine** | Silero VAD (Noise Cancellation via BVC) |
| **UI Framework** | PyQt6 Reactive HUD (Mark LIII UI) |
| **Action Registry** | 76 Active Action Modules (Dynamic auto-discovery) |
| **Latency** | ~1.0s - 2.5s end-to-end voice roundtrip |
| **Python Version** | 3.12 (compatible with 3.10+) |

---

## File Structure

```
ZENITH/
├── agent.py                      # Main entrypoint & LiveKit worker launcher
├── zenith_gui.py                 # PyQt6 main GUI window & event wiring
├── ui.py                         # Reactive HUD components & styling
├── prompts.py                    # Personality & system instructions
├── requirements.txt              # Python package dependencies
├── .env                          # Environment variables & API keys
│
├── Tools/                        # 76 Action Modules
│   ├── autonomous_research.py    # Autonomous Intelligence Engine bridge
│   ├── memory_brain.py           # User profiling & mood tracking
│   ├── desktop_control.py        # Desktop show & window automation
│   ├── code_handler.py           # Code debugging & Groq fixer
│   ├── presentation_controller.py# PPTX automation
│   ├── proactive.py              # Background trigger engine
│   ├── simulation_engine.py      # Physics/Math simulation bridge
│   ├── webcam_overlay.py         # Floating webcam window
│   ├── simulation/               # 9-domain simulation engine sub-package
│   └── [68 other tool modules]
│
├── autonomous_intelligence/       # Self-directed research package
│   ├── director.py               # Research director & session thread
│   ├── planner.py                # Research task planner
│   ├── web_engine.py             # DuckDuckGo search & page reader
│   ├── local_engine.py           # Local file indexing & AST parser
│   └── knowledge.py              # Claim verification & evidence graphs
│
├── core/                         # System core loaders
│   ├── action_loader.py          # Dynamic tool discovery & validation
│   ├── plugin_loader.py          # Plugin registry & settings schemas
│   ├── wake_word.py              # Wake-word detection engine
│   └── audio_devices.py          # Input/output audio device enumeration
│
└── data/                         # Persistent memory storage
    ├── user_profile.json         # Extracted user profile & preferences
    ├── mood_log.json             # Mood history
    └── memory_summary.json       # Fact memory storage
```

---

## License & Credits

Created by **Lalit Manjunatha**. All rights reserved.

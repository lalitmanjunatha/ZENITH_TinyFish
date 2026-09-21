# ZENITH VADRYK Edition 

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
- [MATRIS Mathematical Intelligence](#matris-mathematical-intelligence)
- [Algorithms Reference](#algorithms-reference)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Technical Specifications](#technical-specifications)
- [File Structure](#file-structure)
- [License & Credits](#license--credits)

---

## Overview

ZENITH is a **voice-first AI desktop assistant** running on Windows, created by Lalit Manjunatha. Built with a dual entrypoint architecture (PyQt6 Reactive HUD UI + LiveKit Realtime Voice Agent), ZENITH operates as an autonomous desktop companion that remembers user preferences, tracks mood trends over time, speaks fluent Hinglish, and executes complex system actions via auto-discovered tools.

### Key Differentiators

| Feature | ZENITH | Traditional Assistants |
|---------|--------|----------------------|
| **Voice Model** | Gemini 2.5 Flash Native Audio (Real-time bidirectional) | Text-to-speech overlay |
| **Interface** | PyQt6 Reactive HUD UI + MATRIS Canvas + System Tray + Sound | Static chat window / web UI |
| **Personality** | Living personality with wit, sarcasm, and opinions | Flat, corporate tone |
| **Memory** | Persistent profiling + mood tracking (`MemoryBrain`) | Session-only context |
| **Language** | Hinglish (Hindi + English natural mix) | English-only |
| **Tool Count** | 76 active Action Modules (296+ functions) | 10-20 basic skills |
| **Mathematics** | MATRIS: Interactive canvas, voice feedback, step-by-step explanations | Basic calculator |
| **Autonomy** | Autonomous Intelligence Engine (self-directed web/local research) | Reactive only |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      ZENITH VADRYK Edition                   │
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
| **MATRIS (Mathematics)** | `mathematical_reasoner`, `open_canvas`, `close_canvas` |

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
| **UI Framework** | PyQt6 Reactive HUD |
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
├── Tools/                        # 77+ Action Modules
│   ├── mathematical_reasoner.py  # MATRIS Mathematical Intelligence bridge
│   ├── autonomous_research.py    # Autonomous Intelligence Engine bridge
│   ├── memory_brain.py           # User profiling & mood tracking
│   ├── desktop_control.py        # Desktop show & window automation
│   ├── code_handler.py           # Code debugging & Groq fixer
│   ├── presentation_controller.py# PPTX automation
│   ├── proactive.py              # Background trigger engine
│   ├── simulation_engine.py      # Physics/Math simulation bridge
│   ├── webcam_overlay.py         # Floating webcam window
│   ├── mathematics/              # MATRIS core: solvers, parsers, engines
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
├── mathematics_ui/               # MATRIS PyQt6 Interactive Canvas
│   ├── __init__.py
│   ├── math_canvas.py            # Mathematical state visualization widget
│   ├── drawing_pad.py            # Freehand drawing canvas with OCR
│   └── matrix_input.py           # NxN matrix grid input widget
│
└── data/                         # Persistent memory storage
    ├── user_profile.json         # Extracted user profile & preferences
    ├── mood_log.json             # Mood history
    ├── memory_summary.json       # Fact memory storage
    └── mathematics/              # MATRIS data storage
```

---

## MATRIS Mathematical Intelligence

**MATRIS** (Mathematical Reasoning & Intelligent Solving) is ZENITH's mathematical intelligence subsystem, integrated as an action module in the Action Registry. It features a full PyQt6 interactive canvas with text input, freehand drawing with OCR, NxN matrix grid input, step-by-step explanations, and voice feedback.

### Architecture

```
User Voice/Text Input / Canvas Interaction
        |
        v
  mathematical_reasoner (Action Registry Bridge)
        |
        +---> ProblemParser       (Extract numbers, units, variables, equations)
        +---> ProblemClassifier   (Classify domain, subdomains, model type)
        +---> SolverRouter        (Dispatch to appropriate solver engine)
        |         |
        |         +---> SymPy           (Symbolic algebra, equation solving, calculus)
        |         +---> SciPy linprog   (Linear programming / Optimization)
        |         +---> SciPy odeint    (ODE cooling, SIR epidemic models)
        |         +---> NumPy           (Linear algebra, matrix operations)
        |         +---> Gradient Descent (ML loss optimization)
        |
        +---> ValidationEngine    (Verify solution correctness)
        +---> ErrorDetector       (Diagnose user solution errors)
        +---> ExplanationEngine   (Multi-level explanations)
        +---> SensitivityEngine   (What-if & sensitivity analysis)
        |
        v
  MathematicalState (Unified data model)
        |
        v
  MathCanvas (PyQt6 Interactive Display)
        |
        +---> Text Input    (Type equations, e.g. "Solve 2x + 5 = 17")
        +---> Drawing Pad   (Freehand handwriting → OCR → text extraction)
        +---> Matrix Input  (NxN grid: 1x1 to 8x8, presets for 3x3, 4x4, 3x1, 1x3)
        +---> Step-by-step  (Explain button: progressive step display + voice)
        +---> Voice Output   (AI speaks the final answer after solving)
```

### Canvas Input Modes

| Mode | Description |
|------|-------------|
| **Text** | Type any math problem (e.g. `2x + 5 = 17`, `integrate x^2 dx`) |
| **Draw** | Freehand handwriting on a canvas — captured via pytesseract OCR |
| **Matrix** | Clickable NxN grid — enter matrix elements cell by cell |

### Supported Mathematical Domains

| Domain | Model Type | Solver Backend | Example Problems |
|--------|-----------|---------------|-----------------|
| **Calculus** | Integral / Derivative | SymPy `integrate`, `diff` | `integrate x^2 dx`, `differentiate sin(x)*e^x` |
| **Algebra** | Equation Solving | SymPy `solve` | `2x + 5 = 17`, `x^2 - 4 = 0` |
| **Systems** | System of Equations | SymPy `solve` (multi-var) | `2x + 3y = 12 and x - y = 1` |
| **Linear Algebra** | Matrix Operations | NumPy `linalg` | Determinant, inverse, eigenvalues, rank |
| **Optimization** | Linear Programming | SciPy `linprog` | Maximize profit with resource constraints |
| **Differential Equations** | ODE System | SciPy `odeint` | Newton's Cooling, SIR Epidemic Model |
| **Kinematics** | Physics Equations | SymPy symbolic | `v = u + at`, projectile motion |
| **AI/ML** | Data-Driven | Gradient Descent | Linear regression, loss minimization |

### Actions

| Action | Description |
|--------|-------------|
| `solve_problem` | Parse, formulate, solve, and validate a mathematical problem |
| `model_problem` | Extract and display the mathematical model without solving |
| `classify_problem` | Identify domain, subdomains, and model type |
| `explain_step` | Generate step-by-step explanation displayed progressively on canvas + voice |
| `verify_solution` | Validate solution against constraints and consistency |
| `diagnose_solution` | Detect and explain errors in user-provided solutions |
| `what_if` | Re-solve with a modified parameter value |
| `sensitivity_analysis` | Analyze how changes affect the solution |

### Canvas Tools (AI-callable)

| Tool | Description |
|------|-------------|
| `open_canvas` | Opens MATRIS canvas (modes: `text`, `draw`, `matrix`, or default) |
| `close_canvas` | Closes MATRIS canvas and returns to normal HUD |
| `mathematical_reasoner` | Solve, explain, verify, diagnose, classify math problems |

### Features

- **Voice Feedback**: AI speaks the final answer after solving
- **Step-by-Step Explanation**: Click "Explain" to see each derivation step appear progressively with voice narration
- **Thread-Safe Rendering**: All canvas updates marshaled via Qt signals from solver threads
- **Direct Solve Path**: Canvas solves synchronously for instant results, then notifies the AI session
- **Exit MATRIS**: Click "EXIT MATRIS" button or ask the AI to close the canvas

### File Structure

```
Tools/
  mathematics/
    __init__.py              # Package exports
    mathematical_state.py    # MathematicalState dataclass
    problem_parser.py        # ProblemParser & ProblemClassifier
    solver_router.py         # SolverRouter (SymPy, SciPy, NumPy)
    model_adapter.py         # MathematicalModelAdapter interface
    engines.py               # Validation, Error, Explanation, Sensitivity engines
  mathematical_reasoner.py   # Action Registry bridge (auto-discovered)

mathematics_ui/
  __init__.py                # UI package exports
  math_canvas.py             # PyQt6 interactive Mathematical Canvas (3-mode input)
  drawing_pad.py             # Freehand drawing canvas with OCR
  matrix_input.py            # NxN matrix grid input widget

data/
  mathematics/               # MATRIS data storage
```

---

## License & Credits

Created by **Lalit Manjunatha**. All rights reserved.

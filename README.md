# ZENITH VADRYK Edition

**ZENITH** — An autonomous, voice-first AI companion built on LiveKit Agents, Gemini 2.5 Flash Native Audio, PyQt6 Reactive HUD, TinyFish Search, and an Action Registry with 91+ active tool modules.

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

ZENITH is a **voice-first AI desktop assistant** running on Windows, created by Lalit Manjunatha. Built with a dual entrypoint architecture (PyQt6 Reactive HUD UI + LiveKit Realtime Voice Agent), ZENITH operates as an autonomous desktop companion that remembers user preferences, tracks mood trends over time, speaks fluent Hinglish, and executes complex system actions via an auto-discovered action registry of 91+ tools.

### Key Differentiators

| Feature | ZENITH | Traditional Assistants |
|---------|--------|----------------------|
| **Voice Model** | Gemini 2.5 Flash Native Audio (Real-time bidirectional) | Text-to-speech overlay |
| **Interface** | PyQt6 Reactive HUD UI + MATRIS Canvas + System Tray + Sound | Static chat window / web UI |
| **Personality** | Living personality with wit, sarcasm, and opinions | Flat, corporate tone |
| **Memory** | Persistent profiling + mood tracking (`MemoryBrain`) | Session-only context |
| **Language** | Hinglish (Hindi + English natural mix) | English-only |
| **Provider Identity** | TinyFish (for web-intelligence queries) | N/A |
| **Tool Count** | 91+ active Action Modules (296+ functions) | 10-20 basic skills |
| **Mathematics** | MATRIS: Interactive canvas, voice feedback, step-by-step explanations | Basic calculator |
| **Autonomy** | Autonomous Intelligence Engine (self-directed web/local research with TinyFish) | Reactive only |

---

## Architecture

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                      ZENITH VADRYK Edition                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────────┐  │
│  │   PyQt6 HUD GUI    │  │   LiveKit Agent    │  │   Action Loader  │  │
│  │   (zenith_gui.py / │  │   (agent.py /      │  │   (91 modules in │  │
│  │    ui.py)          │  │    Aoede Voice)    │  │    Tools/)       │  │
│  └─────────┬──────────┘  └─────────┬──────────┘  └────────┬─────────┘  │
│            │                       │                      │             │
│  ┌─────────▼───────────────────────▼──────────────────────▼──────────┐ │
│  │                     Unified Execution Layer                       │ │
│  │  - Real-time bidirectional Gemini native audio streaming          │ │
│  │  - Dynamic Action Registry (91+ active modules auto-discovered)    │ │
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
│  │  9 Domains · 44+ Simulation Types (`simulation_engine` tool)      │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘

### Data Flow

```text
Voice Input / UI Input → LiveKit Agent / PyQt6 Event Loop → Gemini Realtime Model
      ↓                                                          ↓
VAD (Silero VAD) detects speech                  Gemini processes + decides:
      ↓                                      1. Direct voice response
User turn completed                          2. Tool call(s)
      �                                      3. Hybrid response
Agent generates reply                                    ↓
      �                                      Action Registry Dispatcher
Audio response streamed back                             ↓
      �                                      Tool execution (sync/async)
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
| **V** | Veda | Knowledge | Web search, data analysis, deep system info, weather, news, TinyFish Search | 8 |
| **A** | Artha | Logic & System | System power, multi-tasking, window management, app launching, processes | 12 |
| **D** | Dhwani | Sound & Vision | Volume, brightness, Spotify, camera analysis, screen reading, webcam overlay | 10 |
| **R** | Rachna | Creation | AI image generation, code generation, Excel suite, PDF converters, presentation creator | 18 |
| **Y** | Yukt | Connectivity | WhatsApp, email, Discord, smart clipboard, cross-app workflows | 12 |
| **K** | Kriya | Action | Keyboard automation, desktop control, OCR text clicking, virus scan | 15 |
| **I** | Intelligence | Research | Autonomous web & local research, codebase analysis, knowledge graphs | 16 |

**Total: 91+ active Action Modules**

---

ZENITH integrates **TinyFish Search API** as the primary web-intelligence provider, replacing traditional search engines with a privacy-first, free-tier capable solution.

### TinyFish Search API
- **Endpoint**: `GET https://api.search.tinyfish.ai?query=<query>`
- **Header**: `X-API-Key` from `TINYFISH_API_KEY` env var
- **Free Tier**: 12,000 requests/day (then wallet-funded)
- **Public Functions**: `search_web(query)`, `search_news(query)` preserved in `Tools/web_search.py`

### Fallback Chain
```
TinyFish Search API ────→ Web/search results (primary)
          │
          ├─→ DuckDuckGo (text fallback)
          └─→ DuckDuckGo News (news fallback)
                │
                └─→ "No results" message
```

### Capability Awareness
The system includes routing guidelines in `prompts.py`:
- **TinyFish for**: Web-intelligence, prices, news, research queries
- **Gemini for**: General conversation, voice, reasoning, audio
- **Routing**: Queries are directed appropriately based on intent

### AI Provider Identity
When asked "From which AI provider are you?" or similar identity questions, ZENITH responds with just: **"TinyFish"**

This ensures clear provider attribution while maintaining the hybrid Gemini + TinyFish architecture.

### Test Results
```
9/9 web_search tests PASSED
```

The core execution engine uses **Adaptive Voice-Action Dispatch (AVAD)** to route natural speech and UI interactions into validated tool execution calls.

### Algorithm Pseudocode

```text
ALGORITHM AdaptiveVoiceActionDispatch
INPUT: raw_audio_stream (PCM 16-bit, 16kHz) OR ui_text_prompt
OUTPUT: audio_response_stream + UI_updates

1. VOICE ACTIVITY DETECTION (Silero VAD)
   ├── Extract audio features (MFCC, spectral)
   ├── Classify: speech / silence / noise
   └── IF silence_duration > min_endpointing_delay (0.4s) → trigger turn_complete

2. SPEECH-TO-TEXT & INTENT MATCHING (Gemini Realtime)
   ├── Stream audio chunks via WebSocket
   ├── LLM evaluates prompt against 91+ registered Action Declarations
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

### Key Exports & Handler

```json
{
    "name": "memory_brain",
    "description": "Manage the AI's memory system: store facts, recall information, track user preferences, and manage conversation context.",
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

### Sub-Algorithms

- **UserProfileExtractor**: Scans conversation history for names, language mix, habits, and preferences using pattern-based heuristics.
- **MoodTracker**: Performs sentiment scoring (-1.0 to +1.0) with negation and intensifier handling, tracking mood trends over 100+ entries.
- **ResponseAdapter**: Injects real-time tone guidelines into system instructions based on mood trends, language preference, and communication style.

### Memory Capabilities

- **User Profile**: Name, language preference (hindi/english/mixed), communication style (technical/casual/brief/detailed), topics, habits, preferences
- **Mood Tracking**: 5 mood states (stressed, excited, frustrated, tired, happy) with trend detection and shift counting
- **Contextual Recall**: Recent interactions, frequent topics, user habits (peak hours, active days, session pattern)
- **Response Style**: Dynamic guidelines matching user's message length, mood, style, and language preference

### Actions

| Action | Description |
|--------|-------------|
| `store` | Store a fact or preference in memory |
| `recall` | Recall a stored fact or list all stored memories |
| `get_profile` | Get full user profile context for AI system prompt |
| `get_mood` | Get current mood and trend information |
| `clear` | Clear all stored memories |

---

## Personality Engine

Defined in `prompts.py`, ZENITH's personality parameters include:

- **Sharp & Wit**: Warm, sarcastic when appropriate, non-robotic.
- **Hinglish Native**: Seamless mixing of Hindi and English.
- **Dynamic Confirmations**: Rotated response phrases ("Bas ho gaya!", "All set!", "Boom!").
- **Mood Sensitivity**: Adapts conciseness and tone when the user is frustrated or tired.
- **Language Mirroring**: If user speaks Hinglish, ZENITH responds in Hinglish.

### Personality Configuration (`prompts.py`)

- **Tone Guidelines**: Injects mood-aware, language-aware, style-aware instructions into every LLM call.
- **Greeting Generator**: Time-aware, day-aware, gap-aware, mood-aware greetings.
- **Response Adapter**: Adapts response length, tone, and language based on user's current state.

---

## Autonomous Intelligence Engine

The Autonomous Intelligence Engine (`autonomous_intelligence/`) is integrated into the action registry via `Tools/autonomous_research.py`.

### Architecture

```text
Director ──► Planner ──► Web Engine (DuckDuckGo + Scraping)
    │                       │
    ├──► Knowledge Engine ◄─┘
    │       (Verification, Contradictions, Claim Graphs)
    │
    └──► Report Generator ──► Cited Markdown Report
```

### Action Controls (`autonomous_research`)

| Action | Description |
|--------|-------------|
| `start` (with `objective`) | Spawns self-directed research thread |
| `status` / `activity` | Monitors active phase, completed tasks, and open tabs |
| `report` / `report_summary` | Generates cited intelligence summaries |
| `search_local` / `analyze_codebase` | Scans local files and codebase structure |
| `knowledge` | Gets knowledge summary with evidence, claims, contradictions |
| `web_search` | Performs web search and returns results |
| `read_url` | Reads and extracts content from a URL |
| `save` | Saves current research session |
| `config` | Shows research configuration settings |

### Research Domains

- Web research (DuckDuckGo search, page reading)
- Local file indexing and reading
- Codebase analysis (AST parsing, structure extraction)
- Claim verification and contradiction detection
- Evidence graph construction
- Cited markdown report generation

---

## Simulation Engine (v2)

The modular simulation platform (`Tools/simulation/`) features **9 domains** and **44+ simulation types**:

### Physics

| Simulation | Description |
|------------|-------------|
| `pendulum` | Simple pendulum motion |
| `projectile` | Projectile trajectory |
| `spring` | Damped spring-mass system |
| `wave` | Standing wave simulation |

### Mathematics

| Simulation | Description |
|------------|-------------|
| `function_graph` | Graph mathematical functions |
| `derivative` | Compute derivatives |
| `integral` | Compute integrals |
| `fractal` | Generate fractals (Mandelbrot) |

### AI/ML

| Simulation | Description |
|------------|-------------|
| `neural_network` | Neural network visualization |
| `gradient_descent` | Loss minimization visualization |
| `kmeans` | K-Means clustering visualization |

### Electronics

| Simulation | Description |
|------------|-------------|
| `rc_circuit` | RC circuit analysis |
| `rectifier` | Rectifier simulation |
| `logic_gate` | Digital logic gate simulation |

### Biology

| Simulation | Description |
|------------|-------------|
| `sir_model` | SIR epidemic model |
| `predator_prey` | Predator-prey dynamics |

### Robotics

| Simulation | Description |
|------------|-------------|
| `pid_controller` | PID control system |
| `robot_arm` | Robot arm kinematics |
| `astar` | A* pathfinding |

### Computer Science

| Simulation | Description |
|------------|-------------|
| `sorting` | Sorting algorithm visualization |
| `cpu_scheduling` | CPU scheduling simulation |
| `bst` | Binary Search Tree operations |
| `linked_list` | Linked list operations |

### 3D Visualization

| Simulation | Description |
|------------|-------------|
| `surface_3d` | 3D surface plots |
| `vector_field_3d` | Vector field visualization |
| `fourier` | Fourier transform visualization |

### Signal Processing

| Simulation | Description |
|------------|-------------|
| `convolution` | Convolution operation |
| `filter_design` | Filter design visualization |
| `sampling` | Sampling theorem demonstration |

### Chart Creation

| Chart Type | Description |
|------------|-------------|
| `bar_chart` | Bar chart (labels, values) |
| `pie_chart` | Pie chart (labels, values) |
| `line_chart` | Multi-line chart (x_data, y_data, labels) |
| `scatter_plot` | Scatter plot (x_data, y_data) |

### Diagram Creation

| Diagram Type | Description |
|------------|-------------|
| `flowchart` | System architecture (nodes, edges) |
| `network` | Network topology (nodes, connections) |

### Actions

| Action | Description |
|--------|-------------|
| `run_simulation` | Run any simulation by type |
| `create_chart` | Create bar, pie, line, or scatter chart |
| `create_diagram` | Create architecture or network diagram |
| `list_simulation_types` | List all available simulation types |

### Visualization Output

All simulations and charts generate PNG visualizations saved to `~/Downloads/zenith_simulations/` with dark-theme styling matching the ZENITH HUD aesthetic.

---

## Action Registry & Tool Modules

ZENITH automatically discovers and validates all `*.py` files in `Tools/` containing a `TOOL` definition. Currently, **91+ active actions** are registered across 21 domains.

### Domain Overview

| Domain | Key Action Modules |
|--------|-------------------|
| **V - Veda (Knowledge)** | `search_web`, `get_time_info`, `get_weather`, `get_system_info_deep`, `get_system_status`, `news_provider`, `web_search`, `time_volume_brightness` |
| **A - Artha (Logic & System)** | `system_power_action`, `manage_windows`, `list_windows`, `open_app`, `desktop_control`, `scroll_content`, `press_key`, `scan_system_for_viruses`, `terminal_exec`, `code_handler`, `code_generator`, `run_file_in_vscode`, `git_integration` |
| **D - Dhwani (Sound & Vision)** | `spotify`, `control_system_volume`, `control_screen_brightness`, `webcam_overlay`, `screen_short`, `camera_analysis`, `read_screen_text`, `time_volume_brightness`, `get_time_info`, `get_weather` |
| **R - Rachna (Creation)** | `generate_ai_image`, `code_generator`, `code_generator`, `generate_and_type_code`, `run_file_in_vscode`, `word_to_pdf`, `image_to_pdf`, `excel_to_pdf`, `ppt_to_pdf`, `convert_image_format`, `test_converters`, `mathematical_reasoner`, `open_canvas`, `close_canvas`, `create_presentation`, `add_slide_with_content`, `add_slide_with_title`, `get_slide_notes`, `presentation_status` |
| **Y - Yukt (Connectivity)** | `send_whatsapp_message`, `send_media_whatsapp`, `email_tool`, `communication_tools`, `discord_send`, `meeting_link`, `auto_reply_email`, `bulk_email`, `email_reminder`, `call_log`, `fabric_create_pairing`, `fabric_status`, `fabric_request_action`, `fabric_pending_call_reports`, `fabric_sync`, `blynk_write`, `blynk_read`, `blynk_device_status`, `blynk_notify`, `blynk_email_trigger` |
| **K - Kriya (Action)** | `desktop_show`, `manage_windows`, `open_app`, `press_key`, `scroll_content`, `system_power_action`, `system_security_tools`, `scan_system_for_viruses`, `terminal_exec`, `click_on_text`, `screen_analyzer`, `screen_processor`, `file_searching`, `file_processor`, `file_controller`, `create_folder`, `qr_generator`, `mindmap`, `schedule_task`, `reminder` |
| **I - Intelligence (Research)** | `autonomous_research`, `code_handler`, `code_generator`, `code_helper`, `dev_agent`, `image_analysis`, `camera_analysis`, `read_screen_text`, `mathematical_reasoner`, `search_web`, `analysis_screen`, `analyze_local_image`, `universal_file_opener`, `api_tester` |

### Tool Details by Category

#### System & Desktop

| Tool | Description |
|------|-------------|
| `desktop_show` | Shows desktop / hides all windows |
| `manage_windows` | Move, resize, minimize, maximize windows |
| `open_app` | Open any application by name |
| `press_key` | Press keyboard keys (single, combinations, smart clipboard) |
| `scroll_content` | Scroll web pages or documents |
| `system_power_action` | Shutdown, restart, sleep, lock |
| `system_security_tools` | WiFi password, startup apps, disk cleanup, disk usage, screenshot scheduler, app blocker, parental control, firewall rule, encrypted folder, backup files, restore backup, system snapshot |
| `scan_system_for_viruses` | Scan system for viruses |
| `terminal_exec` | Execute command in terminal |
| `click_on_text` | Click on detected text on screen |
| `screen_analyzer` | Analyze screen content |
| `screen_processor` | Process screen content |
| `file_searching` | Universal file opener and search |
| `file_processor` | Process and transform files |
| `file_controller` | File management operations |
| `create_folder` | Create new folders |
| `qr_generator` | Generate QR codes |
| `mindmap` | Create mind maps |
| `schedule_task` | Schedule tasks |
| `reminder` | Set, view, and cancel reminders |

#### Research & AI

| Tool | Description |
|------|-------------|
| `autonomous_research` | Autonomous web & local research with cited reports |
| `code_handler` | Code debugging and error fixing |
| `code_generator` | Generate code from natural language prompts |
| `code_helper` | Code assistance and completion |
| `dev_agent` | Development agent for coding tasks |
| `image_analysis` | Analyze and describe images |
| `camera_analysis` | Real-time camera analysis |
| `read_screen_text` | Read text from screen |
| `mathematical_reasoner` | MATRIS mathematical problem solving |
| `search_web` | Web search functionality |
| `analyze_screen` | Analyze screen content |
| `analyze_local_image` | Analyze local images |

#### Media & Audio

| Tool | Description |
|------|-------------|
| `spotify` | Control Spotify: play, pause, next, previous, play song, liked songs |
| `control_system_volume` | Adjust system volume (0-100) |
| `control_screen_brightness` | Adjust screen brightness (0-100) |
| `get_time_info` | Get current system time |
| `get_weather` | Get weather in Hindi/English |
| `webcam_overlay` | Floating webcam window |
| `screen_short` | Take screen capture |
| `time_volume_brightness` | Comprehensive system controller (time, volume, brightness, weather, status) |
| `youtube_video` | Play YouTube videos |
| `youtube_videos` | Playlist management |

#### Communication

| Tool | Description |
|------|-------------|
| `send_whatsapp_message` | Send WhatsApp messages |
| `send_media_whatsapp` | Send media via WhatsApp |
| `email_tool` | Send, read, search emails |
| `communication_tools` | Discord send, meeting links, auto-reply, bulk email, call logs |
| `fabric_create_pairing` | Fabric device pairing |
| `fabric_status` | Fabric device status |
| `fabric_request_action` | Fabric action requests |
| `fabric_pending_call_reports` | Pending call reports |
| `fabric_sync` | Fabric sync |
| `blynk_write` | Blynk write operations |
| `blynk_read` | Blynk read operations |
| `blynk_device_status` | Blynk device status |
| `blynk_notify` | Blynk notifications |
| `blynk_email_trigger` | Blynk email triggers |

#### Document & Data

| Tool | Description |
|------|-------------|
| `excel_data_entry` | Complete Excel suite: create, save, delete, enter data, move, sort, calculate sum |
| `word_to_pdf` | Convert Word to PDF |
| `image_to_pdf` | Convert images to PDF |
| `excel_to_pdf` | Convert Excel to PDF |
| `ppt_to_pdf` | Convert PowerPoint to PDF |
| `convert_image_format` | Convert between image formats |
| `test_converters` | Test converter availability |
| `data_processor` | CSV/JSON analysis, filtering, sorting, statistics |
| `database_tools` | SQLite: query, create tables, insert, select, list tables, export CSV |
| `file_controller` | File management operations |
| `universal_file_opener` | Open and categorize any file type |

#### Productivity & Utilities

| Tool | Description |
|------|-------------|
| `calendar_tools` | Add events, list tasks, complete tasks, delete events |
| `reminder` | Set, view, and cancel reminders |
| `schedule_task` | Schedule tasks |
| `study_tools` | Flashcards, pomodoro, study planner, GPA calculator, unit convert, scientific calc, number convert, roman convert, vocabulary, stopwatch, todo, expense |
| `mindmap` | Create mind maps |
| `qr_generator` | Generate QR codes |
| `iot_blynk_tools` | Blynk IoT operations |
| `api_tester` | Test API endpoints |
| `git_integration` | Git: status, log, commit, push, pull, branch, diff, clone |
| `calendar_tools` | Calendar and task management |
| `counter_increment` | Counter operations |
| `coin_flip` | Coin flip |
| `dice_roll` | Dice roll |
| `random_number` | Random number generation |
| `breathing_exercise` | breathing exercises |
| `stretch_reminder` | Stretch reminders |
| `pro_tip` | Productivity tips |

#### MATRIS (Mathematical Reasoning)

| Tool | Description |
|------|-------------|
| `mathematical_reasoner` | Solve, explain, verify, diagnose, classify math problems |
| `open_canvas` | Opens MATRIS canvas |
| `close_canvas` | Closes MATRIS canvas |

### Tool Discovery

The Action Registry dynamically loads all tools at startup from `Tools/*.py` files that contain a `TOOL` dict definition with `name`, `description`, `parameters`, and `handler` fields. The registry:

1. Scans all Python files in `Tools/`
2. Imports each file and extracts the `TOOL` definition
3. Validates the schema (name, description, parameters with required fields)
4. Registers the handler function
5. Makes tools available to the Gemini LiveKit agent

Total: **91+ active Action Modules** across all domains.

---

## MATRIS Mathematical Intelligence

**MATRIS** (Mathematical Reasoning & Intelligent Solving) is ZENITH's mathematical intelligence subsystem, integrated as an action module in the Action Registry. It features a full PyQt6 interactive canvas with text input, freehand drawing with OCR, NxN matrix grid input, step-by-step explanations, and voice feedback.

### Architecture

```text
User Voice/Text Input / Canvas Interaction
        |
        v
  mathematical_reasoner (Action Registry Bridge)
        |
        +---> ProblemParser       (Extract numbers, units, variables, equations)
        +---> ProblemClassifier   (Classify domain, subdomains, model type)
        +---> SolverRouter        (Dispatch to appropriate solver engine)
                |
                +---> SymPy           (Symbolic algebra, equation solving, calculus)
                +---> SciPy linprog   (Linear programming / Optimization)
                +---> SciPy odeint    (ODE cooling, SIR epidemic models)
                +---> NumPy           (Linear algebra, matrix operations)
                +---> Gradient Descent (ML loss optimization)
        |
        v
  ValidationEngine    (Verify solution correctness)
        |
        v
  ErrorDetector       (Diagnose user solution errors)
        |
        v
  ExplanationEngine   (Multi-level explanations)
        |
        v
  SensitivityEngine   (What-if & sensitivity analysis)
        |
        v
  MathematicalState (Unified data model)
        |
        v
  MathCanvas (PyQt6 Interactive Display)
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

### File Structure: Mathematics

```text
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

## Autonomous Intelligence Engine

The Autonomous Intelligence Engine (`autonomous_intelligence/`) enables ZENITH to perform self-directed research without constant user prompting.

### Director → Planner → Web/Local Engine → Knowledge → Cited Report

### Research Actions

| Action | Parameters | Description |
|--------|------------|-------------|
| `start` | `objective` (required) | Spawns self-directed research thread with given objective |
| `stop` | none | Stop the active research session |
| `pause` | none | Pause the active research session |
| `resume` | none | Resume a paused research session |
| `status` | none | Get current research status (phase, tasks, evidence, claims) |
| `activity` | none | Get live research activity (recent events, open tabs) |
| `report` | none | Get full cited report |
| `report_summary` | none | Get executive summary with key findings |
| `knowledge` | none | Get knowledge summary (evidence, claims, contradictions, gaps) |
| `search_local` | `query` (required) | Search local files matching query |
| `read_local` | `path` (required) | Read file or directory contents |
| `analyze_codebase` | `path` (required) | Analyze codebase structure, languages, files |
| `web_search` | `query` (required) | Web search via DuckDuckGo |
| `read_url` | `url` (required) | Read and extract content from URL |
| `save` | none | Save current research session |
| `config` | none | Show research configuration |

### Knowledge Graph

The engine maintains a knowledge graph with:
- Evidence items (sources, quotes, data points)
- Claims (propositions extracted from sources)
- Contradictions (conflicting claims)
- Knowledge gaps (unresolved questions)
- Entity-relationship mappings
- Average confidence scores

### Configuration

```text
Max runtime: configurable minutes
Max search queries: limit per session
Max pages: maximum browser tabs visited
Max tabs: concurrent browser tabs
Max tasks: maximum research tasks
Permission level: public / private
Search provider: DuckDuckGo / Google / etc.
Indexed paths: local directories to index
```

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

## Configuration

### Configuration Files

- **`config/api_keys.json`**: Stores Gemini API key, assistant name, user name, voice settings, device I/O, plugin configs
- **`memory/long_term.json`**: Persistent memory with identity, preferences, projects, relationships, wishes, notes
- **`.env`**: Environment variables for LiveKit and API keys

### Key Configuration Options

| Setting | File | Description |
|---------|------|-------------|
| `gemini_api_key` | `config/api_keys.json` | Google Gemini API key |
| `assistant_name` | `config/api_keys.json` | Assistant name (default: ZENITH) |
| `user_name` | `config/api_keys.json` | User name for addressing |
| `voice_name` | `config/api_keys.json` | Live voice (Charon, Puck, Kore, Fenrir, Aoede) |
| `input_device` | `config/api_keys.json` | Microphone device name |
| `output_device` | `config/api_keys.json` | Speaker device name |
| `plugins_enabled` | `config/api_keys.json` | Plugin enable/disable per plugin |
| `wake_word_enabled` | `config/api_keys.json` | Wake-word gating ("Hey Zenith") |
| `morning_brief_enabled` | `config/api_keys.json` | Morning brief on startup |
| `input_device` | `config/api_keys.json` | Microphone device name |
| `output_device` | `config/api_keys.json` | Speaker device name |

### Memory Management

The memory system uses `memory/long_term.json` with categories:
- `identity`: User identity fields (name, age, birthday, city, job, etc.)
- `preferences`: User preferences (language, habits, etc.)
- `projects`: Active projects and goals
- `relationships`: People in user's life
- `wishes`: User wishes and plans
- `notes`: General notes and facts

Memory is managed via:
- `remember(key, value, category)`: Store a fact
- `forget(key, category)`: Forget a fact
- `search_memory(query)`: Search stored facts
- `all_entries_for_ui()`: List all entries for the memory panel

### Plugin System

Plugins are enabled by default (opt-out model). Each plugin can have its own configuration stored under `plugin_config[<namespace>]`. Plugin settings are managed via:
- `get_plugin_config(namespace)`: Get all values for a namespace
- `get_plugin_setting(namespace, key, default)`: Get a single value
- `save_plugin_config(namespace, values)`: Merge values into namespace
- `save_plugin_enabled(plugin_name, enabled)`: Enable/disable a plugin

---

## Technical Specifications

| Parameter | Specification |
|-----------|---------------|
| **Core Voice Model** | Gemini 2.5 Flash Native Audio Preview (`Aoede` voice) |
| **Search Provider** | TinyFish Search API (12,000 free req/day, then wallet-funded) |
| **VAD Engine** | Silero VAD (Noise Cancellation via BVC) |
| **UI Framework** | PyQt6 Reactive HUD |
| **Action Registry** | 91+ Active Action Modules (Dynamic auto-discovery) |
| **Latency** | ~1.0s - 2.5s end-to-end voice roundtrip |
| **Python Version** | 3.12 (compatible with 3.10+) |
| **Mathematics Engine** | MATRIS: SymPy + SciPy + NumPy |
| **Memory Backend** | JSON-based long-term memory with recency-based prompt formatting |
| **Dashboard Port** | 8000 (HTTP) with optional HTTPS |
| **Dashboard Encryption** | AES-256-CBC with session-key-derived key |
| **Concurrent Users** | Single-user desktop companion |
| **Supported Languages** | Hinglish (Hindi + English), English |

### Performance

- **Voice Roundtrip**: 1.0s - 2.5s (depends on network and model)
- **Tool Execution**: Variable (0.5s - 5s depending on tool)
- **Memory Recall**: < 200ms for indexed entries
- **HUD Frame Rate**: 30-60 FPS (adaptive based on activity)
- **Memory Footprint**: ~50KB base, grows with user interaction

---

## File Structure

```
ZENITH/
├ agent.py                      # Main entrypoint & LiveKit worker launcher
├ zenith_gui.py                 # PyQt6 main GUI window & event wiring
├ ui.py                         # Reactive HUD components & styling
├ prompts.py                    # Personality & system instructions
├ requirements.txt              # Python package dependencies
├ .env                          # Environment variables & API keys
│
├ Tools/                        # 91+ Action Modules
│   ├── mathematical_reasoner.py  # MATRIS Mathematical Intelligence bridge
│   ├── autonomous_research.py    # Autonomous Intelligence Engine bridge
│   ├── memory_brain.py           # User profiling & mood tracking
│   ├── desktop_show.py           # Desktop show & window automation
│   ├── code_handler.py           # Code debugging & Groq fixer
│   ├── code_generator.py         # Code generation & file creation
│   ├── presentation_controller.py# PPTX automation
│   ├── proactive.py              # Background trigger engine
│   ├── simulation_engine.py      # Physics/Math simulation bridge
│   ├── webcam_overlay.py         # Floating webcam window
│   ├── mathematics/              # MATRIS core: solvers, parsers, engines
│   ├── simulation/               # 9-domain simulation engine sub-package
│   ├── [85 other tool modules]
│   ├── time_volume_bright.py    # Time, volume, brightness, weather, status
│   ├── send_whatsapp_message.py # WhatsApp messaging
│   ├── spotify.py                # Spotify control
│   ├── code_generator.py         # Code generation & file creation
│   └── [70+ more tool modules]
│
├ autonomous_intelligence/       # Self-directed research package
│   ├── director.py               # Research director & session thread
│   ├── planner.py                # Research task planner
│   ├── web_engine.py             # DuckDuckGo search & page reader
│   ├── local_engine.py           # Local file indexing & AST parser
│   └── knowledge.py              # Claim verification & evidence graphs
│
├ core/                         # System core loaders
│   ├── action_loader.py          # Dynamic tool discovery & validation
│   ├── plugin_loader.py          # Plugin registry & settings schemas
│   ├── wake_word.py              # Wake-word detection engine
│   └── audio_devices.py          # Input/output audio device enumeration
│
├ mathematics_ui/               # MATRIS PyQt6 Interactive Canvas
│   ├── __init__.py
│   ├── math_canvas.py            # Mathematical state visualization widget
│   ├── drawing_pad.py            # Freehand drawing canvas with OCR
│   └── matrix_input.py           # NxN matrix grid input widget
│
├ data/                         # Persistent memory storage
│   ├── user_profile.json         # Extracted user profile & preferences
│   ├── mood_log.json             # Mood history
│   ├── memory_summary.json       # Fact memory storage
│   └── mathematics/              # MATRIS data storage
│
├ project_companion/            # Project management companion
│   ├── orchestrator.py           # Project lifecycle manager
│   ├── models.py                 # Data models (Project, Task, Milestone)
│   ├── store.py                  # Persistence layer
│   └── [tests/]
│
├ dashboard/                    # Local HTTP dashboard
│   ├── server.py                 # FastAPI dashboard server
│   ├── static/                   # Static files (HTML, CSS, JS)
│   │   ├── app.html
│   │   ├── crypto-js.min.js
│   │   └── login.html
│   └── [certs/]
│
└── config/                       # Configuration files
    ├── api_keys.json             # API keys and settings
    ├── jarvis.ico                # Application icon
    └── zenith.ico
```

---

## License & Credits

Created by **Lalit Manjunatha**. All rights reserved.

### Acknowledgment

ZENITH uses the following third-party technologies:

- **LiveKit** - Real-time audio/video networking for voice agents
- **Google Gemini 2.5 Flash Native Audio** - Real-time bidirectional voice model
- **PyQt6** - Python Qt bindings for the HUD UI
- **SymPy** - Symbolic mathematics for MATRIS
- **SciPy** - Scientific computing for simulations
- **NumPy** - Numerical operations for matrices and data
- **psutil** - System monitoring and diagnostics
- **matplotlib** - Chart and visualization generation
- **pyautogui** - GUI automation for desktop control
- **pytesseract** - OCR for handwriting recognition
- **python-dotenv** - Environment variable management

---

*Last updated: October 2026*
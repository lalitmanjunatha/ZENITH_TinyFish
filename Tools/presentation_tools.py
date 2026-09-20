"""
ZENITH Presentation & Fun Tools - System Monitor, Weather, Fun Facts, Quizzes, etc.
"""
import os
import math
import json
import random
import time
from datetime import datetime
from typing import Optional
from livekit.agents import function_tool

TOOL = {
    "name": "presentation_tools",
    "description": "Presentation and entertainment tools: system monitor, timers, fun facts, quizzes, jokes, and quotes. Use when the user wants system stats, entertainment, or presentation aids.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Tool: 'system_monitor', 'system_monitor_chart', 'timer_start', 'timer_check', 'fun_fact', 'joke', 'quote', 'quiz'"},
            "label": {"type": "STRING", "description": "Timer label or quiz topic"}
        },
        "required": ["action"]
    },
    "handler": "system_monitor",
}

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'Downloads', 'zenith_charts')
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==================== SYSTEM MONITOR ====================
@function_tool()
async def system_monitor() -> str:
    """Get live system stats: CPU, RAM, Disk usage."""
    if not HAS_PSUTIL:
        return "psutil not installed"
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return (f"SYSTEM MONITOR:\n"
            f"  CPU: {cpu}%\n"
            f"  RAM: {ram.percent}% ({ram.used // (1024**3)}GB / {ram.total // (1024**3)}GB)\n"
            f"  Disk: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)")


@function_tool()
async def system_monitor_chart() -> str:
    """Generate a system usage chart."""
    if not HAS_PSUTIL or not HAS_MPL:
        return "psutil/matplotlib not installed"
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor('#0a0a0f')
    ax.set_facecolor('#0a0a0f')
    bars = ax.barh(['CPU', 'RAM', 'Disk'], [cpu, ram, disk],
                    color=['#06b6d4', '#22c55e', '#f97316'], height=0.5)
    ax.set_xlim(0, 100)
    ax.set_title('System Usage', color='white', fontsize=14)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#334155')
    for bar, val in zip(bars, [cpu, ram, disk]):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}%', va='center', color='white', fontsize=11)
    path = os.path.join(OUTPUT_DIR, f"sysmon_{datetime.now().strftime('%H%M%S')}.png")
    plt.tight_layout()
    plt.savefig(path, facecolor='#0a0a0f')
    plt.close()
    return f"System monitor chart -> {path}"


# ==================== TIMER WIDGET ====================
_timer_state = {"active": False, "start": None, "label": ""}

@function_tool()
async def timer_start(label: str = "Demo") -> str:
    """Start a visible timer."""
    _timer_state["active"] = True
    _timer_state["start"] = datetime.now()
    _timer_state["label"] = label
    return f"Timer started: {label}"

@function_tool()
async def timer_check() -> str:
    """Check elapsed time."""
    if not _timer_state["active"]:
        return "No timer active."
    elapsed = (datetime.now() - _timer_state["start"]).total_seconds()
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)
    return f"Timer '{_timer_state['label']}': {mins}m {secs}s elapsed"


# ==================== FUN FACTS ====================
_fun_facts = [
    "Honey never spoils. Archaeologists found 3000-year-old honey in Egyptian tombs that was still edible.",
    "Octopuses have three hearts and blue blood.",
    "A day on Venus is longer than a year on Venus.",
    "Bananas are berries, but strawberries are not.",
    "The inventor of the Pringles can is buried in one.",
    "A group of flamingos is called a 'flamboyance'.",
    "Cows have best friends and get stressed when separated.",
    "The shortest war in history lasted 38-45 minutes (Anglo-Zanzibar War).",
    "Scotland's national animal is the unicorn.",
    "A jiffy is an actual unit of time: 1/100th of a second.",
    "The unicorn is Scotland's national animal.",
    "Hot water freezes faster than cold water (Mpemba effect).",
    "There are more possible iterations of a game of chess than atoms in the observable universe.",
    "The moon has moonquakes just like Earth has earthquakes.",
    "Wombat poop is cube-shaped.",
    "A teaspoonful of neutron star would weigh about 6 billion tons.",
    "Bananas produce anti-radiation compounds, so they're slightly radioactive.",
    "The Great Wall of China is not visible from space with the naked eye.",
    "Venus is the only planet that spins clockwise.",
    "The human body contains about 7 octillion atoms.",
]

@function_tool()
async def fun_fact() -> str:
    """Get a random fun fact."""
    return random.choice(_fun_facts)


# ==================== COMPLIMENT GENERATOR ====================
_compliments = [
    "You're doing amazing work!",
    "Your code is cleaner than a freshly wiped whiteboard!",
    "You're the reason someone smiles today.",
    "Keep going - you're closer than you think!",
    "Your potential is limitless.",
    "You make learning look easy!",
    "The world needs more people like you.",
    "You're crushing it today!",
    "Your dedication is inspiring.",
    "You're a problem-solving machine!",
]

@function_tool()
async def compliment() -> str:
    """Get a random compliment."""
    return random.choice(_compliments)


# ==================== JOKE GENERATOR ====================
_jokes = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "There are only 10 types of people in the world: those who understand binary and those who don't.",
    "A SQL query walks into a bar, walks up to two tables and asks... Can I join you?",
    "Why was the JavaScript developer sad? Because he didn't Node how to Express himself.",
    "What's a programmer's favorite hangout place? Foo Bar!",
    "Why do Java developers wear glasses? Because they can't C#!",
    "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
    "What is a robot's favorite type of music? Heavy metal!",
    "Why did the developer go broke? Because he used up all his cache!",
    "What's the object-oriented way to become wealthy? Inheritance!",
    "Why do programmers hate nature? It has too many bugs.",
    "What's a computer's favorite snack? Microchips!",
]

@function_tool()
async def joke() -> str:
    """Tell a random tech joke."""
    return random.choice(_jokes)


# ==================== MOTIVATIONAL QUOTE ====================
_quotes = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Innovation distinguishes between a leader and a follower. - Steve Jobs",
    "Stay hungry, stay foolish. - Steve Jobs",
    "The best time to plant a tree was 20 years ago. The second best time is now.",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. - Churchill",
    "In the middle of difficulty lies opportunity. - Albert Einstein",
    "Code is like humor. When you have to explain it, it's bad. - Cory House",
    "First, solve the problem. Then, write the code. - John Johnson",
    "Talk is cheap. Show me the code. - Linus Torvalds",
    "The only limit to our realization of tomorrow is our doubts of today. - FDR",
]

@function_tool()
async def motivation() -> str:
    """Get a random motivational quote."""
    return random.choice(_quotes)


# ==================== TRIVIA ====================
_trivia = [
    {"q": "What planet is known as the Red Planet?", "a": "Mars"},
    {"q": "What is the speed of light in km/s?", "a": "299,792 km/s"},
    {"q": "Who painted the Mona Lisa?", "a": "Leonardo da Vinci"},
    {"q": "What is the chemical symbol for gold?", "a": "Au"},
    {"q": "How many bits in a byte?", "a": "8"},
    {"q": "What year was the first iPhone released?", "a": "2007"},
    {"q": "What is the largest ocean on Earth?", "a": "Pacific Ocean"},
    {"q": "What does CPU stand for?", "a": "Central Processing Unit"},
    {"q": "How many continents are there?", "a": "7"},
    {"q": "What is the boiling point of water in Celsius?", "a": "100°C"},
]

@function_tool()
async def trivia_question() -> str:
    """Get a random trivia question."""
    q = random.choice(_trivia)
    return f"TRIVIA: {q['q']}\n\nType your answer or say 'reveal answer'"

@function_tool()
async def trivia_answer() -> str:
    """Reveal the last trivia answer."""
    return f"The answer was: {random.choice(_trivia)['a']}"


# ==================== WORD OF THE DAY ====================
_words = [
    {"word": "Ephemeral", "meaning": "Lasting for a very short time", "example": "The ephemeral beauty of cherry blossoms"},
    {"word": "Eloquent", "meaning": "Fluent or persuasive in speaking or writing", "example": "An eloquent speech that moved the audience"},
    {"word": "Resilient", "meaning": "Able to recover quickly from difficulties", "example": "Children are remarkably resilient"},
    {"word": "Ubiquitous", "meaning": "Present, appearing, or found everywhere", "example": "Smartphones have become ubiquitous"},
    {"word": "Pragmatic", "meaning": "Dealing with things sensibly and realistically", "example": "A pragmatic approach to problem-solving"},
    {"word": "Serendipity", "meaning": "Finding pleasant things by chance", "example": "The discovery was pure serendipity"},
    {"word": "Paradigm", "meaning": "A typical example or pattern of something", "example": "A paradigm shift in technology"},
    {"word": "Cacophony", "meaning": "A harsh mixture of sounds", "example": "The cacophony of traffic filled the street"},
]

@function_tool()
async def word_of_the_day() -> str:
    """Get a random vocabulary word of the day."""
    w = random.choice(_words)
    return f"WORD OF THE DAY: {w['word']}\nMeaning: {w['meaning']}\nExample: {w['example']}"


# ==================== THIS DAY IN HISTORY ====================
_history = [
    "1985: The Live Aid concert was held at Wembley Stadium",
    "1969: Apollo 11 astronauts became the first humans on the Moon",
    "1991: The World Wide Web was publicly announced by Tim Berners-Lee",
    "2007: The first iPhone was released by Apple",
    "1752: Benjamin Franklin proved lightning is electricity",
    "1947: India gained independence from British rule",
    "1961: The Berlin Wall was constructed",
    "1971: The first email was sent by Ray Tomlinson",
    "1998: Google was founded by Larry Page and Sergey Brin",
    "2004: Facebook was launched by Mark Zuckerberg",
]

@function_tool()
async def this_day_in_history() -> str:
    """Get historical events that happened today."""
    return random.choice(_history)


# ==================== COUNTER ====================
_counter_state = {"value": 0}

@function_tool()
async def counter_increment(amount: int = 1) -> str:
    """Increment the counter."""
    _counter_state["value"] += amount
    return f"Counter: {_counter_state['value']}"

@function_tool()
async def counter_decrement(amount: int = 1) -> str:
    """Decrement the counter."""
    _counter_state["value"] -= amount
    return f"Counter: {_counter_state['value']}"

@function_tool()
async def counter_reset() -> str:
    """Reset counter to 0."""
    _counter_state["value"] = 0
    return "Counter reset to 0"

@function_tool()
async def counter_get() -> str:
    """Get current counter value."""
    return f"Counter: {_counter_state['value']}"


# ==================== COIN FLIP ====================
@function_tool()
async def coin_flip() -> str:
    """Flip a coin."""
    return random.choice(["Heads!", "Tails!"])


# ==================== DICE ROLL ====================
@function_tool()
async def dice_roll(sides: int = 6) -> str:
    """Roll a dice."""
    return f"You rolled: {random.randint(1, sides)} (d{sides})"


# ==================== RANDOM NUMBER ====================
@function_tool()
async def random_number(min_val: int = 1, max_val: int = 100) -> str:
    """Generate a random number."""
    return f"Random number: {random.randint(min_val, max_val)} (between {min_val} and {max_val
})"


# ==================== BREATHING EXERCISE ====================
@function_tool()
async def breathing_exercise() -> str:
    """Guide a 4-7-8 breathing exercise."""
    return ("BREATHING EXERCISE (4-7-8):\n\n"
            "1. Breathe IN through nose for 4 seconds\n"
            "2. HOLD breath for 7 seconds\n"
            "3. Breathe OUT through mouth for 8 seconds\n\n"
            "Repeat 4 times. This reduces anxiety and helps focus!")


# ==================== STRETCH REMINDER ====================
@function_tool()
async def stretch_reminder() -> str:
    """Get stretching exercises for desk workers."""
    return ("STRETCH BREAK:\n\n"
            "1. Neck rolls - 10 each direction\n"
            "2. Shoulder shrugs - 10 times\n"
            "3. Wrist circles - 10 each hand\n"
            "4. Seated spinal twist - hold 20s each side\n"
            "5. Standing hamstring stretch - 20s each leg\n"
            "6. Eye rest - look at something 20ft away for 20s\n\n"
            "Do this every hour to stay healthy!")


# ==================== TIPS ====================
_tips = [
    "Use Ctrl+Shift+T to reopen closed browser tabs.",
    "Windows+L locks your computer instantly.",
    "Tab in VS Code auto-completes variable names.",
    "Use 'git stash' to temporarily save uncommitted changes.",
    "Press Ctrl+D to select next occurrence in VS Code.",
    "Use 'pip freeze > requirements.txt' to save dependencies.",
    "Ctrl+Shift+P opens command palette in VS Code.",
    "Use 'ls -la' to see hidden files in terminal.",
    "Git commit message: use imperative mood ('Add feature' not 'Added').",
    "Use virtual environments: 'python -m venv env'.",
]

@function_tool()
async def pro_tip() -> str:
    """Get a random coding/tech tip."""
    return random.choice(_tips)

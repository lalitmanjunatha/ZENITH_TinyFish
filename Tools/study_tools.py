"""
ZENITH Study Tools - Flashcards, Pomodoro, Study Planner, GPA Calculator, Unit Converter, etc.
"""
import json
import os
import math
import time
from datetime import datetime, timedelta
from typing import Optional, List
from livekit.agents import function_tool

TOOL = {
    "name": "study_tools",
    "description": "Study assistance tools: flashcard generator, Pomodoro timer, study planner, reading time calculator, GPA calculator, and unit converter. Use when the user wants help with studying or academic tasks.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Tool: 'generate_flashcards', 'pomodoro_start', 'pomodoro_status', 'pomodoro_stop', 'study_planner', 'reading_time', 'gpa_calculator', 'unit_converter'"},
            "notes": {"type": "STRING", "description": "Study notes for flashcard generation"},
            "subjects": {"type": "STRING", "description": "Comma-separated subjects for study planner"},
            "grades": {"type": "STRING", "description": "Grades for GPA calculator (e.g. 'A,B+,B,A-,C+')"},
            "hours_per_day": {"type": "INTEGER", "description": "Study hours per day (default: 6)"}
        },
        "required": ["action"]
    },
    "handler": "generate_flashcards",
}


# ==================== FLASHCARD GENERATOR ====================
@function_tool()
async def generate_flashcards(notes: str) -> str:
    """Generate flashcards from study notes. Paste your notes and get Q&A pairs."""
    lines = [l.strip() for l in notes.split('\n') if l.strip()]
    cards = []
    for i, line in enumerate(lines[:20]):
        if len(line) > 10:
            cards.append(f"Card {i+1}: {line[:80]}")
    if not cards:
        return "No flashcards generated. Provide longer notes."
    output = "FLASHCARDS:\n\n"
    for card in cards:
        output += f"[{card}]\n"
    output += f"\nTotal: {len(cards)} cards created"
    return output


# ==================== POMODORO TIMER ====================
_pomodoro_state = {"active": False, "start_time": None, "sessions": 0, "total_focus_min": 0}

@function_tool()
async def pomodoro_start(work_min: int = 25, break_min: int = 5) -> str:
    """Start a Pomodoro timer. 25min work, 5min break cycle."""
    _pomodoro_state["active"] = True
    _pomodoro_state["start_time"] = datetime.now()
    return f"Pomodoro started! Work: {work_min}min, Break: {break_min}min. Focus mode ON!"

@function_tool()
async def pomodoro_status() -> str:
    """Check current Pomodoro status."""
    if not _pomodoro_state["active"]:
        return f"Pomodoro not active. Sessions completed: {_pomodoro_state['sessions']}, Total focus: {_pomodoro_state['total_focus_min']}min"
    elapsed = (datetime.now() - _pomodoro_state["start_time"]).seconds // 60
    return f"Pomodoro ACTIVE. Elapsed: {elapsed}min | Sessions: {_pomodoro_state['sessions']} | Total focus: {_pomodoro_state['total_focus_min']}min"

@function_tool()
async def pomodoro_stop() -> str:
    """Stop the Pomodoro timer."""
    if _pomodoro_state["active"] and _pomodoro_state["start_time"]:
        elapsed = (datetime.now() - _pomodoro_state["start_time"]).seconds // 60
        _pomodoro_state["total_focus_min"] += elapsed
        _pomodoro_state["sessions"] += 1
    _pomodoro_state["active"] = False
    _pomodoro_state["start_time"] = None
    return f"Pomodoro stopped. Sessions: {_pomodoro_state['sessions']}, Total focus: {_pomodoro_state['total_focus_min']}min"


# ==================== STUDY PLANNER ====================
@function_tool()
async def study_planner(subjects: str, hours_per_day: int = 6, days: int = 7) -> str:
    """Generate a study schedule. subjects: comma-separated list."""
    sub_list = [s.strip() for s in subjects.split(',')]
    hours_each = hours_per_day / max(len(sub_list), 1)
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    schedule = "WEEKLY STUDY PLAN:\n\n"
    for d in range(min(days, 7)):
        day = days_of_week[d % 7]
        schedule += f"{day}:\n"
        start_hour = 9
        for s in sub_list:
            schedule += f"  {start_hour}:00 - {start_hour + int(hours_each)}:00  {s}\n"
            start_hour += int(hours_each)
        schedule += "\n"

    schedule += f"Total: {hours_per_day}h/day x {days} days = {hours_per_day * days} hours"
    return schedule


# ==================== READING TIME ====================
@function_tool()
async def reading_time(text: str) -> str:
    """Calculate estimated reading time for text. Average 200 words/min."""
    words = len(text.split())
    minutes = math.ceil(words / 200)
    return f"Word count: {words} | Estimated reading time: {minutes} minutes"


# ==================== GPA CALCULATOR ====================
@function_tool()
async def gpa_calculator(grades: str) -> str:
    """Calculate GPA. grades format: 'A,B+,B,A-,C+' or '4.0,3.5,3.0'"""
    grade_points = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'F': 0.0
    }
    grade_list = [g.strip().upper() for g in grades.split(',')]
    total = 0
    count = 0
    details = []
    for g in grade_list:
        if g in grade_points:
            total += grade_points[g]
            count += 1
            details.append(f"  {g} = {grade_points[g]}")
        else:
            try:
                val = float(g)
                total += val
                count += 1
                details.append(f"  {g} = {val}")
            except ValueError:
                pass

    if count == 0:
        return "No valid grades. Use format: A,B+,B,A-"

    gpa = total / count
    return f"GPA CALCULATOR:\n" + "\n".join(details) + f"\n\nGPA: {gpa:.2f} / 4.00"


# ==================== UNIT CONVERTER ====================
@function_tool()
async def unit_convert(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between units. Supports: km-miles, kg-lbs, C-F, inches-cm, etc."""
    conversions = {
        ('km', 'miles'): 0.621371, ('miles', 'km'): 1.60934,
        ('kg', 'lbs'): 2.20462, ('lbs', 'kg'): 0.453592,
        ('c', 'f'): lambda x: x * 9/5 + 32, ('f', 'c'): lambda x: (x - 32) * 5/9,
        ('inches', 'cm'): 2.54, ('cm', 'inches'): 0.393701,
        ('feet', 'm'): 0.3048, ('m', 'feet'): 3.28084,
        ('meters', 'feet'): 3.28084, ('feet', 'meters'): 0.3048,
        ('yards', 'm'): 0.9144, ('m', 'yards'): 1.09361,
        ('gallons', 'liters'): 3.78541, ('liters', 'gallons'): 0.264172,
        ('oz', 'grams'): 28.3495, ('grams', 'oz'): 0.035274,
        ('mb', 'gb'): 0.001, ('gb', 'mb'): 1000,
        ('kb', 'mb'): 0.001, ('mb', 'kb'): 1000,
    }
    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        factor = conversions[key]
        if callable(factor):
            result = factor(value)
        else:
            result = value * factor
        return f"{value} {from_unit} = {result:.4f} {to_unit}"
    return f"Conversion {from_unit} -> {to_unit} not supported. Available: km-miles, kg-lbs, C-F, inches-cm, feet-m, etc."


# ==================== SCIENTIFIC CALCULATOR ====================
@function_tool()
async def scientific_calc(expression: str) -> str:
    """Evaluate math expression. Supports: sin, cos, tan, sqrt, log, ln, pi, e, power."""
    import math
    expr = expression.lower()
    expr = expr.replace('pi', str(math.pi))
    expr = expr.replace('e', str(math.e))
    expr = expr.replace('^', '**')
    expr = expr.replace('sqrt', 'math.sqrt')
    expr = expr.replace('sin', 'math.sin')
    expr = expr.replace('cos', 'math.cos')
    expr = expr.replace('tan', 'math.tan')
    expr = expr.replace('log', 'math.log10')
    expr = expr.replace('ln', 'math.log')
    expr = expr.replace('abs', 'abs')
    try:
        result = eval(expr)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error: {str(e)}"


# ==================== BINARY/HEX CONVERTER ====================
@function_tool()
async def number_convert(value: str, from_base: str, to_base: str) -> str:
    """Convert between number bases. from_base/to_base: bin, oct, dec, hex."""
    bases = {'bin': 2, 'oct': 8, 'dec': 10, 'hex': 16}
    try:
        num = int(value, bases[from_base.lower()])
        result = ""
        if to_base.lower() == 'bin':
            result = bin(num)
        elif to_base.lower() == 'oct':
            result = oct(num)
        elif to_base.lower() == 'hex':
            result = hex(num)
        else:
            result = str(num)
        return f"{value} ({from_base}) = {result} ({to_base})"
    except ValueError:
        return f"Invalid {from_base} number: {value}"


# ==================== ROMAN NUMERAL CONVERTER ====================
@function_tool()
async def roman_convert(value: str) -> str:
    """Convert between Roman numerals and integers."""
    roman_map = [('M',1000),('CM',900),('D',500),('CD',400),('C',100),('XC',90),
                 ('L',50),('XL',40),('X',10),('IX',9),('V',5),('IV',4),('I',1)]

    def int_to_roman(num):
        result = ""
        for roman, val in roman_map:
            while num >= val:
                result += roman
                num -= val
        return result

    def roman_to_int(s):
        result = 0
        for roman, val in roman_map:
            while s.startswith(roman):
                result += val
                s = s[len(roman):]
        return result

    try:
        num = int(value)
        return f"{num} = {int_to_roman(num)}"
    except ValueError:
        try:
            val = roman_to_int(value.upper())
            return f"{value.upper()} = {val}"
        except:
            return f"Invalid input: {value}"


# ==================== PASSWORD GENERATOR ====================
@function_tool()
async def password_generate(length: int = 16, include_symbols: bool = True) -> str:
    """Generate a secure random password."""
    import random
    import string
    chars = string.ascii_letters + string.digits
    if include_symbols:
        chars += "!@#$%^&*"
    password = ''.join(random.choice(chars) for _ in range(length))
    return f"Password: {password}\nLength: {length} characters"


# ==================== PERCENTAGE CALCULATOR ====================
@function_tool()
async def percentage_calc(value: float, total: float) -> str:
    """Calculate percentage. value out of total."""
    if total == 0:
        return "Cannot divide by zero"
    pct = (value / total) * 100
    return f"{value} / {total} = {pct:.2f}%"


# ==================== COMPOUND INTEREST ====================
@function_tool()
async def compound_interest(principal: float, rate: float, time: float, n: int = 12) -> str:
    """Calculate compound interest. rate: annual % (e.g. 8.5), time: years, n: compounds/year."""
    r = rate / 100
    amount = principal * (1 + r/n)**(n*time)
    interest = amount - principal
    return f"Principal: {principal}\nRate: {rate}%\nTime: {time} years\nAmount: {amount:.2f}\nInterest Earned: {interest:.2f}"


# ==================== BMI CALCULATOR ====================
@function_tool()
async def bmi_calculator(weight_kg: float, height_cm: float) -> str:
    """Calculate BMI from weight (kg) and height (cm)."""
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return f"BMI: {bmi:.1f} ({category})\nWeight: {weight_kg}kg, Height: {height_cm}cm"


# ==================== COUNTDOWN TIMER ====================
@function_tool()
async def countdown(date_str: str) -> str:
    """Calculate time remaining until a date. Format: 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM'."""
    try:
        if ' ' in date_str:
            target = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        else:
            target = datetime.strptime(date_str, "%Y-%m-%d")
        now = datetime.now()
        diff = target - now
        if diff.days < 0:
            return f"Date {date_str} has passed!"
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        return f"Countdown to {date_str}:\n{diff.days} days, {hours} hours, {minutes} minutes remaining"
    except ValueError:
        return "Invalid date format. Use: YYYY-MM-DD or YYYY-MM-DD HH:MM"


# ==================== VOCABULARY BUILDER ====================
_vocab_list = []
@function_tool()
async def vocabulary_add(word: str, meaning: str) -> str:
    """Add a word to vocabulary list."""
    _vocab_list.append({"word": word, "meaning": meaning})
    return f"Added: {word} = {meaning} (Total: {len(_vocab_list)} words)"

@function_tool()
async def vocabulary_list() -> str:
    """Show all vocabulary words."""
    if not _vocab_list:
        return "Vocabulary list is empty."
    output = "VOCABULARY:\n\n"
    for i, v in enumerate(_vocab_list, 1):
        output += f"{i}. {v['word']}: {v['meaning']}\n"
    return output


# ==================== READING TIME CALCULATOR ====================
@function_tool()
async def estimate_reading_time(word_count: int) -> str:
    """Estimate reading time from word count."""
    minutes = math.ceil(word_count / 200)
    return f"{word_count} words = ~{minutes} minutes to read"


# ==================== STOPWATCH ====================
_stopwatch_state = {"active": False, "start_time": None, "laps": []}

@function_tool()
async def stopwatch_start() -> str:
    """Start a stopwatch."""
    _stopwatch_state["active"] = True
    _stopwatch_state["start_time"] = datetime.now()
    _stopwatch_state["laps"] = []
    return "Stopwatch started!"

@function_tool()
async def stopwatch_lap() -> str:
    """Record a lap time."""
    if not _stopwatch_state["active"]:
        return "Stopwatch not running."
    elapsed = (datetime.now() - _stopwatch_state["start_time"]).total_seconds()
    _stopwatch_state["laps"].append(elapsed)
    return f"Lap {len(_stopwatch_state['laps'])}: {elapsed:.2f}s"

@function_tool()
async def stopwatch_stop() -> str:
    """Stop the stopwatch and show results."""
    if not _stopwatch_state["active"]:
        return "Stopwatch not running."
    elapsed = (datetime.now() - _stopwatch_state["start_time"]).total_seconds()
    _stopwatch_state["active"] = False
    result = f"Final time: {elapsed:.2f}s"
    if _stopwatch_state["laps"]:
        result += f"\nLaps: {', '.join(f'{l:.2f}s' for l in _stopwatch_state['laps'])}"
    return result


# ==================== TODO LIST ====================
_todo_list = []

@function_tool()
async def todo_add(task: str, priority: str = "medium") -> str:
    """Add a task to todo list. priority: high, medium, low."""
    _todo_list.append({"task": task, "priority": priority, "done": False})
    return f"Added: [{priority.upper()}] {task}"

@function_tool()
async def todo_list_all() -> str:
    """Show all todo items."""
    if not _todo_list:
        return "Todo list is empty."
    output = "TODO LIST:\n\n"
    for i, t in enumerate(_todo_list, 1):
        status = "[DONE]" if t["done"] else "[TODO]"
        output += f"{i}. {status} [{t['priority'].upper()}] {t['task']}\n"
    pending = sum(1 for t in _todo_list if not t["done"])
    output += f"\nPending: {pending}/{len(_todo_list)}"
    return output

@function_tool()
async def todo_complete(index: int) -> str:
    """Mark a todo item as complete. index starts at 1."""
    if 1 <= index <= len(_todo_list):
        _todo_list[index-1]["done"] = True
        return f"Completed: {_todo_list[index-1]['task']}"
    return f"Invalid index. Choose 1-{len(_todo_list)}"


# ==================== EXPENSE TRACKER ====================
_expenses = []

@function_tool()
async def expense_add(amount: float, category: str, description: str = "") -> str:
    """Add an expense."""
    _expenses.append({"amount": amount, "category": category, "description": description, "date": datetime.now().isoformat()})
    return f"Added: {amount} in {category}"

@function_tool()
async def expense_summary() -> str:
    """Show expense summary by category."""
    if not _expenses:
        return "No expenses recorded."
    by_cat = {}
    for e in _expenses:
        cat = e["category"]
        by_cat[cat] = by_cat.get(cat, 0) + e["amount"]
    total = sum(by_cat.values())
    output = "EXPENSE SUMMARY:\n\n"
    for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
        pct = (amt / total * 100) if total else 0
        output += f"  {cat}: {amt:.2f} ({pct:.1f}%)\n"
    output += f"\nTotal: {total:.2f}"
    return output

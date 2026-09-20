"""
ZENITH Data Tools - Charts, Graphs, Calculators, Survey Creator, etc.
"""
import os
import math
import json
from datetime import datetime
from typing import Optional
from livekit.agents import function_tool

TOOL = {
    "name": "data_tools",
    "description": "Create charts (bar, pie, line), perform calculations, and generate data visualizations. Use when the user wants to visualize data or perform mathematical operations.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Tool: 'bar_chart', 'pie_chart', 'line_graph', 'calculator', 'unit_converter'"},
            "data": {"type": "STRING", "description": "Data in format 'Label1:Value1,Label2:Value2' for charts, or expression for calculator"},
            "title": {"type": "STRING", "description": "Chart title (optional)"},
            "x_label": {"type": "STRING", "description": "X-axis label for line graph"},
            "y_label": {"type": "STRING", "description": "Y-axis label for line graph"}
        },
        "required": ["action"]
    },
    "handler": "bar_chart",
}

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'Downloads', 'zenith_charts')
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==================== BAR CHART ====================
@function_tool()
async def bar_chart(data: str, title: str = "Bar Chart") -> str:
    """Create a bar chart. data format: 'Label1:Value1,Label2:Value2'"""
    if not HAS_MPL:
        return "matplotlib not installed"
    items = {}
    for pair in data.split(','):
        parts = pair.strip().split(':')
        if len(parts) == 2:
            items[parts[0].strip()] = float(parts[1].strip())

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#0a0a0f')
    ax.set_facecolor('#0a0a0f')
    colors = ['#06b6d4', '#f97316', '#22c55e', '#a855f7', '#ef4444', '#eab308']
    ax.bar(items.keys(), items.values(), color=colors[:len(items)])
    ax.set_title(title, color='white', fontsize=14)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#334155')
    path = os.path.join(OUTPUT_DIR, f"bar_{datetime.now().strftime('%H%M%S')}.png")
    plt.tight_layout()
    plt.savefig(path, facecolor='#0a0a0f')
    plt.close()
    return f"Bar chart created -> {path}"


# ==================== PIE CHART ====================
@function_tool()
async def pie_chart(data: str, title: str = "Pie Chart") -> str:
    """Create a pie chart. data format: 'Label1:Value1,Label2:Value2'"""
    if not HAS_MPL:
        return "matplotlib not installed"
    items = {}
    for pair in data.split(','):
        parts = pair.strip().split(':')
        if len(parts) == 2:
            items[parts[0].strip()] = float(parts[1].strip())

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#0a0a0f')
    colors = ['#06b6d4', '#f97316', '#22c55e', '#a855f7', '#ef4444', '#eab308', '#ec4899']
    wedges, texts, autotexts = ax.pie(items.values(), labels=items.keys(), colors=colors[:len(items)],
                                       autopct='%1.1f%%', textprops={'color': 'white'})
    ax.set_title(title, color='white', fontsize=14)
    path = os.path.join(OUTPUT_DIR, f"pie_{datetime.now().strftime('%H%M%S')}.png")
    plt.tight_layout()
    plt.savefig(path, facecolor='#0a0a0f')
    plt.close()
    return f"Pie chart created -> {path}"


# ==================== LINE GRAPH ====================
@function_tool()
async def line_graph(data: str, title: str = "Line Graph", x_label: str = "X", y_label: str = "Y") -> str:
    """Create a line graph. data format: '1:10,2:20,3:15'"""
    if not HAS_MPL:
        return "matplotlib not installed"
    x_vals, y_vals = [], []
    for pair in data.split(','):
        parts = pair.strip().split(':')
        if len(parts) == 2:
            x_vals.append(float(parts[0].strip()))
            y_vals.append(float(parts[1].strip()))

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#0a0a0f')
    ax.set_facecolor('#0a0a0f')
    ax.plot(x_vals, y_vals, color='#06b6d4', linewidth=2, marker='o', markersize=6)
    ax.set_title(title, color='white', fontsize=14)
    ax.set_xlabel(x_label, color='white')
    ax.set_ylabel(y_label, color='white')
    ax.tick_params(colors='white')
    ax.grid(True, alpha=0.3, color='#334155')
    for spine in ax.spines.values():
        spine.set_color('#334155')
    path = os.path.join(OUTPUT_DIR, f"line_{datetime.now().strftime('%H%M%S')}.png")
    plt.tight_layout()
    plt.savefig(path, facecolor='#0a0a0f')
    plt.close()
    return f"Line graph created -> {path}"


# ==================== SCATTER PLOT ====================
@function_tool()
async def scatter_plot(data: str, title: str = "Scatter Plot") -> str:
    """Create a scatter plot. data format: '1,5;2,8;3,3;4,10' (x,y pairs)"""
    if not HAS_MPL:
        return "matplotlib not installed"
    x_vals, y_vals = [], []
    for pair in data.split(';'):
        parts = pair.strip().split(',')
        if len(parts) == 2:
            x_vals.append(float(parts[0].strip()))
            y_vals.append(float(parts[1].strip()))

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#0a0a0f')
    ax.set_facecolor('#0a0a0f')
    ax.scatter(x_vals, y_vals, color='#06b6d4', s=80, edgecolors='white', linewidth=0.5)
    ax.set_title(title, color='white', fontsize=14)
    ax.tick_params(colors='white')
    ax.grid(True, alpha=0.3, color='#334155')
    for spine in ax.spines.values():
        spine.set_color('#334155')
    path = os.path.join(OUTPUT_DIR, f"scatter_{datetime.now().strftime('%H%M%S')}.png")
    plt.tight_layout()
    plt.savefig(path, facecolor='#0a0a0f')
    plt.close()
    return f"Scatter plot created -> {path}"


# ==================== HISTOGRAM ====================
@function_tool()
async def histogram(data: str, title: str = "Histogram", bins: int = 10) -> str:
    """Create a histogram. data: comma-separated values."""
    if not HAS_MPL:
        return "matplotlib not installed"
    values = [float(x.strip()) for x in data.split(',') if x.strip()]

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#0a0a0f')
    ax.set_facecolor('#0a0a0f')
    ax.hist(values, bins=bins, color='#06b6d4', edgecolor='white', linewidth=0.5)
    ax.set_title(title, color='white', fontsize=14)
    ax.tick_params(colors='white')
    ax.grid(True, alpha=0.3, color='#334155')
    for spine in ax.spines.values():
        spine.set_color('#334155')
    path = os.path.join(OUTPUT_DIR, f"hist_{datetime.now().strftime('%H%M%S')}.png")
    plt.tight_layout()
    plt.savefig(path, facecolor='#0a0a0f')
    plt.close()
    return f"Histogram created -> {path}"


# ==================== STATISTICS CALCULATOR ====================
@function_tool()
async def statistics_calc(data: str) -> str:
    """Calculate statistics for a dataset. data: comma-separated numbers."""
    values = [float(x.strip()) for x in data.split(',') if x.strip()]
    if not values:
        return "No data provided."

    n = len(values)
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n
    std_dev = math.sqrt(variance)
    sorted_v = sorted(values)
    median = sorted_v[n // 2] if n % 2 else (sorted_v[n // 2 - 1] + sorted_v[n // 2]) / 2
    minimum = min(values)
    maximum = max(values)
    data_range = maximum - minimum
    q1 = sorted_v[n // 4]
    q3 = sorted_v[3 * n // 4]
    iqr = q3 - q1

    return (f"STATISTICS (n={n}):\n"
            f"  Mean: {mean:.4f}\n"
            f"  Median: {median:.4f}\n"
            f"  Std Dev: {std_dev:.4f}\n"
            f"  Variance: {variance:.4f}\n"
            f"  Min: {minimum:.4f}\n"
            f"  Max: {maximum:.4f}\n"
            f"  Range: {data_range:.4f}\n"
            f"  Q1: {q1:.4f}\n"
            f"  Q3: {q3:.4f}\n"
            f"  IQR: {iqr:.4f}")


# ==================== EMI CALCULATOR ====================
@function_tool()
async def emi_calculator(principal: float, rate: float, tenure_months: int) -> str:
    """Calculate loan EMI. rate: annual % (e.g. 8.5)"""
    r = rate / 100 / 12
    if r == 0:
        emi = principal / tenure_months
    else:
        emi = principal * r * (1 + r)**tenure_months / ((1 + r)**tenure_months - 1)
    total = emi * tenure_months
    interest = total - principal
    return (f"EMI CALCULATION:\n"
            f"  Loan: {principal:.2f}\n"
            f"  Rate: {rate}%\n"
            f"  Tenure: {tenure_months} months\n"
            f"  EMI: {emi:.2f}/month\n"
            f"  Total Payment: {total:.2f}\n"
            f"  Total Interest: {interest:.2f}")


# ==================== SURVEY CREATOR ====================
_surveys = {}

@function_tool()
async def survey_create(title: str, options: str) -> str:
    """Create a survey. options: comma-separated choices."""
    survey_id = f"survey_{len(_surveys) + 1}"
    opts = [o.strip() for o in options.split(',')]
    _surveys[survey_id] = {"title": title, "options": opts, "votes": {o: 0 for o in opts}}
    return f"Survey created: {title}\nOptions: {', '.join(opts)}\nID: {survey_id}"

@function_tool()
async def survey_vote(survey_id: str, option: str) -> str:
    """Vote on a survey."""
    if survey_id not in _surveys:
        return f"Survey '{survey_id}' not found."
    survey = _surveys[survey_id]
    if option in survey["votes"]:
        survey["votes"][option] += 1
        return f"Voted for '{option}' in {survey['title']}"
    return f"Option '{option}' not found. Available: {', '.join(survey['options'])}"

@function_tool()
async def survey_results(survey_id: str) -> str:
    """Show survey results."""
    if survey_id not in _surveys:
        return f"Survey '{survey_id}' not found."
    survey = _surveys[survey_id]
    total = sum(survey["votes"].values())
    output = f"SURVEY: {survey['title']}\n\n"
    for opt, votes in survey["votes"].items():
        pct = (votes / total * 100) if total else 0
        bar = "#" * int(pct / 5)
        output += f"  {opt}: {votes} votes ({pct:.1f}%) {bar}\n"
    output += f"\nTotal votes: {total}"
    return output


# ==================== QUIZ GENERATOR ====================
@function_tool()
async def quiz_generate(topic: str, num_questions: int = 5) -> str:
    """Generate quiz questions on a topic."""
    templates = {
        "python": [
            "What is the output of print(type([]))?",
            "How do you create a dictionary in Python?",
            "What does 'yield' do in Python?",
            "Explain list comprehension syntax.",
            "What is the difference between 'is' and '=='?",
        ],
        "general": [
            "What does CPU stand for?",
            "What is RAM used for?",
            "What is the binary of 10?",
            "What does HTML stand for?",
            "What is an API?",
        ]
    }
    questions = templates.get(topic.lower(), templates["general"])
    output = f"QUIZ: {topic.upper()}\n\n"
    for i, q in enumerate(questions[:num_questions], 1):
        output += f"{i}. {q
}\n\n"
    return output

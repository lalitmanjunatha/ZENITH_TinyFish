"""
ZENITH Calendar, Todo & Notes Tools
Provides: calendar_add_event, calendar_today, calendar_tomorrow, calendar_week,
          calendar_delete_event, todo_add, todo_list, todo_complete, todo_delete,
          note_create, note_search, note_list
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

from livekit.agents import function_tool

TOOL = {
    "name": "calendar_tools",
    "description": "Manage Google Calendar events, todo lists, and notes. Use when the user wants to add/view/delete calendar events, manage tasks, or create/search notes.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Action: 'add_event', 'today', 'tomorrow', 'week', 'delete_event', 'todo_add', 'todo_list', 'todo_complete', 'todo_delete', 'note_create', 'note_search', 'note_list'"},
            "summary": {"type": "STRING", "description": "Event title or note title"},
            "start_datetime": {"type": "STRING", "description": "Start time format: 'YYYY-MM-DD HH:MM'"},
            "end_datetime": {"type": "STRING", "description": "End time format: 'YYYY-MM-DD HH:MM'"},
            "description": {"type": "STRING", "description": "Event or note description"},
            "location": {"type": "STRING", "description": "Event location"}
        },
        "required": ["action"]
    },
    "handler": "calendar_add_event",
}

# =========================
# PATHS
# =========================
_DATA_DIR = Path(os.path.join(os.path.dirname(__file__), '..', 'data'))
_TODOS_FILE = _DATA_DIR / 'todos.json'
_NOTES_DIR = _DATA_DIR / 'notes'
_CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')
_TOKEN_FILE = os.path.join(os.path.dirname(__file__), '..', 'token.json')

_DATA_DIR.mkdir(exist_ok=True)
_NOTES_DIR.mkdir(exist_ok=True)

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def _load_json(path: str, default=None):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}


def _save_json(path: str, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def _get_calendar_service():
    """Get Google Calendar API service. Returns None if not configured."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        creds = None
        if os.path.exists(_TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(_TOKEN_FILE, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(_CREDENTIALS_FILE):
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(_CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        return build('calendar', 'v3', credentials=creds)
    except Exception:
        return None


# =========================
# GOOGLE CALENDAR TOOLS
# =========================

@function_tool()
async def calendar_add_event(
    summary: str,
    start_datetime: str,
    end_datetime: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
) -> str:
    """
    Add an event to Google Calendar.

    Args:
        summary: Event title
        start_datetime: Start time format: 'YYYY-MM-DD HH:MM' (e.g. '2025-01-15 14:00')
        end_datetime: End time format: 'YYYY-MM-DD HH:MM' (e.g. '2025-01-15 15:00')
        description: Event description (optional)
        location: Event location (optional)

    Example: calendar_add_event("Team Meeting", "2025-01-15 14:00", "2025-01-15 15:00", "Weekly sync", "Office Room 3")
    """
    try:
        service = _get_calendar_service()
        if not service:
            return "Google Calendar not configured. Place credentials.json in project root and run auth flow."

        start_dt = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(end_datetime, "%Y-%m-%d %H:%M")

        event_body = {
            'summary': summary,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
        }
        if description:
            event_body['description'] = description
        if location:
            event_body['location'] = location

        event = service.events().insert(calendarId='primary', body=event_body).execute()
        return (
            f"Event created!\n"
            f"Title: {summary}\n"
            f"Start: {start_datetime}\n"
            f"End: {end_datetime}\n"
            f"Link: {event.get('htmlLink', 'N/A')}"
        )
    except Exception as e:
        return f"Failed to create event: {str(e)}"


@function_tool()
async def calendar_today() -> str:
    """List today's Google Calendar events."""
    try:
        service = _get_calendar_service()
        if not service:
            return "Google Calendar not configured."

        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end_of_day = now.replace(hour=23, minute=59, second=59).isoformat()

        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy='startTime',
        ).execute()

        events = events_result.get('items', [])
        if not events:
            return "No events scheduled for today."

        lines = [f"Today's Events ({now.strftime('%d %B %Y')}):"]
        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            time_str = datetime.fromisoformat(start).strftime('%I:%M %p') if 'T' in start else 'All day'
            lines.append(f"  {i}. {time_str} — {event.get('summary', 'Untitled')}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"


@function_tool()
async def calendar_tomorrow() -> str:
    """List tomorrow's Google Calendar events."""
    try:
        service = _get_calendar_service()
        if not service:
            return "Google Calendar not configured."

        tomorrow = datetime.now() + timedelta(days=1)
        start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end = tomorrow.replace(hour=23, minute=59, second=59).isoformat()

        events_result = service.events().list(
            calendarId='primary',
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy='startTime',
        ).execute()

        events = events_result.get('items', [])
        if not events:
            return "No events scheduled for tomorrow."

        lines = [f"Tomorrow's Events ({tomorrow.strftime('%d %B %Y')}):"]
        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            time_str = datetime.fromisoformat(start).strftime('%I:%M %p') if 'T' in start else 'All day'
            lines.append(f"  {i}. {time_str} — {event.get('summary', 'Untitled')}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"


@function_tool()
async def calendar_week() -> str:
    """Show this week's Google Calendar events (Monday to Sunday)."""
    try:
        service = _get_calendar_service()
        if not service:
            return "Google Calendar not configured."

        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)

        start = monday.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end = sunday.replace(hour=23, minute=59, second=59).isoformat()

        events_result = service.events().list(
            calendarId='primary',
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy='startTime',
        ).execute()

        events = events_result.get('items', [])
        if not events:
            return "No events this week."

        lines = [f"Weekly Schedule ({monday.strftime('%d %b')} - {sunday.strftime('%d %b %Y')}):"]
        current_day = ""
        for event in events:
            start_str = event['start'].get('dateTime', event['start'].get('date'))
            dt = datetime.fromisoformat(start_str)
            day_name = dt.strftime('%A, %d %B')

            if day_name != current_day:
                current_day = day_name
                lines.append(f"\n  {day_name}:")

            time_str = dt.strftime('%I:%M %p') if 'T' in start_str else 'All day'
            lines.append(f"    {time_str} — {event.get('summary', 'Untitled')}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"


@function_tool()
async def calendar_delete_event(event_summary: str) -> str:
    """
    Delete a Google Calendar event by its title (fuzzy match).

    Args:
        event_summary: The event title to search and delete
    """
    try:
        service = _get_calendar_service()
        if not service:
            return "Google Calendar not configured."

        now = datetime.now()
        time_min = (now - timedelta(days=30)).isoformat() + 'Z'
        time_max = (now + timedelta(days=90)).isoformat() + 'Z'

        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            q=event_summary,
        ).execute()

        events = events_result.get('items', [])
        if not events:
            return f"No events matching '{event_summary}' found."

        deleted = []
        for event in events:
            summary = event.get('summary', 'Untitled')
            service.events().delete(calendarId='primary', eventId=event['id']).execute()
            deleted.append(summary)

        return f"Deleted {len(deleted)} event(s):\n" + "\n".join(f"  - {s}" for s in deleted)
    except Exception as e:
        return f"Error: {str(e)}"


# =========================
# TODO TOOLS (JSON-backed)
# =========================

def _load_todos():
    return _load_json(str(_TODOS_FILE), {"tasks": []})


def _save_todos(data):
    _save_json(str(_TODOS_FILE), data)


@function_tool()
async def task_add(
    task: str,
    priority: str = "medium",
    due_date: Optional[str] = None,
) -> str:
    """
    Add a task to the task list with priority and due date.

    Args:
        task: Task description
        priority: 'low', 'medium', or 'high' (default: 'medium')
        due_date: Due date format: 'YYYY-MM-DD' (optional)

    Example: task_add("Buy groceries", "high", "2025-01-15")
    """
    data = _load_todos()
    task_id = str(uuid.uuid4())[:8]

    new_task = {
        "id": task_id,
        "task": task,
        "priority": priority.lower(),
        "due_date": due_date,
        "completed": False,
        "created_at": datetime.now().isoformat(),
    }
    data["tasks"].append(new_task)
    _save_todos(data)

    due_str = f", Due: {due_date}" if due_date else ""
    return f"Task added! [ID: {task_id}]\n  \"{task}\" (Priority: {priority}{due_str})"


@function_tool()
async def task_list(show_completed: bool = False) -> str:
    """
    List all tasks in the task list.

    Args:
        show_completed: If True, also show completed tasks (default: False)
    """
    data = _load_todos()
    tasks = data.get("tasks", [])

    if not tasks:
        return "Todo list is empty."

    if not show_completed:
        tasks = [t for t in tasks if not t.get("completed", False)]

    if not tasks:
        return "All tasks completed!"

    lines = ["Todo List:"]
    for t in tasks:
        status = "[x]" if t.get("completed") else "[ ]"
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(t.get("priority", "medium"), "⚪")
        due = f" (Due: {t['due_date']})" if t.get("due_date") else ""
        lines.append(f"  {status} {priority_icon} {t['id']} — {t['task']}{due}")

    return "\n".join(lines)


@function_tool()
async def task_complete(task_id: str) -> str:
    """
    Mark a task as completed.

    Args:
        task_id: The task ID (from task_list)
    """
    data = _load_todos()
    for task in data.get("tasks", []):
        if task.get("id") == task_id:
            task["completed"] = True
            task["completed_at"] = datetime.now().isoformat()
            _save_todos(data)
            return f"Task completed: \"{task['task']}\""
    return f"Task with ID '{task_id}' not found."


@function_tool()
async def task_delete(task_id: str) -> str:
    """
    Delete a task from the task list.

    Args:
        task_id: The task ID (from task_list)
    """
    data = _load_todos()
    tasks = data.get("tasks", [])
    for i, task in enumerate(tasks):
        if task.get("id") == task_id:
            removed = tasks.pop(i)
            _save_todos(data)
            return f"Deleted: \"{removed['task']}\""
    return f"Task with ID '{task_id}' not found."


# =========================
# NOTES TOOLS
# =========================

@function_tool()
async def note_create(
    title: str,
    content: str,
    tags: Optional[str] = None,
) -> str:
    """
    Create a new note file.

    Args:
        title: Note title (used as filename)
        content: Note content/body
        tags: Comma-separated tags (optional, e.g. "python,study,api")

    Example: note_create("Python Decorators", "Decorators wrap functions...", "python,study")
    """
    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in title)
    safe_title = safe_title.strip().replace(' ', '_')
    filename = f"{safe_title}.md"
    filepath = _NOTES_DIR / filename

    note_data = {
        "title": title,
        "tags": [t.strip() for t in tags.split(',')] if tags else [],
        "created_at": datetime.now().isoformat(),
        "content": content,
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(note_data, f, indent=2, ensure_ascii=False)

    tag_str = f" | Tags: {tags}" if tags else ""
    return f"Note saved: {filename}{tag_str}"


@function_tool()
async def note_search(query: str) -> str:
    """
    Search notes by keyword in title, content, or tags.

    Args:
        query: Search term to find in notes
    """
    results = []
    query_lower = query.lower()

    for note_file in _NOTES_DIR.glob('*.md'):
        try:
            with open(note_file, 'r', encoding='utf-8') as f:
                note = json.load(f)

            searchable = f"{note.get('title', '')} {note.get('content', '')} {' '.join(note.get('tags', []))}".lower()
            if query_lower in searchable:
                results.append(note)
        except Exception:
            continue

    if not results:
        return f"No notes found matching '{query}'."

    lines = [f"Found {len(results)} note(s) matching '{query}':"]
    for note in results:
        tags = f" [{', '.join(note.get('tags', []))}]" if note.get('tags') else ""
        preview = note.get('content', '')[:100]
        lines.append(f"\n  {note.get('title', 'Untitled')}{tags}")
        lines.append(f"    {preview}...")

    return "\n".join(lines)


@function_tool()
async def note_list() -> str:
    """List all saved notes."""
    note_files = list(_NOTES_DIR.glob('*.md'))

    if not note_files:
        return "No notes saved yet."

    lines = ["Saved Notes:"]
    for note_file in sorted(note_files):
        try:
            with open(note_file, 'r', encoding='utf-8') as f:
                note = json.load(f)
            tags = f" [{', '.join(note.get('tags', []))}]" if note.get('tags') else ""
            created = note.get('created_at', '')[:10]
            lines.append(f"  {note_file.stem}{tags} — Created: {created}")
        except Exception:
            lines.append(f"  {note_file.stem} (unreadable)")

    return "\n".join(lines)


# =========================
# AUTH HELPER (run once)
# =========================
if __name__ == "__main__":
    print("Running Google Calendar auth flow...")
    service = _get_calendar_service()
    if service:
        print("Auth successful! token.json saved.")
        events = service.events().list(
            calendarId='primary', maxResults=5,
            singleEvents=True, orderBy='startTime'
        ).execute()
        for e in events.get('items', []):
            print(f"  {e['start'].get('dateTime', e['start'].get('date'))} - {e.get('summary')
}")
    else:
        print("Auth failed. Place credentials.json in project root first.")

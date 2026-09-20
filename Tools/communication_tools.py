"""
ZENITH Communication Tools
Provides: discord_send, meeting_link, auto_reply_email, bulk_email, email_reminder, call_log
"""

import os
import json
import uuid
import asyncio
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

import aiohttp
from livekit.agents import function_tool

TOOL = {
    "name": "communication_tools",
    "description": "Send Discord messages, generate meeting links, manage emails, and log calls. Use when the user wants to communicate via Discord, create video meeting links, or manage email operations.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Action: 'discord_send', 'meeting_link', 'email_reminder', 'call_log'"},
            "message": {"type": "STRING", "description": "Message text to send"},
            "platform": {"type": "STRING", "description": "Meeting platform: 'meet', 'zoom', 'teams'"},
            "to": {"type": "STRING", "description": "Recipient email address"},
            "subject": {"type": "STRING", "description": "Email subject"},
            "body": {"type": "STRING", "description": "Email body text"}
        },
        "required": ["action"]
    },
    "handler": "discord_send",
}

# =========================
# PATHS
# =========================
_DATA_DIR = Path(os.path.join(os.path.dirname(__file__), '..', 'data'))
_CALL_LOG_FILE = _DATA_DIR / 'call_log.json'
_DATA_DIR.mkdir(exist_ok=True)


def _load_json(path, default=None):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}


def _save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def _get_email_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'email_config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {
        "smtp_server": os.environ.get("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.environ.get("SMTP_PORT", "587")),
        "imap_server": os.environ.get("IMAP_SERVER", "imap.gmail.com"),
        "email": os.environ.get("ZENITH_EMAIL", os.environ.get("GMAIL_USER", "")),
        "password": os.environ.get("ZENITH_EMAIL_PASSWORD", os.environ.get("GMAIL_PASSWORD", "")),
    }


# =========================
# DISCORD
# =========================

@function_tool()
async def discord_send(
    message: str,
    webhook_url: Optional[str] = None,
) -> str:
    """
    Send a message to a Discord channel via webhook.

    Args:
        message: Message text to send
        webhook_url: Discord webhook URL (optional, uses DISCORD_WEBHOOK_URL from .env)

    Example: discord_send("Hello from ZENITH!")
    """
    url = webhook_url or os.environ.get("DISCORD_WEBHOOK_URL", "")
    if not url:
        return "Discord webhook not configured. Set DISCORD_WEBHOOK_URL in .env"

    try:
        async with aiohttp.ClientSession() as session:
            payload = {"content": message}
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status in (200, 204):
                    return f"Message sent to Discord!"
                else:
                    body = await resp.text()
                    return f"Discord error (HTTP {resp.status}): {body[:200]}"
    except Exception as e:
        return f"Discord send failed: {str(e)}"


# =========================
# MEETING LINK
# =========================

@function_tool()
async def meeting_link(platform: str = "meet") -> str:
    """
    Generate a video meeting link.

    Args:
        platform: 'meet' for Google Meet, 'zoom' for Zoom (default: 'meet')

    Example: meeting_link("meet")
    """
    import uuid as _uuid
    import hashlib

    if platform.lower() == "zoom":
        meeting_id = ''.join([str(hash(str(_uuid.uuid4())) % 10) for _ in range(11)])
        return (
            f"Zoom Meeting:\n"
            f"  Meeting ID: {meeting_id}\n"
            f"  Join URL: https://zoom.us/j/{meeting_id}\n"
            f"  Note: Create live link at zoom.us → New Meeting"
        )
    else:
        code = hashlib.md5(str(_uuid.uuid4()).encode()).hexdigest()[:10]
        return (
            f"Google Meet:\n"
            f"  Join URL: https://meet.google.com/{code[:3]}-{code[3:7]}-{code[7:]}\n"
            f"  Note: For a persistent link, create via calendar.google.com"
        )


# =========================
# AUTO REPLY EMAIL
# =========================

@function_tool()
async def auto_reply_email(
    tone: str = "professional",
    count: int = 1,
) -> str:
    """
    AI-draft a reply to the latest unread email. Returns draft for review.

    Args:
        tone: Reply tone - 'professional', 'casual', 'formal', 'friendly' (default: 'professional')
        count: Number of recent emails to consider (default: 1)

    Example: auto_reply_email("professional")
    """
    config = _get_email_config()
    if not config["email"] or not config["password"]:
        return "Email not configured. Set GMAIL_USER and GMAIL_PASSWORD in .env"

    try:
        mail = imaplib.IMAP4_SSL(config["imap_server"])
        mail.login(config["email"], config["password"])
        mail.select("INBOX")

        _, data = mail.search(None, "UNSEEN")
        mail_ids = data[0].split()

        if not mail_ids:
            mail.logout()
            return "No unread emails found."

        recent_ids = mail_ids[-count:]
        drafts = []

        for mid in reversed(recent_ids):
            _, msg_data = mail.fetch(mid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            subject = msg["Subject"] or "(no subject)"
            decoded = decode_header(subject)
            subject_text = ""
            for part, enc in decoded:
                if isinstance(part, bytes):
                    subject_text += part.decode(enc or 'utf-8', errors='replace')
                else:
                    subject_text += part

            from_addr = msg["From"]
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors='replace')
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors='replace')

            drafts.append(
                f"From: {from_addr}\n"
                f"Subject: {subject_text}\n"
                f"Preview: {body[:200]}...\n"
                f"---\n"
                f"Suggested {tone} reply:\n"
                f"Thank you for your email regarding \"{subject_text}\". "
                f"I have reviewed your message and will get back to you shortly "
                f"with a detailed response.\n\nBest regards"
            )

        mail.logout()
        return f"Draft replies ({tone}):\n\n" + "\n\n".join(drafts)
    except Exception as e:
        return f"Error: {str(e)}"


# =========================
# BULK EMAIL
# =========================

@function_tool()
async def bulk_email(
    recipients: str,
    subject: str,
    body: str,
) -> str:
    """
    Send the same email to multiple recipients.

    Args:
        recipients: Comma-separated email addresses (e.g. "a@test.com,b@test.com")
        subject: Email subject line
        body: Email body content

    Example: bulk_email("a@test.com,b@test.com", "Meeting Update", "Meeting rescheduled to 3 PM.")
    """
    config = _get_email_config()
    if not config["email"] or not config["password"]:
        return "Email not configured."

    recipient_list = [r.strip() for r in recipients.split(',') if r.strip()]
    if not recipient_list:
        return "No valid recipients provided."

    success = []
    failed = []

    try:
        server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
        server.starttls()
        server.login(config["email"], config["password"])

        for to_email in recipient_list:
            try:
                msg = MIMEMultipart()
                msg['From'] = config["email"]
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                server.send_message(msg)
                success.append(to_email)
            except Exception as e:
                failed.append(f"{to_email}: {str(e)}")

        server.quit()

        result = f"Sent: {len(success)}/{len(recipient_list)}"
        if failed:
            result += f"\nFailed: {', '.join(failed)}"
        return result
    except Exception as e:
        return f"Bulk email error: {str(e)}"


# =========================
# EMAIL REMINDER (schedule delayed send)
# =========================

@function_tool()
async def email_reminder(
    to: str,
    subject: str,
    body: str,
    send_at: str,
) -> str:
    """
    Schedule an email to be sent later (stored for processing).

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body
        send_at: When to send format: 'YYYY-MM-DD HH:MM' (e.g. '2025-01-15 09:00')

    Example: email_reminder("boss@company.com", "Report", "Attached report", "2025-01-16 09:00")
    """
    try:
        send_time = datetime.strptime(send_at, "%Y-%m-%d %H:%M")
    except ValueError:
        return "Invalid date format. Use: YYYY-MM-DD HH:MM"

    scheduled_file = _DATA_DIR / 'scheduled_emails.json'
    scheduled = _load_json(str(scheduled_file), [])

    entry = {
        "id": str(uuid.uuid4())[:8],
        "to": to,
        "subject": subject,
        "body": body,
        "send_at": send_at,
        "created_at": datetime.now().isoformat(),
        "status": "pending",
    }
    scheduled.append(entry)
    _save_json(str(scheduled_file), scheduled)

    return (
        f"Email scheduled!\n"
        f"  To: {to}\n"
        f"  Subject: {subject}\n"
        f"  Send at: {send_at}\n"
        f"  ID: {entry['id']}\n"
        f"Note: Use a cron job or scheduler to process pending emails."
    )


# =========================
# CALL LOG
# =========================

@function_tool()
async def call_log(
    contact: str,
    duration: str = "unknown",
    notes: Optional[str] = None,
    call_type: str = "outgoing",
) -> str:
    """
    Log a phone call with details.

    Args:
        contact: Contact name or number
        duration: Call duration (e.g. '5m 30s', '2 min', 'unknown')
        notes: Additional notes about the call (optional)
        call_type: 'incoming', 'outgoing', or 'missed' (default: 'outgoing')

    Example: call_log("John", "5m 30s", "Discussed project deadline", "outgoing")
    """
    data = _load_json(str(_CALL_LOG_FILE), {"calls": []})

    entry = {
        "id": str(uuid.uuid4())[:8],
        "contact": contact,
        "duration": duration,
        "notes": notes or "",
        "call_type": call_type,
        "timestamp": datetime.now().isoformat(),
    }
    data["calls"].append(entry)
    _save_json(str(_CALL_LOG_FILE), data)

    return (
        f"Call logged!\n"
        f"  Contact: {contact}\n"
        f"  Type: {call_type}\n"
        f"  Duration: {duration}\n"
        f"  Time: {entry['timestamp'][:16]
}"
    )

"""
ZENITH Email Tool (Gmail SMTP)
Provides: send_email, read_email, search_email
"""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import os
import json
from typing import Optional
from livekit.agents import function_tool

TOOL = {
    "name": "email_tool",
    "description": "Send, read, and search emails via Gmail SMTP. Use when the user wants to send an email, check their inbox, or search for specific emails.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Action: 'send', 'read', 'search'"},
            "to": {"type": "STRING", "description": "Recipient email address (for send)"},
            "subject": {"type": "STRING", "description": "Email subject (for send)"},
            "body": {"type": "STRING", "description": "Email body text (for send)"},
            "count": {"type": "INTEGER", "description": "Number of emails to read (default: 5)"},
            "query": {"type": "STRING", "description": "Search query for email search"}
        },
        "required": ["action"]
    },
    "handler": "send_email",
}


def _load_email_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'email_config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {
        "smtp_server": os.environ.get("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.environ.get("SMTP_PORT", "587")),
        "imap_server": os.environ.get("IMAP_SERVER", "imap.gmail.com"),
        "email": os.environ.get("ZENITH_EMAIL", ""),
        "password": os.environ.get("ZENITH_EMAIL_PASSWORD", ""),
    }


@function_tool()
async def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail SMTP. Configure email_config.json first."""
    config = _load_email_config()
    if not config["email"] or not config["password"]:
        return "Email not configured. Create email_config.json with email and password fields."

    try:
        msg = MIMEMultipart()
        msg['From'] = config["email"]
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
        server.starttls()
        server.login(config["email"], config["password"])
        server.send_message(msg)
        server.quit()
        return f"Email sent to {to}"
    except smtplib.SMTPAuthenticationError:
        return "Auth failed. Use Gmail App Password."
    except Exception as e:
        return f"Error: {str(e)}"


@function_tool()
async def read_email(count: int = 5) -> str:
    """Read latest emails from inbox."""
    config = _load_email_config()
    if not config["email"] or not config["password"]:
        return "Email not configured."

    try:
        mail = imaplib.IMAP4_SSL(config["imap_server"])
        mail.login(config["email"], config["password"])
        mail.select("INBOX")

        _, data = mail.search(None, "ALL")
        mail_ids = data[0].split()

        if not mail_ids:
            return "No emails found."

        recent_ids = mail_ids[-count:]
        results = []

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

            results.append(f"From: {msg['From']}\nSubject: {subject_text}\nDate: {msg['Date']}\n")

        mail.logout()
        return f"Latest {len(results)} emails:\n\n" + "\n---\n".join(results)
    except Exception as e:
        return f"Error: {str(e)}"


@function_tool()
async def search_email(query: str, count: int = 5) -> str:
    """Search emails by subject or sender."""
    config = _load_email_config()
    if not config["email"] or not config["password"]:
        return "Email not configured."

    try:
        mail = imaplib.IMAP4_SSL(config["imap_server"])
        mail.login(config["email"], config["password"])
        mail.select("INBOX")

        _, data = mail.search(None, f'(OR SUBJECT "{query}" FROM "{query}")')
        mail_ids = data[0].split()

        if not mail_ids:
            return f"No emails matching '{query}'."

        recent_ids = mail_ids[-count:]
        results = []
        for mid in reversed(recent_ids):
            _, msg_data = mail.fetch(mid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            results.append(f"From: {msg['From']} | Subject: {msg['Subject']} | Date: {msg['Date']}")

        mail.logout()
        return f"Found {len(results)} emails:\n" + "\n".join(results)
    except Exception as e:
        return f"Error: {str(e)
}"

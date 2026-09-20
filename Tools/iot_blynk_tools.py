"""
ZENITH IoT Blynk Tools (ESP8266/ESP32)
Provides: blynk_write, blynk_read, blynk_device_status, blynk_notify, blynk_email_trigger

Blynk HTTP API Documentation:
- Write: https://{server}/external/api/update?token={token}&V0={value}
- Read:  https://{server}/external/api/get?token={token}&V0
- Notify: https://{server}/external/api/notify?token={token}&type=push&body={msg}
- Email: https://{server}/external/api/email?token={token}&to={email}&subject={sub}&body={body}
"""

import os
import json
from typing import Optional
from livekit.agents import function_tool

import aiohttp

TOOL = {
    "name": "iot_blynk_tools",
    "description": "Control IoT devices via Blynk platform. Write/read virtual pins, check device status, and send notifications. Use when the user wants to interact with ESP8266/ESP32 IoT devices through Blynk.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Action: 'write', 'read', 'status', 'notify', 'email'"},
            "pin": {"type": "STRING", "description": "Virtual pin name (e.g. 'V0', 'V1')"},
            "value": {"type": "STRING", "description": "Value to write to the pin"},
            "token": {"type": "STRING", "description": "Blynk auth token (optional, uses .env)"},
            "server": {"type": "STRING", "description": "Blynk server (optional, default: blynk.cloud)"}
        },
        "required": ["action", "pin"]
    },
    "handler": "blynk_write",
}


def _get_blynk_config():
    return {
        "token": os.environ.get("BLYNK_AUTH_TOKEN", ""),
        "server": os.environ.get("BLYNK_SERVER", "blynk.cloud"),
    }


@function_tool()
async def blynk_write(
    pin: str,
    value: str,
    token: Optional[str] = None,
    server: Optional[str] = None,
) -> str:
    """
    Write a value to a Blynk virtual pin (controls your ESP8266/ESP32 device).

    Args:
        pin: Virtual pin name (e.g. 'V0', 'V1', 'V10')
        value: Value to send (e.g. '1', '0', '255', 'hello')
        token: Blynk auth token (optional, uses .env BLYNK_AUTH_TOKEN)
        server: Blynk server (optional, uses .env BLYNK_SERVER, default: blynk.cloud)

    Example: blynk_write("V0", "1")  -- turns ON device on V0
    Example: blynk_write("V1", "150")  -- sets slider value
    """
    config = _get_blynk_config()
    auth_token = token or config["token"]
    blynk_server = server or config["server"]

    if not auth_token:
        return "Blynk not configured. Set BLYNK_AUTH_TOKEN in .env"

    try:
        url = f"https://{blynk_server}/external/api/update"
        params = {"token": auth_token, pin: value}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return f"Written to {pin}: {value}"
                else:
                    body = await resp.text()
                    return f"Blynk write failed (HTTP {resp.status}): {body[:200]}"
    except asyncio.TimeoutError:
        return f"Timeout connecting to Blynk server: {blynk_server}"
    except Exception as e:
        return f"Blynk write error: {str(e)}"


@function_tool()
async def blynk_read(
    pin: str,
    token: Optional[str] = None,
    server: Optional[str] = None,
) -> str:
    """
    Read the current value of a Blynk virtual pin (gets data from your ESP8266/ESP32).

    Args:
        pin: Virtual pin name (e.g. 'V0', 'V1', 'V10')
        token: Blynk auth token (optional, uses .env)
        server: Blynk server (optional, uses .env, default: blynk.cloud)

    Example: blynk_read("V0")  -- reads sensor value from V0
    """
    config = _get_blynk_config()
    auth_token = token or config["token"]
    blynk_server = server or config["server"]

    if not auth_token:
        return "Blynk not configured. Set BLYNK_AUTH_TOKEN in .env"

    try:
        url = f"https://{blynk_server}/external/api/get"
        params = {"token": auth_token, "pin": pin}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    body = await resp.text()
                    try:
                        data = json.loads(body)
                        if isinstance(data, list) and len(data) > 0:
                            return f"{pin} = {data[0]}"
                        return f"{pin} = {data}"
                    except json.JSONDecodeError:
                        return f"{pin} = {body}"
                else:
                    body = await resp.text()
                    return f"Blynk read failed (HTTP {resp.status}): {body[:200]}"
    except asyncio.TimeoutError:
        return f"Timeout connecting to Blynk server: {blynk_server}"
    except Exception as e:
        return f"Blynk read error: {str(e)}"


@function_tool()
async def blynk_device_status(
    token: Optional[str] = None,
    server: Optional[str] = None,
) -> str:
    """
    Check if your Blynk device is online or offline.

    Args:
        token: Blynk auth token (optional, uses .env)
        server: Blynk server (optional, uses .env)

    Example: blynk_device_status()
    """
    config = _get_blynk_config()
    auth_token = token or config["token"]
    blynk_server = server or config["server"]

    if not auth_token:
        return "Blynk not configured. Set BLYNK_AUTH_TOKEN in .env"

    try:
        url = f"https://{blynk_server}/external/api/isHardwareConnected"
        params = {"token": auth_token}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                body = await resp.text()
                is_connected = body.strip().lower() in ('true', '1', '"true"')

                status_icon = "ONLINE" if is_connected else "OFFLINE"
                return f"Device Status: {status_icon}\nServer: {blynk_server}"
    except asyncio.TimeoutError:
        return f"Timeout connecting to Blynk server: {blynk_server}"
    except Exception as e:
        return f"Blynk status error: {str(e)}"


@function_tool()
async def blynk_notify(
    message: str,
    token: Optional[str] = None,
    server: Optional[str] = None,
) -> str:
    """
    Send a push notification to the Blynk mobile app.

    Args:
        message: Notification message text
        token: Blynk auth token (optional, uses .env)
        server: Blynk server (optional, uses .env)

    Example: blynk_notify("Temperature too high!")
    """
    config = _get_blynk_config()
    auth_token = token or config["token"]
    blynk_server = server or config["server"]

    if not auth_token:
        return "Blynk not configured. Set BLYNK_AUTH_TOKEN in .env"

    try:
        url = f"https://{blynk_server}/external/api/notify"
        params = {
            "token": auth_token,
            "type": "push",
            "body": message,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return f"Notification sent: \"{message}\""
                else:
                    body = await resp.text()
                    return f"Notification failed (HTTP {resp.status}): {body[:200]}"
    except asyncio.TimeoutError:
        return f"Timeout connecting to Blynk server"
    except Exception as e:
        return f"Blynk notify error: {str(e)}"


@function_tool()
async def blynk_email_trigger(
    email: str,
    subject: str,
    body: str,
    token: Optional[str] = None,
    server: Optional[str] = None,
) -> str:
    """
    Send an email via Blynk cloud (triggered from device).

    Args:
        email: Recipient email address
        subject: Email subject
        body: Email body text
        token: Blynk auth token (optional, uses .env)
        server: Blynk server (optional, uses .env)

    Example: blynk_email_trigger("user@example.com", "Alert", "Sensor threshold exceeded!")
    """
    config = _get_blynk_config()
    auth_token = token or config["token"]
    blynk_server = server or config["server"]

    if not auth_token:
        return "Blynk not configured. Set BLYNK_AUTH_TOKEN in .env"

    try:
        url = f"https://{blynk_server}/external/api/email"
        params = {
            "token": auth_token,
            "to": email,
            "subject": subject,
            "body": body,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return f"Email sent via Blynk!\n  To: {email}\n  Subject: {subject}"
                else:
                    resp_body = await resp.text()
                    return f"Email failed (HTTP {resp.status}): {resp_body[:200]}"
    except asyncio.TimeoutError:
        return f"Timeout connecting to Blynk server"
    except Exception as e:
        return f"Blynk email error: {str(e)
}"

"""
ZENITH QR Code Generator Tool
Provides: generate_qr
"""

import os
from typing import Optional
from livekit.agents import function_tool

TOOL = {
    "name": "qr_generator",
    "description": "Generate QR codes from text or URLs. Use when the user wants to create a QR code for sharing links, text, or contact information.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "data": {"type": "STRING", "description": "Text or URL to encode in the QR code"},
            "output_path": {"type": "STRING", "description": "Output file path (optional, uses default if empty)"}
        },
        "required": ["data"]
    },
    "handler": "generate_qr",
}


@function_tool()
async def generate_qr(data: str, output_path: str = "") -> str:
    """Generate a QR code from text or URL."""
    try:
        import qrcode
    except ImportError:
        return "QR library not installed. Run: pip install qrcode[pil]"

    try:
        if not output_path:
            output_path = os.path.join(os.path.dirname(__file__), '..', 'zenith_qr.png')

        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#00d4ff", back_color="#0a0a0f")
        img.save(output_path)

        return f"QR Code generated for '{data[:50]}' -> {output_path}"
    except Exception as e:
        return f"Error: {str(e)
}"

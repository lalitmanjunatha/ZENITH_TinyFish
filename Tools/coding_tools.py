"""
ZENITH Coding Tools - Code Formatter, Regex Tester, JSON Validator, Encoders, etc.
"""
import os
import re
import json
import hashlib
import base64
import uuid
import random
import string
from urllib.parse import quote, unquote
from typing import Optional
from livekit.agents import function_tool

TOOL = {
    "name": "coding_tools",
    "description": "Collection of coding utility tools: format code, test regex, validate JSON, encode/decode Base64/URL, generate UUIDs/hashes, preview HTML. Use when the user needs any coding-related utility operation.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Tool to use: 'code_format', 'regex_test', 'json_validate', 'json_format', 'html_preview', 'base64_encode', 'base64_decode', 'url_encode', 'url_decode', 'uuid_generate', 'hash_generate'"},
            "input_text": {"type": "STRING", "description": "Input text, code, or data to process"},
            "language": {"type": "STRING", "description": "Programming language for code formatting (default: python)"},
            "pattern": {"type": "STRING", "description": "Regex pattern for regex testing"},
            "hash_type": {"type": "STRING", "description": "Hash algorithm: 'md5', 'sha256', etc."}
        },
        "required": ["action"]
    },
    "handler": "code_format",
}


# ==================== CODE FORMATTER ====================
@function_tool()
async def code_format(code: str, language: str = "python") -> str:
    """Format/beautify code. language: python, javascript, html, css."""
    try:
        if language == "python":
            lines = code.split('\n')
            formatted = []
            indent = 0
            for line in lines:
                stripped = line.strip()
                if stripped.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ')):
                    if stripped.startswith(('except', 'finally', 'else:', 'elif ')):
                        indent = max(0, indent - 1)
                    formatted.append('    ' * indent + stripped)
                    if not stripped.endswith(':'):
                        continue
                    indent += 1
                elif stripped.startswith(('return ', 'break', 'continue', 'pass')):
                    formatted.append('    ' * indent + stripped)
                else:
                    if stripped.startswith(('}')) or stripped.startswith((']', ')')):
                        indent = max(0, indent - 1)
                    formatted.append('    ' * indent + stripped)
                    if stripped.endswith(('{', '[', '(')):
                        indent += 1
            return '\n'.join(formatted)
        else:
            return code
    except Exception as e:
        return f"Format error: {str(e)}"


# ==================== REGEX TESTER ====================
@function_tool()
async def regex_test(pattern: str, text: str) -> str:
    """Test a regular expression against text."""
    try:
        matches = re.findall(pattern, text)
        if matches:
            return f"Pattern: {pattern}\nMatches ({len(matches)}):\n" + "\n".join(f"  - {m}" for m in matches[:20])
        return f"Pattern: {pattern}\nNo matches found."
    except re.error as e:
        return f"Invalid regex: {str(e)}"


# ==================== JSON VALIDATOR ====================
@function_tool()
async def json_validate(text: str) -> str:
    """Validate and format JSON."""
    try:
        data = json.loads(text)
        formatted = json.dumps(data, indent=2)
        if isinstance(data, dict):
            return f"Valid JSON Object\nKeys: {len(data)}\n{formatted}"
        elif isinstance(data, list):
            return f"Valid JSON Array\nItems: {len(data)}\n{formatted}"
        return f"Valid JSON\n{formatted}"
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {str(e)}"


# ==================== JSON FORMATTER ====================
@function_tool()
async def json_format(text: str, indent: int = 2) -> str:
    """Format/beautify JSON text."""
    try:
        data = json.loads(text)
        return json.dumps(data, indent=indent)
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {str(e)}"


# ==================== HTML PREVIEW ====================
@function_tool()
async def html_preview(html: str) -> str:
    """Show HTML preview description (text-based)."""
    import re
    tags = re.findall(r'<(\w+)', html)
    classes = re.findall(r'class="([^"]*)"', html)
    texts = re.findall(r'>([^<]+)<', html)

    output = "HTML PREVIEW:\n\n"
    output += f"Tags: {', '.join(set(tags))}\n"
    if classes:
        output += f"Classes: {', '.join(set(classes))}\n"
    if texts:
        output += f"Text content:\n"
        for t in texts[:10]:
            t = t.strip()
            if t:
                output += f"  - {t}\n"
    output += f"\nTotal elements: {len(tags)}"
    return output


# ==================== BASE64 ENCODE/DECODE ====================
@function_tool()
async def base64_encode(text: str) -> str:
    """Encode text to Base64."""
    encoded = base64.b64encode(text.encode()).decode()
    return f"Base64: {encoded}"

@function_tool()
async def base64_decode(encoded: str) -> str:
    """Decode Base64 to text."""
    try:
        decoded = base64.b64decode(encoded).decode()
        return f"Decoded: {decoded}"
    except Exception as e:
        return f"Invalid Base64: {str(e)}"


# ==================== URL ENCODE/DECODE ====================
@function_tool()
async def url_encode(text: str) -> str:
    """URL-encode text."""
    return f"URL Encoded: {quote(text)}"

@function_tool()
async def url_decode(text: str) -> str:
    """URL-decode text."""
    return f"URL Decoded: {unquote(text)}"


# ==================== HASH GENERATOR ====================
@function_tool()
async def hash_generate(text: str) -> str:
    """Generate MD5 and SHA256 hashes of text."""
    md5 = hashlib.md5(text.encode()).hexdigest()
    sha256 = hashlib.sha256(text.encode()).hexdigest()
    sha1 = hashlib.sha1(text.encode()).hexdigest()
    return f"MD5:    {md5}\nSHA1:   {sha1}\nSHA256: {sha256}"


# ==================== UUID GENERATOR ====================
@function_tool()
async def uuid_generate(count: int = 1) -> str:
    """Generate UUID v4 identifiers."""
    uuids = [str(uuid.uuid4()) for _ in range(min(count, 10))]
    return "UUIDs:\n" + "\n".join(f"  {u}" for u in uuids)


# ==================== COLOR CODE CONVERTER ====================
@function_tool()
async def color_convert(hex_color: str) -> str:
    """Convert hex color to RGB and HSL."""
    try:
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

        # RGB to HSL
        r_, g_, b_ = r/255, g/255, b/255
        max_c = max(r_, g_, b_)
        min_c = min(r_, g_, b_)
        l = (max_c + min_c) / 2

        if max_c == min_c:
            h = s = 0
        else:
            d = max_c - min_c
            s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
            if max_c == r_:
                h = (g_ - b_) / d + (6 if g_ < b_ else 0)
            elif max_c == g_:
                h = (b_ - r_) / d + 2
            else:
                h = (r_ - g_) / d + 4
            h /= 6

        return f"HEX: #{hex_color}\nRGB: ({r}, {g}, {b})\nHSL: ({int(h*360)}, {int(s*100)}%, {int(l*100)}%)"
    except Exception as e:
        return f"Invalid hex color: {str(e)}"


# ==================== MARKDOWN PREVIEW ====================
@function_tool()
async def markdown_preview(md: str) -> str:
    """Preview markdown formatting as text."""
    import re
    lines = md.split('\n')
    preview = "MARKDOWN PREVIEW:\n\n"
    for line in lines:
        if line.startswith('### '):
            preview += f"[H3] {line[4:]}\n"
        elif line.startswith('## '):
            preview += f"[H2] {line[3:]}\n"
        elif line.startswith('# '):
            preview += f"[H1] {line[2:]}\n"
        elif line.startswith('- '):
            preview += f"  * {line[2:]}\n"
        elif line.startswith('**') and line.endswith('**'):
            preview += f"[BOLD] {line[2:-2]}\n"
        elif line.startswith('`') and line.endswith('`'):
            preview += f"[CODE] {line[1:-1]}\n"
        else:
            preview += line + '\n'
    return preview


# ==================== LOREM IPSUM GENERATOR ====================
@function_tool()
async def lorem_ipsum(paragraphs: int = 3, words_per: int = 50) -> str:
    """Generate Lorem Ipsum placeholder text."""
    words = "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua".split()
    result = []
    for _ in range(min(paragraphs, 10)):
        para = ' '.join(random.choice(words) for _ in range(words_per))
        result.append(para.capitalize() + '.')
    return '\n\n'.join(result)


# ==================== PASSWORD STRENGTH CHECKER ====================
@function_tool()
async def password_strength(password: str) -> str:
    """Check password strength."""
    score = 0
    checks = []
    if len(password) >= 8:
        score += 1; checks.append("+ Length >= 8")
    if len(password) >= 12:
        score += 1; checks.append("+ Length >= 12")
    if any(c.isupper() for c in password):
        score += 1; checks.append("+ Has uppercase")
    if any(c.islower() for c in password):
        score += 1; checks.append("+ Has lowercase")
    if any(c.isdigit() for c in password):
        score += 1; checks.append("+ Has digits")
    if any(c in '!@#$%^&*()_+-=' for c in password):
        score += 1; checks.append("+ Has symbols")

    strength = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong", "Excellent"][min(score, 6)]
    return f"Password Strength: {strength} ({score}/6)\n" + "\n".join(checks)


# ==================== CODE COMPLEXITY ====================
@function_tool()
async def code_analysis(code: str) -> str:
    """Analyze code complexity."""
    lines = code.split('\n')
    total_lines = len(lines)
    blank_lines = sum(1 for l in lines if not l.strip())
    comment_lines = sum(1 for l in lines if l.strip().startswith(('#', '//', '/*', '*')))
    code_lines = total_lines - blank_lines - comment_lines
    functions = len(re.findall(r'def |function |func ', code))
    classes = len(re.findall(r'class ', code))
    imports = len(re.findall(r'import |from |require\(|#include', code))

    return (f"CODE ANALYSIS:\n"
            f"  Total lines: {total_lines}\n"
            f"  Code lines: {code_lines}\n"
            f"  Comments: {comment_lines}\n"
            f"  Blank: {blank_lines}\n"
            f"  Functions: {functions}\n"
            f"  Classes: {classes}\n"
            f"  Imports: {imports}")


# ==================== DIFF VIEWER ====================
@function_tool()
async def diff_view(text1: str, text2: str) -> str:
    """Compare two text blocks."""
    lines1 = text1.split('\n')
    lines2 = text2.split('\n')
    diff = []
    max_len = max(len(lines1), len(lines2))

    for i in range(max_len):
        l1 = lines1[i] if i < len(lines1) else None
        l2 = lines2[i] if i < len(lines2) else None
        if l1 != l2:
            if l1 is not None:
                diff.append(f"  - {l1}")
            if l2 is not None:
                diff.append(f"  + {l2}")

    if not diff:
        return "Texts are identical."
    return f"DIFF ({len(diff)
} changes):\n" + "\n".join(diff[:30])

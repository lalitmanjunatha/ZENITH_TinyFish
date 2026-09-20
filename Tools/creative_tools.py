"""
ZENITH Creative Tools - QR Reader, Image Tools, Certificates, Flowcharts, etc.
"""
import os
import math
import json
from typing import Optional
from livekit.agents import function_tool

TOOL = {
    "name": "creative_tools",
    "description": "Creative image and design tools: generate ASCII art, extract color palettes, resize/apply filters to images, create certificates and flowcharts. Use when the user wants to create or manipulate visual content.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Tool: 'ascii_art', 'color_palette', 'image_resize', 'image_filter', 'certificate', 'flowchart'"},
            "text": {"type": "STRING", "description": "Text input for ASCII art or certificate"},
            "image_path": {"type": "STRING", "description": "Path to image file for processing"},
            "width": {"type": "INTEGER", "description": "Target width for resizing"},
            "height": {"type": "INTEGER", "description": "Target height for resizing"},
            "filter_type": {"type": "STRING", "description": "Filter: 'grayscale', 'sepia', 'blur', 'sharpen', 'invert', 'brightness'"}
        },
        "required": ["action"]
    },
    "handler": "ascii_art",
}


# ==================== ASCII ART GENERATOR ====================
@function_tool()
async def ascii_art(text: str) -> str:
    """Convert text to ASCII art."""
    try:
        import pyfiglet
        fig = pyfiglet.Figlet(font='slant')
        art = fig.renderText(text)
        return art
    except ImportError:
        # Simple fallback ASCII art
        return f"""
*** {text.upper()} ***
  ___   ___
 / __| / __|
| (__  \__ \\
 \___| |___/
"""
    except Exception as e:
        return f"Error: {str(e)}"


# ==================== COLOR PALETTE ====================
@function_tool()
async def color_palette(image_path: str) -> str:
    """Extract dominant colors from an image."""
    try:
        from PIL import Image
        import collections
        img = Image.open(image_path)
        img = img.resize((100, 100))
        pixels = list(img.getdata())
        counter = collections.Counter(pixels)
        top_colors = counter.most_common(5)
        output = "TOP 5 COLORS:\n"
        for i, (color, count) in enumerate(top_colors, 1):
            hex_color = '#{:02x}{:02x}{:02x}'.format(*color[:3])
            output += f"{i}. RGB{color[:3]} = {hex_color}\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"


# ==================== IMAGE RESIZER ====================
@function_tool()
async def image_resize(image_path: str, width: int, height: int, output_path: str = "") -> str:
    """Resize an image to custom dimensions."""
    try:
        from PIL import Image
        if not output_path:
            name, ext = os.path.splitext(image_path)
            output_path = f"{name}_resized{ext}"
        img = Image.open(image_path)
        img_resized = img.resize((width, height), Image.LANCZOS)
        img_resized.save(output_path)
        return f"Resized to {width}x{height} -> {output_path}"
    except Exception as e:
        return f"Error: {str(e)}"


# ==================== IMAGE FILTERS ====================
@function_tool()
async def image_filter(image_path: str, filter_type: str = "grayscale") -> str:
    """Apply filter to image. Types: grayscale, sepia, blur, sharpen, invert, brightness."""
    try:
        from PIL import Image, ImageFilter, ImageEnhance
        name, ext = os.path.splitext(image_path)
        output_path = f"{name}_{filter_type}{ext}"
        img = Image.open(image_path)

        if filter_type == "grayscale":
            img = img.convert('L')
        elif filter_type == "sepia":
            img = img.convert('L')
            sepia = Image.merge('RGB', [img.point(lambda x: min(255, int(x * 1.2))),
                                         img.point(lambda x: min(255, int(x * 1.0))),
                                         img.point(lambda x: min(255, int(x * 0.8)))])
            img = sepia
        elif filter_type == "blur":
            img = img.filter(ImageFilter.GaussianBlur(radius=5))
        elif filter_type == "sharpen":
            img = img.filter(ImageFilter.SHARPEN)
        elif filter_type == "invert":
            from PIL import ImageOps
            img = ImageOps.invert(img.convert('RGB'))
        elif filter_type == "brightness":
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.5)

        img.save(output_path)
        return f"Filter '{filter_type}' applied -> {output_path}"
    except Exception as e:
        return f"Error: {str(e)}"


# ==================== CERTIFICATE GENERATOR ====================
@function_tool()
async def generate_certificate(name: str, course: str, date: str = "") -> str:
    """Generate a completion certificate."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        if not date:
            date = datetime.now().strftime("%B %d, %Y")

        img = Image.new('RGB', (1200, 800), color='#1a1a2e')
        draw = ImageDraw.Draw(img)

        # Border
        draw.rectangle([20, 20, 1180, 780], outline='#00d4ff', width=3)
        draw.rectangle([30, 30, 1170, 770], outline='#00d4ff', width=1)

        # Title
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            name_font = ImageFont.truetype("arial.ttf", 36)
            body_font = ImageFont.truetype("arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            body_font = ImageFont.load_default()

        draw.text((400, 100), "CERTIFICATE", fill='#00d4ff', font=title_font)
        draw.text((350, 180), "OF COMPLETION", fill='#ffffff', font=title_font)
        draw.text((350, 280), "This is to certify that", fill='#aaaaaa', font=body_font)
        draw.text((350, 340), name, fill='#00d4ff', font=name_font)
        draw.text((350, 420), f"has successfully completed", fill='#aaaaaa', font=body_font)
        draw.text((350, 480), course, fill='#ffffff', font=name_font)
        draw.text((350, 580), f"Date: {date}", fill='#aaaaaa', font=body_font)
        draw.text((350, 640), "ZENITH AI - VADRYK Edition", fill='#00d4ff', font=body_font)

        output_path = os.path.join(os.path.dirname(__file__), '..', f'certificate_{name.replace(" ", "_")}.png')
        img.save(output_path)
        return f"Certificate generated for {name} -> {output_path}"
    except Exception as e:
        return f"Error: {str(e)}"


# ==================== INVOICE GENERATOR ====================
@function_tool()
async def generate_invoice(client: str, items: str, tax: float = 18.0) -> str:
    """Generate an invoice. items format: 'Item1:100,Item2:200'"""
    try:
        item_list = []
        subtotal = 0
        for item in items.split(','):
            parts = item.strip().split(':')
            if len(parts) == 2:
                name = parts[0].strip()
                price = float(parts[1].strip())
                item_list.append((name, price))
                subtotal += price

        tax_amount = subtotal * tax / 100
        total = subtotal + tax_amount

        output = f"INVOICE\n{'='*40}\nClient: {client}\nDate: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        output += f"{'Item':<20} {'Price':>10}\n{'-'*30}\n"
        for name, price in item_list:
            output += f"{name:<20} {price:>10.2f}\n"
        output += f"{'-'*30}\n"
        output += f"{'Subtotal':<20} {subtotal:>10.2f}\n"
        output += f"{'Tax (' + str(tax) + '%)':<20} {tax_amount:>10.2f}\n"
        output += f"{'TOTAL':<20} {total:>10.2f}\n"

        return output
    except Exception as e:
        return f"Error: {str(e)}"


# ==================== FLOWCHART FROM TEXT ====================
@function_tool()
async def text_to_flowchart(steps: str) -> str:
    """Convert text steps to a text-based flowchart."""
    step_list = [s.strip() for s in steps.split(',') if s.strip()]
    if not step_list:
        return "No steps provided."

    output = "FLOWCHART:\n\n"
    for i, step in enumerate(step_list):
        if i == 0:
            output += f"  (START)\n    |\n    v\n  [{step}]\n"
        elif i == len(step_list) - 1:
            output += f"    |\n    v\n  [{step}]\n    |\n    v\n  (END)\n"
        else:
            output += f"    |\n    v\n  [{step}]\n"

    return output


# ==================== TIMELINE GENERATOR ====================
@function_tool()
async def generate_timeline(events: str) -> str:
    """Generate a timeline from events. format: '2020:Event1,2021:Event2'"""
    event_list = []
    for e in events.split(','):
        parts = e.strip().split(':')
        if len(parts) == 2:
            event_list.append((parts[0].strip(), parts[1].strip()))

    if not event_list:
        return "No events provided."

    output = "TIMELINE:\n\n"
    for date, event in event_list:
        output += f"  {date} ---- {event}\n"

    return output


# ==================== ORG CHART ====================
@function_tool()
async def org_chart(title: str, levels: str) -> str:
    """Create org chart. levels format: 'CEO:Manager1,Manager2'"""
    level_list = [l.strip() for l in levels.split(',')]
    output = f"ORG CHART: {title}\n\n"
    output += f"  [{level_list[0]}]\n"
    output += f"  {'|' * 2}\n"
    for member in level_list[1:]:
        output += f"  |--- [{member}]\n"
    return output


# ==================== MEME GENERATOR ====================
@function_tool()
async def meme_text(above: str, below: str) -> str:
    """Generate meme text layout."""
    return f"""
    =====================
    |                   |
    |  {above.upper():<15}  |
    |                   |
    |    [IMAGE HERE]   |
    |                   |
    |  {below.upper():<15}  |
    |                   |
    =====================
"""


# ==================== BADGE GENERATOR ====================
@function_tool()
async def badge_generator(label: str, value: str, color: str = "blue") -> str:
    """Generate a badge/shield-style label."""
    colors = {"blue": "007bff", "green": "28a745", "red": "dc3545", "yellow": "ffc107", "purple": "6f42c1"}
    c = colors.get(color, "007bff")
    badge_len = len(label) + len(value) + 3
    return f"""
[{label}: {value}]
Color: #{c}
URL: https://img.shields.io/badge/{label}-{value}-{c
}
"""

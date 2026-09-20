import os
import asyncio
import threading
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from livekit.agents import function_tool

TOOL = {
    "name": "presentation_controller",
    "description": "Control PowerPoint presentations: load, navigate slides, present, and create new presentations. Use when the user wants to control or create PowerPoint slideshows.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Action: 'load', 'next_slide', 'prev_slide', 'start_presentation', 'stop_presentation', 'create'"},
            "file_path": {"type": "STRING", "description": "Path to PowerPoint file (for load/create)"},
            "slide_content": {"type": "STRING", "description": "Content for new presentation slides"}
        },
        "required": ["action"]
    },
    "handler": "handle_presentation_controller",
}

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    Presentation = None

try:
    import pythoncom
    import win32com.client
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


class PresentationController:
    """Controls PowerPoint presentations and creates new ones."""

    def __init__(self):
        self.current_pptx: Optional[Presentation] = None
        self.current_file: Optional[str] = None
        self.current_slide_index: int = 0
        self.ppt_app = None
        self.presentation = None
        self._tts_engine = None

    def _init_tts(self):
        """Initialize text-to-speech engine."""
        if TTS_AVAILABLE and self._tts_engine is None:
            try:
                self._tts_engine = pyttsx3.init()
                self._tts_engine.setProperty('rate', 170)
                self._tts_engine.setProperty('volume', 0.9)
                voices = self._tts_engine.getProperty('voices')
                for v in voices:
                    if 'female' in v.name.lower() or 'zira' in v.name.lower() or 'hazel' in v.name.lower():
                        self._tts_engine.setProperty('voice', v.id)
                        break
            except Exception as e:
                print(f"TTS init failed: {e}")
                self._tts_engine = None

    def speak(self, text: str) -> bool:
        """Speak text using TTS."""
        self._init_tts()
        if self._tts_engine:
            try:
                self._tts_engine.say(text)
                self._tts_engine.runAndWait()
                return True
            except Exception as e:
                print(f"TTS error: {e}")
        return False

    def _init_com(self):
        """Initialize COM for PowerPoint automation."""
        if not COM_AVAILABLE:
            return False
        try:
            pythoncom.CoInitialize()
            return True
        except Exception:
            return False

    def _get_ppt_app(self):
        """Get or create PowerPoint application."""
        if self.ppt_app is None:
            try:
                self.ppt_app = win32com.client.Dispatch("PowerPoint.Application")
                self.ppt_app.Visible = True
            except Exception as e:
                print(f"Failed to start PowerPoint: {e}")
                return None
        return self.ppt_app

    def load_presentation(self, file_path: str = None) -> str:
        """Load a PPTX file for reading content and control."""
        if file_path is None:
            file_path = self._open_file_dialog()
            if not file_path:
                return "❌ No file selected."

        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return f"❌ File not found: {file_path}"

        try:
            if Presentation is None:
                return "❌ python-pptx not installed."

            self.current_pptx = Presentation(str(path))
            self.current_file = str(path)
            self.current_slide_index = 0

            slide_count = len(self.current_pptx.slides)
            return f"✅ Loaded: {path.name} ({slide_count} slides)"

        except Exception as e:
            return f"❌ Failed to load presentation: {str(e)}"

    def _open_file_dialog(self) -> Optional[str]:
        """Open file dialog to select PPTX file."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            file_path = filedialog.askopenfilename(
                title="Select PowerPoint Presentation",
                filetypes=[("PowerPoint Files", "*.pptx *.ppt"), ("All Files", "*.*")]
            )
            root.destroy()
            return file_path if file_path else None
        except Exception:
            return None

    def get_slide_content(self, slide_index: int = None) -> str:
        """Extract text content from a slide."""
        if self.current_pptx is None:
            return "❌ No presentation loaded."

        idx = slide_index if slide_index is not None else self.current_slide_index
        if idx < 0 or idx >= len(self.current_pptx.slides):
            return f"❌ Invalid slide index: {idx + 1}"

        slide = self.current_pptx.slides[idx]
        texts = []

        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    text = paragraph.text.strip()
                    if text:
                        texts.append(text)

        if not texts:
            return f"Slide {idx + 1}: (no text content)"

        return f"Slide {idx + 1}:\n" + "\n".join(texts)

    def narrate_current_slide(self) -> str:
        """Read current slide content aloud."""
        content = self.get_slide_content()
        if content.startswith("❌") or content.startswith("Slide"):
            spoken = content.replace("Slide", "Slide").replace(":", " says")
            success = self.speak(spoken)
            return f"🔊 Narrating: {content}" if success else f"❌ TTS failed: {content}"
        return content

    def next_slide(self) -> str:
        """Advance to next slide in live PowerPoint."""
        return self._navigate_slide("next")

    def previous_slide(self) -> str:
        """Go to previous slide in live PowerPoint."""
        return self._navigate_slide("previous")

    def _navigate_slide(self, direction: str) -> str:
        if not self._init_com():
            return "❌ COM not available."

        app = self._get_ppt_app()
        if app is None:
            return "❌ Could not connect to PowerPoint."

        try:
            if app.SlideShowWindows.Count > 0:
                slideshow = app.SlideShowWindows(1)
                if direction == "next":
                    slideshow.View.Next()
                    return "➡️ Next slide"
                else:
                    slideshow.View.Previous()
                    return "⬅️ Previous slide"
            else:
                return "❌ No slideshow running. Say 'start slideshow' first."
        except Exception as e:
            return f"❌ Navigation failed: {str(e)}"

    def go_to_slide(self, slide_number: int) -> str:
        """Jump to specific slide number (1-indexed)."""
        if not self._init_com():
            return "❌ COM not available."

        app = self._get_ppt_app()
        if app is None:
            return "❌ Could not connect to PowerPoint."

        try:
            if app.SlideShowWindows.Count > 0:
                slideshow = app.SlideShowWindows(1)
                slideshow.View.GotoSlide(slide_number)
                return f"📍 Jumped to slide {slide_number}"
            else:
                return "❌ No slideshow running."
        except Exception as e:
            return f"❌ Go to slide failed: {str(e)}"

    def start_slideshow(self, from_slide: int = 1) -> str:
        """Start PowerPoint slideshow from specified slide."""
        if not self._init_com():
            return "❌ COM not available."

        if self.current_file is None:
            return "❌ No presentation loaded. Say 'load presentation' first."

        app = self._get_ppt_app()
        if app is None:
            return "❌ Could not start PowerPoint."

        try:
            self.presentation = app.Presentations.Open(self.current_file, ReadOnly=True)
            self.presentation.SlideShowSettings.StartingSlide = from_slide
            self.presentation.SlideShowSettings.EndingSlide = len(self.current_pptx.slides) if self.current_pptx else 999
            self.presentation.SlideShowSettings.Run()
            return f"▶️ Slideshow started from slide {from_slide}"
        except Exception as e:
            return f"❌ Failed to start slideshow: {str(e)}"

    def stop_slideshow(self) -> str:
        """Stop the current slideshow."""
        if not self._init_com():
            return "❌ COM not available."

        app = self._get_ppt_app()
        if app is None:
            return "❌ PowerPoint not connected."

        try:
            if app.SlideShowWindows.Count > 0:
                app.SlideShowWindows(1).View.Exit()
            if self.presentation:
                self.presentation.Close()
                self.presentation = None
            return "⏹️ Slideshow stopped"
        except Exception as e:
            return f"❌ Stop failed: {str(e)}"

    def create_presentation(
        self,
        topic: str,
        slides: List[Dict[str, Any]],
        output_path: str = None
    ) -> str:
        """
        Create a new PowerPoint presentation.
        
        Args:
            topic: Presentation title
            slides: List of dicts with keys: title, bullets (list), layout (optional)
            output_path: Where to save (default: Downloads)
        """
        if Presentation is None:
            return "❌ python-pptx not installed."

        try:
            prs = Presentation()
            prs.slide_width = Inches(13.333)
            prs.slide_height = Inches(7.5)

            # Title slide
            title_slide_layout = prs.slide_layouts[0]  # Title slide
            slide = prs.slides.add_slide(title_slide_layout)
            title = slide.shapes.title
            subtitle = slide.placeholders[1]
            title.text = topic
            subtitle.text = "Presented with ZENITH AI"

            # Content slides
            for slide_data in slides:
                layout_idx = slide_data.get('layout', 1)  # Title + Content
                slide_layout = prs.slide_layouts[layout_idx]
                slide = prs.slides.add_slide(slide_layout)

                # Title
                if slide.shapes.title:
                    slide.shapes.title.text = slide_data.get('title', '')

                # Bullets
                bullets = slide_data.get('bullets', [])
                if bullets:
                    body_shape = slide.placeholders[1] if len(slide.placeholders) > 1 else None
                    if body_shape and body_shape.has_text_frame:
                        tf = body_shape.text_frame
                        tf.clear()
                        for i, bullet in enumerate(bullets):
                            if i == 0:
                                tf.text = bullet
                            else:
                                p = tf.add_paragraph()
                                p.text = bullet
                            p.level = 0
                            p.font.size = Pt(20)

            # Save
            if output_path is None:
                safe_topic = "".join(c for c in topic[:30] if c.isalnum() or c in " _-").strip() or "presentation"
                downloads = Path.home() / "Downloads"
                output_path = str(downloads / f"{safe_topic}_{time.strftime('%Y%m%d_%H%M%S')}.pptx")

            prs.save(output_path)
            return f"✅ Presentation created: {output_path}\n📊 {len(slides) + 1} slides (title + {len(slides)} content)"

        except Exception as e:
            return f"❌ Failed to create presentation: {str(e)}"

    def get_slide_count(self) -> str:
        """Get total slide count."""
        if self.current_pptx is None:
            return "❌ No presentation loaded."
        return f"📊 Total slides: {len(self.current_pptx.slides)}"

    def get_current_slide_number(self) -> str:
        """Get current slide number (1-indexed)."""
        if self.current_pptx is None:
            return "❌ No presentation loaded."
        return f"📍 Current slide: {self.current_slide_index + 1} of {len(self.current_pptx.slides)}"


# Global instance
_presentation = PresentationController()


@function_tool()
async def load_presentation(file_path: str = None) -> str:
    """Load a PowerPoint presentation for control and narration."""
    return _presentation.load_presentation(file_path)


@function_tool()
async def next_slide() -> str:
    """Advance to the next slide in the live slideshow."""
    return _presentation.next_slide()


@function_tool()
async def previous_slide() -> str:
    """Go back to the previous slide in the live slideshow."""
    return _presentation.previous_slide()


@function_tool()
async def go_to_slide(slide_number: int) -> str:
    """Jump to a specific slide number (1-indexed)."""
    return _presentation.go_to_slide(slide_number)


@function_tool()
async def start_slideshow(from_slide: int = 1) -> str:
    """Start the PowerPoint slideshow from a specific slide."""
    return _presentation.start_slideshow(from_slide)


@function_tool()
async def stop_slideshow() -> str:
    """Stop the current slideshow and close presentation."""
    return _presentation.stop_slideshow()


@function_tool()
async def narrate_slide() -> str:
    """Read the current slide's content aloud using text-to-speech."""
    return _presentation.narrate_current_slide()


@function_tool()
async def get_slide_content(slide_number: int = None) -> str:
    """Get the text content of a specific slide (or current slide)."""
    return _presentation.get_slide_content(slide_number - 1 if slide_number else None)


@function_tool()
async def get_slide_count() -> str:
    """Get the total number of slides in the loaded presentation."""
    return _presentation.get_slide_count()


@function_tool()
async def get_current_slide() -> str:
    """Get the current slide number."""
    return _presentation.get_current_slide_number()


@function_tool()
async def create_presentation(
    topic: str,
    slide_titles: List[str],
    slide_bullets: List[List[str]],
    output_path: str = None
) -> str:
    """
    Create a new PowerPoint presentation.
    
    Args:
        topic: Main presentation title
        slide_titles: List of slide titles
        slide_bullets: List of bullet lists (one per slide)
        output_path: Optional output file path
    """
    if len(slide_titles) != len(slide_bullets):
        return "❌ Number of titles must match number of bullet lists."

    slides = []
    for title, bullets in zip(slide_titles, slide_bullets):
        slides.append({"title": title, "bullets": bullets, "layout": 1})

    return _presentation.create_presentation(topic, slides, output_path)


@function_tool()
async def start_presentation_mode() -> str:
    """Enter presentation mode - ready to load and control slides."""
    return """🎬 Presentation Mode Active

Available commands:
• "Load my presentation" - Open file dialog or specify path
• "Start slideshow" - Launch fullscreen presentation
• "Next slide" / "Previous slide" - Navigate
• "Go to slide X" - Jump to slide number
• "Explain this slide" - Narrate current slide content
• "What's on this slide?" - Get slide text
• "Run simulation of X" - Show visual simulation
• "Create presentation about X" - Generate new PPT
• "Stop presentation" - Exit slideshow

Ready when you are!"""


@function_tool()
async def stop_presentation_mode() -> str:
    """Exit presentation mode and cleanup."""
    result = _presentation.stop_slideshow()
    return f"👋 Presentation mode ended.\n{result}"


def handle_presentation_controller(parameters: dict) -> str:
    """Module-level handler for the action loader — dispatches by action."""
    action = parameters.get("action", "")
    file_path = parameters.get("file_path")
    slide_content = parameters.get("slide_content", "")

    try:
        if action == "load":
            return _presentation.load_presentation(file_path)
        elif action == "next_slide":
            return _presentation.next_slide()
        elif action == "prev_slide":
            return _presentation.previous_slide()
        elif action == "start_presentation":
            return _presentation.start_slideshow()
        elif action == "stop_presentation":
            return _presentation.stop_slideshow()
        elif action == "create":
            return f"✅ Use create_presentation tool for full slide creation. Content hint: {slide_content}"
        else:
            return (
                f"❌ Unknown action '{action}'. "
                "Use: load, next_slide, prev_slide, start_presentation, stop_presentation, create."
            )
    except Exception as e:
        return f"❌ Presentation controller error: {e}"
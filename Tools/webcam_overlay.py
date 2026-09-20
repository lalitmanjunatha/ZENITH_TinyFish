import asyncio
import cv2
import threading
import time
from typing import Optional, Tuple
from pathlib import Path
from livekit.agents import function_tool

TOOL = {
    "name": "webcam_overlay",
    "description": "Display a webcam overlay window on screen for presentations or video calls. Use when the user wants to show their webcam feed in a floating window.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Action: 'start', 'stop', 'settings'"},
            "position": {"type": "STRING", "description": "Window position: 'top-right', 'top-left', 'bottom-right', 'bottom-left', 'center'"},
            "size": {"type": "STRING", "description": "Window size as 'width,height' (default: '320,240')"},
            "opacity": {"type": "NUMBER", "description": "Window opacity 0.0-1.0 (default: 1.0)"}
        },
        "required": ["action"]
    },
    "handler": "handle_webcam_overlay",
}


class WebcamOverlay:
    """Manages webcam overlay window for presentations."""

    def __init__(self):
        self.cap = None
        self.running = False
        self.thread = None
        self.window_name = "ZENITH Webcam"
        self.position = "top-right"
        self.size = (320, 240)
        self.opacity = 1.0

    def _get_window_position(self, screen_width: int, screen_height: int) -> Tuple[int, int]:
        """Calculate window position based on position setting."""
        w, h = self.size
        margin = 20

        if self.position == "top-right":
            return screen_width - w - margin, margin
        elif self.position == "top-left":
            return margin, margin
        elif self.position == "bottom-right":
            return screen_width - w - margin, screen_height - h - margin
        elif self.position == "bottom-left":
            return margin, screen_height - h - margin
        elif self.position == "center":
            return (screen_width - w) // 2, (screen_height - h) // 2
        else:
            return screen_width - w - margin, margin

    def _overlay_loop(self):
        """Main loop for displaying webcam feed."""
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("❌ Could not open webcam")
            self.running = False
            return

        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.size[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.size[1])

        # Get screen resolution
        try:
            import tkinter as tk
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
        except:
            screen_width, screen_height = 1920, 1080

        # Create window
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        
        x, y = self._get_window_position(screen_width, screen_height)
        cv2.moveWindow(self.window_name, x, y)
        cv2.resizeWindow(self.window_name, self.size[0], self.size[1])
        
        # Make window always on top
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_TOPMOST, 1)

        print(f"📷 Webcam overlay started at {self.position} ({self.size[0]}x{self.size[1]})")

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Flip horizontally for mirror effect
            frame = cv2.flip(frame, 1)

            # Add border
            cv2.rectangle(frame, (0, 0), (frame.shape[1]-1, frame.shape[0]-1), (0, 255, 200), 2)

            # Add label
            cv2.putText(frame, "ZENITH", (10, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 200), 2)

            cv2.imshow(self.window_name, frame)

            # Check for window close or ESC key
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                break

        self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        if self.cap:
            self.cap.release()
            self.cap = None
        cv2.destroyWindow(self.window_name)
        cv2.waitKey(1)

    def start(self, position: str = "top-right", size: Tuple[int, int] = (320, 240)) -> str:
        """Start webcam overlay."""
        if self.running:
            return "⚠️ Webcam overlay already running"

        self.position = position
        self.size = size
        self.running = True

        self.thread = threading.Thread(target=self._overlay_loop, daemon=True)
        self.thread.start()

        return f"📷 Webcam overlay started at {position} ({size[0]}x{size[1]})"

    def stop(self) -> str:
        """Stop webcam overlay."""
        if not self.running:
            return "⚠️ Webcam overlay not running"

        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None

        self.cleanup()
        return "📷 Webcam overlay stopped"

    def set_position(self, position: str) -> str:
        """Change overlay position (requires restart)."""
        valid = ["top-right", "top-left", "bottom-right", "bottom-left", "center"]
        if position not in valid:
            return f"❌ Invalid position. Choose from: {', '.join(valid)}"
        
        was_running = self.running
        if was_running:
            self.stop()
            time.sleep(0.5)
        
        self.position = position
        
        if was_running:
            self.start(position, self.size)
        
        return f"📍 Position set to {position}"

    def set_size(self, width: int, height: int) -> str:
        """Change overlay size (requires restart)."""
        if width < 160 or height < 120:
            return "❌ Minimum size is 160x120"
        if width > 640 or height > 480:
            return "❌ Maximum size is 640x480"
        
        was_running = self.running
        if was_running:
            self.stop()
            time.sleep(0.5)
        
        self.size = (width, height)
        
        if was_running:
            self.start(self.position, self.size)
        
        return f"📏 Size set to {width}x{height}"

    def capture_photo(self, filename: str = None) -> str:
        """Capture a photo from webcam."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "❌ Could not open webcam"
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return "❌ Failed to capture photo"
        
        if filename is None:
            filename = f"webcam_{time.strftime('%Y%m%d_%H%M%S')}.png"
        
        filepath = Path.home() / "Downloads" / filename
        cv2.imwrite(str(filepath), frame)
        
        return f"📸 Photo saved: {filepath}"


# Global instance
_webcam = WebcamOverlay()


@function_tool()
async def start_webcam_overlay(
    position: str = "top-right",
    width: int = 320,
    height: int = 240
) -> str:
    """Start webcam overlay window in corner of screen.
    
    Position options: top-right, top-left, bottom-right, bottom-left, center
    """
    return _webcam.start(position, (width, height))


@function_tool()
async def stop_webcam_overlay() -> str:
    """Stop webcam overlay window."""
    return _webcam.stop()


@function_tool()
async def set_webcam_position(position: str) -> str:
    """Change webcam overlay position (restarts overlay if running)."""
    return _webcam.set_position(position)


@function_tool()
async def set_webcam_size(width: int, height: int) -> str:
    """Change webcam overlay size (restarts overlay if running)."""
    return _webcam.set_size(width, height)


@function_tool()
async def capture_webcam_photo(filename: str = None) -> str:
    """Capture a photo from webcam."""
    return _webcam.capture_photo(filename)


@function_tool()
async def webcam_status() -> str:
    """Get webcam overlay status."""
    if _webcam.running:
        return f"📷 Webcam overlay: RUNNING at {_webcam.position} ({_webcam.size[0]}x{_webcam.size[1]})"
    return "📷 Webcam overlay: STOPPED"


def handle_webcam_overlay(parameters: dict) -> str:
    """Module-level handler for the action loader — dispatches by action."""
    action = parameters.get("action", "")
    try:
        if action == "start":
            position = parameters.get("position", "top-right")
            size_str = parameters.get("size", "320,240")
            try:
                w, h = map(int, str(size_str).split(","))
            except Exception:
                w, h = 320, 240
            return _webcam.start(position, (w, h))
        elif action == "stop":
            return _webcam.stop()
        elif action == "settings":
            return (
                f"📷 Webcam settings:\n"
                f"  Position: {_webcam.position}\n"
                f"  Size: {_webcam.size[0]}x{_webcam.size[1]}\n"
                f"  Running: {_webcam.running}"
            )
        else:
            return (
                f"❌ Unknown action '{action}'. "
                "Use: start, stop, settings."
            )
    except Exception as e:
        return f"❌ Webcam overlay error: {e}"
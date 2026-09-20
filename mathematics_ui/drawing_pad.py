"""
drawing_pad.py — MATRIS Drawing Pad Widget

Freehand drawing canvas for handwriting equations.
Exports to PIL Image for OCR via pytesseract.
Integrated with ZENITH's HUD design language.
"""
from __future__ import annotations

import io
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt6.QtGui import (
    QFont, QPainter, QPen, QColor, QPixmap, QImage, QBrush, QMouseEvent,
    QPaintEvent, QResizeEvent
)


class DrawingCanvas(QWidget):
    """Low-level drawing surface — captures mouse strokes."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMinimumSize(200, 150)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._strokes: list[list[QPoint]] = []
        self._current_stroke: list[QPoint] = []
        self._pen_color = QColor("#00d4ff")
        self._pen_width = 3
        self._bg_color = QColor("#0a0e1a")
        self._last_pixmap: Optional[QPixmap] = None
        self._repaint_needed = True

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.LeftButton:
            self._current_stroke = [e.position().toPoint()]
            self.update()

    def mouseMoveEvent(self, e: QMouseEvent):
        if self._current_stroke:
            self._current_stroke.append(e.position().toPoint())
            self.update()

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.LeftButton and self._current_stroke:
            self._strokes.append(self._current_stroke)
            self._current_stroke = []
            self._repaint_needed = True
            self.update()

    def paintEvent(self, _event: QPaintEvent):
        p = QPainter(self)
        if not p.isActive():
            return
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        p.fillRect(self.rect(), self._bg_color)

        # Grid dots (subtle)
        p.setPen(QPen(QColor("#0d2030"), 1))
        for x in range(0, self.width(), 24):
            for y in range(0, self.height(), 24):
                p.drawPoint(x, y)

        # Draw completed strokes
        pen = QPen(self._pen_color, self._pen_width, Qt.PenStyle.SolidLine,
                   Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        for stroke in self._strokes:
            if len(stroke) >= 2:
                for i in range(1, len(stroke)):
                    p.drawLine(stroke[i - 1], stroke[i])

        # Draw current stroke in progress
        if self._current_stroke:
            p.setPen(QPen(self._pen_color, self._pen_width + 1,
                          Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                          Qt.PenJoinStyle.RoundJoin))
            for i in range(1, len(self._current_stroke)):
                p.drawLine(self._current_stroke[i - 1], self._current_stroke[i])

        # "Draw here" hint if empty
        if not self._strokes and not self._current_stroke:
            p.setPen(QPen(QColor("#1a4a5a"), 1))
            p.setFont(QFont("Courier New", 10))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                       "Draw your equation here")

        p.end()

    def has_strokes(self) -> bool:
        return bool(self._strokes)

    def clear(self):
        self._strokes.clear()
        self._current_stroke = []
        self._last_pixmap = None
        self.update()

    def undo(self):
        if self._strokes:
            self._strokes.pop()
            self.update()

    def to_pixmap(self) -> QPixmap:
        """Render strokes to a clean white-background QPixmap for OCR."""
        pm = QPixmap(self.size())
        pm.fill(QColor("#ffffff"))
        p = QPainter(pm)
        if not p.isActive():
            return pm
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#000000"), self._pen_width + 1,
                   Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                   Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        for stroke in self._strokes:
            if len(stroke) >= 2:
                for i in range(1, len(stroke)):
                    p.drawLine(stroke[i - 1], stroke[i])
        p.end()
        return pm


class DrawingPad(QWidget):
    """
    MATRIS Drawing Pad — full widget with canvas, buttons, and OCR.

    Signals:
        text_captured(str): Emitted when OCR produces text from drawing.
    """

    text_captured = pyqtSignal(str)

    PAD_STYLE = """
        QWidget {
            background-color: #0a0e1a;
            border: 1px solid #1e293b;
            border-radius: 8px;
        }
        QPushButton {
            background-color: #1e293b; color: #00d4ff;
            border: 1px solid #00d4ff; border-radius: 4px;
            padding: 4px 10px; font-size: 11px;
        }
        QPushButton:hover {
            background-color: #00d4ff; color: #0a0e1a;
        }
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setStyleSheet(self.PAD_STYLE)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("DRAW EQUATION")
        title.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        title.setStyleSheet("color: #00d4ff; background: transparent;")
        hdr.addWidget(title)
        hdr.addStretch()
        layout.addLayout(hdr)

        # Canvas
        self._canvas = DrawingCanvas()
        self._canvas.setMinimumHeight(120)
        self._canvas.setMaximumHeight(200)
        layout.addWidget(self._canvas)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        for label, handler in [
            ("Clear", self._on_clear),
            ("Undo", self._on_undo),
            ("Recognize", self._on_recognize),
        ]:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(handler)
            btn_row.addWidget(btn)

        layout.addLayout(btn_row)

        # Status label
        self._status = QLabel("")
        self._status.setFont(QFont("Courier New", 8))
        self._status.setStyleSheet("color: #94a3b8; background: transparent;")
        layout.addWidget(self._status)

    def _on_clear(self):
        self._canvas.clear()
        self._status.setText("")

    def _on_undo(self):
        self._canvas.undo()

    def _on_recognize(self):
        if not self._canvas.has_strokes():
            self._status.setText("Nothing to recognize — draw first")
            return

        self._status.setText("Recognizing...")
        self.repaint()

        try:
            text = self._ocr_canvas()
            if text:
                self._status.setText(f"Detected: {text}")
                self.text_captured.emit(text)
            else:
                self._status.setText("Could not read — try drawing clearer")
        except Exception as e:
            self._status.setText(f"OCR error: {str(e)[:40]}")

    def _ocr_canvas(self) -> str:
        """Convert canvas to PIL Image and run pytesseract OCR."""
        try:
            import pytesseract
            from PIL import Image

            pm = self._canvas.to_pixmap()
            # Convert QPixmap → QImage → bytes → PIL Image
            qimg = pm.toImage().convertToFormat(QImage.Format.Format_RGB888)
            buffer = qimg.bits().asstring(qimg.sizeInBytes())
            pil_img = Image.frombuffer(
                "RGB", (qimg.width(), qimg.height()), buffer,
                "raw", "RGB", qimg.bytesPerLine(), 1
            )

            # Preprocess: resize for better OCR, convert to grayscale
            pil_img = pil_img.convert("L")

            # OCR with math-friendly config
            text = pytesseract.image_to_string(
                pil_img,
                config="--psm 7 -c tessedit_char_whitelist=0123456789+-*/=(). abcdefghijklmnopqrstuvwxyz"
            )
            return text.strip()
        except ImportError:
            return ""
        except Exception:
            return ""

    def clear(self):
        self._canvas.clear()
        self._status.setText("")

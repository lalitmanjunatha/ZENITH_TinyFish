"""
matrix_input.py — MATRIS Matrix/Grid Input Widget

Structured grid input for matrices (NxN), vectors, and tables
that cannot be spoken or typed as plain text. Integrated with ZENITH's HUD.
"""
from __future__ import annotations

import re
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QGridLayout, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeyEvent


class MatrixCell(QLineEdit):
    """Single cell in the matrix grid — auto-advances focus on Enter."""

    def __init__(self, row: int, col: int, parent=None):
        super().__init__(parent)
        self._row = row
        self._col = col
        self.setFixedSize(52, 32)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Consolas", 11))
        self.setStyleSheet("""
            QLineEdit {
                background-color: #0d1220; color: #00d4ff;
                border: 1px solid #1e293b; border-radius: 3px;
                font-family: 'Consolas', monospace; font-size: 11px;
                padding: 2px;
            }
            QLineEdit:focus {
                border: 1px solid #00d4ff;
                background-color: #0f1828;
            }
        """)

    def keyPressEvent(self, e: QKeyEvent):
        # Tab/Shift+Tab handled by Qt focus system
        super().keyPressEvent(e)


class MatrixInputWidget(QWidget):
    """
    NxN matrix grid input — user fills cells directly.

    Signals:
        matrix_submitted(str): Emitted with formatted matrix string
                               (e.g. "matrix: [[1,2,3],[4,5,6],[7,8,9]]").
        vector_submitted(str): Emitted with vector string.
    """

    matrix_submitted = pyqtSignal(str)

    WIDGET_STYLE = """
        QWidget { background-color: #0a0e1a; }
        QLabel { color: #94a3b8; }
        QPushButton {
            background-color: #1e293b; color: #00d4ff;
            border: 1px solid #00d4ff; border-radius: 4px;
            padding: 4px 10px; font-size: 11px;
        }
        QPushButton:hover { background-color: #00d4ff; color: #0a0e1a; }
        QSpinBox, QComboBox {
            background-color: #0d1220; color: #e2e8f0;
            border: 1px solid #1e293b; border-radius: 3px;
            padding: 2px 6px; font-size: 11px;
        }
        QSpinBox:focus, QComboBox:focus { border: 1px solid #00d4ff; }
    """

    def __init__(self, rows: int = 3, cols: int = 3, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setStyleSheet(self.WIDGET_STYLE)
        self._rows = rows
        self._cols = cols
        self._cells: list[list[MatrixCell]] = []
        self._build_ui()
        self._rebuild_grid()

    def _build_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(6)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("MATRIX INPUT")
        title.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        title.setStyleSheet("color: #00d4ff; background: transparent;")
        hdr.addWidget(title)
        hdr.addStretch()

        # Dimensions selector
        dim_label = QLabel("Size:")
        dim_label.setStyleSheet("color: #94a3b8; background: transparent; font-size: 10px;")
        hdr.addWidget(dim_label)

        self._rows_spin = QSpinBox()
        self._rows_spin.setRange(1, 8)
        self._rows_spin.setValue(self._rows)
        self._rows_spin.setFixedWidth(40)
        self._rows_spin.valueChanged.connect(self._on_dim_changed)
        hdr.addWidget(self._rows_spin)

        x_label = QLabel("x")
        x_label.setStyleSheet("color: #94a3b8; background: transparent;")
        hdr.addWidget(x_label)

        self._cols_spin = QSpinBox()
        self._cols_spin.setRange(1, 8)
        self._cols_spin.setValue(self._cols)
        self._cols_spin.setFixedWidth(40)
        self._cols_spin.valueChanged.connect(self._on_dim_changed)
        hdr.addWidget(self._cols_spin)

        self._layout.addLayout(hdr)

        # Grid frame
        self._grid_frame = QFrame()
        self._grid_frame.setStyleSheet("""
            QFrame {
                background-color: #111827; border: 1px solid #1e293b;
                border-radius: 6px; padding: 6px;
            }
        """)
        self._grid_layout = QGridLayout(self._grid_frame)
        self._grid_layout.setSpacing(3)
        self._layout.addWidget(self._grid_frame)

        # Preset buttons + Submit
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        for label, dims in [("3x3", (3, 3)), ("4x4", (4, 4)),
                            ("3x1", (3, 1)), ("1x3", (1, 3))]:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedWidth(45)
            btn.clicked.connect(lambda _, r=dims[0], c=dims[1]: self._set_dims(r, c))
            btn_row.addWidget(btn)

        btn_row.addStretch()

        clear_btn = QPushButton("Clear")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self._clear_grid)
        btn_row.addWidget(clear_btn)

        submit_btn = QPushButton("Submit Matrix")
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #00d4ff; color: #0a0e1a;
                border: 1px solid #00d4ff; border-radius: 4px;
                padding: 5px 12px; font-size: 11px; font-weight: bold;
            }
            QPushButton:hover { background-color: #33ddff; }
        """)
        submit_btn.clicked.connect(self._on_submit)
        btn_row.addWidget(submit_btn)

        self._layout.addLayout(btn_row)

        # ── Describe what you want ────────────────────────────────────
        desc_frame = QFrame()
        desc_frame.setStyleSheet("""
            QFrame {
                background-color: #111827; border: 1px solid #1e293b;
                border-radius: 6px; padding: 4px;
            }
        """)
        desc_layout = QVBoxLayout(desc_frame)
        desc_layout.setContentsMargins(8, 4, 8, 4)
        desc_layout.setSpacing(3)

        desc_label = QLabel("Describe what you want (optional)")
        desc_label.setFont(QFont("Courier New", 8))
        desc_label.setStyleSheet("color: #94a3b8; background: transparent;")
        desc_layout.addWidget(desc_label)

        self._desc_input = QLineEdit()
        self._desc_input.setPlaceholderText(
            "e.g. find eigenvalues, calculate determinant, find inverse, solve Ax=b ..."
        )
        self._desc_input.setFont(QFont("Consolas", 10))
        self._desc_input.setStyleSheet("""
            QLineEdit {
                background-color: #0d1220; color: #e2e8f0;
                border: 1px solid #1e293b; border-radius: 4px;
                font-family: 'Consolas', monospace; font-size: 10px;
                padding: 4px 8px;
            }
            QLineEdit:focus { border: 1px solid #00d4ff; }
        """)
        desc_layout.addWidget(self._desc_input)

        self._layout.addWidget(desc_frame)

        # Status
        self._status = QLabel("")
        self._status.setFont(QFont("Courier New", 8))
        self._status.setStyleSheet("color: #94a3b8; background: transparent;")
        self._layout.addWidget(self._status)

    def _on_dim_changed(self):
        self._rows = self._rows_spin.value()
        self._cols = self._cols_spin.value()
        self._rebuild_grid()

    def _set_dims(self, r: int, c: int):
        self._rows_spin.setValue(r)
        self._cols_spin.setValue(c)
        self._rows = r
        self._cols = c
        self._rebuild_grid()

    def _rebuild_grid(self):
        """Recreate the NxN cell grid."""
        # Clear old cells
        self._cells.clear()
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        # Build new grid
        for r in range(self._rows):
            row_cells = []
            for c in range(self._cols):
                cell = MatrixCell(r, c)
                cell.setPlaceholderText("0")
                cell.returnPressed.connect(self._on_cell_enter)
                self._grid_layout.addWidget(cell, r, c)
                row_cells.append(cell)
            self._cells.append(row_cells)

        # Focus first cell
        if self._cells and self._cells[0]:
            self._cells[0][0].setFocus()

        self._status.setText(f"{self._rows}x{self._cols} grid ready")

    def _on_cell_enter(self):
        """Auto-advance focus to next cell on Enter."""
        sender = self.sender()
        if not isinstance(sender, MatrixCell):
            return
        r, c = sender._row, sender._col
        # Move to next cell in same row, then next row
        if c + 1 < self._cols:
            self._cells[r][c + 1].setFocus()
        elif r + 1 < self._rows:
            self._cells[r + 1][0].setFocus()
        else:
            # Last cell — submit
            self._on_submit()

    def _clear_grid(self):
        for row in self._cells:
            for cell in row:
                cell.clear()
        self._status.setText("Grid cleared")

    def _get_matrix(self) -> list[list[float]]:
        """Read grid into nested list of floats."""
        matrix = []
        for row in self._cells:
            vals = []
            for cell in row:
                text = cell.text().strip() or "0"
                try:
                    vals.append(float(text))
                except ValueError:
                    vals.append(0.0)
            matrix.append(vals)
        return matrix

    def _on_submit(self):
        matrix = self._get_matrix()
        rows = len(matrix)
        cols = len(matrix[0]) if matrix else 0
        desc = self._desc_input.text().strip()

        # Format as string for the solver — include description if provided
        if desc:
            matrix_str = f"matrix {rows}x{cols}: {matrix}. {desc}"
        else:
            matrix_str = f"matrix {rows}x{cols}: {matrix}"
        self._status.setText(f"Submitted {rows}x{cols} matrix")
        self.matrix_submitted.emit(matrix_str)

    def get_matrix_string(self) -> str:
        """Return the matrix as a readable string."""
        matrix = self._get_matrix()
        lines = []
        for row in matrix:
            lines.append("  [" + ", ".join(f"{v:g}" for v in row) + "]")
        return "[\n" + "\n".join(lines) + "\n]"

    def clear(self):
        self._clear_grid()

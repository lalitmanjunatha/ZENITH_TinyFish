"""
math_canvas.py — MATRIS Mathematical Canvas

Interactive display of MathematicalState with text input, drawing pad,
matrix grid input, action buttons, step-by-step explanation, and voice feedback.
Integrated with ZENITH's HUD design.
"""
from __future__ import annotations

import json
import re
import time
from typing import Optional, Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit,
    QPushButton, QScrollArea, QFrame, QSplitter, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from mathematics_ui.drawing_pad import DrawingPad
from mathematics_ui.matrix_input import MatrixInputWidget


class MathCanvas(QWidget):
    """
    MATRIS Mathematical Canvas — full interactive panel.

    Signals:
        problem_submitted(str): Emitted when user types, draws, or enters a matrix.
        action_requested(str, str): Emitted on button click (action, problem_text).
        close_requested(): Emitted when user wants to leave MATRIS mode.
        result_solved(str): Emitted with result text after a problem is solved.
    """

    problem_submitted = pyqtSignal(str)
    action_requested = pyqtSignal(str, str)
    close_requested = pyqtSignal()
    result_solved = pyqtSignal(str)

    CANVAS_STYLE = """
        QWidget { background-color: #0a0e1a; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
        QFrame { background-color: #111827; border: 1px solid #1e293b; border-radius: 8px; }
        QLabel { color: #e2e8f0; }
        QScrollArea { border: none; background-color: transparent; }
        QPushButton {
            background-color: #1e293b; color: #00d4ff; border: 1px solid #00d4ff;
            border-radius: 6px; padding: 6px 14px; font-size: 12px;
        }
        QPushButton:hover { background-color: #00d4ff; color: #0a0e1a; }
        QTextEdit {
            background-color: #0d1220; color: #e2e8f0; border: 1px solid #1e293b;
            border-radius: 6px; font-family: 'Consolas', monospace; font-size: 13px;
        }
        QLineEdit {
            background-color: #0d1220; color: #e2e8f0; border: 1px solid #1e293b;
            border-radius: 6px; font-family: 'Consolas', monospace; font-size: 13px;
            padding: 6px 10px;
        }
        QLineEdit:focus { border: 1px solid #00d4ff; }
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setStyleSheet(self.CANVAS_STYLE)
        self._state = None
        self._current_problem = ""
        self.solve_callback = None   # callable(str|dict) -> str
        self.speak_callback = None   # callable(str) -> None
        self._explanation_queue: list[str] = []
        self._explanation_timer = QTimer(self)
        self._explanation_timer.timeout.connect(self._next_explanation_step)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # ── Header row with close button ─────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(8)

        matris_badge = QLabel("MATRIS")
        matris_badge.setFont(QFont("Courier New", 11, QFont.Weight.Bold))
        matris_badge.setStyleSheet(
            "color: #0a0e1a; background-color: #00d4ff; "
            "border-radius: 4px; padding: 2px 8px;"
        )
        hdr.addWidget(matris_badge)

        title = QLabel("Mathematical Intelligence")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #e2e8f0; letter-spacing: 0.5px;")
        hdr.addWidget(title)
        hdr.addStretch()

        close_btn = QPushButton("EXIT MATRIS")
        close_btn.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #ff3355;
                border: 1px solid #ff3355; border-radius: 4px; padding: 3px 10px;
            }
            QPushButton:hover { background-color: #ff3355; color: #0a0e1a; }
        """)
        close_btn.clicked.connect(self.close_requested.emit)
        hdr.addWidget(close_btn)

        layout.addLayout(hdr)

        # ── Main content: left info + right display ──────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: metadata frames
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        self._domain_label = self._make_info_frame("Domain", "")
        self._model_label = self._make_info_frame("Model Type", "")
        self._vars_label = self._make_info_frame("Variables", "")
        self._given_label = self._make_info_frame("Given Values", "")
        self._obj_label = self._make_info_frame("Objective", "")
        self._status_label = self._make_info_frame("Validation", "")

        for w in [self._domain_label, self._model_label, self._vars_label,
                  self._given_label, self._obj_label, self._status_label]:
            left_layout.addWidget(w)
        left_layout.addStretch()
        splitter.addWidget(left)

        # Right: problem, equations, steps, solution
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        for label_text, attr_name, color, h_min, h_max in [
            ("Problem", "_problem_view", "#7c3aed", -1, 70),
            ("Equations", "_equations_view", "#00d4ff", -1, 70),
            ("Derivation Steps", "_derivation_view", "#10b981", 80, -1),
            ("Solution", "_solution_view", "#f59e0b", -1, 70),
            ("Interpretation", "_interpretation_view", "#94a3b8", -1, 70),
        ]:
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px;")
            right_layout.addWidget(lbl)
            view = QTextEdit()
            view.setReadOnly(True)
            if h_min > 0:
                view.setMinimumHeight(h_min)
            if h_max > 0:
                view.setMaximumHeight(h_max)
            setattr(self, attr_name, view)
            right_layout.addWidget(view)

        splitter.addWidget(right)
        splitter.setSizes([200, 500])
        layout.addWidget(splitter, stretch=1)

        # ── Input area: mode selector + stacked panels ──────────────────
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame { background-color: #111827; border: 1px solid #1e293b; border-radius: 8px; }
        """)
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 8, 10, 8)
        input_layout.setSpacing(6)

        # Mode selector row
        mode_row = QHBoxLayout()
        mode_row.setSpacing(4)

        self._mode_btns: list[QPushButton] = []
        self._input_stack = QStackedWidget()

        for label, index in [("Text", 0), ("Draw", 1), ("Matrix", 2)]:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setFixedWidth(55)
            btn.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
            btn.clicked.connect(lambda _, i=index: self._switch_input_mode(i))
            mode_row.addWidget(btn)
            self._mode_btns.append(btn)

        mode_row.addStretch()

        # -- Panel 0: Text input --
        text_panel = QWidget()
        text_panel.setStyleSheet("background: transparent;")
        tp_layout = QHBoxLayout(text_panel)
        tp_layout.setContentsMargins(0, 0, 0, 0)
        tp_layout.setSpacing(6)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Type a math problem... (e.g. Solve 2x + 5 = 17)")
        self._input.returnPressed.connect(self._on_text_submit)
        tp_layout.addWidget(self._input, stretch=1)

        solve_btn = QPushButton("Solve")
        solve_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        solve_btn.clicked.connect(self._on_text_submit)
        tp_layout.addWidget(solve_btn)

        self._input_stack.addWidget(text_panel)

        # -- Panel 1: Drawing pad --
        self._drawing_pad = DrawingPad()
        self._drawing_pad.text_captured.connect(self._on_drawing_captured)
        self._input_stack.addWidget(self._drawing_pad)

        # -- Panel 2: Matrix input --
        self._matrix_input = MatrixInputWidget()
        self._matrix_input.matrix_submitted.connect(self._on_matrix_submitted)
        self._input_stack.addWidget(self._matrix_input)

        input_layout.addLayout(mode_row)
        input_layout.addWidget(self._input_stack)

        # Default: text mode
        self._switch_input_mode(0)

        layout.addWidget(input_frame)

        # ── Action buttons row ───────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        for label, action in [
            ("Verify", "verify_solution"),
            ("Explain", "explain_step"),
            ("What-If", "what_if"),
            ("Diagnose", "diagnose_solution"),
            ("Classify", "classify_problem"),
        ]:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, a=action: self._on_action(a))
            btn_row.addWidget(btn)

        layout.addLayout(btn_row)

    def _make_info_frame(self, title: str, value: str) -> QFrame:
        frame = QFrame()
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(8, 4, 8, 4)
        fl.setSpacing(1)

        t = QLabel(title)
        t.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: bold;")
        v = QLabel(value)
        v.setStyleSheet("color: #e2e8f0; font-size: 11px;")
        v.setWordWrap(True)

        fl.addWidget(t)
        fl.addWidget(v)
        frame.setProperty("value_label", v)
        return frame

    def _set_frame_value(self, frame: QFrame, value: str):
        lbl = frame.property("value_label")
        if lbl:
            lbl.setText(value)

    # ── Mode switching ──────────────────────────────────────────────────

    def _switch_input_mode(self, index: int):
        """Switch between Text (0), Draw (1), Matrix (2) input panels."""
        self._input_stack.setCurrentIndex(index)
        for i, btn in enumerate(self._mode_btns):
            btn.setChecked(i == index)
            if i == index:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #00d4ff; color: #0a0e1a;
                        border: 1px solid #00d4ff; border-radius: 4px;
                        padding: 4px 10px; font-size: 11px; font-weight: bold;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1e293b; color: #00d4ff;
                        border: 1px solid #1e293b; border-radius: 4px;
                        padding: 4px 10px; font-size: 11px;
                    }
                    QPushButton:hover { border: 1px solid #00d4ff; }
                """)

    def open_matrix_input(self):
        self._switch_input_mode(2)

    def open_drawing_input(self):
        self._switch_input_mode(1)

    def open_text_input(self):
        self._switch_input_mode(0)

    # ── Solve + Speak helpers ───────────────────────────────────────────

    def _solve_and_speak(self, problem_text: str, action: str = "solve_problem") -> None:
        """Solve a problem, render result, and speak the answer."""
        if not self.solve_callback:
            return
        try:
            result = self.solve_callback({"action": action, "problem": problem_text})
            if result:
                self.render_from_text(str(result))
                result_str = str(result)
                # Emit result so the AI layer knows what was solved
                self.result_solved.emit(result_str)
                # Speak the answer directly
                speak_text = self._extract_speak_text(result_str)
                if speak_text and self.speak_callback:
                    self.speak_callback(speak_text)
        except Exception as e:
            self._problem_view.setPlainText(f"Solve error: {e}")

    def _extract_speak_text(self, result: str) -> str:
        """Extract a short spoken summary from the MATRIS result text."""
        lines = result.split("\n")
        parts = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("Interpretation") and ":" in stripped:
                parts.append(stripped.split(":", 1)[1].strip())
            elif stripped.startswith("Solution") and ":" in stripped and "{" in stripped:
                val = stripped.split(":", 1)[1].strip()
                try:
                    d = json.loads(val)
                    if "value" in d:
                        parts.append(f"The answer is {d['value']}")
                    elif "integral" in d:
                        parts.append(f"The integral is {d['integral']} plus C")
                    elif "derivative" in d:
                        parts.append(f"The derivative is {d['derivative']}")
                    elif "x" in d and "y" in d:
                        parts.append(f"x equals {d['x']}, y equals {d['y']}")
                    elif "eigenvalues" in d:
                        ev = d["eigenvalues"]
                        parts.append(f"Eigenvalues are {ev}")
                        if "eigenvectors" in d:
                            parts.append(f"Eigenvectors are {d['eigenvectors']}")
                    elif "determinant" in d:
                        parts.append(f"Determinant is {d['determinant']}")
                        if "rank" in d:
                            parts.append(f"Rank is {d['rank']}")
                    elif "inverse" in d:
                        parts.append("Inverse matrix computed successfully")
                    elif "rref" in d:
                        parts.append("Reduced row echelon form computed")
                    elif "trace" in d:
                        parts.append(f"Trace is {d['trace']}")
                    else:
                        parts.append(f"Solution: {val[:100]}")
                except (json.JSONDecodeError, TypeError):
                    parts.append(f"Solution: {val[:100]}")
            elif stripped.startswith("The ") and ("is " in stripped or "equals " in stripped):
                parts.append(stripped)
        return ". ".join(parts) if parts else ""

    # ── Step-by-step explanation ────────────────────────────────────────

    def _explain_step_by_step(self, problem_text: str) -> None:
        """Run explain action and display each step one-by-one with typing effect."""
        if not self.solve_callback:
            return
        try:
            result = self.solve_callback({"action": "explain_step", "problem": problem_text})
            if not result:
                return

            # Parse the result into individual steps
            self._explanation_queue = []
            self._derivation_view.clear()

            # Split by step markers
            steps = re.split(r'(?=\[Step \d+\]|Step \d+:|\n\d+\.\s)', str(result))
            steps = [s.strip() for s in steps if s.strip()]

            if not steps:
                # No step markers found — treat each non-empty line as a step
                steps = [s for s in str(result).split("\n") if s.strip()]

            self._explanation_queue = steps
            self._explanation_step_index = 0

            # Start the step-by-step timer
            self._explanation_timer.start(1200)  # 1.2s per step

            # Speak intro
            if self.speak_callback:
                self.speak_callback(
                    f"Let me explain this step by step. "
                    f"There are {len(steps)} steps."
                )

        except Exception as e:
            self._problem_view.setPlainText(f"Explanation error: {e}")

    def _next_explanation_step(self):
        """Pop and display the next explanation step."""
        if not self._explanation_queue:
            self._explanation_timer.stop()
            # Speak completion
            if self.speak_callback:
                self.speak_callback("That completes the step-by-step explanation.")
            return

        step = self._explanation_queue.pop(0)
        current = self._derivation_view.toPlainText()
        if current:
            current += "\n\n"
        self._derivation_view.setPlainText(current + step)

        # Speak this step
        if self.speak_callback:
            # Clean up the step text for speech
            clean = re.sub(r'\[Step \d+\]', '', step).strip()
            clean = re.sub(r'Step \d+:', '', clean).strip()
            if clean:
                self.speak_callback(clean[:200])

    # ── Input handlers ───────────────────────────────────────────────────

    def _on_text_submit(self):
        text = self._input.text().strip()
        if text:
            self._current_problem = text
            self._input.clear()
            self._solve_and_speak(text)

    def _on_drawing_captured(self, text: str):
        self._current_problem = text
        self._input.setText(text)
        self._solve_and_speak(text)

    def _on_matrix_submitted(self, matrix_str: str):
        self._current_problem = matrix_str
        self._solve_and_speak(matrix_str)

    def _on_action(self, action: str):
        problem = self._current_problem or ""
        self.action_requested.emit(action, problem)
        if not problem:
            return

        if action == "explain_step":
            self._explain_step_by_step(problem)
        else:
            self._solve_and_speak(problem, action=action)

    # ── State rendering ──────────────────────────────────────────────────

    def render_state(self, state) -> None:
        """Render a MathematicalState object to the canvas."""
        self._state = state
        if not state:
            return

        self._set_frame_value(self._domain_label, str(state.domain))
        self._set_frame_value(self._model_label, str(state.model_type))
        self._set_frame_value(self._vars_label,
                              ", ".join(f"{k}={v}" for k, v in state.variables.items()))
        self._set_frame_value(self._given_label,
                              ", ".join(f"{k}={v}" for k, v in state.given_values.items()))
        self._set_frame_value(self._obj_label, str(state.objective) or "-")
        self._set_frame_value(self._status_label,
                              state.validation.get("status", "Pending"))

        self._problem_view.setPlainText(state.problem)
        self._current_problem = state.problem
        self._equations_view.setPlainText(
            "\n".join(state.equations + state.constraints))

        steps = []
        for s in state.derivation_steps:
            step_num = s.get("step", "?")
            explanation = s.get("explanation", "")
            content = " | ".join(
                f"{k}: {v}" for k, v in s.items()
                if k not in ("step", "explanation"))
            steps.append(f"[Step {step_num}] {content}\n   -> {explanation}")
        self._derivation_view.setPlainText("\n\n".join(steps))

        self._solution_view.setPlainText(
            json.dumps(state.solution, indent=2, default=str))
        self._interpretation_view.setPlainText(state.real_world_interpretation)

    def render_from_text(self, text: str) -> None:
        """Parse a MATRIS text result and render what we can."""
        self._problem_view.setPlainText(text)

        # Extract domain
        m = re.search(r"\[(.+?)\]", text)
        if m:
            self._set_frame_value(self._domain_label, m.group(1))

        # Parse structured fields
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("Status") and ":" in stripped:
                self._set_frame_value(self._status_label,
                                      stripped.split(":", 1)[1].strip())
            elif stripped.startswith("Model Type") and ":" in stripped:
                self._set_frame_value(self._model_label,
                                      stripped.split(":", 1)[1].strip())
            elif stripped.startswith("Solution") and ":" in stripped and "{" in stripped:
                self._solution_view.setPlainText(
                    stripped.split(":", 1)[1].strip())
            elif stripped.startswith("Interpretation") and ":" in stripped:
                self._interpretation_view.setPlainText(
                    stripped.split(":", 1)[1].strip())

    def clear(self):
        self._state = None
        self._current_problem = ""
        self._explanation_queue.clear()
        self._explanation_timer.stop()
        for view in [self._problem_view, self._equations_view,
                     self._derivation_view, self._solution_view,
                     self._interpretation_view]:
            view.clear()
        self._set_frame_value(self._domain_label, "")
        self._set_frame_value(self._model_label, "")
        self._set_frame_value(self._vars_label, "")
        self._set_frame_value(self._given_label, "")
        self._set_frame_value(self._obj_label, "")
        self._set_frame_value(self._status_label, "")
        self._matrix_input.clear()

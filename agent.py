# ==============================================================================
# ZENITH VADRYK Edition — Unified Main AI Agent & Desktop Companion
# ==============================================================================
# Created by Lalit Manjunatha
# Features: Real-time Voice AI, PyQt6 Reactive HUD UI, Wake-Word Engine,
#           Safety Confirmation Gate, Undo System, Remote Mobile Dashboard,
#           and 296 Integrated Tools across 21 Domains.
# ==============================================================================

from dotenv import load_dotenv
import asyncio
import os
import sys
import time
import json
import socket
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

load_dotenv()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# =========================
# STARTUP ANIMATION
# =========================
ZENITH_BANNER = r"""
   ______                 _           
  / ____/___  _________  (_)___  ___ 
 / /   / __ \/ ___/ __ \/ / __ \/ _ \
/ /___/ /_/ / /  / /_/ / / / / /  __/
\____/\____/_/  / .___/_/_/ /_/\___/ 
               /_/                    
"""
BANNER_COLOR = "\033[96m"  # Cyan
RESET_COLOR = "\033[0m"
SUCCESS_COLOR = "\033[92m"  # Green
WARN_COLOR = "\033[93m"     # Yellow
ERROR_COLOR = "\033[91m"    # Red
DIM_COLOR = "\033[90m"      # Gray

def print_banner():
    """Print styled startup banner"""
    print(f"\n{BANNER_COLOR}{ZENITH_BANNER}{RESET_COLOR}")
    print(f"{DIM_COLOR}  VADRYK Edition (Mark LIII UI)  |  Created by Lalit Manjunatha{RESET_COLOR}")
    print(f"{DIM_COLOR}  {'=' * 56}{RESET_COLOR}\n")

def status(msg: str, state: str = "info"):
    """Print styled status messages"""
    icons = {
        "ok": f"{SUCCESS_COLOR}[OK]{RESET_COLOR}",
        "warn": f"{WARN_COLOR}[WARN]{RESET_COLOR}",
        "err": f"{ERROR_COLOR}[ERR]{RESET_COLOR}",
        "load": f"{BANNER_COLOR}[...]{RESET_COLOR}",
        "info": f"{DIM_COLOR}[--]{RESET_COLOR}",
    }
    icon = icons.get(state, icons["info"])
    print(f"  {icon} {msg}")

# =========================
# LIVEKIT IMPORTS
# =========================
from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions
from livekit.plugins import noise_cancellation

# Gemini realtime (network-safe)
network_available = False
try:
    socket.create_connection(("8.8.8.8", 53), timeout=3)
    from livekit.plugins.google.beta.realtime import RealtimeModel
    network_available = True
except Exception:
    pass

# =========================
# PROMPTS
# =========================
from prompts import (
    AGENT_INSTRUCTION,
    SESSION_INSTRUCTION,
    AGENT_INSTRUCTION_FOR_TOOLS,
)

# =========================
# VADRYK CORE & SYSTEM TOOLS (45+ tools)
# =========================
from Tools.manage_windows import manage_window, list_windows
from Tools.search_web import search_web
from Tools.send_whatsapp_message import send_whatsapp_message
from Tools.system_power_action import system_power_action
from Tools.type_user_message_auto import type_user_message_auto
from Tools.write_in_notepad import write_in_notepad
from Tools.desktop_control import desktop_control
from Tools.scroll_content import scroll_content
from Tools.code_handler import fix_code_error
from Tools.file_searching import universal_file_opener
from Tools.press_key import press_key, use_smart_clipboard
from Tools.open_app import open_app
from Tools.scan_system_for_viruses import scan_system_for_viruses
from Tools.time_volume_bright import (
    control_screen_brightness,
    control_system_volume,
    get_time_info,
    get_weather,
    get_system_info_deep,
)
from Tools.multi_task import execute_multi_task
from Tools.generate_ai_image import generate_ai_image
from Tools.code_generator import generate_and_type_code, run_file_in_vscode
from Tools.news_provider import get_top_news
from Tools.youtube_videos import play_media
from Tools.device_fabric import (
    fabric_create_pairing, fabric_pending_call_reports, fabric_request_action, fabric_status, fabric_sync,
)
from Tools.reminder import set_reminder, view_reminders, cancel_reminder
from Tools.screen_short import screen_short
from Tools.pdf_reader import process_document_query
from Tools.send_media_whatsapp import send_media_to_whatsapp
from Tools.excel_data_entery import (
    create_excel_file, save_excel_changes, delete_all_data,
    move_left, move_up, enter_data_quick, enter_multiple_data_quick,
    move_down, move_right, delete_current_cell, go_to_cell,
    toggle_text_bold, select_row_or_column, sort_excel_data,
    excel_clipboard_action, calculate_sum,
)
from Tools.word_to_pdf import (
    word_to_pdf, image_to_pdf, excel_to_pdf, ppt_to_pdf,
    convert_image_format, test_converters,
)
from Tools.create_folder import create_here
from Tools.read_screen_text import read_screen_text
from Tools.camera_analysis import camera_analysis
from Tools.screen_analyzer import analyze_screen
from Tools.image_analysis import analyze_local_image
from Tools.spotify import (
    open_spotify, spotify_next, spotify_previous,
    spotify_play_song, spotify_play_liked, spotify_pause,
)

# FaithMakes Unique Actions Adapter
from Tools.faithmakes_adapter import (
    find_flights, check_game_updates, manage_topic_monitor, run_dev_agent,
)

# =========================
# SPECIALIZED TOOL MODULES
# =========================
PRESENTATION_AVAILABLE = False
try:
    from Tools.presentation_controller import (
        load_presentation, start_slideshow, stop_slideshow,
        go_to_next_slide, go_to_previous_slide, go_to_slide,
        get_current_slide_number, get_total_slides, narrate_current_slide,
        create_presentation, add_slide_with_content, add_slide_with_title,
        get_slide_notes, presentation_status
    )
    PRESENTATION_AVAILABLE = True
except ImportError:
    pass

SIMULATION_AVAILABLE = False
try:
    from Tools.simulation_engine import (
        run_simulation, create_chart, create_diagram, list_simulation_types
    )
    SIMULATION_AVAILABLE = True
except ImportError:
    pass

SIM_V2_AVAILABLE = False
try:
    from Tools.simulation.api import (
        sim_create, sim_run, sim_step, sim_pause, sim_resume, sim_stop, sim_reset,
        sim_set_param, sim_visualize, sim_explain, sim_save, sim_list, sim_status,
        sim_run_n_times, sim_get_state,
        sim_pendulum, sim_projectile, sim_graph_function,
        sim_show_derivative, sim_show_integral, sim_fractal,
        sim_neural_network, sim_gradient_descent, sim_kmeans,
        sim_rc_circuit, sim_rectifier, sim_logic_gate, sim_probability,
        sim_sir_model, sim_predator_prey, sim_population_growth, sim_enzyme_kinetics,
        sim_pid_controller, sim_robot_arm, sim_astar, sim_inverted_pendulum,
        sim_sorting, sim_cpu_scheduling, sim_bst, sim_linked_list,
        sim_surface_3d, sim_parametric_3d, sim_vector_field_3d,
        sim_fourier, sim_convolution, sim_filter_design, sim_sampling,
    )
    SIM_V2_AVAILABLE = True
except ImportError:
    pass

WEBCAM_AVAILABLE = False
try:
    from Tools.webcam_overlay import (
        start_webcam_overlay, stop_webcam_overlay,
        set_webcam_position, set_webcam_size,
        capture_webcam_photo, webcam_status
    )
    WEBCAM_AVAILABLE = True
except ImportError:
    pass

GIT_AVAILABLE = False
try:
    from Tools.git_integration import (
        git_status, git_log, git_commit, git_push, git_pull,
        git_branch_list, git_diff, git_clone,
    )
    GIT_AVAILABLE = True
except ImportError:
    pass

TERMINAL_AVAILABLE = False
try:
    from Tools.terminal_exec import (
        run_command, run_python, list_processes, kill_process,
    )
    TERMINAL_AVAILABLE = True
except ImportError:
    pass

DATABASE_AVAILABLE = False
try:
    from Tools.database_tools import (
        sqlite_query, sqlite_create_table, sqlite_insert, sqlite_select,
        sqlite_list_tables, sqlite_export_csv,
    )
    DATABASE_AVAILABLE = True
except ImportError:
    pass

NETWORK_AVAILABLE = False
try:
    from Tools.network_diag import (
        ping_host, dns_lookup, port_scan, traceroute, check_http,
    )
    NETWORK_AVAILABLE = True
except ImportError:
    pass

DATA_AVAILABLE = False
try:
    from Tools.data_processor import (
        csv_analyze, json_parse, csv_filter, csv_sort, data_statistics, csv_to_json,
    )
    DATA_AVAILABLE = True
except ImportError:
    pass

EMAIL_AVAILABLE = False
try:
    from Tools.email_tool import send_email, read_email, search_email
    EMAIL_AVAILABLE = True
except ImportError:
    pass

QR_AVAILABLE = False
try:
    from Tools.qr_generator import generate_qr
    QR_AVAILABLE = True
except ImportError:
    pass

MINDMAP_AVAILABLE = False
try:
    from Tools.mindmap import create_mindmap
    MINDMAP_AVAILABLE = True
except ImportError:
    pass

CALENDAR_AVAILABLE = False
try:
    from Tools.calendar_tools import (
        calendar_add_event, calendar_today, calendar_tomorrow, calendar_week,
        calendar_delete_event, task_add, task_list, task_complete, task_delete,
        note_create, note_search, note_list,
    )
    CALENDAR_AVAILABLE = True
except ImportError:
    pass

COMMUNICATION_TOOLS_AVAILABLE = False
try:
    from Tools.communication_tools import (
        discord_send, meeting_link, auto_reply_email, bulk_email,
        email_reminder, call_log,
    )
    COMMUNICATION_TOOLS_AVAILABLE = True
except ImportError:
    pass

SYSTEM_SECURITY_AVAILABLE = False
try:
    from Tools.system_security_tools import (
        wifi_password, startup_apps, disk_cleanup, disk_usage,
        screenshot_scheduler, app_blocker, parental_control, firewall_rule,
        encrypted_folder, backup_files, restore_backup, system_snapshot,
    )
    SYSTEM_SECURITY_AVAILABLE = True
except ImportError:
    pass

API_TEST_AVAILABLE = False
try:
    from Tools.api_tester import api_test
    API_TEST_AVAILABLE = True
except ImportError:
    pass

IOT_BLYNK_AVAILABLE = False
try:
    from Tools.iot_blynk_tools import (
        blynk_write, blynk_read, blynk_device_status, blynk_notify, blynk_email_trigger,
    )
    IOT_BLYNK_AVAILABLE = True
except ImportError:
    pass

STUDY_AVAILABLE = False
try:
    from Tools.study_tools import (
        generate_flashcards, pomodoro_start, pomodoro_status, pomodoro_stop,
        study_planner, reading_time, gpa_calculator, unit_convert,
        scientific_calc, number_convert, roman_convert, password_generate,
        percentage_calc, compound_interest, bmi_calculator, countdown,
        vocabulary_add, vocabulary_list, estimate_reading_time,
        stopwatch_start, stopwatch_lap, stopwatch_stop,
        todo_add, todo_list_all, todo_complete,
        expense_add, expense_summary,
    )
    STUDY_AVAILABLE = True
except ImportError:
    pass

CREATIVE_AVAILABLE = False
try:
    from Tools.creative_tools import (
        ascii_art, color_palette, image_resize, image_filter,
        generate_certificate, generate_invoice, text_to_flowchart,
        generate_timeline, org_chart, meme_text, badge_generator,
    )
    CREATIVE_AVAILABLE = True
except ImportError:
    pass

CODING_AVAILABLE = False
try:
    from Tools.coding_tools import (
        code_format, regex_test, json_validate, json_format,
        html_preview, base64_encode, base64_decode,
        url_encode, url_decode, hash_generate, uuid_generate,
        color_convert, markdown_preview, lorem_ipsum,
        password_strength, code_analysis, diff_view,
    )
    CODING_AVAILABLE = True
except ImportError:
    pass

DATA_TOOLS_AVAILABLE = False
try:
    from Tools.data_tools import (
        bar_chart, pie_chart, line_graph, scatter_plot, histogram,
        statistics_calc, emi_calculator,
        survey_create, survey_vote, survey_results, quiz_generate,
    )
    DATA_TOOLS_AVAILABLE = True
except ImportError:
    pass

PRESENTATION_TOOLS_AVAILABLE = False
try:
    from Tools.presentation_tools import (
        system_monitor, system_monitor_chart,
        timer_start, timer_check,
        fun_fact, compliment, joke, motivation,
        trivia_question, trivia_answer, word_of_the_day, this_day_in_history,
        counter_increment, counter_decrement, counter_reset, counter_get,
        coin_flip, dice_roll, random_number,
        breathing_exercise, stretch_reminder, pro_tip,
    )
    PRESENTATION_TOOLS_AVAILABLE = True
except ImportError:
    pass

AI_ENGINE_AVAILABLE = False
try:
    from autonomous_intelligence.api import (
        research_start, research_stop, research_pause, research_resume,
        research_status, research_activity, research_report, research_report_summary,
        research_knowledge, research_search_local, research_read_local,
        research_analyze_codebase, research_web_search, research_read_url,
        research_save, research_config_show,
    )
    AI_ENGINE_AVAILABLE = True
except ImportError:
    pass

MATRIS_AVAILABLE = False
try:
    from Tools.mathematical_reasoner import mathematical_reasoner
    MATRIS_AVAILABLE = True
except ImportError:
    pass

# =========================
# MAIN ZENITH AGENT CLASS
# =========================
class ZenithAgent(Agent):
    def __init__(self):
        self._reminders: Dict[str, Dict[str, Any]] = {}
        self._reminder_task: Optional[asyncio.Task] = None
        self._session: Optional[AgentSession] = None
        self._reminder_counter = 0

        tools = [
            # Information & VADRYK Core
            search_web, get_time_info, get_weather, get_system_info_deep,
            # System Control
            system_power_action, manage_window, list_windows,
            desktop_control, scroll_content, press_key,
            open_app, scan_system_for_viruses,
            # Media & Communication
            play_media, send_whatsapp_message, send_media_to_whatsapp,
            fabric_create_pairing, fabric_status, fabric_request_action, fabric_pending_call_reports, fabric_sync,
            get_top_news,
            # Productivity
            write_in_notepad, type_user_message_auto, use_smart_clipboard,
            universal_file_opener, execute_multi_task,
            # Code & AI
            generate_and_type_code, run_file_in_vscode, fix_code_error,
            generate_ai_image, screen_short,
            # Volume & Brightness
            control_system_volume, control_screen_brightness,
            # Reminders & Documents
            set_reminder, view_reminders, cancel_reminder, process_document_query,
            # Excel Suite
            create_excel_file, save_excel_changes, delete_all_data,
            move_left, move_up, move_down, move_right,
            enter_data_quick, enter_multiple_data_quick,
            delete_current_cell, go_to_cell, toggle_text_bold,
            select_row_or_column, sort_excel_data,
            excel_clipboard_action, calculate_sum,
            # File Conversion Suite
            word_to_pdf, image_to_pdf, excel_to_pdf, ppt_to_pdf,
            convert_image_format, test_converters,
            # Folders & Vision
            create_here, read_screen_text, camera_analysis, analyze_screen, analyze_local_image,
            # Spotify Suite
            open_spotify, spotify_next, spotify_previous,
            spotify_play_song, spotify_play_liked, spotify_pause,
            # FaithMakes Cloned Tools
            find_flights, check_game_updates, manage_topic_monitor, run_dev_agent,
        ]

        if PRESENTATION_AVAILABLE:
            tools.extend([
                load_presentation, start_slideshow, stop_slideshow,
                go_to_next_slide, go_to_previous_slide, go_to_slide,
                get_current_slide_number, get_total_slides, narrate_current_slide,
                create_presentation, add_slide_with_content, add_slide_with_title,
                get_slide_notes, presentation_status
            ])

        if SIMULATION_AVAILABLE:
            tools.extend([
                run_simulation, create_chart, create_diagram, list_simulation_types
            ])

        if WEBCAM_AVAILABLE:
            tools.extend([
                start_webcam_overlay, stop_webcam_overlay,
                set_webcam_position, set_webcam_size,
                capture_webcam_photo, webcam_status
            ])

        if SIM_V2_AVAILABLE:
            tools.extend([
                sim_create, sim_run, sim_step, sim_pause, sim_resume, sim_stop, sim_reset,
                sim_set_param, sim_visualize, sim_explain, sim_save, sim_list, sim_status,
                sim_run_n_times, sim_get_state,
                sim_pendulum, sim_projectile, sim_graph_function,
                sim_show_derivative, sim_show_integral, sim_fractal,
                sim_neural_network, sim_gradient_descent, sim_kmeans,
                sim_rc_circuit, sim_rectifier, sim_logic_gate, sim_probability,
                sim_sir_model, sim_predator_prey, sim_population_growth, sim_enzyme_kinetics,
                sim_pid_controller, sim_robot_arm, sim_astar, sim_inverted_pendulum,
                sim_sorting, sim_cpu_scheduling, sim_bst, sim_linked_list,
                sim_surface_3d, sim_parametric_3d, sim_vector_field_3d,
                sim_fourier, sim_convolution, sim_filter_design, sim_sampling,
            ])

        if GIT_AVAILABLE:
            tools.extend([
                git_status, git_log, git_commit, git_push, git_pull,
                git_branch_list, git_diff, git_clone,
            ])

        if TERMINAL_AVAILABLE:
            tools.extend([
                run_command, run_python, list_processes, kill_process,
            ])

        if DATABASE_AVAILABLE:
            tools.extend([
                sqlite_query, sqlite_create_table, sqlite_insert, sqlite_select,
                sqlite_list_tables, sqlite_export_csv,
            ])

        if NETWORK_AVAILABLE:
            tools.extend([
                ping_host, dns_lookup, port_scan, traceroute, check_http,
            ])

        if DATA_AVAILABLE:
            tools.extend([
                csv_analyze, json_parse, csv_filter, csv_sort, data_statistics, csv_to_json,
            ])

        if EMAIL_AVAILABLE:
            tools.extend([send_email, read_email, search_email])

        if QR_AVAILABLE:
            tools.extend([generate_qr])

        if MINDMAP_AVAILABLE:
            tools.extend([create_mindmap])

        if STUDY_AVAILABLE:
            tools.extend([
                generate_flashcards, pomodoro_start, pomodoro_status, pomodoro_stop,
                study_planner, reading_time, gpa_calculator, unit_convert,
                scientific_calc, number_convert, roman_convert, password_generate,
                percentage_calc, compound_interest, bmi_calculator, countdown,
                vocabulary_add, vocabulary_list, estimate_reading_time,
                stopwatch_start, stopwatch_lap, stopwatch_stop,
                todo_add, todo_list_all, todo_complete,
                expense_add, expense_summary,
            ])

        if CREATIVE_AVAILABLE:
            tools.extend([
                ascii_art, color_palette, image_resize, image_filter,
                generate_certificate, generate_invoice, text_to_flowchart,
                generate_timeline, org_chart, meme_text, badge_generator,
            ])

        if CODING_AVAILABLE:
            tools.extend([
                code_format, regex_test, json_validate, json_format,
                html_preview, base64_encode, base64_decode,
                url_encode, url_decode, hash_generate, uuid_generate,
                color_convert, markdown_preview, lorem_ipsum,
                password_strength, code_analysis, diff_view,
            ])

        if DATA_TOOLS_AVAILABLE:
            tools.extend([
                bar_chart, pie_chart, line_graph, scatter_plot, histogram,
                statistics_calc, emi_calculator,
                survey_create, survey_vote, survey_results, quiz_generate,
            ])

        if PRESENTATION_TOOLS_AVAILABLE:
            tools.extend([
                system_monitor, system_monitor_chart,
                timer_start, timer_check,
                fun_fact, compliment, joke, motivation,
                trivia_question, trivia_answer, word_of_the_day, this_day_in_history,
                counter_increment, counter_decrement, counter_reset, counter_get,
                coin_flip, dice_roll, random_number,
                breathing_exercise, stretch_reminder, pro_tip,
            ])

        if AI_ENGINE_AVAILABLE:
            tools.extend([
                research_start, research_stop, research_pause, research_resume,
                research_status, research_activity, research_report, research_report_summary,
                research_knowledge, research_search_local, research_read_local,
                research_analyze_codebase, research_web_search, research_read_url,
                research_save, research_config_show,
            ])

        if MATRIS_AVAILABLE:
            tools.extend([mathematical_reasoner])

        if CALENDAR_AVAILABLE:
            tools.extend([
                calendar_add_event, calendar_today, calendar_tomorrow, calendar_week,
                calendar_delete_event, task_add, task_list, task_complete, task_delete,
                note_create, note_search, note_list,
            ])

        if COMMUNICATION_TOOLS_AVAILABLE:
            tools.extend([
                discord_send, meeting_link, auto_reply_email, bulk_email,
                email_reminder, call_log,
            ])

        if SYSTEM_SECURITY_AVAILABLE:
            tools.extend([
                wifi_password, startup_apps, disk_cleanup, disk_usage,
                screenshot_scheduler, app_blocker, parental_control, firewall_rule,
                encrypted_folder, backup_files, restore_backup, system_snapshot,
            ])

        if API_TEST_AVAILABLE:
            tools.extend([api_test])

        if IOT_BLYNK_AVAILABLE:
            tools.extend([
                blynk_write, blynk_read, blynk_device_status,
                blynk_notify, blynk_email_trigger,
            ])

        super().__init__(
            instructions=self._build_instructions(),
            tools=tools,
            llm=self._init_llm(),
        )

    def _init_llm(self):
        if network_available:
            return RealtimeModel(
                model="gemini-2.5-flash-native-audio-preview-12-2025",
                voice="Charon",
                temperature=0.9,
                max_output_tokens=4096,
            )
        return None

    def _build_instructions(self):
        return "\n".join([
            AGENT_INSTRUCTION,
            AGENT_INSTRUCTION_FOR_TOOLS,
            "You have access to ALL 296 system, voice, simulation, automation, presentation, and reminder tools.",
            "Use tools aggressively when required.",
        ])

    def set_session(self, session: AgentSession):
        self._session = session

    def add_reminder(self, text: str, time_: datetime):
        rid = f"rem_{self._reminder_counter}"
        self._reminder_counter += 1
        self._reminders[rid] = {"text": text, "time": time_}
        if not self._reminder_task or self._reminder_task.done():
            self._reminder_task = asyncio.create_task(self._monitor_reminders())
        return rid

    async def _monitor_reminders(self):
        while self._reminders:
            now = datetime.now()
            triggered = [rid for rid, data in self._reminders.items() if now >= data["time"]]
            for rid in triggered:
                await self._trigger_reminder(self._reminders[rid]["text"])
                self._reminders.pop(rid, None)
            await asyncio.sleep(5)

    async def _trigger_reminder(self, text: str):
        if self._session:
            await self._session.generate_reply(instructions=f"Reminder: {text}")

# =========================
# LIVEKIT ENTRYPOINT
# =========================
async def entrypoint(ctx: agents.JobContext):
    print_banner()
    status("Checking network connectivity...", "load")
    if network_available:
        status("Network online - Gemini realtime available", "ok")
    else:
        status("Network offline - limited functionality", "warn")

    status("Loading 296 tools across 21 domains...", "load")
    agent = ZenithAgent()
    tool_count = len(agent.tools) if hasattr(agent, 'tools') else '?'
    status(f"Agent initialized — {tool_count} tools active", "ok")

    status("Starting LiveKit session...", "load")
    session = AgentSession()

    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            video_enabled=False,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    agent.set_session(session)
    status("Voice module active — Aoede voice loaded", "ok")

    await ctx.connect()
    status("Connected to LiveKit cloud", "ok")

    await session.generate_reply(instructions=SESSION_INSTRUCTION)
    status("ZENITH is LIVE & READY", "ok")
    print(f"\n{BANNER_COLOR}  Say 'Hey Zenith' or type a command to begin.{RESET_COLOR}\n")

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        status("Zenith stopped", "info")

# =========================
# PYQT6 HUD GUI LAUNCHER
# =========================
def run_gui():
    print_banner()
    status("Initializing ZENITH HUD Interface...", "load")
    try:
        import zenith_gui
        zenith_gui.main()
    except Exception as e:
        status(f"GUI launch error: {e}", "err")
        sys.exit(1)

# =========================
# MAIN UNIFIED ENTRYPOINT
# =========================
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("dev", "start", "worker", "--cli"):
        agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
    else:
        run_gui()

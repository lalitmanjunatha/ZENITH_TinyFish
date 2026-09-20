"""
Autonomous Intelligence Engine -- Action Loader Bridge
======================================================
Bridges the autonomous_intelligence package into the ZENITH action registry
so it is available inside the Gemini Live GUI (zenith_gui.py) as a first-class
tool, alongside all other file-backed actions in Tools/.

Every action is dispatched through a single TOOL dict with an "action" parameter,
which keeps the Gemini function-declaration count low while exposing the full
research API surface.
"""
from __future__ import annotations
import json
from typing import Optional

# -- Lazy import so startup never fails if the package has a missing dep ------
_director = None
_import_error: Optional[str] = None

def _get_director():
    global _director, _import_error
    if _director is not None:
        return _director, None
    try:
        from autonomous_intelligence.director import ResearchDirector
        _director = ResearchDirector()
        return _director, None
    except Exception as e:
        _import_error = str(e)
        return None, _import_error


# -- TOOL declaration (Gemini function schema) ---------------------------------
TOOL = {
    "name": "autonomous_research",
    "description": (
        "Autonomous Intelligence Engine: runs multi-step AI-powered research sessions "
        "that independently search the internet and local files, extract knowledge, "
        "verify claims, detect contradictions, and produce cited intelligence reports. "
        "Use for deep research, fact-finding, codebase analysis, or any topic that "
        "requires gathering information from multiple sources autonomously. "
        "Actions: start, stop, pause, resume, status, activity, report, report_summary, "
        "knowledge, search_local, read_local, analyze_codebase, web_search, read_url, "
        "save, config."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": (
                    "Research action to perform. One of: "
                    "start | stop | pause | resume | status | activity | "
                    "report | report_summary | knowledge | "
                    "search_local | read_local | analyze_codebase | "
                    "web_search | read_url | save | config"
                ),
            },
            "objective": {
                "type": "STRING",
                "description": "Research objective / topic (required for start).",
            },
            "query": {
                "type": "STRING",
                "description": "Search query (for search_local and web_search).",
            },
            "path": {
                "type": "STRING",
                "description": "File or directory path (for read_local and analyze_codebase).",
            },
            "url": {
                "type": "STRING",
                "description": "URL to read (for read_url).",
            },
        },
        "required": ["action"],
    },
    "handler": "handle_autonomous_research",
}


# -- Module-level dispatcher --------------------------------------------------
def handle_autonomous_research(parameters: dict) -> str:
    """
    Single module-level handler -- dispatches to the correct ResearchDirector
    method based on the action parameter.
    """
    action    = parameters.get("action", "").strip().lower()
    objective = parameters.get("objective", "")
    query     = parameters.get("query", "")
    path      = parameters.get("path", "")
    url       = parameters.get("url", "")

    if action == "":
        return (
            "No action specified. Use one of: "
            "start, stop, pause, resume, status, activity, report, report_summary, "
            "knowledge, search_local, read_local, analyze_codebase, "
            "web_search, read_url, save, config."
        )

    director, err = _get_director()
    if err:
        return f"Autonomous Intelligence Engine failed to load: {err}"

    try:
        # -- Session control --------------------------------------------------
        if action == "start":
            if not objective:
                return "objective is required for action start."
            session = director.start_research(objective)
            return (
                f"Research session started!\n"
                f"  ID: {session.id}\n"
                f"  Objective: {objective}\n"
                f"  Tasks planned: {len(session.tasks)}\n"
                f"  Running autonomously in background.\n"
                f"  Say check research status to monitor progress."
            )

        elif action == "stop":
            return director.stop_research()

        elif action == "pause":
            return director.pause_research()

        elif action == "resume":
            return director.resume_research()

        # -- Status & monitoring ----------------------------------------------
        elif action == "status":
            s = director.get_status()
            if s.get("status") == "no active session":
                return "No active research session. Use action=start with an objective."
            return (
                f"RESEARCH STATUS\n"
                f"  Objective : {str(s.get('objective','?'))[:80]}\n"
                f"  Phase     : {s.get('phase','?')}\n"
                f"  Running   : {s.get('running', False)}\n"
                f"  Tasks     : {s.get('tasks_completed',0)}/{s.get('tasks_total',0)} completed\n"
                f"  Current   : {s.get('current_task') or 'None'}\n"
                f"  Evidence  : {s.get('evidence_count',0)} items\n"
                f"  Claims    : {s.get('claims_count',0)}\n"
                f"  Contradict: {s.get('contradictions',0)}\n"
                f"  Gaps      : {s.get('knowledge_gaps',0)}\n"
                f"  Sources   : {s.get('sources_count',0)}\n"
                f"  Elapsed   : {s.get('elapsed_seconds',0)}s\n"
                f"  Errors    : {s.get('errors',0)}"
            )

        elif action == "activity":
            activity = director.get_live_activity()
            if activity.get("status", {}).get("status") == "no active session":
                return "No active research session."
            s = activity["status"]
            lines = [
                "LIVE RESEARCH ACTIVITY",
                f"Phase: {s.get('phase','?')} | Tasks: {s.get('tasks_completed',0)}/{s.get('tasks_total',0)}",
            ]
            events = activity.get("recent_events", [])
            if events:
                lines.append("\nRecent events:")
                for ev in events[-8:]:
                    etype  = ev.get("event_type", "?")
                    data   = ev.get("data", {})
                    detail = data.get("query", data.get("title", data.get("url", "")))
                    lines.append(f"  [{etype}] {str(detail)[:80]}" if detail else f"  [{etype}]")
            tabs = activity.get("open_tabs", [])
            if tabs:
                lines.append(f"\nOpen tabs ({len(tabs)}):")
                for tab in tabs[:5]:
                    lines.append(f"  {tab.get('title', tab.get('url','?'))[:60]}")
            return "\n".join(lines)

        # -- Report -----------------------------------------------------------
        elif action == "report":
            report = director.get_report()
            if not report:
                s = director.get_status()
                if s.get("status") == "no active session":
                    return "No research session found."
                return f"Research still in progress (phase: {s.get('phase','?')}). Check back soon."
            return report.full_text

        elif action == "report_summary":
            report = director.get_report()
            if not report:
                return "No report available yet."
            lines = [
                f"REPORT: {report.title}",
                f"\nOBJECTIVE: {report.objective}",
                f"\nCONFIDENCE: {report.confidence}",
                f"\nEXECUTIVE SUMMARY:\n{report.executive_summary}",
            ]
            if report.key_findings:
                lines.append("\nKEY FINDINGS:")
                for i, finding in enumerate(report.key_findings[:5], 1):
                    lines.append(f"  {i}. {finding[:150]}")
            if report.contradictions:
                lines.append("\nCONTRADICTIONS:")
                for c in report.contradictions[:3]:
                    lines.append(f"  ! {c[:150]}")
            if report.recommendations:
                lines.append("\nRECOMMENDATIONS:")
                for r in report.recommendations:
                    lines.append(f"  -> {r}")
            return "\n".join(lines)

        # -- Knowledge --------------------------------------------------------
        elif action == "knowledge":
            if not director.session:
                return "No active session."
            summary = director.knowledge.get_summary()
            return (
                f"KNOWLEDGE SUMMARY\n"
                f"  Evidence items : {summary['total_evidence']}\n"
                f"  Claims         : {summary['total_claims']}\n"
                f"  Verified       : {summary['verified_claims']}\n"
                f"  Contradictions : {summary['contradictions']}\n"
                f"  Knowledge gaps : {summary['knowledge_gaps']}\n"
                f"  Avg confidence : {summary['average_confidence']:.2f}\n"
                f"  Graph entities : {summary['entities_in_graph']}\n"
                f"  Relationships  : {summary['relationships_in_graph']}"
            )

        # -- Local intelligence -----------------------------------------------
        elif action == "search_local":
            if not query:
                return "query is required for action search_local."
            results = director.local.search(query)
            if not results:
                return f"No local files found matching '{query}'."
            lines = [f"LOCAL SEARCH: '{query}' ({len(results)} results)\n"]
            for r in results[:8]:
                lines.append(f"  {r['name']} ({r['type']}) -- {r['path']}")
                if r.get("preview"):
                    lines.append(f"    Preview: {r['preview'][:100]}...")
            return "\n".join(lines)

        elif action == "read_local":
            if not path:
                return "path is required for action read_local."
            content = director.local.read_file(path)
            if not content:
                return f"Could not read file: {path}"
            return f"Content of {path}:\n\n{content[:3000]}"

        elif action == "analyze_codebase":
            if not path:
                return "path is required for action analyze_codebase."
            analysis = director.local.analyze_codebase(path)
            if "error" in analysis:
                return f"Error: {analysis['error']}"
            lines = [
                f"CODEBASE ANALYSIS: {path}",
                f"  Total files : {analysis['total_files']}",
                f"  Total lines : {analysis['total_lines']}",
                f"  Languages   : {', '.join(analysis['languages']) if analysis['languages'] else 'unknown'}",
                f"  File types  : {json.dumps(analysis['by_type'])}",
            ]
            if analysis.get("classes"):
                lines.append(f"\n  Classes ({len(analysis['classes'])}):")
                for c in analysis["classes"][:5]:
                    lines.append(f"    {c}")
            if analysis.get("functions"):
                lines.append(f"\n  Functions ({len(analysis['functions'])}):")
                for f in analysis["functions"][:5]:
                    lines.append(f"    {f}")
            if analysis.get("key_files"):
                lines.append("\n  Key files:")
                for f in analysis["key_files"]:
                    lines.append(f"    {f}")
            return "\n".join(lines)

        # -- Web intelligence -------------------------------------------------
        elif action == "web_search":
            if not query:
                return "query is required for action web_search."
            results = director.web.search(query)
            if not results:
                return f"No web results found for '{query}'."
            lines = [f"WEB SEARCH: '{query}' ({len(results)} results)\n"]
            for r in results[:6]:
                lines.append(f"  {r['title'][:60]}")
                lines.append(f"    {r['url']}")
                if r.get("snippet"):
                    lines.append(f"    {r['snippet'][:100]}...")
                lines.append("")
            return "\n".join(lines)

        elif action == "read_url":
            if not url:
                return "url is required for action read_url."
            content = director.web.read_page(url)
            if not content:
                return f"Could not read: {url}"
            return f"Content from {url}:\n\n{content[:3000]}"

        # -- Session management -----------------------------------------------
        elif action == "save":
            return director.save_session()

        elif action == "config":
            cfg = director.config
            return (
                f"RESEARCH CONFIG\n"
                f"  Max runtime      : {cfg.max_runtime_minutes} min\n"
                f"  Max search queries: {cfg.max_search_queries}\n"
                f"  Max pages        : {cfg.max_pages_visited}\n"
                f"  Max tabs         : {cfg.max_browser_tabs}\n"
                f"  Max tasks        : {cfg.max_tasks}\n"
                f"  Permission level : {cfg.permission_level}\n"
                f"  Search provider  : {cfg.search_provider}\n"
                f"  Indexed paths    : {', '.join(cfg.indexed_paths[:3])}"
            )

        else:
            return (
                f"Unknown action '{action}'. Valid actions: "
                "start, stop, pause, resume, status, activity, report, report_summary, "
                "knowledge, search_local, read_local, analyze_codebase, "
                "web_search, read_url, save, config."
            )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Autonomous research error: {e}"

"""
Voice-callable API for the Autonomous Intelligence Engine.
These are the function_tools registered with the LiveKit agent.
"""
import json
from typing import Optional
from livekit.agents import function_tool

from .config import ResearchConfig
from .director import ResearchDirector

# Global director instance
_director: Optional[ResearchDirector] = None


def get_director() -> ResearchDirector:
    global _director
    if _director is None:
        _director = ResearchDirector()
    return _director


@function_tool()
async def research_start(objective: str) -> str:
    """
    Start an autonomous research session.
    ZENITH will independently search the Internet and local files,
    extract knowledge, verify claims, and produce an intelligence report.

    Example: "Research the latest AI agent architectures and determine how ZENITH could improve."
    """
    director = get_director()
    session = director.start_research(objective)
    return (f"Research session started!\n"
            f"ID: {session.id}\n"
            f"Objective: {objective}\n"
            f"Tasks planned: {len(session.tasks)}\n"
            f"Say 'check research status' to monitor progress.")


@function_tool()
async def research_stop() -> str:
    """Stop the current autonomous research session."""
    director = get_director()
    return director.stop_research()


@function_tool()
async def research_pause() -> str:
    """Pause the current research session."""
    director = get_director()
    return director.pause_research()


@function_tool()
async def research_resume() -> str:
    """Resume a paused research session."""
    director = get_director()
    return director.resume_research()


@function_tool()
async def research_status() -> str:
    """Check the status of the current research session."""
    director = get_director()
    status = director.get_status()
    if status.get("status") == "no active session":
        return "No active research session. Use research_start to begin."

    lines = [
        f"RESEARCH STATUS:",
        f"  Objective: {status.get('objective', '?')[:80]}",
        f"  Phase: {status.get('phase', '?')}",
        f"  Running: {status.get('running', False)}",
        f"  Tasks: {status.get('tasks_completed', 0)}/{status.get('tasks_total', 0)} completed",
        f"  Current: {status.get('current_task', 'None')}",
        f"  Evidence: {status.get('evidence_count', 0)} items",
        f"  Claims: {status.get('claims_count', 0)}",
        f"  Contradictions: {status.get('contradictions', 0)}",
        f"  Knowledge gaps: {status.get('knowledge_gaps', 0)}",
        f"  Sources: {status.get('sources_count', 0)}",
        f"  Open tabs: {status.get('open_tabs', 0)}",
        f"  Elapsed: {status.get('elapsed_seconds', 0)}s",
    ]
    return "\n".join(lines)


@function_tool()
async def research_activity() -> str:
    """Get live activity stream from the current research."""
    director = get_director()
    activity = director.get_live_activity()
    if activity.get("status", {}).get("status") == "no active session":
        return "No active research session."

    lines = ["LIVE RESEARCH ACTIVITY:\n"]

    # Status
    s = activity["status"]
    lines.append(f"Phase: {s.get('phase', '?')} | Tasks: {s.get('tasks_completed', 0)}/{s.get('tasks_total', 0)}")

    # Recent events
    events = activity.get("recent_events", [])
    if events:
        lines.append("\nRecent events:")
        for ev in events[-8:]:
            etype = ev.get("event_type", "?")
            data = ev.get("data", {})
            detail = data.get("query", data.get("title", data.get("url", "")))
            if detail:
                lines.append(f"  [{etype}] {str(detail)[:80]}")
            else:
                lines.append(f"  [{etype}]")

    # Open tabs
    tabs = activity.get("open_tabs", [])
    if tabs:
        lines.append(f"\nOpen tabs ({len(tabs)}):")
        for tab in tabs[:5]:
            lines.append(f"  {tab.get('title', tab.get('url', '?'))[:60]}")

    return "\n".join(lines)


@function_tool()
async def research_report() -> str:
    """Get the final research report."""
    director = get_director()
    report = director.get_report()
    if not report:
        status = director.get_status()
        if status.get("status") == "no active session":
            return "No research session found."
        return f"Research still in progress (phase: {status.get('phase', '?')}). Wait for completion."

    return report.full_text


@function_tool()
async def research_report_summary() -> str:
    """Get a summary of the research report."""
    director = get_director()
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
        for i, f in enumerate(report.key_findings[:5], 1):
            lines.append(f"  {i}. {f[:150]}")

    if report.contradictions:
        lines.append("\nCONTRADICTIONS:")
        for c in report.contradictions[:3]:
            lines.append(f"  ! {c[:150]}")

    if report.recommendations:
        lines.append("\nRECOMMENDATIONS:")
        for r in report.recommendations:
            lines.append(f"  -> {r}")

    return "\n".join(lines)


@function_tool()
async def research_knowledge() -> str:
    """Get the current knowledge summary from the research."""
    director = get_director()
    if not director.session:
        return "No active session."

    summary = director.knowledge.get_summary()
    return (f"KNOWLEDGE SUMMARY:\n"
            f"  Evidence items: {summary['total_evidence']}\n"
            f"  Claims: {summary['total_claims']}\n"
            f"  Verified: {summary['verified_claims']}\n"
            f"  Contradictions: {summary['contradictions']}\n"
            f"  Knowledge gaps: {summary['knowledge_gaps']}\n"
            f"  Avg confidence: {summary['average_confidence']:.2f}\n"
            f"  Graph entities: {summary['entities_in_graph']}\n"
            f"  Graph relationships: {summary['relationships_in_graph']}")


@function_tool()
async def research_search_local(query: str) -> str:
    """Search local files for information related to a query."""
    director = get_director()
    results = director.local.search(query)
    if not results:
        return f"No local files found matching '{query}'"

    lines = [f"LOCAL SEARCH: '{query}' ({len(results)} results)\n"]
    for r in results[:8]:
        lines.append(f"  {r['name']} ({r['type']}) - {r['path']}")
        if r.get('preview'):
            lines.append(f"    Preview: {r['preview'][:100]}...")
    return "\n".join(lines)


@function_tool()
async def research_read_local(path: str) -> str:
    """Read a local file's content."""
    director = get_director()
    content = director.local.read_file(path)
    return content[:3000] if content else "Could not read file."


@function_tool()
async def research_analyze_codebase(path: str) -> str:
    """Analyze a local codebase for structure and patterns."""
    director = get_director()
    analysis = director.local.analyze_codebase(path)
    if "error" in analysis:
        return analysis["error"]

    lines = [
        f"CODEBASE ANALYSIS: {path}",
        f"  Total files: {analysis['total_files']}",
        f"  Total lines: {analysis['total_lines']}",
        f"  Languages: {', '.join(analysis['languages']) if analysis['languages'] else 'unknown'}",
        f"  File types: {json.dumps(analysis['by_type'], indent=4)}",
    ]

    if analysis['classes']:
        lines.append(f"\n  Classes ({len(analysis['classes'])}):")
        for c in analysis['classes'][:5]:
            lines.append(f"    {c}")

    if analysis['functions']:
        lines.append(f"\n  Functions ({len(analysis['functions'])}):")
        for f in analysis['functions'][:5]:
            lines.append(f"    {f}")

    if analysis['key_files']:
        lines.append(f"\n  Key files:")
        for f in analysis['key_files']:
            lines.append(f"    {f}")

    return "\n".join(lines)


@function_tool()
async def research_web_search(query: str) -> str:
    """Search the web for information."""
    director = get_director()
    results = director.web.search(query)
    if not results:
        return f"No results found for '{query}'"

    lines = [f"WEB SEARCH: '{query}' ({len(results)} results)\n"]
    for r in results[:6]:
        lines.append(f"  {r['title'][:60]}")
        lines.append(f"    {r['url']}")
        if r.get('snippet'):
            lines.append(f"    {r['snippet'][:100]}...")
        lines.append("")
    return "\n".join(lines)


@function_tool()
async def research_read_url(url: str) -> str:
    """Read and extract content from a URL."""
    director = get_director()
    content = director.web.read_page(url)
    if not content:
        return f"Could not read: {url}"
    return f"Content from {url}:\n\n{content[:3000]}"


@function_tool()
async def research_save() -> str:
    """Save the current research session to disk."""
    director = get_director()
    return director.save_session()


@function_tool()
async def research_config_show() -> str:
    """Show the current research configuration."""
    config = get_director().config
    return (f"RESEARCH CONFIG:\n"
            f"  Max runtime: {config.max_runtime_minutes} min\n"
            f"  Max search queries: {config.max_search_queries}\n"
            f"  Max pages: {config.max_pages_visited}\n"
            f"  Max tabs: {config.max_browser_tabs}\n"
            f"  Max tasks: {config.max_tasks}\n"
            f"  Permission level: {config.permission_level}\n"
            f"  Indexed paths: {', '.join(config.indexed_paths[:3])}\n"
            f"  Search provider: {config.search_provider}")

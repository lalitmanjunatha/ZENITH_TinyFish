"""
ZENITH Network Diagnostics Tool
Provides: ping, dns_lookup, port_scan, traceroute, check_http
"""

import subprocess
import socket
import time
import asyncio
import concurrent.futures
from typing import Optional
from livekit.agents import function_tool

TOOL = {
    "name": "network_diagnostics",
    "description": "Network diagnostic tools: ping hosts, DNS lookup, scan ports, traceroute, and check HTTP status. Use when the user wants to troubleshoot network connectivity or investigate servers.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Action: 'ping', 'dns_lookup', 'port_scan', 'traceroute', 'check_http'"},
            "host": {"type": "STRING", "description": "Host or domain to diagnose"},
            "count": {"type": "INTEGER", "description": "Number of ping packets (default: 4)"},
            "ports": {"type": "STRING", "description": "Ports to scan (e.g. '22,80,443' or '1-1000')"},
            "url": {"type": "STRING", "description": "URL for HTTP check"}
        },
        "required": ["action"]
    },
    "handler": "ping_host",
}


@function_tool()
async def ping_host(host: str, count: int = 4) -> str:
    """Ping a host and return results."""
    try:
        param = "-n" if __import__("sys").platform == "win32" else "-c"
        result = await asyncio.to_thread(
            subprocess.run,
            ["ping", param, str(count), host],
            capture_output=True, text=True, timeout=15
        )
        return f"Ping {host}:\n{result.stdout}"
    except subprocess.TimeoutExpired:
        return f"Ping timed out for {host}"
    except Exception as e:
        return f"Ping error: {str(e)}"


@function_tool()
async def dns_lookup(domain: str) -> str:
    """Resolve domain name to IP addresses."""
    try:
        results = socket.getaddrinfo(domain, None)
        ips = set()
        for res in results:
            ips.add(res[4][0])

        lines = [f"DNS Lookup for {domain}:"]
        for ip in ips:
            lines.append(f"  {ip}")

        try:
            hostname = socket.gethostbyaddr(list(ips)[0])
            lines.append(f"  Reverse DNS: {hostname[0]}")
        except socket.herror:
            pass

        return "\n".join(lines)
    except socket.gaierror:
        return f"Could not resolve {domain}"
    except Exception as e:
        return f"DNS error: {str(e)}"


def _check_port(host: str, port: int) -> tuple:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return (port, result == 0)
    except:
        return (port, False)


@function_tool()
async def port_scan(host: str, ports: str = "22,80,443,8080") -> str:
    """Scan ports on a host. ports format: '22,80,443' or '1-1000'"""
    try:
        if "-" in ports:
            start, end = ports.split("-")
            port_list = list(range(int(start), int(end) + 1))
        elif "," in ports:
            port_list = [int(p.strip()) for p in ports.split(",")]
        else:
            port_list = [int(ports)]

        open_ports = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(_check_port, host, p): p for p in port_list}
            for future in concurrent.futures.as_completed(futures):
                port, is_open = future.result()
                if is_open:
                    open_ports.append(port)

        open_ports.sort()
        common = {22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL", 5432: "PostgreSQL", 8080: "HTTP-Alt"}
        lines = [f"Port Scan for {host}:"]
        if open_ports:
            for p in open_ports:
                svc = common.get(p, "unknown")
                lines.append(f"  Port {p}: OPEN ({svc})")
        else:
            lines.append("  No open ports found")

        return "\n".join(lines)
    except Exception as e:
        return f"Port scan error: {str(e)}"


@function_tool()
async def traceroute(host: str) -> str:
    """Trace route to a host."""
    try:
        cmd = ["tracert", host] if __import__("sys").platform == "win32" else ["traceroute", host]
        result = await asyncio.to_thread(
            subprocess.run, cmd, capture_output=True, text=True, timeout=30
        )
        return f"Traceroute to {host}:\n{result.stdout}"
    except subprocess.TimeoutExpired:
        return f"Traceroute timed out for {host}"
    except Exception as e:
        return f"Traceroute error: {str(e)}"


@function_tool()
async def check_http(url: str) -> str:
    """Check HTTP response from a URL."""
    import urllib.request
    try:
        start = time.time()
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'ZENITH/1.0')
        response = urllib.request.urlopen(req, timeout=10)
        elapsed = time.time() - start
        return f"HTTP {response.status} {response.reason}\nResponse Time: {elapsed*1000:.0f}ms\nContent-Type: {response.headers.get('Content-Type', 'unknown')}"
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return f"HTTP error: {str(e)
}"

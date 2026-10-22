#!/usr/bin/env python3
"""Helper to query Brek MCP and return structuredContent room offers & prices."""
import json
import subprocess
import sys


def mcp_post(url: str, payload: dict, session_id: str | None = None, extra_headers: dict | None = None):
    cmd = [
        "curl",
        "-sS",
        "-i",
        "-X",
        "POST",
        url,
        "-H",
        "Content-Type: application/json",
        "-H",
        "Accept: application/json, text/event-stream",
        "-H",
        (
            "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ),
    ]
    if session_id:
        cmd.extend(["-H", f"Mcp-Session-Id: {session_id}"])
    if extra_headers:
        for k, v in extra_headers.items():
            cmd.extend(["-H", f"{k}: {v}"])
    cmd.extend(["--data-raw", json.dumps(payload)])

    res = subprocess.run(cmd, capture_output=True, text=True, timeout=35, check=True)
    raw = res.stdout
    headers_part, _, body_part = raw.partition("\r\n\r\n")
    if not body_part and "\n\n" in raw:
        headers_part, _, body_part = raw.partition("\n\n")

    new_session = session_id
    for line in headers_part.splitlines():
        if line.lower().startswith("mcp-session-id:"):
            new_session = line.split(":", 1)[1].strip()

    for line in reversed(body_part.splitlines()):
        if line.startswith("data:"):
            data_str = line[len("data:") :].strip()
            if data_str:
                return json.loads(data_str), new_session
    return json.loads(body_part.strip()), new_session


def call_brek(tool_name: str, arguments: dict) -> dict:
    url = "https://mcp.brek.com/mcp"
    _, session_id = mcp_post(
        url,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "travel-planner", "version": "1.0"},
            },
        },
    )
    res, _ = mcp_post(
        url,
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        },
        session_id=session_id,
    )
    result = res.get("result", {})
    return {
        "text": [c.get("text") for c in result.get("content", []) if c.get("type") == "text"],
        "structuredContent": result.get("structuredContent"),
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: fetch_brek_offers.py <tool_name> '<json_args>'")
        sys.exit(1)
    out = call_brek(sys.argv[1], json.loads(sys.argv[2]))
    print(json.dumps(out, indent=2))

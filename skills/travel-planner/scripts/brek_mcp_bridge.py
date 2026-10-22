#!/usr/bin/env python3
"""Stdio MCP Bridge for Brek (https://mcp.brek.com/mcp).

Forwards JSON-RPC requests to Brek's remote MCP server and automatically merges
`structuredContent` into `content[0].text` so MCP clients that ignore `structuredContent`
receive the full room-offer and pricing array.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fetch_brek_offers import mcp_post

BREK_URL = "https://mcp.brek.com/mcp"


def main() -> None:
    session_id: str | None = None
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = req.get("method", "")
        req_id = req.get("id")

        # Notifications (no id)
        if req_id is None:
            try:
                mcp_post(BREK_URL, req, session_id=session_id)
            except Exception:
                pass
            continue

        try:
            resp, session_id = mcp_post(BREK_URL, req, session_id=session_id)
            if method == "tools/call" and "result" in resp:
                result = resp["result"]
                sc = result.get("structuredContent")
                if sc is not None:
                    content = result.get("content", [])
                    sc_json = json.dumps(sc, indent=2)
                    if content and content[0].get("type") == "text":
                        content[0]["text"] = f"{content[0].get('text', '')}\n\n--- structuredContent ---\n{sc_json}"
                    else:
                        content.insert(0, {"type": "text", "text": sc_json})
                    result["content"] = content
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as exc:
            err_resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(exc)},
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()

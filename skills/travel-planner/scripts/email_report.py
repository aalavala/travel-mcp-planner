#!/usr/bin/env python3
"""Send a Markdown travel report to aalavala@gmail.com via AWS SES (HTML + Plain Text)."""
import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def inline_md(text: str) -> str:
    """Convert inline markdown (links, bold, italics, code, br) to safe HTML."""
    # Preserve <br> tags using placeholder
    text = re.sub(r"<br\s*/?>", "\x00BR\x00", text, flags=re.IGNORECASE)
    escaped = html.escape(text)
    escaped = escaped.replace("\x00BR\x00", "<br>")
    # Links [label](url)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^\)]+)\)",
        r'<a href="\2" style="color:#0b57d0;text-decoration:underline;font-weight:600;">\1</a>',
        escaped,
    )
    # Bold **text**
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    # Italic *text*
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)
    # Inline code `code`
    escaped = re.sub(
        r"`([^`]+)`",
        r'<code style="background:#f1f3f4;padding:2px 5px;border-radius:4px;font-family:monospace;">\1</code>',
        escaped,
    )
    return escaped


def md_to_html(md_text: str) -> str:
    """Zero-dependency Markdown-to-HTML converter optimized for email clients (Gmail)."""
    lines = md_text.splitlines()
    out: list[str] = [
        '<div style="font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,Helvetica,Arial,sans-serif;'
        'color:#1f1f1f;line-height:1.5;max-width:960px;margin:0 auto;padding:16px;">'
    ]
    in_table = False
    in_ul = False
    in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def close_table():
        nonlocal in_table
        if in_table:
            out.append("</tbody></table>")
            in_table = False

    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        # Table detection
        if stripped.startswith("|") and stripped.endswith("|"):
            close_lists()
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            # Check if next line is separator | :--- |
            if not in_table and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
                out.append(
                    '<table style="border-collapse:collapse;width:100%;margin:14px 0;font-size:14px;">'
                    "<thead><tr>"
                )
                for c in cells:
                    out.append(
                        f'<th style="border:1px solid #d0d7de;background:#f6f8fa;padding:8px 10px;text-align:left;">'
                        f"{inline_md(c)}</th>"
                    )
                out.append("</tr></thead><tbody>")
                in_table = True
                i += 2
                continue
            elif in_table:
                out.append("<tr>")
                for c in cells:
                    out.append(
                        f'<td style="border:1px solid #d0d7de;padding:8px 10px;vertical-align:top;">'
                        f"{inline_md(c)}</td>"
                    )
                out.append("</tr>")
                i += 1
                continue
        else:
            close_table()

        if not stripped:
            close_lists()
            i += 1
            continue

        if stripped == "---":
            close_lists()
            out.append('<hr style="border:none;border-top:1px solid #d0d7de;margin:20px 0;">')
        elif stripped.startswith("# "):
            close_lists()
            out.append(f'<h1 style="font-size:22px;margin:20px 0 8px;">{inline_md(stripped[2:])}</h1>')
        elif stripped.startswith("## "):
            close_lists()
            out.append(
                f'<h2 style="font-size:18px;margin:20px 0 8px;border-bottom:1px solid #eaecef;padding-bottom:4px;">'
                f"{inline_md(stripped[3:])}</h2>"
            )
        elif stripped.startswith("### "):
            close_lists()
            out.append(f'<h3 style="font-size:15px;margin:16px 0 6px;">{inline_md(stripped[4:])}</h3>')
        elif re.match(r"^[-*]\s+", stripped):
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append('<ul style="margin:6px 0 12px 20px;padding:0;">')
                in_ul = True
            item_text = re.sub(r"^[-*]\s+", "", stripped)
            out.append(f'<li style="margin:4px 0;">{inline_md(item_text)}</li>')
        elif re.match(r"^\d+\.\s+", stripped):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append('<ol style="margin:6px 0 12px 20px;padding:0;">')
                in_ol = True
            item_text = re.sub(r"^\d+\.\s+", "", stripped)
            out.append(f'<li style="margin:4px 0;">{inline_md(item_text)}</li>')
        else:
            close_lists()
            out.append(f'<p style="margin:8px 0;">{inline_md(stripped)}</p>')

        i += 1

    close_lists()
    close_table()
    out.append("</div>")
    return "\n".join(out)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: email_report.py <report.md> [subject] [recipient]")
        return 1

    report_path = Path(sys.argv[1]).expanduser().resolve()
    subject = (
        sys.argv[2]
        if len(sys.argv) >= 3
        else f"Travel Report: {report_path.stem.replace('_', ' ').title()}"
    )
    recipients = (
        [r.strip() for r in sys.argv[3].split(",") if r.strip()]
        if len(sys.argv) >= 4
        else ["aalavala@yahoo.com", "aalavala@gmail.com"]
    )

    body_text = report_path.read_text(encoding="utf-8")
    body_html = md_to_html(body_text)
    payload = {
        "Source": "aalavala@gmail.com",
        "Destination": {"ToAddresses": recipients},
        "Message": {
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {
                "Text": {"Data": body_text, "Charset": "UTF-8"},
                "Html": {"Data": body_html, "Charset": "UTF-8"},
            },
        },
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(payload, tmp)
        tmp_path = tmp.name

    try:
        res = subprocess.run(
            ["aws", "ses", "send-email", "--cli-input-json", f"file://{tmp_path}"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(res.stdout.strip())
        return 0
    finally:
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Clean a YouTube auto-generated VTT into plain readable text.

Auto-VTT has heavy duplication: each visible word appears in a "rolling caption"
block AND as inline <c> tags. We extract only the inline tag content (the
authoritative word stream) and assemble it into paragraphs.
"""
import re
import sys
from pathlib import Path

def clean(vtt_text: str) -> str:
    out_words = []
    seen_lines = set()
    for line in vtt_text.splitlines():
        # Skip headers and timing cues
        if not line.strip(): continue
        if line.startswith("WEBVTT"): continue
        if line.startswith("Kind:") or line.startswith("Language:"): continue
        if "-->" in line: continue
        if "align:" in line and not "<" in line: continue
        # Strip inline tags: <00:00:00.240><c> wake</c> -> wake
        text = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", line)
        text = re.sub(r"</?c[^>]*>", "", text)
        text = text.strip()
        if not text: continue
        # The "rolling" plain lines are duplicates of the inline-tag content.
        # If a line had no inline tags, skip it to avoid duplication.
        if "<c>" not in line and "<" not in line:
            continue
        if text in seen_lines:
            continue
        seen_lines.add(text)
        out_words.append(text)
    raw = " ".join(out_words)
    # Collapse multiple spaces
    raw = re.sub(r"\s+", " ", raw).strip()
    # Insert paragraph breaks roughly every ~80 words at a sentence boundary.
    words = raw.split(" ")
    out = []
    para = []
    for w in words:
        para.append(w)
        if len(para) >= 80 and w.endswith((".", "!", "?")):
            out.append(" ".join(para))
            para = []
    if para:
        out.append(" ".join(para))
    return "\n\n".join(out)

if __name__ == "__main__":
    src = Path(sys.argv[1])
    txt = clean(src.read_text(encoding="utf-8", errors="replace"))
    out = src.with_suffix(".txt")
    out.write_text(txt, encoding="utf-8")
    print(f"wrote {out} ({len(txt)} chars, {len(txt.split())} words)")

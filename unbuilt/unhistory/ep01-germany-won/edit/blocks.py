"""Narration blocks, read from ../SCRIPT.md in order: [(block_id, spoken_text), ...].

Bracketed notes such as [M] or [YOUR CALL] are stripped. C5 (the title card) has no narration and is left out.
"""
import os
import re

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SCRIPT.md")


def blocks():
    body = open(SCRIPT).read().split("## COLD OPEN")[1].split("## Notes for the owner")[0]
    out, cur = [], None
    for line in body.splitlines():
        m = re.match(r"\*\*\[([A-Z]\d+)\]", line)
        if m:
            cur = m.group(1)
            out.append([cur, ""])
        elif line.startswith("> ") and not line.startswith("> *Note") and cur:
            text = re.sub(r"\[[^\]]*\]", "", line[2:]).replace("*", "").strip()
            out[-1][1] = (out[-1][1] + " " + text).strip()
    return [(b, t) for b, t in out if t]


def claim_tags():
    """{block: "HAPPENED" | "LIKELY" | "GUESS"} from the bold block lines of SCRIPT.md."""
    out = {}
    for line in open(SCRIPT):
        m = re.match(r"\*\*\[([A-Z]\d+)\]\*\*.*\*\*\[(HAPPENED|LIKELY|GUESS)\]\*\*", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


if __name__ == "__main__":
    for b, t in blocks():
        print(f"{b:4} {t}")

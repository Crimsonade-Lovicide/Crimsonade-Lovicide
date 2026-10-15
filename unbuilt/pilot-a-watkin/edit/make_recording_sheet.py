"""Write ../RECORDING.md from SCRIPT.md, so the read order always matches what split_narration.py expects."""
from blocks import blocks

SECTIONS = {"C": "Cold open", "E": "1. Eiffel envy", "D": "2. Sixty-eight designs", "B": "3. Building it",
            "W": "4. Why it stopped", "S": "5. What's there now", "O": "Outro"}
HEAD = """# Recording sheet: Pilot A, Watkin's Tower

This is your read, block by block, in the exact order the edit expects.

## How to record

1. **Room:** quiet, with soft furnishings (curtains, a sofa, a bed). Avoid bare walls and kitchens. Turn off fans and the fridge if you can hear them.
2. **Microphone:** about a hand's width from your mouth, slightly off to one side. A phone works if you don't have a mic yet. Use its voice-memo app, held the same way.
3. **Level:** your loudest words should never hit the red. Leave headroom, because quiet is fixable and distortion isn't.
4. **Read each block, then stay silent for about two seconds** before the next one. **This matters.** The edit finds the blocks by those pauses, so every block needs its pause, including the short ones.
5. **Retakes:** if you fluff a block, pause, then read the **whole block** again. **Then tell me which blocks you retook** (for example "D4 twice"). I'll use the last take.
6. **Pace:** slower than feels natural. Conversational, not announcer. Smile slightly on the lighter lines.
7. **O2:** say your name, or just "This was UNBUILT". Your choice.
8. **One file or several:** one long file is easiest. If you split it, name the files in order (part1, part2, …).

## Getting the file to me

- **Easiest:** put it in your Google Drive and tell me the file name. I can download it from there.
- **Format:** whatever your device makes is fine (WAV, M4A or MP3). WAV is best.

---
"""


def main():
    lines, prev, n = [HEAD], None, 0
    for b, t in blocks():
        if b[0] != prev:
            lines += [f"## {SECTIONS[b[0]]}", ""]
            prev = b[0]
        n += 1
        lines += [f"**{n}. [{b}]**  {t}", "", " *(pause)*", ""]
    lines += ["---", "", f"That's {n} blocks. Thank you."]
    open("../RECORDING.md", "w").write("\n".join(lines) + "\n")
    print(n, "blocks")


if __name__ == "__main__":
    main()

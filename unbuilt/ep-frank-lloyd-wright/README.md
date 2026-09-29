# UNBUILT Special No. 3: Frank Lloyd Wright

A Hugo Ashby countdown of five unbuilt Wright projects, escalating in scale: the Automobile Objective, Pittsburgh's Point Park Civic Center, the Plan for Greater Baghdad, Broadacre City and the Mile-High Illinois. Crystal Heights is the stinger.

**State (29 Sep 2026):** script, shot plan and wardrobe references done. Nothing else rendered: 0.25 credits spent so far.

## Files

- `RESEARCH.md`: every figure and quote, with sources and a confidence rating, plus the myths the script avoids.
- `SCRIPT.md`: the script, about 1,140 spoken words, running about 7:45.
- `build_shotlist.py`: builds `shotlist.json` (full generation prompts) and `SHOTLIST.md` (the readable plan and budget). It reads each spoken line from `SCRIPT.md` by shot ID. Run it with `python3 build_shotlist.py`.
- `SHOTLIST.md` and `shotlist.json`: the output.

## Before rendering

1. **Approve the spend.** The plan is about 810 credits, or about 608 lean, against about 563 available.
2. ~~Make the wardrobe references.~~ Done 29 Sep, for 0.25 credits: `host/hugo_wright_portrait.jpg` (`292cd695-…`) and `host/hugo_wright_portrait_alt.jpg` (`8fa8b468-…`). Both are GPT Image 2.5 edits of the locked hero portrait, both hold the likeness, and both are now in `HOST_REFS`.
3. **Check the quotes** against the page scans listed in the script notes.
4. **Render in the same order as Special No. 2:**
   - voice lines first;
   - then Hugo's shots, checking each with `qc_sync.py`, mouth strip included;
   - then stills and moving shots.

   The edit scripts (`assemble.py`, `score.py`, `shorts.py`, `qc_sync.py`) come from `ep-monuments-to-the-dead/edit/`, with the Halloween identity removed.

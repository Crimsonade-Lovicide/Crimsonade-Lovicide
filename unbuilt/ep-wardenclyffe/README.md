# Wardenclyffe: Shorts

"Tesla's Tower Wasn't Killed by a Banker. It Was a Hotel Bill." is a standard episode hosted by Chiara Valenti, live at https://youtu.be/ZR6H4mVwAMs. It went public on 28 Sep 2026.

The episode itself was built in another session and isn't in this repo. This folder only cuts Shorts from its finished 9:16 master, Higgsfield media `8a5e17d6-…`, at no credit cost. That master carries the 16:9 picture as a full-width band at y = 656–1263.

- `shorts.py`: cuts each Short from one continuous stretch of the master, so the music under the voice never jumps.
  - The layout matches the standard episodes' other Shorts: an ivory Bebas Neue title with amber key words, the picture full width, captions in short phrases, and the UNBUILT footer.
- `youtube/SHORTS.md`: titles, descriptions and schedule.

## Rebuild

```
ffmpeg -i master_9x16.mp4 -vn -ac 2 -ar 48000 mix.wav
# transcribe mix.wav with faster-whisper small.en, word_timestamps=True, and save the segments as
# transcript.json: [{"start", "end", "text", "words": [[word, start, end], ...]}, ...]
python3 shorts.py master_9x16.mp4 transcript.json <out_dir> [hotel_bill|morgan|castle|dynamite|worked]
```

The fonts come from `$FONTS` (Bebas Neue) and `$MONO` (DejaVu Sans Mono).

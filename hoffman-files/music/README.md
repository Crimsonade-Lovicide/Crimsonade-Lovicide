# Hoffman Files music (shared by every episode)

- **Theme: "Measured in Sunlight"** (`measured_in_sunlight.mp3`, not committed). Made with Gemini; commercial use
  confirmed by Eric Hoffman, Oct 7 2026. Keep the generation record (prompt, date, account and plan) with the masters.
  It opens every episode (its first full-section downbeat, 0:56.70, lands on the title card) and closes it
  (the outro, 2:30.2 to the end, finishes with the end card).
- **Act music: public domain.** Musopen Kickstarter recordings (2012), released to the public domain; compositions
  public domain too. `./fetch_music.sh` downloads them from the Internet Archive and checks the SHA-256 sums in
  `PROVENANCE.json` (keep that file: it answers any false Content ID claim).

Mixing note: classical recordings put 67-78% of their energy in the speech band, so act cues are compressed and get a
4 dB dip around 1.8 kHz before they are ducked under the voice (see `ep01-hot-coffee/edit/music_cues.py`).

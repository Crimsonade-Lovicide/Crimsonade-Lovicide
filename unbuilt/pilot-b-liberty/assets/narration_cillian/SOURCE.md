# Pilot B narration (synthetic)

26 blocks, one file per script block in SCRIPT.md order (C4, the silent title card, has no file).
Voice: Higgsfield preset "Cillian", ElevenLabs engine (text2speech_v2), generated 12 Oct 2026 from the
text in SCRIPT.md. The owner chose a synthetic narrator for this episode instead of recording it.

Because the narration is AI-generated, upload with "Altered or synthetic content: Yes" and say so in the description.

Rebuild the voice track: join the blocks with 2 s gaps into edit/build/cillian_recording.wav, then
`python3 edit/split_narration.py edit/build/cillian_recording.wav`.

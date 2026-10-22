"""Music for ep. 1: the series theme opens and closes; public domain recordings carry the acts.

Theme: "Measured in Sunlight" (made with Gemini; commercial use confirmed by Eric Hoffman, Oct 7 2026).
  open : the song's first full-section downbeat (HIT) lands on the title card; fades under the next segment
  close: the song's outro (CLOSE_IN to the end) finishes with the end card
Acts: Musopen Kickstarter recordings, released to the public domain (see music_pd/PROVENANCE.json).
Each act cue: (first segment, segment that ends it or None = until the theme close, file, composer/work, performer)."""
THEME = dict(file='measured_in_sunlight.mp3', hit=56.70, title_seg='s03', fade_seg='s04', fade=3.0,
             close_in=150.20, song_end=175.70)
CUES = [
    ('s04', 's06', 'goldberg_aria.flac', 'Bach, Goldberg Variations, Aria', 'Shelley Katz'),
    ('s06', 's13', 'schubert_d959_andantino.flac', 'Schubert, Sonata in A, D. 959, II. Andantino', 'Paul Pitman'),
    ('s13', 's27', 'dvorak_american_lento.flac', 'Dvorak, String Quartet No. 12 "American", II. Lento', 'Musopen String Quartet'),
    ('s27', 's29', 'aase_death.flac', "Grieg, Peer Gynt, Aase's Death", 'Czech National Symphony Orchestra'),
    ('s29', None, 'suk_meditation.flac', 'Suk, Meditation on an Old Czech Chorale', 'Musopen String Quartet'),
]
XFADE = 2.5          # seconds of crossfade between cues
TARGET_DB = -27.0    # act cues: RMS level before ducking under the voice
THEME_DB = -21.0     # the theme sits higher: it is the show's signature and plays mostly without narration
# classical recordings put most of their energy where speech lives: tame the dynamics and carve a pocket
ACT_FILTER = 'highpass=f=40,acompressor=threshold=-26dB:ratio=3:attack=20:release=400,equalizer=f=1800:width_type=o:width=1.6:g=-4'
THEME_FILTER = 'equalizer=f=1800:width_type=o:width=1.6:g=-2'

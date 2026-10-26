"""Ep. 2 music: Eric's theme "Measured in Sunlight" opens and closes; public domain Musopen recordings carry the acts.
Files and SHA-256 checksums: ../../music/PROVENANCE.json. The theme's downbeat (56.70 s) lands on the title card; its
outro (150.20 s to the end) runs under the last line, the sign-off and the end card.
A cue marked 'cut' stops dead at its end instead of crossfading: Aase's Death ends right after "never tried",
and the next two seconds are silent."""
THEME = dict(file='measured_in_sunlight.mp3', hit=56.70, title_seg='s03', fade_seg='s04', fade=3.0,
             close_in=150.20, song_end=175.70)
CUES = [
    ('s04', 's10', 'schubert_d959_andantino.flac', 'Schubert, Sonata in A, D. 959, II. Andantino', 'Paul Pitman'),
    ('s10', 's18', 'egmont_overture.flac', 'Beethoven, Egmont Overture, Op. 84 (opening)', 'Czech National Symphony Orchestra'),
    ('s18', 's21', 'dvorak_american_lento.flac', 'Dvorak, String Quartet No. 12 "American", II. Lento', 'Musopen String Quartet'),
    ('s21', 's23', 'aase_death.flac', "Grieg, Peer Gynt, Aase's Death", 'Czech National Symphony Orchestra', 'cut'),
    ('s24', None, 'suk_meditation.flac', 'Suk, Meditation on an Old Czech Chorale', 'Musopen String Quartet'),
]
XFADE = 2.5; TARGET_DB = -27.0; THEME_DB = -21.0
ACT_FILTER = 'highpass=f=40,acompressor=threshold=-26dB:ratio=3:attack=20:release=400,equalizer=f=1800:width_type=o:width=1.6:g=-4'
THEME_FILTER = 'equalizer=f=1800:width_type=o:width=1.6:g=-2'

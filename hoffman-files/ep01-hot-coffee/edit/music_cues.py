"""Music cue sheet for ep. 1: Epidemic Sound tracks chosen per act (dark, steady, low energy in the
300-3400 Hz voice band so they sit under narration). Downloading/licensing needs an Epidemic Sound plan
that covers the channel; until then the review cut uses the public preview files.

Each cue: (first segment, segment that ends it or None for the end, file stem, Epidemic Sound id, title, artist)."""
CUES = [
    ('s01', 's06', 'unfinished_stories', '1419406f-2b2b-42cc-a51c-2d85994050dd', 'Unfinished Stories', 'Lennon Hutton'),
    ('s06', 's13', 'consequences', 'f43d8d7f-2f0d-4238-9629-1035c18afd4a', 'Consequences', 'Magnus Ludvigsson'),
    ('s13', 's27', 'dox', '07e2e4ec-0727-4b5a-a76a-c360d6afb20e', 'DOX', 'Lennon Hutton'),
    ('s27', 's29', 'when_the_sun_sets', '34eb8980-d894-489b-92bd-3c080c49e364', 'When the Sun Sets', 'Anna Landström'),
    ('s29', None, 'life_in_peace', '35ba5310-ccb4-321a-9f6c-ceb41888cdab', 'Life in Peace', 'David Celeste'),
]
XFADE = 2.5        # seconds of crossfade between cues
TARGET_DB = -27.0  # each cue is levelled to this RMS before ducking under the voice

#!/bin/bash
# Temp/fallback score for ep. 2: Musopen Kickstarter recordings (public domain), pulled one track at a time from the
# 7.5 GB Internet Archive zip, then checked against the SHA-256 sums in PROVENANCE.json.
cd "$(dirname "$0")"
B="https://archive.org/download/musopen-lossless-dvd-flac/Musopen%20DVD%20%28FLAC-Lossless%29.zip/Musopen%20DVD%20%28FLAC-Lossless%29%2F"
while IFS='|' read name path; do
  [ -f "$name.flac" ] || curl -sSL -o "$name.flac" "$B$path"
done <<'LIST'
goldberg_var25|Goldberg%20Variations%2FGoldberg%20Variations%2C%20BWV.%20988%20-%20Variation%2025.flac
goldberg_aria|Goldberg%20Variations%2FGoldberg%20Variations%2C%20BWV%20988%20-%20Aria.flac
egmont_overture|Beethoven%20-%20Egmont%20Overture%20Op%2084%2FEgmont%20Overture%20Op.%2084.flac
aase_death|Grieg%20-%20Peer%20Gynt%2FPeer%20Gynt%20Suite%20No.%201%2C%20Op.%2046%20-%20II.%20Aase%27s%20Death.flac
brahms3_poco_allegretto|Brahms%20-%20Symphony%20No%203%2FSymphony%20No.%203%20in%20F%20Major%2C%20Op.%2090%20-%20III.%20Poco%20allegretto.flac
suk_meditation|String%20Quartets%2FSuk%20-Meditation%2FMeditation.flac
beethoven_malinconia|String%20Quartets%2FBeethoven%20String%20Quartet%20in%20B%20flat%20Major%20Op%2018%2FString%20Quartet%20No.%206%20in%20B%20Flat%20Major%2C%20Op.%2018%2C%20No.%206%20-%20IV.%20%28Adagio%29%20La%20Malinconia.flac
dvorak_american_lento|String%20Quartets%2FDvorak%20-%20American%20in%20F%20major%2FString%20Quartet%20No.%2012%20in%20F%20Major%2C%20Op.%2096%2C%20American%20-%20II.%20Lento.flac
schubert_d959_andantino|Schubert%20-%20The%20Piano%20Sonatas%2FSonata%20in%20A%20Minor%2C%20D.%20959%20-%20II.%20Andantino.flac
LIST
python3 -c "
import json,hashlib
for t in json.load(open('PROVENANCE.json'))['tracks']:
    ok = hashlib.sha256(open(t['file'],'rb').read()).hexdigest() == t['sha256']
    print(('OK  ' if ok else 'BAD ') + t['file'])"

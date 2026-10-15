# Fetching the photographs

Wikimedia Commons rate-limits this machine (HTTP 429), so the originals were imported through Higgsfield's
media_import_url and downloaded from its CDN into raw/. The import costs no credits, and there is no generation or
editing. Every file was checked against its Commons original size. Sources and licences are in rights.csv.

Exception: D04 is Commons' own 1920 px render of page 6 of the protocol's DjVu scan, which is public domain.

Prep done in the edit, not on the originals:
- R03: rotate upright (EXIF orientation 6).
- H04: crop off the "IWM" watermark, bottom right.
- H01: crop to Lord Halifax, on the right.

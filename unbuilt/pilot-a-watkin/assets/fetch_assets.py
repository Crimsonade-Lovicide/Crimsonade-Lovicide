#!/usr/bin/env python3
"""Rebuild assets/raw/ for Pilot A (Watkin's Tower) from the URLs in assets/rights.csv.

Downloads ORIGINAL files only: no resizing, no re-encoding, no upscaling, no AI.
Then converts the Natural Earth shapefiles to GeoJSON (pure Python, pyshp) and
writes small region clips for the Manchester-London-Dover-Paris map to assets/geo/
(including assets/geo/land.geojson, which edit/build.py uses for the E3 route map).

Usage:
    pip install requests pyshp pillow
    python3 assets/fetch_assets.py            # download what is missing, then build map data
    python3 assets/fetch_assets.py --force    # re-download everything
    python3 assets/fetch_assets.py --only A02_spec_p8.jpg W03_today_arch_close.jpg

Polite by design: descriptive User-Agent, one request at a time, a pause between
requests, and exponential back-off honouring Retry-After on HTTP 429/5xx.
"""
import argparse
import csv
import io
import json
import sys
import time
import zipfile
from pathlib import Path

import requests

UA = "UNBUILT-research/1.0 (contact via YouTube @unbuiltdoc)"
HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
GEO = HERE / "geo"
CSV = HERE / "rights.csv"
PAUSE = {"upload.wikimedia.org": 10.0, "iiif.archive.org": 1.0, "archive.org": 1.0, "naciscdn.org": 0.5}

# Region for the route map: covers Manchester, London, Dover, the Channel and Paris with margin.
REGION = (-7.0, 47.5, 6.0, 56.5)  # min lon, min lat, max lon, max lat (WGS84)

# City coordinates (WGS84, decimal degrees; city-centre / landmark points).
CITIES = {
    "Manchester": {"lat": 53.4808, "lon": -2.2426, "note": "city centre (Albert Square)"},
    "London": {"lat": 51.5074, "lon": -0.1278, "note": "Charing Cross"},
    "London Baker Street": {"lat": 51.5226, "lon": -0.1571, "note": "Metropolitan Railway terminus"},
    "Wembley Park (tower site)": {"lat": 51.5560, "lon": -0.2796, "note": "Wembley Stadium centre spot"},
    "Dover": {"lat": 51.1279, "lon": 1.3134, "note": "town / harbour"},
    "Shakespeare Cliff (Watkin's 1880s tunnel heading)": {"lat": 51.1050, "lon": 1.2620, "note": "approximate"},
    "Calais": {"lat": 50.9513, "lon": 1.8587, "note": "town"},
    "Sangatte (French 1880s heading)": {"lat": 50.9450, "lon": 1.7500, "note": "approximate"},
    "Paris": {"lat": 48.8566, "lon": 2.3522, "note": "Hotel de Ville"},
    "Eiffel Tower": {"lat": 48.8584, "lon": 2.2945, "note": "for scale shots"},
}

session = requests.Session()
session.headers["User-Agent"] = UA


TRIES = 8


def fetch(url, dest, tries=None):
    tries = tries or TRIES
    host = url.split("/")[2]
    delay = 15
    for attempt in range(tries):
        try:
            r = session.get(url, timeout=120, stream=True)
        except requests.RequestException as e:
            print(f"    network error {e}; retry in {delay}s")
            time.sleep(delay)
            delay = min(delay * 2, 300)
            continue
        if r.status_code == 429 or r.status_code >= 500:
            ra = r.headers.get("retry-after", "")
            wait = int(ra) + 2 if ra.isdigit() else delay
            if attempt == tries - 1:
                print(f"    HTTP {r.status_code} (Retry-After {ra or '?'}s); giving up for this run")
                break
            print(f"    HTTP {r.status_code}; sleeping {wait}s")
            time.sleep(wait)
            delay = min(delay * 2, 300)
            continue
        r.raise_for_status()
        tmp = dest.with_suffix(dest.suffix + ".part")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 16):
                f.write(chunk)
        tmp.replace(dest)
        time.sleep(PAUSE.get(host, 1.0))
        return True
    print(f"    GAVE UP on {url}")
    return False


def image_size(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None


def download(rows, force=False, only=None):
    RAW.mkdir(parents=True, exist_ok=True)
    failed = []
    for row in rows:
        fn = row["file"]
        if only and fn not in only:
            continue
        dest = RAW / fn
        if dest.exists() and not force:
            print(f"  have  {fn}")
            continue
        print(f"  get   {fn}  <-  {row['download_url']}")
        if not fetch(row["download_url"], dest):
            failed.append(fn)
            continue
        size = image_size(dest)
        if size and row.get("width") and row.get("height"):
            exp = (int(row["width"]), int(row["height"]))
            if size != exp:
                print(f"    WARNING: got {size[0]}x{size[1]}, rights.csv says {exp[0]}x{exp[1]}")
    return failed


# ---------- Natural Earth: shapefile -> GeoJSON (pure Python) ----------

def _bbox_hits(bb, region=REGION):
    return not (bb[2] < region[0] or bb[0] > region[2] or bb[3] < region[1] or bb[1] > region[3])


def _ring_bbox(coords):
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    return (min(xs), min(ys), max(xs), max(ys))


def _round(coords, nd=5):
    return [[round(x, nd), round(y, nd)] for x, y in coords]


def shp_to_features(zpath, keep_fields=None):
    import shapefile  # pyshp

    with zipfile.ZipFile(zpath) as z:
        stem = [n for n in z.namelist() if n.endswith(".shp")][0][:-4]
        rd = shapefile.Reader(shp=io.BytesIO(z.read(stem + ".shp")), shx=io.BytesIO(z.read(stem + ".shx")),
                              dbf=io.BytesIO(z.read(stem + ".dbf")), encoding="utf-8", encodingErrors="replace")
        names = [f[0] for f in rd.fields[1:]]
        for sr in rd.iterShapeRecords():
            props = dict(zip(names, sr.record))
            if keep_fields:
                props = {k: props.get(k) for k in keep_fields if k in props}
            geo = sr.shape.__geo_interface__
            yield {"type": "Feature", "properties": props, "geometry": geo}


def clip_feature(feat):
    """Keep only the parts (lines / polygons) whose bbox touches REGION. Not a geometric clip."""
    g = feat["geometry"]
    t = g["type"]
    if t == "LineString":
        parts = [g["coordinates"]] if _bbox_hits(_ring_bbox(g["coordinates"])) else []
        if not parts:
            return None
        return {**feat, "geometry": {"type": "LineString", "coordinates": _round(parts[0])}}
    if t == "MultiLineString":
        parts = [_round(l) for l in g["coordinates"] if _bbox_hits(_ring_bbox(l))]
        if not parts:
            return None
        return {**feat, "geometry": {"type": "MultiLineString", "coordinates": parts}}
    if t == "Polygon":
        polys = [g["coordinates"]]
    elif t == "MultiPolygon":
        polys = g["coordinates"]
    else:
        return None
    keep = [[_round(r) for r in p] for p in polys if _bbox_hits(_ring_bbox(p[0]))]
    if not keep:
        return None
    return {**feat, "geometry": {"type": "MultiPolygon", "coordinates": keep}}


def build_map():
    try:
        import shapefile  # noqa: F401
    except ImportError:
        print("  pyshp not installed (pip install pyshp); skipping map conversion")
        return
    GEO.mkdir(parents=True, exist_ok=True)
    country_fields = ["NAME", "NAME_EN", "ADM0_A3", "ISO_A3", "SOVEREIGNT", "TYPE"]
    jobs = [
        ("N01_ne_10m_coastline.zip", "ne_10m_coastline", None),
        ("N02_ne_10m_admin_0_countries.zip", "ne_10m_admin_0_countries", country_fields),
        ("N03_ne_50m_coastline.zip", "ne_50m_coastline", None),
        ("N04_ne_50m_admin_0_countries.zip", "ne_50m_admin_0_countries", country_fields),
    ]
    for zname, stem, fields in jobs:
        zp = RAW / zname
        if not zp.exists():
            print(f"  missing {zname}; skipping")
            continue
        feats = list(shp_to_features(zp, fields))
        # Full-world GeoJSON stays in raw/ (large, git-ignored).
        full = RAW / f"{stem}.geojson"
        full.write_text(json.dumps({"type": "FeatureCollection", "features": feats}, separators=(",", ":")))
        clipped = [c for c in (clip_feature(f) for f in feats) if c]
        out = GEO / f"{stem}_uk_channel_france.geojson"
        out.write_text(json.dumps({"type": "FeatureCollection", "bbox": list(REGION), "features": clipped},
                                  separators=(",", ":")))
        print(f"  geo   {stem}: {len(feats)} features -> raw/{full.name}; {len(clipped)} in region -> geo/{out.name}")
        if stem == "ne_10m_admin_0_countries":
            # The edit build (edit/build.py -> kit.maproute) reads assets/geo/land.geojson: land polygons
            # with country borders, region-clipped. Same content as this clip.
            (GEO / "land.geojson").write_text(out.read_text())
            print("  geo   land.geojson (= 10m countries, region clip) for edit/build.py")
    cities = {"crs": "EPSG:4326 (WGS84 lon/lat)", "source": "Rounded public coordinates (OpenStreetMap / Wikipedia city-centre points); "
              "tunnel headings approximate.", "cities": CITIES, "route_order": ["Manchester", "London", "Dover", "Calais", "Paris"]}
    (GEO / "cities.json").write_text(json.dumps(cities, indent=2))
    print("  geo   cities.json written")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="re-download files that already exist")
    ap.add_argument("--only", nargs="*", help="only these file names")
    ap.add_argument("--no-map", action="store_true", help="skip the Natural Earth GeoJSON step")
    ap.add_argument("--tries", type=int, default=8, help="attempts per file (default 8; back-off between attempts)")
    a = ap.parse_args()
    global TRIES
    TRIES = a.tries
    with open(CSV, newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"{len(rows)} rows in {CSV.name}")
    failed = download(rows, a.force, set(a.only) if a.only else None)
    if not a.no_map:
        build_map()
    if failed:
        print("FAILED:", ", ".join(failed))
        sys.exit(1)
    print("done")


if __name__ == "__main__":
    main()

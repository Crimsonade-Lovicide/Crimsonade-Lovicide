"""Download Pilot B's Library of Congress pictures (all "no known restrictions on publication") at up to 3000 px.

Wikimedia Commons rate-limits this machine, so Commons files come in through the import noted in rights.csv.
Usage: python3 fetch_loc.py
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
IIIF = "https://tile.loc.gov/image-services/iiif/{}/full/!3000,3000/0/default.jpg"
ITEMS = {
    # asset id: (IIIF service id, LoC item page)
    "N01_springfield_1886-10-15_p2": None,     # full newspaper page: IIIF full/full of service:ndnp:mb:batch_mb_keres_ver01:data:sn83020847:00517171359:1886101501:1164
    "A05_khedive_ismail": ("service:pnp:cph:3c00000:3c04000:3c04800:3c04847v", "https://www.loc.gov/item/92500741/"),
    "A11_lesseps_statue_matson": ("service:pnp:matpc:01400:01448v", "https://www.loc.gov/pictures/item/mpc2004001448/"),
    "A14_liberty_aerial_highsmith": ("service:pnp:highsm:13700:13746", "https://www.loc.gov/item/2011631940/"),
}
# These have only small IIIF copies, so the master TIFF (86-208 MB) is fetched and reduced to 3000 px.
MASTERS = {
    "A06_suez_opening_blessing_1869": "cph/3b40000/3b42000/3b42000/3b42029u",   # https://www.loc.gov/item/91786320/
    "A09a_liberty_assembly_paris": "ds/14900/14922u",                         # https://www.loc.gov/item/2020634761/
    "A09b_liberty_workshop_hand_head": "ds/14900/14915u",                     # https://www.loc.gov/item/97502750/
    "A09c_liberty_head_1878": "ds/14900/14924u",                              # https://www.loc.gov/item/97502744/
}


def main():
    os.makedirs(os.path.join(HERE, "raw"), exist_ok=True)
    for aid, spec in ITEMS.items():
        if not spec:
            continue
        out = os.path.join(HERE, "raw", aid + ".jpg")
        if os.path.exists(out):
            continue
        r = subprocess.run(["curl", "-sS", "-m", "300", "-f", "-o", out, IIIF.format(spec[0])])
        print(aid, "ok" if r.returncode == 0 else "FAILED")
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    for aid, src in MASTERS.items():
        out = os.path.join(HERE, "raw", aid + ".jpg")
        if os.path.exists(out):
            continue
        tif = os.path.join(HERE, "raw", aid + ".tif")
        subprocess.run(["curl", "-sS", "-m", "900", "-f", "-o", tif,
                        f"https://tile.loc.gov/storage-services/master/pnp/{src}.tif"], check=True)
        im = Image.open(tif).convert("RGB")
        im.thumbnail((3000, 3000))
        im.save(out, quality=92)
        os.remove(tif)
        print(aid, "ok")


if __name__ == "__main__":
    main()

"""Pilot A shot list: one picture per narration block (C5 is the silent title card).

Each entry: block -> (toolkit function, kwargs). `duration` and `out` are filled in by build.py from the
recorded narration's timings. Images are referenced by asset number ("A03") and resolved in assets/raw/.
Every picture is a real archive item, a code-drawn graphic, or (marked PRESENT) a CC-licensed photo of
Wembley today that stands in for a Google Earth Studio shot until those exist. No generative AI.

Coordinates are fractions of each image (0,0 top-left), set by looking at the downloaded scans.
"""

SPEC_UNDERLINE = {"type": "underline", "from": (0.18, 0.52), "to": (0.86, 0.52)}   # clause 1 on the spec page (A02)

SHOTS = {
    # ---- cold open
    "C1": ("kenburns", dict(image="A03", start=(0.5, 0.80, 1.6), end=(0.5, 0.25, 1.6))),
    "C2": ("annotate", dict(image="A14", marks=[{"type": "label", "text": "155 FT", "pos": (0.08, 0.2), "anchor": "l", "size": 64}],
                            start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.06))),
    "C3": ("kenburns", dict(image="PRESENT_aerial", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.15), mode="cover")),
    "C4": ("annotate", dict(image="A02", marks=[SPEC_UNDERLINE], start=(0.5, 0.52, 1.6), end=(0.5, 0.52, 1.9))),
    "C5": ("title_card", dict(title="UNBUILT", subtitle="London's Eiffel Tower", fixed=2.5)),
    # ---- 1. Eiffel envy
    "E1": ("kenburns", dict(image="A12", start=(0.5, 0.5, 1.0), end=(0.35, 0.45, 1.5))),
    "E2": ("kenburns", dict(image="A21", start=(0.5, 0.4, 1.0), end=(0.5, 0.3, 1.25),
                            lower_third=("Sir Edward Watkin", "Railway chairman, 1819 to 1901"))),
    "E3": ("maproute", dict(stops=[("Manchester", -2.24, 53.48), ("London", -0.13, 51.51), ("Dover", 1.31, 51.13),
                                   ("Paris", 2.35, 48.86)], dashed=(2,), bbox=(-5.5, 47.6, 5.0, 54.6),
                            title="Watkin's dream: Manchester to Paris")),
    "E4": ("kenburns", dict(image="A17", start=(0.5, 0.5, 1.0), end=(0.6, 0.45, 1.3))),
    "E5": ("highlight", dict(image="A11", box=(0.1, 0.30, 0.9, 0.36))),
    # ---- 2. Sixty-eight designs
    "D1": ("highlight", dict(image="A02", box=(0.12, 0.47, 0.90, 0.57))),
    "D2": ("annotate", dict(image="A02", marks=[SPEC_UNDERLINE], start=(0.5, 0.52, 2.2), end=(0.5, 0.52, 2.3))),
    "D3": ("montage", dict(images=["A10a", "A10b", "A10c", "A10d", "A06", "A08", "A09", "A05"], cols=4, rows=2)),
    "D4": ("annotate", dict(image="A06", marks=[{"type": "label", "text": "spiral road", "pos": (0.62, 0.40), "anchor": "l", "size": 40},
                                                 {"type": "label", "text": "railway", "pos": (0.62, 0.55), "anchor": "l", "size": 40},
                                                 {"type": "label", "text": "parachute", "pos": (0.62, 0.20), "anchor": "l", "size": 40}])),
    "D5": ("annotate", dict(image="A08", marks=[{"type": "label", "text": "2,296 FT · GRANITE", "pos": (0.58, 0.25), "anchor": "l", "size": 46}])),
    "D6": ("kenburns", dict(image="A09", start=(0.5, 0.7, 1.2), end=(0.5, 0.35, 1.5))),
    "D7": ("kenburns", dict(image="A39page", start=(0.5, 0.5, 1.0), end=(0.5, 0.4, 1.3))),
    "D8": ("kenburns", dict(image="A05", start=(0.5, 0.85, 1.5), end=(0.5, 0.2, 1.5))),
    "D9": ("annotate", dict(image="A05", marks=[{"type": "label", "text": "Not in the 1890 catalogue", "pos": (0.55, 0.5), "anchor": "l", "size": 44}])),
    "D10": ("annotate", dict(image="A03", marks=[{"type": "label", "text": "1,200 FT", "pos": (0.62, 0.20), "anchor": "l", "size": 48},
                                                  {"type": "label", "text": "8 LEGS", "pos": (0.62, 0.70), "anchor": "l", "size": 48},
                                                  {"type": "label", "text": "£352,222", "pos": (0.62, 0.80), "anchor": "l", "size": 48}])),
    # ---- 3. Building it
    "B1": ("scale_compare", dict(items=[{"name": "Watkin's Tower (design)", "height_m": 366, "shape": "taper", "accent": True},
                                        {"name": "Eiffel Tower today", "height_m": 330, "shape": "taper"},
                                        {"name": "The Shard", "height_m": 310, "shape": "taper"},
                                        {"name": "Wembley arch", "height_m": 133, "shape": "arch"},
                                        {"name": "Big Ben", "height_m": 96}], title="Drawn to one scale")),
    "B2": ("annotate", dict(image="A03", marks=[{"type": "label", "text": "8 legs became 4", "pos": (0.62, 0.72), "anchor": "l", "size": 48}])),
    "B3": ("kenburns", dict(image="A16", start=(0.5, 0.5, 1.0), end=(0.5, 0.4, 1.2))),
    "B4": ("kenburns", dict(image="A22", start=(0.5, 0.4, 1.0), end=(0.5, 0.35, 1.2), lower_third=("May 1894", None))),
    "B5": ("scale_compare", dict(items=[{"name": "Watkin's Tower (design)", "height_m": 366, "shape": "taper", "accent": True},
                                        {"name": "Blackpool Tower (opened May 1894)", "height_m": 158, "shape": "taper"}],
                                 title="May 1894")),
    "B6": ("annotate", dict(image="A14", marks=[{"type": "label", "text": "155 FT built of 1,200", "pos": (0.06, 0.15), "anchor": "l", "size": 52}])),
    # ---- 4. Why it stopped
    "W1": ("kenburns", dict(image="A19", start=(0.4, 0.5, 1.0), end=(0.6, 0.5, 1.15))),
    "W2": ("quote_card", dict(quote="there was no money left to carry on", attribution="Philip Grant, Wembley History Society (Brent Archives)")),
    "W3": ("kenburns", dict(image="A14", start=(0.5, 0.5, 1.0), end=(0.5, 0.85, 1.8))),
    "W4": ("annotate", dict(image="A02", marks=[SPEC_UNDERLINE], start=(0.5, 0.52, 2.2), end=(0.5, 0.52, 2.4))),
    "W5": ("kenburns", dict(image="A15", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.15), lower_third=("'Watkin's Folly'", None))),
    "W6": ("timeline", dict(events=[(1889, "Brief issued"), (1890, "68 designs"), (1892, "Work starts"), (1896, "Opens to the public"),
                                    (1902, "Lifts closed"), (1904, "Demolition starts"), (1907, "Foundations blown up")],
                            title="Watkin's Tower, 1889 to 1907")),
    # ---- 5. What's there now
    "S1": ("annotate", dict(image="A24", marks=[{"type": "ellipse", "center": (0.5, 0.5), "radii": (0.12, 0.12)}])),
    "S2": ("kenburns", dict(image="A27", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.15))),
    "S3": ("kenburns", dict(image="A29", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.2),
                            lower_third=("FA Cup Final, 28 April 1923", "Bolton Wanderers 2, West Ham United 0"))),
    "S4": ("kenburns", dict(image="PRESENT_aerial", start=(0.5, 0.5, 1.15), end=(0.5, 0.5, 1.0), mode="cover")),
    "S5": ("kenburns", dict(image="PRESENT_arch", start=(0.5, 0.6, 1.0), end=(0.5, 0.4, 1.15), mode="cover",
                            lower_third=("The Wembley arch: 133 m", None))),
    # ---- outro
    "O1": ("annotate", dict(image="A02", marks=[SPEC_UNDERLINE], start=(0.5, 0.52, 1.6), end=(0.5, 0.52, 1.2))),
    "O2": ("end_card", dict(text="Sources in the description")),
}

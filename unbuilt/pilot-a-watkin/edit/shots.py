"""Pilot A shot list: one picture per narration block (C5 is the silent title card).

Each entry: block -> (toolkit function, kwargs). `duration` and `out` are filled in by build.py from the
recorded narration's timings. Images are referenced by asset number ("A03") and resolved in assets/raw/.
Every picture is a real archive item, a code-drawn graphic, or (marked PRESENT) a CC-licensed photo of
Wembley today that stands in for a Google Earth Studio shot until those exist. No generative AI.

Coordinates are fractions of each image (0,0 top-left), set by looking at the downloaded scans.
"""

# Clause 1 on the spec page (A02, printed p. 8): "assume that the foundations are / perfect" runs over two lines.
# Measured from the scan's text rows and word gaps (line 1: 0.459-0.472, line 2: 0.478-0.490).
SPEC_UNDERLINE = [{"type": "underline", "from": (0.447, 0.4733), "to": (0.892, 0.4733)},   # "assume that the foundations are"
                  {"type": "underline", "from": (0.085, 0.4932), "to": (0.180, 0.4932)}]   # "perfect"
SPEC_VIEW = (0.5, 0.483)

SHOTS = {
    # ---- cold open
    "C1": ("kenburns", dict(image="A03", start=(0.55, 0.64, 1.7), end=(0.55, 0.27, 1.7))),
    "C2": ("annotate", dict(image="A14", marks=[{"type": "underline", "from": (0.985, 0.17), "to": (0.985, 0.93)},
                                             {"type": "label", "text": "155 FT", "pos": (0.72, 0.05), "anchor": "l", "size": 44}],
                            start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.06))),
    # Google Earth Studio renders (GOOGLE_EARTH.md) replace these stand-in photos as soon as they arrive.
    "C3": ("footage", dict(source="GE1_cold_open",
                           fallback=("kenburns", dict(image="W01", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.15), mode="cover")))),
    "C4": ("annotate", dict(image="A02", marks=SPEC_UNDERLINE, start=(*SPEC_VIEW, 1.7), end=(*SPEC_VIEW, 2.0))),
    "C5": ("title_card", dict(title="UNBUILT", subtitle="London's Eiffel Tower", fixed=2.5)),
    # ---- 1. Eiffel envy
    "E1": ("highlight", dict(image="A11", box=(0.09, 0.105, 0.92, 0.205))),   # "net takings... almost equal to its cost"
    "E2": ("kenburns", dict(image="A21", start=(0.5, 0.4, 1.0), end=(0.5, 0.3, 1.25),
                            lower_third=("Sir Edward Watkin", "Railway chairman, 1819 to 1901"))),
    # Only the Channel crossing (Dover-Calais) is dashed: the railways either side existed; the tunnel didn't.
    "E3": ("maproute", dict(stops=[("Manchester", -2.24, 53.48), ("London", -0.13, 51.51), ("Dover", 1.31, 51.13),
                                   ("Calais", 1.86, 50.95), ("Paris", 2.35, 48.86)], dashed=(2,), bbox=(-5.5, 47.6, 5.0, 54.6),
                            title="Watkin's dream: Manchester to Paris")),
    "E4": ("kenburns", dict(image="A17", start=(0.5, 0.5, 1.0), end=(0.6, 0.45, 1.3))),
    "E5": ("kenburns", dict(image="A12", start=(0.5, 0.5, 1.0), end=(0.5, 0.42, 1.25))),   # The Graphic, 1894: Wembley tower beside Eiffel
    # ---- 2. Sixty-eight designs
    "D1": ("highlight", dict(image="A02", box=(0.07, 0.452, 0.91, 0.512))),
    "D2": ("annotate", dict(image="A02", marks=SPEC_UNDERLINE, start=(*SPEC_VIEW, 2.3), end=(*SPEC_VIEW, 2.4))),
    "D3": ("montage", dict(images=["A10a", "A10b", "A10c", "A10d", "A06", "A08", "A09", "A05"], cols=4, rows=2)),
    # The plate doesn't visibly show these features, so mark the catalogue's own words (text page, p. 45) instead.
    "D4": ("annotate", dict(image="A06_design18_p45_text", marks=[
               {"type": "underline", "from": (0.48, 0.695), "to": (0.875, 0.695)},
               {"type": "underline", "from": (0.29, 0.718), "to": (0.52, 0.718)},
               {"type": "underline", "from": (0.07, 0.812), "to": (0.62, 0.812)}],
           start=(0.5, 0.74, 2.0), end=(0.5, 0.76, 2.1))),
    "D5": ("annotate", dict(image="A08", marks=[{"type": "label", "text": "2,296 FT · GRANITE", "pos": (0.67, 0.30), "anchor": "l", "size": 40}])),
    "D6": ("kenburns", dict(image="A09", start=(0.5, 0.7, 1.2), end=(0.5, 0.35, 1.5))),
    "D7": ("kenburns", dict(image="A39page", start=(0.5, 0.5, 1.0), end=(0.5, 0.4, 1.3))),
    "D8": ("kenburns", dict(image="A05", start=(0.5, 0.85, 1.5), end=(0.5, 0.2, 1.5))),
    "D10": ("annotate", dict(image="A03", marks=[{"type": "label", "text": "1,200 FT", "pos": (0.66, 0.22), "anchor": "l", "size": 40},
                                                  {"type": "label", "text": "8 LEGS", "pos": (0.70, 0.50), "anchor": "l", "size": 40},
                                                  {"type": "label", "text": "£352,222", "pos": (0.70, 0.57), "anchor": "l", "size": 40}])),
    # ---- 3. Building it
    "B1": ("scale_compare", dict(items=[{"name": "Watkin's Tower (design)", "height_m": 366, "shape": "taper", "accent": True},
                                        {"name": "Eiffel Tower today", "height_m": 330, "shape": "taper"},
                                        {"name": "The Shard", "height_m": 310, "shape": "taper"},
                                        {"name": "Wembley arch", "height_m": 133, "shape": "arch"},
                                        {"name": "Big Ben", "height_m": 96}], title="Drawn to one scale")),
    "B2": ("annotate", dict(image="A03", marks=[{"type": "label", "text": "8 legs became 4", "pos": (0.66, 0.50), "anchor": "l", "size": 40}])),
    "B3": ("kenburns", dict(image="A16", start=(0.5, 0.5, 1.0), end=(0.5, 0.4, 1.2))),
    "B4": ("kenburns", dict(image="A22", start=(0.5, 0.4, 1.0), end=(0.5, 0.35, 1.2), lower_third=("May 1894", None))),
    "B5": ("scale_compare", dict(items=[{"name": "Watkin's Tower (design)", "height_m": 366, "shape": "taper", "accent": True},
                                        {"name": "Blackpool Tower (opened May 1894)", "height_m": 158, "shape": "taper"}],
                                 title="May 1894")),
    "B6": ("annotate", dict(image="A14", marks=[{"type": "underline", "from": (0.985, 0.17), "to": (0.985, 0.93)},
                                             {"type": "label", "text": "155 FT of 1,200", "pos": (0.60, 0.05), "anchor": "l", "size": 40}])),
    # ---- 4. Why it stopped
    "W1": ("kenburns", dict(image="A19", start=(0.4, 0.5, 1.0), end=(0.6, 0.5, 1.15))),
    "W2": ("quote_card", dict(quote="there was no money left to carry on", attribution="Philip Grant, Wembley History Society (Brent Archives)")),
    "W3": ("kenburns", dict(image="A14", start=(0.5, 0.5, 1.0), end=(0.15, 0.80, 1.8))),   # push to the left foot
    "W4": ("annotate", dict(image="A02", marks=SPEC_UNDERLINE, start=(*SPEC_VIEW, 2.3), end=(*SPEC_VIEW, 2.5))),
    "W5": ("kenburns", dict(image="A15", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.15), lower_third=("'Watkin's Folly'", None))),
    "W6": ("timeline", dict(events=[(1889, "Brief issued"), (1890, "68 designs"), (1892, "Work starts"), (1896, "Opens to the public"),
                                    (1902, "Lifts closed"), (1904, "Demolition starts"), (1907, "Foundations blown up")],
                            title="Watkin's Tower, 1889 to 1907")),
    # ---- 5. What's there now
    # The two deep pits sit at about (0.40, 0.61) and (0.49, 0.56), with fainter ones beside them. Circle the group,
    # not a precise spot: the exact match to today's pitch is not established (RESEARCH.md section 7).
    "S1": ("annotate", dict(image="A24", marks=[{"type": "ellipse", "center": (0.48, 0.585), "radii": (0.13, 0.065)}],
                            start=(0.48, 0.60, 1.3), end=(0.48, 0.59, 1.7))),
    "S2": ("kenburns", dict(image="A27", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.15))),
    "S3": ("kenburns", dict(image="A28",   # 1923 (NYT, 13 May 1923); A29 shows the 1924 final, so not here
 start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.2),
                            lower_third=("FA Cup Final, 28 April 1923", "Bolton Wanderers 2, West Ham United 0"))),
    "S4": ("footage", dict(source="GE2_topdown",
                           fallback=("kenburns", dict(image="W01", start=(0.5, 0.45, 1.35), end=(0.5, 0.45, 1.1), mode="cover")))),
    "S5": ("footage", dict(source="GE3_arch_orbit", lower_third=("The Wembley arch: 133 m", None),
                           fallback=("kenburns", dict(image="W03", start=(0.5, 0.6, 1.0), end=(0.5, 0.4, 1.15), mode="cover")))),
    # ---- outro
    "O1": ("footage", dict(source="GE4_dusk",
                           fallback=("annotate", dict(image="A02", marks=SPEC_UNDERLINE, start=(*SPEC_VIEW, 1.7), end=(*SPEC_VIEW, 1.2))))),
    "O2": ("end_card", dict(text="Sources in the description")),
}

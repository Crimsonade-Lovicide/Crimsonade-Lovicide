"""Pilot B shot list: one picture per narration block (C4 is the silent title card).

Each entry: block -> (toolkit function, kwargs). `duration` and `out` are filled in by build.py from the
recorded narration's timings. Images are referenced by asset id and resolved in assets/derived/, then assets/raw/.
Every picture is a real archive item (assets/rights.csv), a code-drawn graphic, or a flyover drawn from the
USGS laser scan of Liberty Island. No generative AI.

Coordinates are fractions of each image (0,0 top-left), measured on the downloaded scans.
"""

# Springfield Weekly Republican, 15 Oct 1886, p. 2, column 2 (line positions from the LoC text layer).
RUMOUR = (0.350, 0.581, 0.506, 0.628)       # "It has even been charged ... the spirit of freedom."
REBUTTAL = (0.350, 0.623, 0.506, 0.651)     # "It is a fact ... the one now on Bedloe's island."

SHOTS = {
    # ---- cold open
    "C1": ("kenburns", dict(image="P01", start=(0.5, 0.62, 2.85), end=(0.53, 0.24, 2.85))),   # full width; pedestal up to the lamp
    "C2": ("footage", dict(source="LIB1_push", tail=True,
                           fallback=("kenburns", dict(image="A14", start=(0.5, 0.5, 1.0), end=(0.5, 0.45, 1.3), mode="cover")))),
    "C3": ("kenburns", dict(image="C3_split", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.06))),
    "C4": ("title_card", dict(title="UNBUILT", subtitle="Liberty and Egypt", fixed=2.5)),
    # ---- 1. The Nile
    "E1": ("kenburns", dict(image="A02", start=(0.5, 0.35, 1.0), end=(0.5, 0.3, 1.2),
                            lower_third=("Frédéric Auguste Bartholdi", "Sculptor, 1834 to 1904"))),
    "E2": ("kenburns", dict(image="A03", start=(0.5, 0.55, 1.0), end=(0.62, 0.40, 1.35),
                            lower_third=("The Colossi of Memnon", "Photographed by Bartholdi, 1855"))),
    "E3": ("kenburns", dict(image="A05", start=(0.5, 0.4, 1.0), end=(0.5, 0.35, 1.2),
                            lower_third=("Isma'il Pasha", "Khedive of Egypt, 1863 to 1879"))),
    "E4": ("maproute", dict(stops=[("Paris, 1867", 2.35, 48.86), ("Port Said, 1869", 32.30, 31.26)],
                            bbox=(-2, 26, 38, 52), title="Bartholdi's pitch")),
    # ---- 2. The pitch
    "P1": ("kenburns", dict(image="P01", start=(0.5, 0.5, 1.0), end=(0.47, 0.24, 2.0))),
    # Measure the figure only (lamp top y=137 to feet y=1175 of 2550). The painted pedestal isn't drawn to the
    # 48 ft of the design, so it is named in text rather than measured.
    "P2": ("annotate", dict(image="P01", marks=[{"type": "underline", "from": (0.66, 0.054), "to": (0.66, 0.461)},
                                             {"type": "label", "text": "86 FT", "pos": (0.68, 0.24), "anchor": "l", "size": 46},
                                             {"type": "label", "text": "on a 48 ft pedestal", "pos": (0.68, 0.55), "anchor": "l", "size": 34}],
                            start=(0.5, 0.33, 1.25), end=(0.5, 0.33, 1.3))),
    "P3": ("kenburns", dict(image="P01", start=(0.5, 0.25, 1.4), end=(0.5, 0.65, 1.15),
                            lower_third=("Watercolour, 1869", "Musée Bartholdi, Colmar"))),
    "P4": ("kenburns", dict(image="A06", start=(0.5, 0.5, 1.0), end=(0.35, 0.5, 1.3),
                            lower_third=("Opening of the Suez Canal, Port Said", "November 1869"))),
    "P5": ("kenburns", dict(image="A07", start=(0.5, 0.5, 1.0), end=(0.52, 0.35, 1.5),
                            lower_third=("Port Said lighthouse, 1869", "Concrete, 56 m. Still standing"))),
    # ---- 3. Liberty
    "L1": ("kenburns", dict(image="A08", start=(0.5, 0.35, 1.0), end=(0.5, 0.3, 1.2),
                            lower_third=("Édouard de Laboulaye", "1811 to 1883"))),
    "L2": ("maproute", dict(stops=[("Paris", 2.35, 48.86), ("New York", -74.04, 40.69)],
                            bbox=(-80, 30, 8, 56), title="1871: looking for a site")),
    "L3": ("montage", dict(images=["A09c", "A09b", "A09a"], cols=3, rows=1)),
    "L4": ("footage", dict(source="LIB2_arc", lower_third=("151 ft, base to torch", "Unveiled 28 October 1886"),
                           fallback=("kenburns", dict(image="A10", start=(0.5, 0.5, 1.0), end=(0.5, 0.35, 1.3))))),
    # ---- 4. The rumour
    "R1": ("highlight", dict(image="N01", box=RUMOUR)),
    "R2": ("highlight", dict(image="N01", box=REBUTTAL)),
    "R3": ("annotate", dict(image="N01", marks=[{"type": "underline", "from": (0.3543, 0.6506), "to": (0.5009, 0.6506)}],
                            start=(0.428, 0.640, 6.0), end=(0.428, 0.645, 6.4))),
    # ---- 5. The verdict
    "V1": ("kenburns", dict(image="V1_side_by_side", start=(0.5, 0.5, 1.0), end=(0.5, 0.52, 1.05))),
    "V2": ("quote_card", dict(quote="The Statue of Liberty Was Originally a Muslim Woman",
                              attribution="Smithsonian.com headline, 2015. The article itself says \"fellah, or Arab peasant\"")),
    "V3": ("annotate", dict(image="A10", marks=[{"type": "label", "text": "HALF TRUE", "pos": (0.06, 0.08), "anchor": "l", "size": 64}],
                            start=(0.5, 0.45, 1.0), end=(0.5, 0.4, 1.12))),
    # ---- 6. The other statue
    "T1": ("kenburns", dict(image="A11", start=(0.5, 0.5, 1.0), end=(0.5, 0.35, 1.5),
                            lower_third=("Ferdinand de Lesseps, Port Said", "Unveiled 1899"))),
    "T2": ("kenburns", dict(image="A12", start=(0.5, 0.5, 1.0), end=(0.45, 0.45, 1.25),
                            lower_third=("The same statue, 2013", "Photo: Mohamed kamal 1984, CC BY-SA 4.0"))),
    # ---- outro
    "O1": ("footage", dict(source="LIB3_dusk",
                           fallback=("kenburns", dict(image="A14", start=(0.5, 0.45, 1.3), end=(0.5, 0.5, 1.0), mode="cover")))),
    "O2": ("end_card", dict(text="Sources in the description")),
}

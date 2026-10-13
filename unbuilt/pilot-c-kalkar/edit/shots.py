"""Pilot C shot list: one picture per narration block (C4 is the silent title card).

Each entry: block -> (toolkit function, kwargs). build.py fills in `duration` and `out` from the narration's
timings. Images are referenced by asset id and looked up in assets/derived/ first, then assets/raw/.
Every picture is a real photograph (assets/rights.csv) or a graphic drawn by assets/derive.py. No generative AI.

Coordinates are fractions of each image (0,0 top-left).
"""

ANEFO = "Nationaal Archief / Anefo, CC0"

SHOTS = {
    # ---- cold open
    "C1": ("kenburns", dict(image="P01", mode="cover", start=(0.5, 0.75, 1.15), end=(0.5, 0.3, 1.35))),
    "C2": ("kenburns", dict(image="K06", mode="cover", start=(0.5, 0.5, 1.0), end=(0.42, 0.45, 1.25),
                            lower_third=("Kalkar, September 1985", "Finished, never switched on"))),
    "C3": ("kenburns", dict(image="K01", mode="cover", start=(0.5, 0.55, 1.05), end=(0.55, 0.4, 1.3))),
    "C4": ("title_card", dict(title="UNBUILT", subtitle="The reactor at Kalkar", fixed=2.5)),
    # ---- 1. The promise
    "B1": ("kenburns", dict(image="K02", mode="cover", start=(0.5, 0.5, 1.0), end=(0.6, 0.4, 1.2),
                            lower_third=("Kalkar, July 1974", "Photo: Bert Verhoeff, " + ANEFO))),
    "B2": ("kenburns", dict(image="G01", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.04))),
    "B3": ("kenburns", dict(image="G02", start=(0.5, 0.5, 1.0), end=(0.56, 0.42, 1.35))),
    "B4": ("kenburns", dict(image="K03", mode="cover", start=(0.5, 0.5, 1.0), end=(0.53, 0.42, 1.35))),
    # ---- 2. The bill
    "M1": ("scale_compare", dict(items=[{"name": "1965 estimate", "height_m": 310},
                                        {"name": "1971 estimate", "height_m": 670},
                                        {"name": "1972 contract", "height_m": 1535},
                                        {"name": "1982 estimate", "height_m": 6050, "accent": True}],
                                 unit="million DM", title="What Kalkar would cost")),
    "M2": ("kenburns", dict(image="G03", start=(0.5, 0.5, 1.0), end=(0.5, 0.45, 1.06))),
    # ---- 3. The farmer
    "F1": ("kenburns", dict(image="M01", mode="cover", start=(0.5, 0.5, 1.0), end=(0.5, 0.45, 1.15),
                            lower_third=("Hönnepel, next to the site", "Photo 2020: Pieter Delicaat, CC BY-SA 4.0"))),
    "F2": ("kenburns", dict(image="G04", start=(0.5, 0.5, 1.0), end=(0.5, 0.48, 1.05))),
    "F3": ("kenburns", dict(image="K10", mode="cover", start=(0.5, 0.5, 1.0), end=(0.45, 0.55, 1.2),
                            lower_third=("Kalkar, 24 September 1977", "Photo: Koen Suyk, " + ANEFO))),
    "F4": ("kenburns", dict(image="K04", mode="cover", start=(0.5, 0.55, 1.0), end=(0.5, 0.55, 1.12))),
    # ---- 4. The state turns
    "S1": ("kenburns", dict(image="G05", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.05))),
    "S2": ("kenburns", dict(image="K11", mode="cover", start=(0.5, 0.5, 1.0), end=(0.45, 0.4, 1.2),
                            lower_third=("The reactor building", "Photo 1979: Koen Suyk, " + ANEFO))),
    "S3": ("quote_card", dict(quote="Dieses Höllenfeuer nicht entfachen.",
                              attribution="\"Don't kindle this hell fire.\" Der Spiegel 27/1985: interview with "
                                          "Friedhelm Farthmann (SPD)")),
    "S4": ("title_card", dict(title="26 April 1986", subtitle="Chernobyl")),
    "S5": ("kenburns", dict(image="G06", start=(0.5, 0.5, 1.0), end=(0.5, 0.48, 1.05))),
    # ---- 5. Hot and waiting
    "W1": ("kenburns", dict(image="K07", mode="cover", start=(0.5, 0.5, 1.0), end=(0.55, 0.42, 1.25),
                            lower_third=("Kalkar, September 1985", "Photo: Rob Bogaerts, " + ANEFO))),
    "W2": ("kenburns", dict(image="K08", mode="cover", start=(0.5, 0.45, 1.25), end=(0.5, 0.5, 1.0))),
    "W3": ("kenburns", dict(image="G08", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.05))),
    "W4": ("kenburns", dict(image="G09", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.03))),
    # ---- 6. The end
    "E1": ("title_card", dict(title="20 March 1991", subtitle="The money stops")),
    "E2": ("quote_card", dict(quote="The responsibility for the end of Kalkar ... clearly lies with the State of "
                                    "North Rhine-Westphalia.",
                              attribution="Federal research ministry, press release 14/91, 21 March 1991 (English as in KfK 5455)")),
    "E3": ("quote_card", dict(quote="The time will come when our descendants will be amazed that we did not know "
                                    "things so plain.",
                              attribution="Seneca. In Latin, the last line of the project's official history "
                                          "(KfK 5455, Karlsruhe, 1994)")),
    # ---- 7. The twist
    "T1": ("kenburns", dict(image="K05", mode="cover", start=(0.5, 0.4, 1.0), end=(0.45, 0.3, 1.3),
                            lower_third=("\"Stop Kalkar\", 1977", "Photo: Bert Verhoeff, " + ANEFO))),
    "T2": ("kenburns", dict(image="G11", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.08))),
    "T3": ("kenburns", dict(image="P03", mode="cover", start=(0.5, 0.5, 1.0), end=(0.45, 0.45, 1.2),
                            lower_third=("The site today", "Photo 2024: Rolfcosar, CC BY-SA 4.0"))),
    "T4": ("kenburns", dict(image="G10", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.04))),
    "T5": ("kenburns", dict(image="P02", mode="cover", start=(0.5, 0.6, 1.0), end=(0.5, 0.45, 1.25),
                            lower_third=("Wunderland Kalkar", "The cooling tower as a climbing wall. Photo 2008: Koetjuh"))),
    # ---- 8. Coda
    "K1": ("kenburns", dict(image="Z01", mode="cover", start=(0.5, 0.5, 1.0), end=(0.55, 0.45, 1.2),
                            lower_third=("Zwentendorf, Austria", "Photo 2018: Simon Legner, CC BY-SA 4.0"))),
    "K2": ("kenburns", dict(image="S01", mode="cover", start=(0.5, 0.5, 1.0), end=(0.5, 0.4, 1.2),
                            lower_third=("Shoreham, Long Island", "Photo 2007: Paul Searing, CC BY 2.0"))),
    # ---- close
    "O1": ("kenburns", dict(image="P01", mode="cover", start=(0.5, 0.3, 1.4), end=(0.5, 0.55, 1.0))),
    "O2": ("end_card", dict(text="Sources in the description")),
}

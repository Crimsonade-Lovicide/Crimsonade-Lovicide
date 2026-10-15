"""UNHISTORY 01 shot list: one picture per narration block (C5 is the silent title card, logo option C).

Each entry: block -> (toolkit function, kwargs). build.py fills in `duration` and `out` from the narration's
timings. Images are referenced by asset id, looked up in assets/derived/ first, then assets/raw/.
Every picture is a real photograph or document (assets/rights.csv) or a graphic drawn by assets/derive.py.
No generative AI. Coordinates are fractions of each image (0,0 top-left).
The HISTORY / UNHISTORY tag for each block comes from SCRIPT.md (blocks.claim_tags).
"""

BA = "Bundesarchiv"

SHOTS = {
    # ---- cold open
    "C1": ("kenburns", dict(image="G01", start=(0.5, 0.72, 1.0), end=(0.5, 0.32, 1.35),
                            lower_third=("Model of the planned north-south axis, Berlin, 1939",
                                         BA + ", Bild 146III-373 / CC-BY-SA 3.0"))),
    "C2": ("kenburns", dict(image="G02", start=(0.5, 0.55, 1.0), end=(0.5, 0.38, 1.35),
                            lower_third=("Model of the Great Hall, 1939", BA + ", Bild 146-1986-029-02 / CC-BY-SA 3.0"))),
    "C3": ("montage", dict(images=["D04", "D05", "U15", "G03"], cols=2, rows=2)),
    "C4": ("kenburns", dict(image="U01", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.04))),
    "C5": ("kenburns", dict(image="U00", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.03), fixed=2.5)),
    # ---- 1. the odds
    "O1": ("kenburns", dict(image="U03", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.04))),
    "O2": ("kenburns", dict(image="U04", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.04))),
    # ---- 2. the door: May 1940
    "D1": ("kenburns", dict(image="H01", start=(0.5, 0.4, 1.0), end=(0.5, 0.32, 1.15),
                            lower_third=("Lord Halifax, foreign secretary", "Photo 1941: Narodowe Archiwum Cyfrowe"))),
    "D2": ("kenburns", dict(image="H02", mode="cover", start=(0.5, 0.5, 1.0), end=(0.5, 0.42, 1.2),
                            lower_third=("Neville Chamberlain, 1938", "Photo: Narodowe Archiwum Cyfrowe"))),
    "D3": ("kenburns", dict(image="H03", mode="cover", start=(0.6, 0.45, 1.0), end=(0.72, 0.35, 1.45),
                            lower_third=("Churchill in the Cabinet Room, 1940", "Photo: Cecil Beaton / IWM MH 26392"))),
    "D4": ("kenburns", dict(image="H04", mode="cover", start=(0.5, 0.5, 1.0), end=(0.45, 0.55, 1.18),
                            lower_third=("Bray Dunes, near Dunkirk, May 1940", "Photo: IWM HU 1137"))),
    "D5": ("kenburns", dict(image="H03", mode="cover", start=(0.25, 0.65, 1.5), end=(0.45, 0.55, 1.25))),
    "D6": ("kenburns", dict(image="U06", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.03))),
    "D7": ("kenburns", dict(image="U07", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.03))),
    # ---- 3. a Europe at peace (our timeline)
    "P1": ("kenburns", dict(image="U08", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.04))),
    "P2": ("kenburns", dict(image="E01", mode="cover", start=(0.5, 0.5, 1.0), end=(0.4, 0.45, 1.15),
                            lower_third=("Real photo: Soviet Union, June 1941", "Otto / " + BA + ", Bild 101I-186-0184-02A / CC-BY-SA 3.0"))),
    "P3": ("kenburns", dict(image="U09", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.04))),
    "P4": ("kenburns", dict(image="U10", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.04))),
    # ---- 4. 1950: the world they planned
    "H1": ("kenburns", dict(image="U15", start=(0.5, 0.5, 1.0), end=(0.45, 0.42, 1.08))),
    "H2": ("highlight", dict(image="U15", box=(0.07, 0.43, 0.86, 0.58))),
    "G1": ("kenburns", dict(image="U11", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.04))),
    "G2": ("kenburns", dict(image="U16", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.04))),
    "W1": ("kenburns", dict(image="D03", mode="cover", start=(0.5, 0.5, 1.0), end=(0.5, 0.45, 1.15),
                            lower_third=("The villa at Wannsee, Berlin", "Photo 2015: Franek Vetulani, CC BY-SA 4.0"))),
    "W2": ("highlight", dict(image="D04", box=(0.26, 0.553, 0.88, 0.597))),
    "W3": ("kenburns", dict(image="U12", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.03))),
    "W4": ("kenburns", dict(image="U17", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.03))),
    "B1": ("highlight", dict(image="D05", box=(0.06, 0.74, 0.455, 0.775),
                             lower_third=("Sonderfahndungsliste G.B., 1940, page 32",
                                          "The Imperial War Museum's copy. Entry 49: Churchill"))),
    "B2": ("kenburns", dict(image="U18", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.05))),
    "A1": ("kenburns", dict(image="A01", start=(0.5, 0.5, 1.0), end=(0.26, 0.7, 1.9),
                            lower_third=("Einstein's letter to Roosevelt, 2 August 1939", "FDR Library (public domain)"))),
    "A2": ("kenburns", dict(image="A02", start=(0.5, 0.45, 1.0), end=(0.5, 0.4, 1.15),
                            lower_third=("Real photo: Einstein becomes a US citizen, 1940", "Al Aumuller / NYWT&S, Library of Congress"))),
    "G3": ("kenburns", dict(image="G01", start=(0.5, 0.5, 1.0), end=(0.5, 0.55, 1.12))),
    "T1": ("kenburns", dict(image="R02", mode="cover", start=(0.4, 0.45, 1.0), end=(0.35, 0.4, 1.12),
                            lower_third=("The Schwerbelastungskörper, Berlin", "Photo 2016: Elgaard, CC BY-SA 4.0"))),
    "T2": ("kenburns", dict(image="U14", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.04))),
    "T3": ("kenburns", dict(image="G01", start=(0.5, 0.5, 1.0), end=(0.5, 0.58, 1.6))),
    # ---- 5. what's missing from their 1950 (real photos, in our timeline)
    "M1": ("kenburns", dict(image="U19", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.04))),
    "M2": ("kenburns", dict(image="M01", mode="cover", start=(0.5, 0.5, 1.0), end=(0.5, 0.45, 1.12),
                            lower_third=("Real photo: Australia signs the UN Charter, 1945", "Australian Government (public domain)"))),
    "M3": ("kenburns", dict(image="M02", mode="cover", start=(0.5, 0.5, 1.0), end=(0.5, 0.45, 1.12),
                            lower_third=("Real photo: the Berlin Airlift, Tempelhof, 1948", "US Air Force (public domain)"))),
    "M4": ("kenburns", dict(image="M03", start=(0.5, 0.4, 1.0), end=(0.5, 0.3, 1.25),
                            lower_third=("Real document: the Basic Law, published 23 May 1949", "Bundesgesetzblatt (public domain)"))),
    "M5": ("montage", dict(images=["M01", "M02", "M03"], cols=3, rows=1)),
    # ---- 6. the stop line
    "X1": ("kenburns", dict(image="U13", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.05))),
    # ---- 7. what happened
    "R1": ("kenburns", dict(image="R01", start=(0.5, 0.5, 1.0), end=(0.5, 0.42, 1.15),
                            lower_third=("Berlin, 1945", "Photo: Sgt A. Wilkes / IWM BU 8604"))),
    "R4": ("kenburns", dict(image="R02b", mode="cover", start=(0.5, 0.5, 1.12), end=(0.5, 0.5, 1.0),
                            lower_third=("General-Pape-Straße, Berlin", "Photo 2011: Sekamor, CC BY-SA 3.0"))),
    # ---- close
    "Z1": ("kenburns", dict(image="G01", start=(0.5, 0.4, 1.3), end=(0.5, 0.5, 1.0))),
    "Z2": ("kenburns", dict(image="U99", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.02))),
}

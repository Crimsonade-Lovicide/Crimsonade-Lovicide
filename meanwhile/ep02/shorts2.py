"""MEANWHILE — vertical (9:16) cutdowns of Episode 2, using the Episode 1 Shorts layout (../shorts.py).

    python meanwhile/ep02/shorts2.py                    # all Shorts -> meanwhile/build/shorts_ep02/
    python meanwhile/ep02/shorts2.py --only seoul
    python meanwhile/ep02/shorts2.py --still seoul 12
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import episode2  # noqa: E402,F401  (sets up Episode 2 in the engine)
import shorts as SH  # noqa: E402

SH.EP_LABEL = "Ep. 2 · The First Question"
SH.OUT = SH.E.HERE / "build" / "shorts_ep02"
SH.SHORTS = {
    "nairobi": dict(scene="nairobi", hook="A retired teacher tested an AI. Then: what's “no cap”?", cx=0.58),
    "seoul": dict(scene="seoul", hook="She offered an AI her bank password. It was a test.", cx=0.5),
    "manila": dict(scene="manila", hook="How many r's in strawberry?", cx=0.5),
    "auckland": dict(scene="auckland", hook="Two brothers. One bet. Can a chicken lay two eggs in a day?", cx=0.45),
    "mexico": dict(scene="mexico", hook="A taxi driver asked an AI how it was doing.", cx=0.6),
    "newyork": dict(scene="newyork", hook="2 a.m. Can't sleep. The AI tried toaster instructions.", cx=0.45),
    "firstq": dict(scene="finale", hook="An AI on the first thing everyone asks it.", cx=0.5, from_=0.0, quote=True),
}

if __name__ == "__main__":
    SH.main()

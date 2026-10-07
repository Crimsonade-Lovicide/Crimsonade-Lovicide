# The Hoffman Files, Ep. 2: Miranda

Production doc: the Episode 2 production doc in Claude Docs (fact base, script, visuals, music brief, guests, clearance).

- Music lives in `../music/`: the series theme opens and closes; public domain Musopen recordings carry the acts.

## 3D (`blender/`)

No people in any scene: rooms, objects and empty chairs carry it.

| Scene | File | What it shows | Label on screen |
|---|---|---|---|
| M1 | `m1_card.py` | Warning card on a steel table under one lamp, push-in | none |
| M2 | `m2_busstop.py` | Empty bus stop under a sodium streetlight, night | Illustration |
| M3 | `m3_room.py` | Interrogation Room No. 2: table, two chairs, hanging lamp, door marked 2, clock running two hours | Reconstruction · layout illustrative |
| M6 | `m6_bench.py` | Nine high-backed chairs; five light up, four stay dark | none (abstract bench, not the real seating) |
| M9 | `m9_cards.py` | Stack of warning cards and a pen; the top card flips to a blank back | none |
| M10 | `m10_bar.py` | Bar exterior at night, unlit nameless sign, empty street | Illustration |

`./render_ep2.sh` renders look-check previews. The scenes reuse the ep. 1 kit and `common.py`.

The edit reuses the ep. 1 pipeline (`../ep01-hot-coffee/`): new scenes go in `blender/`, a new `edit/episode.py`.

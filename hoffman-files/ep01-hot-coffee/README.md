# The Hoffman Files, Ep. 1: Hot Coffee (Liebeck v. McDonald's)

Blender reconstructions for episode 1. They are plain procedural 3D (matte clay figures with amber for coffee and heat), with no AI-generated footage and no real person's likeness. Every scene is built from code in `blender/`, so any shot can be re-timed or re-framed by editing a number.

| Scene | File | Length | What it shows | Script beat |
|---|---|---|---|---|
| E1 | `e1_cup.py` | 8 s | Unbranded paper cup steaming on a dashboard at dawn; slow push-in | Cold open |
| E2 | `e2_car.py` | 6 s | Generic hatchback parked at a drive-through (parked, not moving) | "The car was stopped" |
| E3 | `e3_spill.py` | 10 s | Faceless figure, cup between the knees, lid pulled toward her, cup tips into the lap, fabric darkens | The spill |
| E4 | `e4_skin.py` | 12 s | Skin layer cross-section; heat front moves through epidermis, then dermis, to full thickness | Third-degree burns |
| E7 | `e7_folders.py` | 12 s | 70 folders stack up (1 folder = 10 reports, about 700 burn reports, 1982–92) | Prior complaints |
| E9 | `e9_clock.py` | 8 s | 24-hour dial turns twice while a bar fills: two days of coffee sales | The punitive ask |

Accuracy notes for the edit:
- E4 is **illustrative, not to scale**. Say so in a lower third ("Illustration, not to scale").
- E3 is a reconstruction drawn from the trial record, not footage. Label it "Reconstruction".
- E7 and E9 numbers must match the fact base in the episode doc. Overlays read their positions from `renders/<scene>_tracks.json`, so the numbers live in the overlay layer, not in the 3D.

## Render

Needs `pip install bpy==4.2.*` and ffmpeg. The shared helpers (`common.py`) come from `documentary-pilots/pipeline/blender`.

```bash
./render_ep1.sh   # preview: 960x540, 8 samples, every 2nd frame (~1 h on CPU)
./ep1_reel.sh     # motion-interpolates to 24 fps, labels, and concatenates out/ep1/ep1_reconstructions_preview.mp4
```

Single still for look checks: `python3 blender/e3_spill.py still 118`.
Final renders: `RES=1920x1080 SAMPLES=64 STEP=1 python3 blender/<scene>.py anim`.

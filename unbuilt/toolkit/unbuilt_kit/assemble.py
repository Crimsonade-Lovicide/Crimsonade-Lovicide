"""Cut clips together over narration (and optional music), finish at -14 LUFS."""
import json
import os
import re
import subprocess
import tempfile

from .core import FPS, HD, PAPER, ffmpeg_exe, run_ffmpeg

IMAGE_EXT = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp")


def _media_len(path):
    """Length in seconds of a media file (video or audio), read from ffmpeg's header line."""
    err = subprocess.run([ffmpeg_exe(), "-nostdin", "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def load_shotlist(shotlist, crossfade=0.0):
    """Accept a path to JSON or a list. Entries: {"clip": path, "start": s} (placed on the timeline), or
    {"clip": path, "duration": s} / {"clip": path} laid end to end. Optional "in": seconds into the source.
    The JSON may be a bare list or {"shots": [...]}. Relative paths resolve against the JSON's folder.

    "start" is when a clip is fully on screen: its dissolve runs in the `crossfade` seconds before it.
    Laid end to end, each clip plays its whole length and overlaps the previous one by the dissolve.
    Returns [(clip, start, length, in_point)], length running to the next clip's start (the last: its own)."""
    root = "."
    if isinstance(shotlist, str):
        root = os.path.dirname(os.path.abspath(shotlist))
        with open(shotlist) as f:
            shotlist = json.load(f)
    if isinstance(shotlist, dict):
        shotlist = shotlist["shots"]
    shots, t = [], 0.0
    for k, s in enumerate(shotlist):
        clip = s["clip"] if os.path.isabs(s["clip"]) else os.path.join(root, s["clip"])
        lead = crossfade if k > 0 else 0.0
        start = float(s["start"]) if "start" in s else t
        if "duration" in s:
            natural = float(s["duration"])
        elif clip.lower().endswith(IMAGE_EXT):
            natural = 4.0
        else:
            natural = _media_len(clip) - float(s.get("in", 0))
        shots.append([clip, start, natural - lead, float(s.get("in", 0))])
        t = start + natural - lead
    shots.sort(key=lambda s: s[1])
    for a, b in zip(shots, shots[1:]):
        a[2] = b[1] - a[1]
    return [tuple(s) for s in shots]


def _picture(shots, out, size, crossfade, total):
    """Normalise every clip (fit onto paper, 24 fps, exact length; a clip that runs short holds its last frame),
    then join with cross-dissolves that end on each clip's start time."""
    W, H = size
    pad_color = "0x%02X%02X%02X" % tuple(int(round(c * 255)) for c in PAPER)
    inputs, chains = [], []
    n = len(shots)
    for k, (clip, start, length, in_pt) in enumerate(shots):
        if k == n - 1:
            length = max(length, total - start)
        need = length + (crossfade if k > 0 else 0.0)
        if clip.lower().endswith(IMAGE_EXT):
            inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{need + 1:.3f}", "-i", clip]
        else:
            inputs += ["-ss", f"{in_pt:.3f}", "-i", clip]
        chains.append(
            f"[{k}:v]fps={FPS},scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={pad_color},setsar=1,format=yuv420p,"
            f"tpad=stop_mode=clone:stop_duration={need + 1:.3f},trim=duration={need:.3f},setpts=PTS-STARTPTS,fps={FPS}[c{k}]")
    if shots[0][1] > 0:      # the timeline starts with a gap: paper until the first clip
        inputs += ["-f", "lavfi", "-i", f"color=c={pad_color}:s={W}x{H}:r={FPS}:d={shots[0][1]:.3f}"]
        chains.append(f"[{n}:v]format=yuv420p,setsar=1[lead]")
        chains.append("[lead][c0]concat=n=2:v=1:a=0[c0p]")
        prev = "c0p"
    else:
        prev = "c0"
    for k in range(1, n):
        if crossfade > 0:
            chains.append(f"[{prev}][c{k}]xfade=transition=fade:duration={crossfade:.3f}:"
                          f"offset={shots[k][1] - crossfade:.3f}[x{k}]")
        else:
            chains.append(f"[{prev}][c{k}]concat=n=2:v=1:a=0[x{k}]")
        prev = f"x{k}"
    chains.append(f"[{prev}]trim=duration={total:.4f},setpts=PTS-STARTPTS[v]")
    run_ffmpeg(inputs + ["-filter_complex", ";".join(chains), "-map", "[v]", "-an", "-c:v", "libx264",
                         "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), out])


def _measure(path, af):
    err = subprocess.run([ffmpeg_exe(), "-nostdin", "-hide_banner", "-i", path, "-af",
                          af + ",loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return json.loads(err[err.rindex("{"):err.rindex("}") + 1])


def _mix(narration, music, out_wav, total, music_db):
    """Narration levelled to -16 LUFS; music bed levelled, lowered, and sidechain-ducked under the voice;
    then two-pass loudnorm of the mix to -14 LUFS / -1 dBTP."""
    voice = (f"[0:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.5:LRA=11,"
             f"aresample=48000,apad,atrim=duration={total:.3f}")
    if music:
        fc = (f"{voice},asplit=2[v][key];"
              f"[1:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-16:LRA=11,aresample=48000,"
              f"volume={music_db}dB,apad,atrim=duration={total:.3f}[bed];"
              f"[bed][key]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=500:knee=4[ducked];"
              f"[v][ducked]amix=inputs=2:normalize=0:duration=first[mix]")
        ins = ["-i", narration, "-stream_loop", "-1", "-i", music]
    else:
        fc = f"{voice}[mix]"
        ins = ["-i", narration]
    premix = out_wav + ".premix.wav"
    run_ffmpeg(ins + ["-filter_complex", fc, "-map", "[mix]", "-ar", "48000", "-c:a", "pcm_s16le", premix])
    m = _measure(premix, "anull")
    final = (f"loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
             f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
             f"linear=true,aresample=48000")
    run_ffmpeg(["-i", premix, "-af", final, "-ar", "48000", "-c:a", "pcm_s16le", out_wav])
    os.remove(premix)


def assemble(shotlist_json, narration_wav, music_wav_or_None, out_mp4, crossfade=0.5, size=HD, music_db=-14):
    """Shot list + narration (+ music) -> 1080p H.264 / AAC 48 kHz mp4 at -14 LUFS.
    The programme runs for the longer of the picture and the narration (the last shot holds if needed).
    crossfade: seconds of dissolve between clips (0 for straight cuts). music_db: bed level under the voice."""
    shots = load_shotlist(shotlist_json, crossfade)
    last = shots[-1]
    total = max(last[1] + last[2], _media_len(narration_wav))
    with tempfile.TemporaryDirectory() as tmp:
        pic = os.path.join(tmp, "picture.mp4")
        mix = os.path.join(tmp, "mix.wav")
        _picture(shots, pic, size, crossfade, total)
        _mix(narration_wav, music_wav_or_None, mix, total, music_db)
        run_ffmpeg(["-i", pic, "-i", mix, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-ar", "48000", "-t", f"{total:.3f}", "-movflags", "+faststart", out_mp4])
    return out_mp4

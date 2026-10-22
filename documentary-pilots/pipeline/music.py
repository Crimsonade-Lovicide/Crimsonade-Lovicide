"""Procedural, royalty-free documentary score per pilot: drone pad + heartbeat sub + optional ticks,
riser into the title card, impact hit on the title, and a low hit on the hook."""
import json, numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 48000
TL = json.load(open('timeline.json'))
# root (Hz), minor flavour, tick?  one key per series
STYLE = {
    'p1_pink_slime':    (73.42, 'aeolian', False),   # D
    'p2_the_count':     (65.41, 'phrygian', True),   # C, clock ticks
    'p3_server_nation': (82.41, 'dorian', False),    # E
    'p4_long_arm':      (55.00, 'phrygian', False),  # A
    'p5_brokered':      (87.31, 'aeolian', True),    # F, ticks
}


def lp(x, f, order=2):
    return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)


def env_ad(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1) * np.exp(-np.maximum(t - a, 0) / d)


def score(pid):
    root, mode, ticks = STYLE[pid]
    segs = TL[pid]['segs']; total = TL[pid]['total']
    n = int(total * SR); t = np.arange(n) / SR
    rng = np.random.default_rng(abs(hash(pid)) % 2**32)
    starts = np.cumsum([0] + [s['dur'] for s in segs])
    seg_at = {s['vis']: (starts[i], starts[i + 1]) for i, s in enumerate(segs)}
    t_title, t_end = seg_at['T'][0], seg_at['END'][0]
    # --- drone pad: root, fifth, minor third / flat second, octave; slow beating
    third = 6/5 if mode != 'phrygian' else 16/15
    pad = np.zeros(n)
    for ratio, amp in ((1, 1.0), (1.5, .55), (third * 2, .35), (2, .45), (3, .12)):
        f = root * ratio
        for det in (-0.35, 0.0, 0.41):
            ph = rng.uniform(0, 2 * np.pi)
            w = np.sin(2 * np.pi * (f + det) * t + ph)
            w += 0.35 * np.sin(2 * np.pi * 2 * (f + det) * t + ph)    # a little edge
            pad += amp * w
    pad *= 0.6 + 0.4 * np.sin(2 * np.pi * t / 9.0 + 1.3)               # breathing swell
    pad = lp(pad, 900)
    # build: pad opens up after the hook, swells toward the title
    shape = np.interp(t, [0, 3, 6, t_title - 1, t_title, t_end, total - 1.5, total], [0.0, .35, .55, .8, 1.0, .75, .25, 0])
    pad *= shape
    # --- heartbeat sub (lub-dub) from end of hook to title
    hb = np.zeros(n); bpm = 62
    beat = env_ad(int(.35 * SR), .004, .09) * np.sin(2 * np.pi * 52 * np.arange(int(.35 * SR)) / SR)
    k = 3.0
    while k < t_title - .2:
        for off, g in ((0, 1.0), (.23, .6)):
            i = int((k + off) * SR); hb[i:i + len(beat)] += g * beat[:max(0, min(len(beat), n - i))]
        k += 60 / bpm
    # --- ticks (clock / data)
    tk = np.zeros(n)
    if ticks:
        click = hp(rng.standard_normal(int(.012 * SR)), 5000) * env_ad(int(.012 * SR), .0005, .003)
        k = 3.0
        while k < t_title:
            i = int(k * SR); tk[i:i + len(click)] += click; k += 0.5
    # --- riser into title + impact
    rz = np.zeros(n); r0, r1 = int((t_title - 2.2) * SR), int(t_title * SR)
    noise = rng.standard_normal(r1 - r0)
    ramp = np.linspace(0, 1, r1 - r0) ** 2.5
    rz[r0:r1] = hp(noise, 1500) * ramp * 0.5
    def boom(at, gain):
        m = int(2.5 * SR); tt = np.arange(m) / SR
        f = 70 * np.exp(-tt * 1.6) + 28
        b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 1.4)
        b += 0.4 * lp(rng.standard_normal(m), 400) * np.exp(-tt * 6)
        i = int(at * SR); seg = b[:max(0, min(m, n - i))]; out = np.zeros(n); out[i:i + len(seg)] = gain * seg; return out
    hits = boom(t_title, 1.0) + boom(0.05, 0.6) + boom(t_end, 0.35)
    mix = 0.10 * pad + 0.55 * hb + 0.25 * tk + 0.35 * rz + 0.6 * hits
    mix = np.tanh(mix * 1.2) * 0.8
    st = np.stack([mix, np.roll(mix, int(.011 * SR))], 1)            # cheap stereo width
    wavfile.write(f'audio/{pid}_music.wav', SR, (st * 32767 * 0.9).astype(np.int16))
    print(pid, 'music ok', round(total, 2))


if __name__ == '__main__':
    for pid in TL: score(pid)

"""Compose, design, mix and master the 35 s soundtrack for the AL MOHIB SAKINA spot.

    python3 audio/src/build.py

Writes SFX one-shots, aligned stems, broadcast and web masters, a timeline image and a
preview video into audio/.
"""
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import ndimage, signal

import synth as s
from synth import SR, db, midi_hz, n_samples

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audio"
DUR = 35.0
BPM = 120
BEAT = 60 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(11)

# Picture-locked story beats (seconds)
T_HIT = 24.0        # music climax; cut to interior, hand on the handle
T_DUCK = 24.18      # cut to interior after the hit lands
T_SLIDE = 24.2      # sash starts to slide
T_SEAL = 25.0       # sash seals -> outside world collapses
T_LOCK = 25.45      # multipoint lock engages
T_CALM = 26.2       # calm cue enters
VO_IN = 26.8       # first VO line; the qalam scratch plays alone before it
VO_LATEST_END = 32.95  # "By AL Mohib" must finish before the logo's seal
T_LOGO = 32.4       # sonic logo (slide + seal + chime)
T_MEGA = 22.5       # director's megaphone: "Action!"
T_BLOT = 16.0       # ink blot falls (music ducks)
INTERIOR_SHOTS = [(5.0, 7.5), (10.5, 11.0), (15.5, 17.0)]  # Act 1 cuts inside, window still open
VO_GAPS = {"ar": (0.3, 0.25), "en": (0.4, 0.35)}  # Arabic lines run longer


class Track:
    def __init__(self):
        self.buf = np.zeros((n_samples(DUR), 2))

    def add(self, x, t0, gain_db=0.0, pan=0.0):
        if x.ndim == 1:
            x = s.pan_mono(x, pan)
        i = n_samples(max(t0, 0))
        j = min(len(self.buf), i + len(x))
        if j > i:
            self.buf[i:j] += x[:j - i] * db(gain_db)


def hum(t):
    return t + rng.normal(0, 0.004)


# ================================================================ ACT 1: "Rush Hour Heist" (D minor, 120 BPM)
CHORDS = ["Dm", "Dm", "Bb", "A", "Dm", "Dm", "Bb", "A", "Gm", "Gm", "A", "A"]
ROOT_MIDI = {"Dm": 38, "Bb": 34, "A": 33, "Gm": 31}
VOICING = {"Dm": [50, 57, 62, 65], "Bb": [46, 53, 58, 62], "A": [45, 52, 57, 61], "Gm": [43, 50, 55, 58]}
BASS_PATTERN = [0, 0, 12, 0, 7, 0, 10, 12]
_ = None
PIZZ = {  # two-bar phrases in eighths
    "A": [62, _, 65, 62, 69, _, 68, 69, 70, 69, 67, 65, 64, _, 61, _],
    "B": [65, _, 70, 65, 74, _, 72, 70, 69, _, 64, _, 61, 64, 69, _],
    "C": [67, _, 70, 67, 74, _, 72, 70, 67, _, 70, 67, 74, 75, 74, 72],
    "D": [73, _, 76, 73, 81, _, 79, 76],
}


def act1_music():
    tr = Track()
    for b, ch in enumerate(CHORDS):
        t0 = b * BAR
        root = ROOT_MIDI[ch]
        # bass ostinato (bars 1-11), driving eighths
        if b < 11:
            for k, off in enumerate(BASS_PATTERN):
                tr.add(s.bass_note(root + off, BEAT / 2 * 0.9, 0.9 if k % 2 == 0 else 0.75), hum(t0 + k * BEAT / 2), -7)
        # drums from bar 3
        if b >= 2:
            for beat in range(4):
                tb = t0 + beat * BEAT
                if beat in (0, 2):
                    tr.add(s.kick(), hum(tb), -4)
                if beat in (1, 3):
                    tr.add(s.snare(0.9), hum(tb), -10, 0.05)
                if beat == 1 and b >= 4:
                    tr.add(s.kick(0.7), hum(tb + BEAT / 2), -6)
            step = BEAT / 4 if b >= 4 else BEAT / 2
            for k in range(int(BAR / step)):
                tr.add(s.hat(0.7 + 0.3 * (k % 2 == 0)), hum(t0 + k * step), -17, 0.3)
        # pizzicato motif (bars 1-11), doubled an octave up from bar 5
        if b < 11:
            phrase = {0: "A", 1: "A", 2: "B", 3: "B", 4: "A", 5: "A", 6: "B", 7: "B", 8: "C", 9: "C", 10: "D"}[b]
            notes = PIZZ[phrase]
            half = (b % 2) * 8 if phrase != "D" else 0
            for k, m in enumerate(notes[half:half + 8]):
                if m is None:
                    continue
                tk = hum(t0 + k * BEAT / 2)
                tr.add(s.pluck(m, 0.6, 0.9), tk, -9, -0.3)
                if b >= 4:
                    tr.add(s.pluck(m + 12, 0.5, 0.7, 0.7), tk + 0.006, -14, 0.35)
        # brass stabs from bar 5
        if 4 <= b < 11:
            for off in (0, 1.5 * BEAT):
                tr.add(s.brass(VOICING[ch], 0.32, 0.9), hum(t0 + off), -10, 0.0)
        # spiccato strings 16ths from bar 9
        if 8 <= b < 11:
            tones = [VOICING[ch][i] + 24 for i in (0, 2, 1, 3)]
            for k in range(16):
                tr.add(s.string_short(tones[k % 4] - 12, 0.15, 0.8), hum(t0 + k * BEAT / 4), -15, 0.4)
        # timpani on downbeats bars 9-11
        if 8 <= b < 11:
            tr.add(s.timpani(midi_hz(root + 12), 1.0), t0, -8, -0.15)
    # bar 12 build: tom/snare roll, chromatic strings, timpani roll, riser
    t0 = 11 * BAR
    for k in range(30):  # roll stops an eighth short: a breath before the hit
        frac = k / 29
        tk = t0 + k * BAR / 32
        tr.add(s.snare(0.4 + 0.6 * frac), tk, -16 + 8 * frac, 0.05)
        if k % 2 == 0:
            tr.add(s.timpani(midi_hz(45), 0.3 + 0.7 * frac, 0.6), tk, -14 + 8 * frac, -0.15)
    for k in range(16):
        tr.add(s.string_short(69 + k * 12 / 15, 0.15, 0.6 + 0.4 * k / 15), t0 + k * BEAT / 4, -14, 0.4)
    for k, m in enumerate([45, 46, 47, 48, 49, 50, 51, 52]):
        tr.add(s.bass_note(m, BEAT / 2 * 0.9), t0 + k * BEAT / 2, -7)
    tr.add(s.riser(BAR - 0.12), t0, -11)
    # the climax hit
    hit = Track()
    hit.add(s.brass([38, 50, 57, 62, 65, 69], 2.2, 1.0), T_HIT, -3)
    hit.add(s.timpani(midi_hz(38), 1.0, 3.0), T_HIT, -4, -0.1)
    hit.add(s.crash(3.5), T_HIT, -9, 0.2)
    hit.add(s.sub_boom(2.5), T_HIT, -5)
    hit.add(s.kick(), T_HIT, -3)
    hit.add(s.snare(), T_HIT, -8)
    tr.buf += hit.buf
    return s.reverb(tr.buf, s.make_ir(1.3, seed=3), 0.16)


# ================================================================ ACT 1: the city (exterior SFX)
def exterior_sfx():
    tr = Track()
    trf = s.traffic(T_SEAL + 2)
    ramp = np.interp(s.t_axis(T_SEAL + 2), [0, 22, 24], [db(-6), 1.0, 1.0])
    tr.add(trf * ramp, 0, -24)
    bell = s.alarm_bell(7.5) * np.interp(s.t_axis(7.5), [0, 5.5, 7.5], [1, 1, 0])
    tr.add(bell, 0.0, -17, -0.35)
    tr.add(s.doppler_pass(s.siren(8.0, "wail"), 3.5, 14, 8), 1.5, -9)
    for t0, d in [(4.0, 0.25), (4.32, 0.18), (4.55, 0.35)]:
        tr.add(s.horn(d), t0, -15, 0.55)
    bike = s.motorbike(3.0, [0, 0.6, 1.0, 1.25, 2.2, 3.0], [1800, 1900, 7000, 5000, 8500, 8500])
    tr.add(s.doppler_pass(bike, 1.8, 22, 4), 7.5, -6)
    tr.add(s.tire_screech(1.2), 10.8, -13, -0.2)
    yelp_dur = T_SEAL + 1.5 - 11.0
    tr.add(s.siren(yelp_dur, "yelp"), 11.0, -17, 0.4 * np.sin(2 * np.pi * s.t_axis(yelp_dur) / 9))
    for t0, d, f in [(13.5, 0.3, (410, 520)), (13.9, 0.6, (370, 466)), (14.4, 0.2, (440, 554)), (14.7, 0.5, (410, 520))]:
        tr.add(s.horn(d, f), t0, -18, rng.uniform(-0.7, 0.7))
    tr.add(s.jackhammer(6.0), 14.0, -22, 0.6)
    heli_dur = T_SEAL + 1.5 - 15.5
    heli = s.sweep_filter(s.helicopter(heli_dur), "lowpass", lambda tc: 400 * 15 ** min(tc / 8.5, 1))
    tr.add(heli * np.interp(s.t_axis(heli_dur), [0, 8.5], [db(-20), 1.0]), 15.5, -9, -0.2)
    bike2 = s.motorbike(2.4, [0, 0.4, 1.4, 2.4], [5000, 9000, 6500, 9500])
    tr.add(s.doppler_pass(bike2, 1.0, -26, 5), 18.0, -9)
    tr.add(s.tire_screech(1.0), 20.5, -12, 0.3)
    tr.add(s.horn(1.4, (370, 466)), 21.0, -14, -0.5)
    return s.reverb(tr.buf, s.make_ir(0.8, predelay=0.03, damp=4000, seed=5), 0.12)


def window_closes(x):
    """The SAKINA moment: as the sash closes, the outside narrows, then dies on the seal."""
    t = np.arange(len(x)) / SR

    def cutoff(tc):
        if tc < T_DUCK:
            return 20000
        if tc < T_SEAL - 0.05:
            return 12000 * (1500 / 12000) ** ((tc - T_DUCK) / (T_SEAL - 0.05 - T_DUCK))
        if tc < T_SEAL + 0.07:
            return 1500 * (140 / 1500) ** ((tc - T_SEAL + 0.05) / 0.12)
        return 140

    y = s.sweep_filter(x, "lowpass", cutoff)
    g = np.interp(t, [0, T_DUCK - 0.02, T_DUCK + 0.02, T_SEAL - 0.05, T_SEAL + 0.03, 26.0, 27.0],
                  [0, 0, -5, -14, -40, -40, -90])
    return y * db(g)[:, None]


# ================================================================ ACT 2: interior foley
def interior_foley():
    tr = Track()
    tr.add(s.window_slide(T_SEAL - T_SLIDE), T_SLIDE, -2)
    tr.add(s.seal_thunk(), T_SEAL, 0)
    tr.add(s.lock_clicks(), T_LOCK, -8, 0.15)
    tone = s.room_tone(DUR - T_HIT) * np.interp(s.t_axis(DUR - T_HIT), [0, 1, DUR - T_HIT - 1, DUR - T_HIT], [0, 1, 1, 0])
    tr.add(tone, T_HIT, -52)
    return s.reverb(tr.buf, s.make_ir(0.45, predelay=0.005, damp=7000, seed=7), 0.08)


# ================================================================ ACT 3: "Sakina" (D major, rubato)
PIANO = [  # (time, midi, velocity)
    (26.4, 38, .45), (26.4, 50, .35), (26.9, 57, .40), (27.3, 64, .38), (27.7, 66, .40), (28.1, 73, .33),
    (28.6, 35, .40), (28.6, 47, .30), (29.1, 54, .38), (29.5, 61, .36), (29.9, 62, .38), (30.3, 69, .32),
    (30.8, 31, .40), (30.8, 43, .30), (31.2, 62, .36), (31.5, 66, .36), (31.8, 71, .32),
    (32.2, 33, .36), (32.2, 45, .28), (32.45, 62, .32), (32.7, 64, .30),
    (33.0, 38, .45), (33.0, 50, .35),
]
PADS = [  # (start, end, voicing)
    (26.2, 28.8, [50, 57, 61, 64, 66]),
    (28.5, 31.0, [47, 54, 57, 61, 62]),
    (30.7, 32.5, [43, 50, 54, 59, 62]),
    (32.1, 33.3, [45, 52, 57, 62, 64]),
    (32.9, 35.6, [50, 57, 62, 64, 66]),
]


def act3_music():
    """Returns (piano, pad) separately so the pad can duck under the VO."""
    piano, pad = Track(), Track()
    for t0, m, v in PIANO:
        piano.add(s.felt_piano(m, 4.0, v), t0, -6, (m - 60) / 60)
    for t0, t1, voicing in PADS:
        pad.add(s.pad_chord(voicing, t1 - t0, attack=min(1.4, (t1 - t0) / 2), release=min(1.6, (t1 - t0) / 2)), t0, -14)
    ir = s.make_ir(3.2, predelay=0.025, damp=5000, seed=9)
    return s.reverb(piano.buf, ir, 0.35), s.reverb(pad.buf, ir, 0.35)


# ================================================================ script revisions (v2)
def _mask(spans, ramp=0.06):
    """0..1 envelope that is 1 inside the given time spans, with short ramps."""
    t = np.arange(n_samples(DUR)) / SR
    m = np.zeros_like(t)
    for a, b in spans:
        m = np.maximum(m, np.clip(np.minimum((t - a) / ramp + 1, (b - t) / ramp + 1), 0, 1))
    return m[:, None]


def interior_perspective(fx):
    """Act 1 interior cuts: the city heard through the open window, about 3 dB down with some room."""
    m = _mask(INTERIOR_SHOTS)
    roomy = s.reverb(fx, s.make_ir(0.6, predelay=0.008, damp=5000, seed=21), 0.3)
    return (1 - m) * fx + m * db(-3) * roomy


def blot_duck(x):
    """Comic beat: the score catches its breath as the ink blot lands."""
    return x * db(-9 * _mask([(T_BLOT - 0.03, T_BLOT + 0.4)], ramp=0.04))


def pen_foley():
    tr = Track()
    # Act 1: the first letter (seen), mostly masked by the city
    tr.add(s.nib_tap(), 5.4, -6)
    for t0 in (5.45, 5.75, 6.05):  # the three teeth of the letter sin
        tr.add(s.qalam_stroke(0.22, [0, 0.11, 0.22], [0.3, 0.7, 0]), t0, -4)
    tr.add(s.qalam_stroke(0.5, [0, 0.1, 0.2, 0.3, 0.5], [0.4, 0.9, 0.2, 0.8, 0]), 10.5, -4)  # the wobble
    tr.add(s.ink_drip(), T_BLOT, -2, 0.1)
    # Act 3: the steady stroke, then the dots of the word (two under ya, one over nun, two over ta marbuta)
    tr.add(s.nib_tap(), 26.3, -4)
    tr.add(s.qalam_stroke(2.53, [0, 0.3, 1.0, 1.7, 2.2, 2.53], [0.15, 0.5, 0.9, 0.7, 0.4, 0]), 26.32, 0, 0.1)
    for t0 in (28.95, 29.08, 29.35, 29.48, 29.75):
        tr.add(s.nib_tap(), t0, -5, 0.1)
    return s.reverb(tr.buf, s.make_ir(0.45, predelay=0.005, damp=7000, seed=7), 0.06)


def _load_vo(name):
    x, sr = sf.read(OUT / "vo" / f"{name}.wav")
    x = x if x.ndim == 1 else x.mean(1)
    idx = np.nonzero(np.abs(x) > 0.02 * np.max(np.abs(x)))[0]  # trim TTS silence
    return x[max(idx[0] - 200, 0):idx[-1] + int(0.12 * sr)], sr


def dialogue(lang):
    """VO lines laid back to back from VO_IN, plus the megaphone. Returns (megaphone, vo, [(start, end, label)])."""
    mega_tr, tr = Track(), Track()
    marks = []
    mega, sr = _load_vo("en_megaphone")
    mega_tr.add(s.reverb(s.megaphone(mega, sr), s.make_ir(0.8, predelay=0.03, damp=4000, seed=5), 0.2), T_MEGA, 0, -0.2)
    marks.append((T_MEGA, T_MEGA + len(mega) / sr * 112 / 100, "MEGAPHONE"))
    t = VO_IN
    for k in (1, 2, 3):
        x, sr = _load_vo(f"{lang}_vo{k}")
        x = s.hp(signal.resample_poly(x, SR, sr), 80)
        tr.add(s.reverb(x, s.make_ir(0.35, predelay=0.004, damp=8000, seed=31), 0.05), t, 0)
        marks.append((t, t + len(x) / SR, f"VO{k}"))
        t += len(x) / SR + (VO_GAPS[lang][k - 1] if k < 3 else 0)
    if marks[-1][1] > VO_LATEST_END:
        raise SystemExit(f"{lang} VO overruns: ends {marks[-1][1]:.2f}s > {VO_LATEST_END}s; tighten gaps or length_scale")
    return mega_tr.buf, tr.buf, marks


def duck_under(x, key, depth_db=-3.0):
    """Side-chain: pull x down by depth_db while the key signal (VO) is speaking."""
    env = signal.lfilter([1 - 0.9993], [1, -0.9993], np.abs(key).max(1))
    gate = np.clip(env / (0.25 * env.max()), 0, 1)
    gate = signal.lfilter([1 - 0.9995], [1, -0.9995], gate)  # smooth release
    return x * db(depth_db * gate)[:, None]


def sonic_logo(t0=0.0, track=None):
    """Brand signature: soft slide, air-tight seal, rising A-D-F# chime (the 'Sakina' motif)."""
    tr = track or Track()
    tr.add(s.window_slide(0.55), t0, -12)
    tr.add(s.seal_thunk(), t0 + 0.55, -6)
    for k, m in enumerate([69, 74, 78]):
        tr.add(s.chime(m, 3.0, 0.9), t0 + 0.6 + 0.2 * k, -10, -0.2 + 0.2 * k)
        tr.add(s.felt_piano(m - 12, 3.0, 0.4), t0 + 0.6 + 0.2 * k, -14, -0.2 + 0.2 * k)
    tr.buf = s.reverb(tr.buf, s.make_ir(2.4, seed=13), 0.3)
    return tr


# ================================================================ loudness & mastering
_K1 = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1, -1.69065929318241, 0.73248077421585])
_K2 = ([1.0, -2.0, 1.0], [1, -1.99004745483398, 0.99007225036621])


def lufs(x):
    """Integrated loudness per ITU-R BS.1770-4 (48 kHz)."""
    y = signal.lfilter(*_K2, signal.lfilter(*_K1, x, axis=0), axis=0)
    blk, hop = n_samples(0.4), n_samples(0.1)
    z = np.array([np.mean(y[i:i + blk] ** 2, axis=0).sum() for i in range(0, len(y) - blk, hop)])
    z = z[-0.691 + 10 * np.log10(z + 1e-12) > -70]
    if len(z) == 0:
        return -70.0
    rel = -0.691 + 10 * np.log10(z.mean()) - 10
    z = z[-0.691 + 10 * np.log10(z) > rel]
    return -0.691 + 10 * np.log10(z.mean())


def true_peak_db(x):
    return 20 * np.log10(np.max(np.abs(signal.resample_poly(x, 4, 1, axis=0))) + 1e-12)


def limit(x, ceiling_db=-1.5, look=0.005):
    w = n_samples(look)
    need = np.minimum(1.0, db(ceiling_db) / (np.max(np.abs(x), axis=1) + 1e-12))
    g = ndimage.uniform_filter1d(ndimage.minimum_filter1d(need, 2 * w + 1), w + 1)
    return x * g[:, None]


def master(x, target, tp=-1.0):
    for _ in range(4):
        x = limit(x * db(target - lufs(x)), tp - 0.6)
        if abs(lufs(x) - target) < 0.1 and true_peak_db(x) <= tp:
            break
    return x


def level(x, t0, t1, target):
    """Gain a stem so its loudness inside [t0, t1] hits target LUFS."""
    return x * db(target - lufs(x[n_samples(t0):n_samples(t1)]))


# ================================================================ outputs
def write(path, x):
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, x, SR, subtype="PCM_24")


def export_sfx_library():
    lib = {
        "siren_wail": s.siren(4.0), "siren_yelp": s.siren(3.0, "yelp"),
        "motorbike_pass": s.doppler_pass(s.motorbike(3.0, [0, 0.6, 1.0, 1.25, 2.2, 3.0], [1800, 1900, 7000, 5000, 8500, 8500]), 1.8, 22, 4),
        "tire_screech": s.tire_screech(1.2), "car_horn": s.horn(0.6), "bank_alarm_bell": s.alarm_bell(3.0),
        "helicopter": s.helicopter(4.0), "jackhammer": s.jackhammer(3.0), "city_traffic_bed": s.traffic(6.0),
        "whoosh": s.whoosh(1.2), "window_slide": s.window_slide(0.95), "window_seal_thunk": s.seal_thunk(),
        "multipoint_lock": s.lock_clicks(), "room_tone": s.room_tone(5.0),
        "qalam_stroke": s.qalam_stroke(2.53, [0, 0.3, 1.0, 1.7, 2.2, 2.53], [0.15, 0.5, 0.9, 0.7, 0.4, 0]),
        "qalam_nib_tap": s.nib_tap(), "ink_drip": s.ink_drip(),
    }
    for name, x in lib.items():
        write(OUT / "sfx" / f"{name}.wav", s.norm(x, db(-3)))
    return list(lib)


def timeline_png(mix, path, vo_marks, version):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    mono = mix.mean(1)
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor="#0b1020")
    L, W = 0.06, 0.9
    ax1 = fig.add_axes([L, 0.62, W, 0.22], facecolor="#0b1020")
    ax2 = fig.add_axes([L, 0.12, W, 0.46], facecolor="#0b1020")
    t = np.arange(len(mono)) / SR
    ax1.fill_between(t[::40], -np.abs(mono[::40]), np.abs(mono[::40]), color="#4f8cff", lw=0)
    ax2.specgram(mono, NFFT=2048, Fs=SR, noverlap=1536, cmap="magma", vmin=-130, vmax=-30)
    ax2.set_yscale("symlog", linthresh=500)
    ax2.set_ylim(40, 16000)
    for ax in (ax1, ax2):
        ax.set_xlim(0, DUR)
        ax.tick_params(colors="#9aa4b8")
        for sp in ax.spines.values():
            sp.set_color("#2a3350")
    ax1.set_yticks([])
    ax2.set_xlabel("seconds", color="#9aa4b8")
    ax2.set_ylabel("Hz", color="#9aa4b8")
    marks = [(0, "ACT 1 · THE CITY  — 'Rush Hour Heist' (Dm, 120 BPM)"), (T_HIT, "HIT"), (T_SEAL, "SEAL"),
             (T_CALM, "ACT 3 · 'Sakina' (D major)"), (T_LOGO, "SONIC LOGO")]
    for x, label in marks:
        for ax in (ax1, ax2):
            ax.axvline(x, color="#e9dcc6", lw=0.8, alpha=0.6)
        ax1.text(x + 0.15, 1.02, label, transform=ax1.get_xaxis_transform(), color="#e9dcc6", fontsize=11)
    for a, b, label in vo_marks:
        ax1.axvspan(a, b, color="#0b4fb3", alpha=0.35)
        ax1.text(a + 0.05, 0.05, label, transform=ax1.get_xaxis_transform(), color="#9ec0ff", fontsize=9)
    ax1.text(T_BLOT + 0.05, 0.9, "ink blot", transform=ax1.get_xaxis_transform(), color="#9ec0ff", fontsize=9)
    ax1.text(26.3, 0.9, "qalam", transform=ax1.get_xaxis_transform(), color="#9ec0ff", fontsize=9)
    fig.text(L, 0.92, f"AL Mohib · SAKINA · 'The First Word' — Soundtrack v2 ({version})", color="white", fontsize=22, weight="bold")
    fig.text(L, 0.885, "All of the view. None of the noise.  ·  Scratch VO (TTS guide) — replace with cast talent", color="#9aa4b8", fontsize=14)
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)
    return L, W


def preview_mp4(png, wav, mp4, L, W):
    x0, w = int(1920 * L), int(1920 * W)
    fc = (f"[0:v]scale=1920:1080,format=yuv420p[bg];color=c=white:s=3x820:r=30[ph];"
          f"[bg][ph]overlay=x='{x0}+t/{DUR}*{w}':y=150:shortest=1[v]")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-framerate", "30", "-i", str(png), "-i", str(wav),
                    "-filter_complex", fc, "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
                    "-crf", "20", "-c:a", "aac", "-b:a", "256k", "-t", str(DUR), str(mp4)], check=True)


def mp3(wav):
    out = wav.with_suffix(".mp3")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav), "-b:a", "320k", str(out)], check=True)
    return out


def main():
    print("rendering act 1 music ...")
    m1 = act1_music()
    print("rendering exterior sfx ...")
    fx = exterior_sfx()
    print("rendering foley, act 3, logo, dialogue ...")
    fol = interior_foley()
    pen = pen_foley()
    piano, pad = act3_music()
    logo = sonic_logo(T_LOGO).buf

    # balance (loudness targets inside each stem's working window), then the script automation
    m1 = window_closes(blot_duck(level(m1, 2, T_HIT, -20)))
    fx = window_closes(interior_perspective(level(fx, 2, T_HIT, -23)))
    fol = level(fol, T_SLIDE, T_SEAL + 0.6, -21)
    pen = level(pen, 26.3, 28.85, -31)
    g3 = db(-31 - lufs((piano + pad)[n_samples(T_CALM):n_samples(T_LOGO)]))
    piano, pad = piano * g3, pad * g3
    logo = level(logo, T_LOGO, DUR, -27)

    dlg = {}
    for lang in ("ar", "en"):
        mega, vo, marks = dialogue(lang)
        vo_end = max(e for a, e, l in marks if l.startswith("VO"))
        dlg[lang] = (level(mega, T_MEGA, T_MEGA + 0.6, -17), level(vo, VO_IN, vo_end, -22), marks)

    fade = np.interp(np.arange(n_samples(DUR)) / SR, [0, DUR - 0.8, DUR], [1, 1, 0])[:, None]
    me_stems = {"music_act1_rush_hour_heist": m1, "sfx_exterior_city": fx, "foley_interior_window": fol,
                "foley_pen_and_ink": pen, "music_act3_sakina": piano + pad, "sonic_logo": logo}
    me_stems = {k: v * fade for k, v in me_stems.items()}
    stems = dict(me_stems, dialogue_megaphone=dlg["ar"][0] * fade,
                 dialogue_vo_ar=dlg["ar"][1] * fade, dialogue_vo_en=dlg["en"][1] * fade)
    for k, v in stems.items():
        write(OUT / "stems" / f"{k}.wav", v)

    me = sum(me_stems.values())
    report = {}
    mixdir = OUT / "mix"
    for old in mixdir.glob("*"):
        old.unlink()
    me_master = master(me, -23.0)
    write(mixdir / "sakina_tvc35_ME_broadcast_-23LUFS.wav", me_master)
    report["ME"] = {"broadcast": {"LUFS": round(lufs(me_master), 2), "dBTP": round(true_peak_db(me_master), 2)}}

    for lang in ("ar", "en"):
        mega, vo, marks = dlg[lang]
        # the pad (-3 dB) and the logo's slide (-6 dB) side-chain under the voice; the rest is shared with the M&E
        mix = (me - me_stems["music_act3_sakina"] - me_stems["sonic_logo"]
               + (piano + duck_under(pad, vo) + duck_under(logo, vo, -6.0) + mega + vo) * fade)
        tag = lang.upper()
        broadcast, web = master(mix, -23.0), master(mix, -14.0)
        write(mixdir / f"sakina_tvc35_{tag}_broadcast_-23LUFS.wav", broadcast)
        web_wav = mixdir / f"sakina_tvc35_{tag}_web_-14LUFS.wav"
        write(web_wav, web)
        web_mp3 = mp3(web_wav)
        png = OUT / f"sakina_soundtrack_timeline_{tag}.png"
        L, W = timeline_png(web, png, marks, f"{'Arabic' if lang == 'ar' else 'English'} version")
        preview_mp4(png, web_mp3, OUT / f"sakina_soundtrack_preview_{tag}.mp4", L, W)
        seg = lambda a, b: round(lufs(web[n_samples(a):n_samples(b)]), 1)
        vo_a, vo_b = marks[1][0], marks[-1][1]
        report[tag] = {
            "broadcast": {"LUFS": round(lufs(broadcast), 2), "dBTP": round(true_peak_db(broadcast), 2)},
            "web": {"LUFS": round(lufs(web), 2), "dBTP": round(true_peak_db(web), 2)},
            "segments_LUFS_web": {"act1_chaos": seg(0, T_HIT), "hit_and_slide": seg(T_HIT, T_SEAL),
                                  "post_seal": seg(T_SEAL + 0.3, T_CALM), "calm_with_vo": seg(T_CALM, T_LOGO),
                                  "logo": seg(T_LOGO, DUR)},
            "vo_lines_s": [(round(a, 2), round(b, 2), l) for a, b, l in marks],
            "vo_over_music_LU": round(lufs(vo[n_samples(vo_a):n_samples(vo_b)])
                                      - lufs((piano + duck_under(pad, vo))[n_samples(vo_a):n_samples(vo_b)]), 1),
        }

    logo_alone = sonic_logo(0.1)
    write(OUT / "sonic_logo" / "al_mohib_sakina_sonic_logo.wav",
          master(logo_alone.buf[:n_samples(3.6)] * np.interp(s.t_axis(3.6), [0, 3.0, 3.6], [1, 1, 0])[:, None], -16.0))
    report["sfx_library"] = export_sfx_library()
    (mixdir / "loudness_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

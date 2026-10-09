"""Procedural synthesis toolkit: DSP helpers, instruments and sound effects.

Every sound is generated from oscillators, noise and filters. No samples or
third-party recordings are used, so the whole soundtrack is original.
"""
import numpy as np
from scipy import signal

SR = 48000
NYQ = SR / 2
_rng = np.random.default_rng(2026)


# ---------------------------------------------------------------- basics
def n_samples(dur):
    return int(round(dur * SR))


def t_axis(dur):
    return np.arange(n_samples(dur)) / SR


def noise(dur):
    return _rng.standard_normal(n_samples(dur))


def db(x):
    return 10 ** (x / 20)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def norm(x, peak=1.0):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


def _coloured(dur, power):
    n = n_samples(dur)
    spec = np.fft.rfft(_rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = f[1]
    y = np.fft.irfft(spec / f ** power, n)
    return y / np.std(y)


def pink(dur):
    return _coloured(dur, 0.5)


def brown(dur):
    return _coloured(dur, 1.0)


# ---------------------------------------------------------------- filters
def _sos(kind, fc, order=2):
    if kind == "bandpass":
        lo, hi = fc
        return signal.butter(order, [max(lo, 10), min(hi, NYQ * 0.95)], "bandpass", fs=SR, output="sos")
    return signal.butter(order, min(max(fc, 10), NYQ * 0.95), kind, fs=SR, output="sos")


def lp(x, fc, order=2):
    return signal.sosfilt(_sos("lowpass", fc, order), x, axis=0)


def hp(x, fc, order=2):
    return signal.sosfilt(_sos("highpass", fc, order), x, axis=0)


def bp(x, lo, hi, order=2):
    return signal.sosfilt(_sos("bandpass", (lo, hi), order), x, axis=0)


def sweep_filter(x, kind, fc_fn, block=256, order=2):
    """Time-varying Butterworth filter. fc_fn(t) gives the cutoff (or (lo, hi)) at time t."""
    x = np.asarray(x, float)
    mono = x.ndim == 1
    if mono:
        x = x[:, None]
    y = np.zeros_like(x)
    zi = None
    for start in range(0, len(x), block):
        seg = x[start:start + block]
        sos = _sos(kind, fc_fn((start + len(seg) / 2) / SR), order)
        if zi is None:
            zi = np.zeros((sos.shape[0], 2, x.shape[1]))
        y[start:start + block], zi = signal.sosfilt(sos, seg, axis=0, zi=zi)
    return y[:, 0] if mono else y


# ---------------------------------------------------------------- envelopes & space
def env_ar(dur, attack, release):
    t = t_axis(dur)
    e = np.clip(t / max(attack, 1e-4), 0, 1)
    return e * np.clip((dur - t) / max(release, 1e-4), 0, 1)


def smooth_ar(dur, attack, release):
    """Raised-cosine attack and release, for pads."""
    t = t_axis(dur)
    a = np.clip(t / attack, 0, 1)
    r = np.clip((dur - t) / release, 0, 1)
    return (0.5 - 0.5 * np.cos(np.pi * a)) * (0.5 - 0.5 * np.cos(np.pi * r))


def pan_mono(x, pan=0.0):
    th = (np.asarray(pan, float) + 1) * np.pi / 4
    return np.stack([x * np.cos(th), x * np.sin(th)], 1)


def make_ir(rt60, predelay=0.012, damp=6000, seed=1):
    r = np.random.default_rng(seed)
    n = n_samples(rt60 * 1.1)
    t = np.arange(n) / SR
    chans = []
    for _ in range(2):
        nz = r.standard_normal(n)
        ir = 0.45 * hp(nz, 2500) * np.exp(-t * 6.9 / (rt60 * 0.4)) + lp(nz, damp) * np.exp(-t * 6.9 / rt60)
        ir[:n_samples(0.004)] *= np.linspace(0, 1, n_samples(0.004))
        ir = np.concatenate([np.zeros(n_samples(predelay)), ir])
        chans.append(ir / np.sqrt(np.sum(ir ** 2)))
    return np.stack(chans, 1)


def reverb(x, ir, wet):
    """Stereo convolution reverb; output keeps the input length."""
    if x.ndim == 1:
        x = pan_mono(x)
    wet_sig = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in range(2)], 1)
    return x + wet * wet_sig


def doppler_pass(x, t_closest, speed, dist):
    """Source moving past the listener on a straight line: delay-based pitch shift, 1/r level, air absorption, pan."""
    n = len(x)
    t = np.arange(n) / SR
    pos = speed * (t - t_closest)
    r = np.sqrt(pos ** 2 + dist ** 2)
    src = (t - (r - dist) / 343.0) * SR
    y = np.interp(src, np.arange(n), x, left=0, right=0)
    w = np.clip((r - dist) / 40, 0, 1)
    y = (1 - w) * y + w * lp(y, 1800)
    return pan_mono(y * dist / r, np.clip(pos / r, -1, 1) * 0.9)


# ---------------------------------------------------------------- oscillators
def additive(freq, dur, rolloff, kmax=48, odd_only=False):
    """Band-limited harmonic oscillator. Harmonic k has weight exp(-(k-1)*rolloff)/k.
    freq and rolloff may be scalars or per-sample arrays."""
    n = n_samples(dur)
    f = np.broadcast_to(np.asarray(freq, float), (n,))
    ro = np.broadcast_to(np.asarray(rolloff, float), (n,))
    phase = 2 * np.pi * np.cumsum(f) / SR
    y = np.zeros(n)
    fmax = f.max()
    for k in range(1, kmax + 1):
        if odd_only and k % 2 == 0:
            continue
        if k * fmax >= NYQ * 0.9:
            break
        y += np.exp(-(k - 1) * ro) / k * np.sin(k * phase + _rng.uniform(0, 2 * np.pi))
    return y


# ================================================================ instruments
def kick(vel=1.0):
    t = t_axis(0.5)
    f = 45 + 110 * np.exp(-t * 32)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    click = hp(noise(0.5), 3000) * np.exp(-t * 350) * 0.25
    return vel * (body + click)


def snare(vel=1.0):
    t = t_axis(0.35)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 28) * 0.5
    wires = bp(noise(0.35), 1500, 8000) * np.exp(-t * 17)
    return vel * norm(tone + wires)


def hat(vel=1.0, open_=False):
    dur = 0.4 if open_ else 0.08
    t = t_axis(dur)
    return vel * 0.6 * hp(noise(dur), 7500) * np.exp(-t * (9 if open_ else 65))


def tom(f, vel=1.0):
    t = t_axis(0.6)
    ff = f * (1 + 0.5 * np.exp(-t * 18))
    return vel * np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t * 7)


def timpani(f, vel=1.0, dur=2.5):
    t = t_axis(dur)
    glide = f * (1 + 0.04 * np.exp(-t * 20))
    y = np.zeros_like(t)
    for ratio, amp, dec in [(1, 1, 2.2), (1.504, 0.6, 2.8), (1.742, 0.35, 3.2), (2.0, 0.3, 3.8), (2.245, 0.2, 4.5)]:
        y += amp * np.sin(2 * np.pi * np.cumsum(glide * ratio) / SR) * np.exp(-t * dec)
    y += lp(noise(dur), 400) * np.exp(-t * 35) * 0.5
    return vel * norm(y)


def crash(dur=3.5, vel=1.0):
    t = t_axis(dur)
    y = hp(noise(dur), 3500) * np.exp(-t * 1.4) * 0.6
    for _ in range(40):
        f = _rng.uniform(2500, 11000)
        y += _rng.uniform(0.02, 0.06) * np.sin(2 * np.pi * f * t) * np.exp(-t * _rng.uniform(1.0, 2.6))
    y += bp(noise(dur), 2000, 9000) * np.exp(-t * 30)
    return vel * norm(y)


def sub_boom(dur=2.5):
    t = t_axis(dur)
    f = 30 + 32 * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.8)


def riser(dur):
    t = t_axis(dur)
    x = t / dur
    sweep = sweep_filter(noise(dur), "bandpass",
                         lambda tc: (300 * 30 ** (tc / dur) / 1.4, 300 * 30 ** (tc / dur) * 1.4))
    gliss = additive(80 * 10 ** x, dur, 0.3, kmax=30)
    rev_cym = crash(dur)[::-1]
    return norm(norm(sweep) * x ** 2.5 + 0.3 * norm(gliss) * x ** 3 + 0.5 * rev_cym * x)


def pluck(m, dur=0.7, vel=1.0, bright=0.5):
    """Pizzicato string via Karplus-Strong."""
    f = midi_hz(m)
    N = int(round(SR / f - 0.5))
    n = n_samples(dur)
    exc = np.zeros(n)
    exc[:N] = lp(_rng.uniform(-1, 1, N), 1200 + 6000 * bright)
    a = np.zeros(N + 2)
    a[0], a[N], a[N + 1] = 1, -0.4975, -0.4975
    y = signal.lfilter([1], a, exc)
    t = t_axis(dur)
    y = lp(y * np.exp(-t * 7), 3800) * np.clip(t / 0.002, 0, 1)
    return vel * norm(y)


def bass_note(m, dur, vel=1.0):
    f = midi_hz(m)
    t = t_axis(dur)
    roll = 0.12 + 0.6 * (1 - np.exp(-t * 14))
    y = additive(f, dur, roll, kmax=40) + 0.6 * np.sin(2 * np.pi * f * t)
    e = np.clip(t / 0.004, 0, 1) * (0.6 + 0.4 * np.exp(-t * 10)) * np.clip((dur - t) / 0.03, 0, 1)
    return vel * norm(np.tanh(1.5 * y * e))


def brass(midis, dur, vel=1.0):
    t = t_axis(dur)
    roll = 0.5 - 0.32 * np.clip(t / 0.05, 0, 1) + 0.15 * np.clip((t - 0.05) / 0.3, 0, 1)
    y = np.zeros_like(t)
    for m in midis:
        for cents in (-7, 0, 7):
            y += additive(midi_hz(m) * 2 ** (cents / 1200), dur, roll, kmax=36)
    e = np.clip(t / 0.018, 0, 1) * np.exp(-t * 3) * np.clip((dur - t) / 0.06, 0, 1)
    return vel * norm(np.tanh(0.8 * norm(y)) * e)


def string_short(m, dur=0.16, vel=1.0):
    t = t_axis(dur)
    y = sum(additive(midi_hz(m) * 2 ** (c / 1200), dur, 0.28, kmax=30) for c in (-5, 5))
    e = np.clip(t / 0.006, 0, 1) * np.exp(-t * 16) * np.clip((dur - t) / 0.02, 0, 1)
    return vel * norm(y * e)


def felt_piano(m, dur=4.0, vel=0.6):
    f = midi_hz(m)
    t = t_axis(dur)
    B, d0 = 0.0004, 0.5 + f / 600
    y = np.zeros_like(t)
    for k in range(1, 25):
        fk = k * f * np.sqrt(1 + B * k * k)
        if fk > NYQ * 0.9:
            break
        amp = vel ** (1 + 0.15 * k) / k ** 1.1 * np.exp(-(k - 1) * (0.55 - 0.35 * vel))
        dk = d0 * (1 + 0.25 * (k - 1))
        env = 0.55 * np.exp(-t * dk * 2.5) + 0.45 * np.exp(-t * dk * 0.45)
        for cents in (-0.6, 0.6):
            y += amp * 0.5 * env * np.sin(2 * np.pi * fk * 2 ** (cents / 1200) * t + _rng.uniform(0, 6.28))
    y *= np.clip(t / 0.004, 0, 1) * np.clip((dur - t) / 0.3, 0, 1)
    y += lp(noise(dur), 1200) * np.exp(-t * 90) * 0.02 * vel
    return y


def pad_chord(midis, dur, attack=1.4, release=1.8, roll=0.55):
    t = t_axis(dur)
    ro = roll + 0.06 * np.sin(2 * np.pi * 0.13 * t)
    y = np.zeros_like(t)
    for m in midis:
        for cents in (-7, 0, 7):
            y += additive(midi_hz(m) * 2 ** (cents / 1200), dur, ro, kmax=20)
    return norm(lp(y, 2500)) * smooth_ar(dur, attack, release)


def chime(m, dur=3.0, vel=1.0):
    f = midi_hz(m)
    t = t_axis(dur)
    y = np.zeros_like(t)
    for ratio, amp, dec in [(1, 1.0, 1.2), (2.0, 0.35, 2.0), (3.01, 0.12, 3.5), (4.2, 0.06, 5.0)]:
        y += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t * dec)
    return vel * y * np.clip(t / 0.003, 0, 1) * np.clip((dur - t) / 0.2, 0, 1)


# ================================================================ sound effects
def siren(dur, mode="wail"):
    t = t_axis(dur)
    if mode == "wail":
        ph = (t % 3.2) / 3.2
        shape = np.where(ph < 0.55, np.sin(np.pi / 2 * ph / 0.55), np.cos(np.pi / 2 * (ph - 0.55) / 0.45))
        f = 650 + 900 * shape
    else:  # yelp
        ph = (t % 0.34) / 0.34
        f = 700 + 850 * np.sin(np.pi / 2 * ph)
    y = np.tanh(2.5 * norm(additive(f, dur, 0.25, kmax=12, odd_only=True)))
    return norm(bp(y, 450, 4500))


def motorbike(dur, times, rpms):
    t = t_axis(dur)
    rpm = np.interp(t, times, rpms)
    f = rpm / 60.0
    phase = 2 * np.pi * np.cumsum(f) / SR
    pulse = (0.5 + 0.5 * np.cos(phase)) ** 6
    body = np.zeros_like(t)
    for k in range(1, 40):
        if k * f.max() > NYQ * 0.8:
            break
        body += 0.9 ** k * np.sin(k * phase + _rng.uniform(0, 6.28))
    nz = bp(noise(dur), 150, 2500) * pulse
    y = np.tanh(1.8 * (0.8 * pulse + 0.6 * norm(nz) + 0.3 * norm(body)))
    g = 0.45 + 0.55 * (rpm - min(rpms)) / (max(rpms) - min(rpms))
    return norm(lp(hp(y, 40), 3500) * g)


def tire_screech(dur):
    t = t_axis(dur)
    wob = lp(noise(dur), 6)
    f0 = 1050 + 120 * norm(wob)
    tone = np.sin(2 * np.pi * np.cumsum(f0) / SR) + 0.3 * np.sin(2 * np.pi * np.cumsum(2 * f0) / SR)
    am = 0.6 + 0.4 * norm(lp(noise(dur), 30))
    y = tone * am + 0.4 * norm(bp(noise(dur), 1500, 5000))
    return norm(y * np.clip(t / 0.05, 0, 1) * np.clip((dur - t) / 0.3, 0, 1))


def horn(dur, freqs=(410, 520)):
    y = sum(additive(f, dur, 0.18, kmax=20, odd_only=True) for f in freqs)
    return norm(bp(np.tanh(2 * norm(y)), 300, 3500) * env_ar(dur, 0.01, 0.03))


def alarm_bell(dur):
    t = t_axis(dur)
    strike = np.exp(-((t * 21) % 1) / 21 * 90)
    y = sum(a * np.sin(2 * np.pi * 1850 * r * t) for r, a in [(1, 1), (2.32, 0.5), (4.25, 0.3), (6.63, 0.15)])
    y = y * (0.35 + 0.65 * strike) + bp(noise(dur), 3000, 8000) * strike * 0.05
    return norm(y)


def helicopter(dur):
    t = t_axis(dur)
    y = np.zeros_like(t)
    tt = t_axis(0.07)
    slap = lp(noise(0.07), 900) * np.exp(-tt * 70) + 0.8 * np.sin(2 * np.pi * 75 * tt) * np.exp(-tt * 50)
    for bt in np.arange(0, dur - 0.07, 1 / 10.5):
        i = n_samples(bt)
        y[i:i + len(slap)] += slap * _rng.uniform(0.85, 1.0)
    y = norm(y) + 0.25 * norm(lp(brown(dur), 300)) + 0.02 * np.sin(2 * np.pi * 4100 * t)
    return norm(y)


def jackhammer(dur):
    t = t_axis(dur)
    y = np.zeros_like(t)
    tt = t_axis(0.04)
    hit = bp(noise(0.04), 1500, 5000) * np.exp(-tt * 220) * 0.6 + np.sin(2 * np.pi * 130 * tt) * np.exp(-tt * 90)
    hit += 0.15 * (np.sin(2 * np.pi * 2300 * tt) + np.sin(2 * np.pi * 3700 * tt)) * np.exp(-tt * 120)
    for bt in np.arange(0, dur - 0.04, 1 / 23):
        if (bt % 1.7) < 1.3:
            i = n_samples(bt)
            y[i:i + len(hit)] += hit
    return norm(y)


def traffic(dur):
    am = 0.7 + 0.3 * norm(lp(noise(dur), 0.3))
    return norm((norm(lp(brown(dur), 500)) + 0.3 * norm(lp(pink(dur), 2500))) * am)


def whoosh(dur):
    t = t_axis(dur)
    shape = lambda tc: np.sin(np.pi * np.clip(tc / dur, 0, 1))
    y = sweep_filter(noise(dur), "bandpass",
                     lambda tc: (300 * 8 ** shape(tc) / 1.6, 300 * 8 ** shape(tc) * 1.6))
    return norm(y * np.sin(np.pi * t / dur) ** 2)


def window_slide(dur=0.95):
    """Heavy glass sash on stainless rollers: roller rumble, brush-seal 'shhh', faint frame ring."""
    t = t_axis(dur)
    v = np.clip(t / 0.12, 0, 1) * (1 - np.clip((t - 0.12) / (dur - 0.12), 0, 1) ** 2)
    roller_am = 0.7 + 0.3 * np.sin(2 * np.pi * np.cumsum(35 * v) / SR)
    rumble = norm(bp(brown(dur), 70, 700)) * v ** 1.2 * roller_am
    shh = norm(bp(noise(dur), 2500, 9500)) * v ** 1.6 * 0.35
    ring = norm(bp(noise(dur), 850, 1050)) * v * 0.12
    return pan_mono(norm(rumble + shh + ring), np.linspace(-0.3, 0.3, len(t)))


def seal_thunk():
    """Sash meeting the interlock: low air-tight thump, gasket click, rubber puff."""
    dur = 1.0
    t = t_axis(dur)
    f = 52 + 45 * np.exp(-t * 25)
    thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 13)
    click = bp(noise(dur), 1200, 3800) * np.exp(-t * 260) * 0.45
    puff = lp(noise(dur), 350) * np.exp(-t * 28) * 0.35
    knock = bp(noise(dur), 180, 600) * np.exp(-t * 40) * 0.3
    return norm(thump + click + puff + knock)


def lock_clicks():
    """Multipoint lock: three hook clicks and a final handle clunk."""
    dur = 0.6
    t = t_axis(dur)
    y = np.zeros_like(t)

    def tick(t0, freqs, dec, amp):
        tt = np.clip(t - t0, 0, None)
        on = t >= t0
        return on * amp * (sum(np.sin(2 * np.pi * f * tt) for f in freqs) * np.exp(-tt * dec))

    for t0 in (0.0, 0.05, 0.10):
        y += tick(t0, (3150, 4720, 6900), 160, 0.5)
    y += tick(0.22, (1850, 2900), 60, 0.6) + tick(0.22, (200,), 45, 0.8)
    return norm(y)


def room_tone(dur):
    return norm(hp(lp(pink(dur), 350), 25))


def qalam_stroke(dur, times, speeds):
    """Reed pen dragged across paper: stick-slip micro-impulses and fibre friction, both driven by stroke speed."""
    t = t_axis(dur)
    v = np.interp(t, times, speeds)
    rate = (200 + 1400 * v) * (1 + 0.5 * norm(lp(noise(dur), 40)))
    ticks = np.floor(np.cumsum(np.clip(rate, 0, None)) / SR)
    imp = np.zeros_like(t)
    idx = np.nonzero(np.diff(ticks, prepend=0))[0]
    imp[idx] = _rng.uniform(0.3, 1.0, len(idx)) * v[idx]
    grains = norm(bp(imp, 1800, 7000))
    friction = norm(bp(noise(dur), 1200, 6000)) * v ** 1.3 * 0.35
    body = norm(bp(noise(dur), 300, 900)) * v * 0.1
    return norm((grains + friction + body) * env_ar(dur, 0.005, 0.02))


def nib_tap():
    """Nib touching the paper (a calligraphy dot)."""
    t = t_axis(0.12)
    return norm(bp(noise(0.12), 2000, 6000) * np.exp(-t * 400) + 0.5 * np.sin(2 * np.pi * 400 * t) * np.exp(-t * 120))


def ink_drip():
    """A single drop of ink landing on paper: a tiny rising 'plip' and a soft splat."""
    t = t_axis(0.25)
    f = 700 + 1300 * (1 - np.exp(-t * 40))
    plip = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)
    splat = lp(noise(0.25), 2500) * np.exp(-t * 60) * 0.3
    return norm(plip + splat)


def megaphone(x, sr_in):
    """Voice through a bullhorn: pitched up for urgency, band-limited, driven into the horn, with a horn resonance."""
    x = signal.resample_poly(x, SR, sr_in)
    x = signal.resample_poly(x, 100, 112)  # ~+2 semitones, slightly faster
    x = bp(x, 450, 3800, 4)
    x = np.tanh(2.5 * norm(x))  # driven, but not so hard the consonants smear
    return norm(x + 0.6 * bp(x, 1000, 1500))

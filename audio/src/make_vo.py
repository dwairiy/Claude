"""Scratch voiceover and megaphone lines via Piper neural TTS.

This is a GUIDE track for timing the edit. Replace it with the cast voice talent for the final mix.

    pip install piper-tts
    python3 audio/src/make_vo.py      # downloads voices on first run into ~/.cache/piper-voices
"""
import difflib
import os
import re
import ssl
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audio" / "vo"
CACHE = Path(os.environ.get("PIPER_VOICES", Path.home() / ".cache" / "piper-voices"))
HF = "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
VOICES = {
    "ar": "ar/ar_JO/kareem/medium/ar_JO-kareem-medium",
    "en": "en/en_US/ryan/high/en_US-ryan-high",
}
# Crews in KSA shout the loanword "أكشن" = "Action!", so one megaphone take serves both versions.
# (text, length_scale[, expected transcript when spelled phonetically]): diacritised Arabic for correct pronunciation; English spelled phonetically for brand names
LINES = {
    "ar": {
        "vo1": ("فِي الخَارِجِ... العَالَمُ لا يَهْدَأُ.", 1.0),
        "vo2": ("وَفِي الدَّاخِلِ... سَكِينَة.", 1.05),
        "vo3": ("مِنَ المُهِيبْ.", 1.0),
    },
    "en": {
        "vo1": ("Outside, the world never stops.", 1.1),
        "vo2": ("Inside... Sakeena.", 1.15, "Inside Sakina"),
        "vo3": ("By Al Mohib.", 1.1),
        "megaphone": ("Action!", 0.85),
    },
}


def voice_path(rel):
    CACHE.mkdir(parents=True, exist_ok=True)
    onnx = CACHE / (Path(rel).name + ".onnx")
    cafile = os.environ.get("SSL_CERT_FILE")
    ctx = ssl.create_default_context(cafile=cafile) if cafile else ssl.create_default_context()
    for suffix in (".onnx", ".onnx.json"):
        dst = CACHE / (Path(rel).name + suffix)
        if not dst.exists():
            print(f"downloading {dst.name} ...")
            with urllib.request.urlopen(HF + rel + suffix, context=ctx) as r:
                dst.write_bytes(r.read())
    return onnx


TAKES = 8  # Piper is stochastic: record several takes, keep the one Whisper hears most accurately


def _plain(text):
    text = re.sub(r"[\u064B-\u0652]", "", text.lower())  # strip Arabic diacritics
    return re.sub(r"[^\w\s]", "", text).split()


def _scorer():
    try:
        import numpy as np
        import soundfile as sf
        from faster_whisper import WhisperModel
        from scipy.signal import resample_poly
    except ImportError:
        print("faster-whisper not installed: keeping the first take of each line")
        return None
    model = WhisperModel("small", device="cpu", compute_type="int8")

    def score(path, lang, text):
        x, sr = sf.read(path)
        x = resample_poly(x, 16000, sr).astype(np.float32)
        segs, _ = model.transcribe(x, language=lang, beam_size=5)
        heard = " ".join(s.text for s in segs)
        return difflib.SequenceMatcher(None, _plain(text), _plain(heard)).ratio(), len(x) / 16000, heard.strip()
    return score


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    score = _scorer()
    for lang, lines in LINES.items():
        model = voice_path(VOICES[lang])
        for key, (text, scale, *expect) in lines.items():
            out = OUT / f"{lang}_{key}.wav"
            takes = []
            for k in range(TAKES if score else 1):
                take = OUT / f".take_{lang}_{key}_{k}.wav"
                subprocess.run([sys.executable, "-m", "piper", "-m", str(model), "-f", str(take),
                                "--length-scale", str(scale)], input=text.encode(), check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                takes.append((score(take, lang, expect[0] if expect else text) if score else (1.0, 0.0, ""), take))
            # most accurate first, then the shortest (tighter timing)
            (acc, dur, heard), best = max(takes, key=lambda tk: (round(tk[0][0], 2), -tk[0][1]))
            best.replace(out)
            for _, take in takes:
                take.unlink(missing_ok=True)
            print(f"{out.relative_to(ROOT)}  acc={acc:.2f} {dur:.2f}s  heard: {heard}")


if __name__ == "__main__":
    main()

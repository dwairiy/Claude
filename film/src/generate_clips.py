"""Generate the AI shots of "The First Word": Nano Banana keyframe, then Veo image-to-video.

    export GEMINI_API_KEY=...
    python3 film/src/generate_clips.py                 # the 11 exterior AI shots
    python3 film/src/generate_clips.py 05 14 --n 3     # selected shots, 3 variants each
    python3 film/src/generate_clips.py --include-live  # also AI placeholders for the live-action shots
    python3 film/src/render.py                         # re-cut: clips replace the boards automatically

Writes film/keyframes/shot_XX.png and film/clips/shot_XX[_vK].mp4 (variant 1 is used by the cut;
rename a better variant to shot_XX.mp4 to swap it in). Calligraphy (20, 22) and the end card (23)
stay rendered: AI image models cannot be trusted with Arabic letterforms.

Note: written against the public Gemini API (generateContent for images, predictLongRunning for Veo)
but not yet run here, because no key was available. Check the first shot before batch runs.
"""
import argparse
import base64
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILM = ROOT / "film"
API = "https://generativelanguage.googleapis.com/v1beta/"
IMAGE_MODELS = ["gemini-3-pro-image-preview", "gemini-2.5-flash-image"]   # Nano Banana Pro, Nano Banana
VIDEO_MODELS = ["veo-3.1-generate-preview", "veo-3.0-generate-001", "veo-3.0-fast-generate-001", "veo-2.0-generate-001"]
CTX = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or None)


def request(url, key, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, context=CTX, timeout=600) as r:
        return json.load(r)


def keyframe(prompt, key, out):
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}}}
    for model in IMAGE_MODELS:
        try:
            data = request(f"{API}models/{model}:generateContent", key, body)
        except urllib.error.HTTPError as e:
            print(f"    {model}: HTTP {e.code}")
            continue
        for part in data["candidates"][0]["content"]["parts"]:
            blob = part.get("inlineData") or part.get("inline_data")
            if blob:
                out.write_bytes(base64.b64decode(blob["data"]))
                return model
    raise RuntimeError("no keyframe generated")


def video(prompt, negative, image, key, out):
    inst = {"prompt": prompt, "image": {"bytesBase64Encoded": base64.b64encode(image.read_bytes()).decode(),
                                        "mimeType": "image/png"}}
    for model in VIDEO_MODELS:
        try:
            op = request(f"{API}models/{model}:predictLongRunning", key,
                         {"instances": [inst], "parameters": {"aspectRatio": "16:9", "negativePrompt": negative}})
        except urllib.error.HTTPError as e:
            print(f"    {model}: HTTP {e.code} {e.read()[:160]!r}")
            continue
        while not op.get("done"):
            time.sleep(10)
            op = request(f"{API}{op['name']}", key)
        if "error" in op:
            print(f"    {model}: {op['error']}")
            continue
        uri = op["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]
        req = urllib.request.Request(uri, headers={"x-goog-api-key": key})
        with urllib.request.urlopen(req, context=CTX, timeout=600) as r:
            out.write_bytes(r.read())
        return model
    raise RuntimeError("no video generated")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots", nargs="*")
    ap.add_argument("--n", type=int, default=1, help="variants per shot")
    ap.add_argument("--include-live", action="store_true")
    ap.add_argument("--keyframes-only", action="store_true")
    args = ap.parse_args()
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.exit("Set GEMINI_API_KEY first.")

    spec = json.loads((FILM / "shots_ai.json").read_text())
    pool = dict(spec["shots"], **(spec["live_placeholders"] if args.include_live else {}))
    todo = {k: v for k, v in pool.items() if not args.shots or k in args.shots}
    (FILM / "keyframes").mkdir(exist_ok=True)
    (FILM / "clips").mkdir(exist_ok=True)
    for sid, shot in todo.items():
        style = spec["interior_style"] if sid in spec["live_placeholders"] else spec["style"]
        kf_prompt = shot["keyframe"].format(**spec["characters"]) + "\n\n" + style
        mo_prompt = shot["motion"].format(**spec["characters"]) + " " + style
        kf = FILM / "keyframes" / f"shot_{sid}.png"
        if not kf.exists():
            print(f"shot {sid}: keyframe via {keyframe(kf_prompt, key, kf)}")
        if args.keyframes_only:
            continue
        for k in range(1, args.n + 1):
            out = FILM / "clips" / (f"shot_{sid}.mp4" if k == 1 else f"shot_{sid}_v{k}.mp4")
            if out.exists():
                continue
            print(f"shot {sid}: clip v{k} via {video(mo_prompt, spec['negative'], kf, key, out)}")


if __name__ == "__main__":
    main()

"""Generate AL MOHIB SAKINA product images with Google's Nano Banana (Gemini image models).

Usage:
    export GEMINI_API_KEY=...            # from https://aistudio.google.com/apikey
    python3 product_images/src/generate.py                  # all shots
    python3 product_images/src/generate.py 01 03 --n 3      # selected shots, 3 variants each
    python3 product_images/src/generate.py --model gemini-2.5-flash-image

Outputs land in product_images/output/<shot_id>_v<k>.png
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
PROMPTS = ROOT / "product_images" / "prompts.json"
OUT = ROOT / "product_images" / "output"
LOGO = ROOT / "brand" / "al_mohib_logo.png"
API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
# Nano Banana Pro first, then the original Nano Banana.
DEFAULT_MODELS = ["gemini-3-pro-image-preview", "gemini-2.5-flash-image"]


def _ssl_ctx():
    cafile = os.environ.get("SSL_CERT_FILE")
    return ssl.create_default_context(cafile=cafile) if cafile else ssl.create_default_context()


def call(model, key, parts, aspect_ratio):
    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect_ratio},
        },
    }
    req = urllib.request.Request(
        API.format(model=model),
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    with urllib.request.urlopen(req, context=_ssl_ctx(), timeout=300) as r:
        data = json.load(r)
    for cand in data.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            blob = part.get("inlineData") or part.get("inline_data")
            if blob:
                return base64.b64decode(blob["data"])
    raise RuntimeError(f"no image in response: {json.dumps(data)[:500]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots", nargs="*", help="shot id prefixes, e.g. 01 03")
    ap.add_argument("--n", type=int, default=2, help="variants per shot")
    ap.add_argument("--model", help="force a model id")
    args = ap.parse_args()

    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.exit("Set GEMINI_API_KEY (Google AI Studio key) first.")

    spec = json.loads(PROMPTS.read_text())
    shots = [s for s in spec["shots"] if not args.shots or any(s["id"].startswith(p) for p in args.shots)]
    models = [args.model] if args.model else DEFAULT_MODELS
    OUT.mkdir(parents=True, exist_ok=True)

    for shot in shots:
        text = f"{shot['prompt']}\n\n{spec['product_dna']}\n\n{spec['style']}"
        parts = [{"text": text}]
        if shot.get("use_logo_reference"):
            parts.append({"inlineData": {"mimeType": "image/png",
                                         "data": base64.b64encode(LOGO.read_bytes()).decode()}})
        for k in range(1, args.n + 1):
            for model in models:
                try:
                    img = call(model, key, parts, shot["aspect_ratio"])
                except urllib.error.HTTPError as e:
                    print(f"  {model}: HTTP {e.code} {e.read()[:200]!r}")
                    continue
                path = OUT / f"{shot['id']}_v{k}.png"
                path.write_bytes(img)
                print(f"{path.relative_to(ROOT)}  ({model})")
                break
            else:
                print(f"FAILED {shot['id']} v{k}")
            time.sleep(1)


if __name__ == "__main__":
    main()

# Film: "The First Word" (35 s)

| File | What it is |
|---|---|
| `out/sakina_the_first_word_animatic_AR.mp4` / `_EN.mp4` | **Animatic v1**: full 35 s cut, frame-accurate to soundtrack v2, 1080p25 |
| `src/render.py` | Builds the cut from `production/shot_list.csv`; clips, renders and boards are chosen per shot |
| `src/generate_clips.py` + `shots_ai.json` | Nano Banana keyframes, then Veo image-to-video for the AI shots (needs `GEMINI_API_KEY`) |
| `fonts/` | Amiri, IBM Plex Sans Arabic, Aref Ruqaa (all SIL Open Font License) |
| `logo_alpha.png` | AL Mohib logo cut out of its white background (interim; replace with the vector redraw) |

## What is in v1
- **Rendered at final quality (7 shots):** 01 inkwell ripple (one ring per bass note) · 15 the airborne hit with a flash on 24.00 · 16 the slide (the city through the closing gap) · 17 the seal macro · 20 calligraphy write-on of سكينة (the stroke follows the pen sound, and each of the 5 dots lands on its nib tap) · 22 ink-to-logotype · 23 end card (the panel slides and seals at 32.95, the logo resolves on the chime).
- **Boards (16 shots):** designed slates with framing, lens, move, fps and method, pending footage.
- Supers, VO subtitles (AR/EN) and a review burn-in (shot, source, time).

## Upgrade path
```bash
export GEMINI_API_KEY=...
python3 film/src/generate_clips.py                 # 11 exterior shots: keyframe, then Veo clip
python3 film/src/generate_clips.py --include-live  # optional: AI stand-ins for the 6 live-action shots
python3 film/src/render.py                         # boards are replaced by clips automatically
```
Real footage from the shoot day drops in the same way: name it `film/clips/shot_XX.mp4`.

# 05: Shot List and Production Plan: "The First Word"

**Shot list (sortable):** `production/shot_list.csv`: 23 shots plus 3 pickups. Continuous 0.0–35.0 s, locked to soundtrack v2.
**Method:** Hybrid. Live-action interior, AI-generated exterior, CG end card.

---

## 1. The production model at a glance

| Bucket | Shots | Share of runtime | Why this method |
|---|---|---|---|
| **LIVE** (1 shoot day) | 1, 4, 6, 10, 16–22 | about 15 s | Hands, faces, real calligraphy and the real product carry the emotion and the proof. AI is weakest exactly here. |
| **AI** (generated) | 2, 3, 5, 7–9, 11–15 | about 17 s | Stunts, a helicopter, a police convoy and a film set: very expensive to shoot, and fast, cheap and spectacular to generate. |
| **COMP** (live plate + AI) | 4, 16, 19, 21 | (within LIVE) | Chaos seen *through the glass*. This ties the two worlds together in one frame. |
| **CG / MoGraph** | 22 (morph), 23 | about 4 s | Ink-to-logotype and the SAKINA panel seal reveal |

**Design choices that make AI viable:**
- **The rider wears a helmet** (no face to keep consistent).
- **Exterior shots are all short** (0.5–3 s).
- **No exterior shot contains the hero family.**
- **Only one recurring AI character:** the Director, in shots 14 and 21. He gets a locked character reference sheet.

---

## 2. Schedule (5 weeks)

| Week | Pre-production | Generation and shoot | Post | Gate |
|---|---|---|---|---|
| **1** | Script lock · casting (grandfather, girl, hand double/calligrapher) · location scout · logo vector redraw · AI style frames | Nano Banana keyframes for the 11 AI shots (round 1) | — | **Storyboard and casting approval** |
| **2** | Recce · shoot schedule · props and wardrobe · calligraphy rehearsal (the word written 30+ times; pick the best) | AI keyframes round 2, then image-to-video (3–5 variants per shot) | Assembly of AI shots on the locked soundtrack | Look approval |
| **3** | — | **SHOOT DAY** (interior) plus the foley session | Selects · rough cut | **Rough cut** |
| **4** | — | AI pickups for gaps | Composites (4, 16, 19, 21) · ink morph · end card CG · grade | Fine cut |
| **5** | — | VO record (AR/EN talent) | Final mix (replace scratch VO and synth foley) · masters · cutdowns (15 s, 6 s, 9:16) | **Delivery** |

> The cut is built **to the music**, which is already locked. This is the opposite of normal practice, and it saves about a week: every sync point (hit 24.00, seal 25.00, dots 28.95–29.75) is known before the shoot.

---

## 3. Shoot day: one day, interior location

**Location requirements:** a high-rise apartment in Riyadh, ideally 15th floor or higher, with:
- a **floor-to-ceiling slim black sliding system** on a west-facing wall (for golden hour);
- a city view;
- 4 m or more of depth for the wide shot (shot 19);
- power and building permission to film.

Cover or tape any real hardware brand marks on the window.

**Call sheet (25 fps base; slow-motion at 50/200+):**

| Time | Setup | Shots | Notes |
|---|---|---|---|
| 07:00 | Crew call, load-in, dress the set | — | Art: desk, majlis seating, framed calligraphy, olive tree |
| 08:30 | **Inserts: inkwell and macro** | 1, 17, 18 | Ripple with a contact transducer under the desk playing the real bass track. Seal macro at the highest fps available. |
| 10:00 | **Hero product: the slide** | 16 + clean plates | Slider tracking with the panel. 10+ takes. Talent: grandfather's hand. |
| 11:30 | **Child block 1** (fresh energy) | 4, 6, 10 | Fan on the curtain, hard daylight, practical ink blot via a hidden pipette |
| 13:00 | Lunch · **child rest** | — | Observe the child working-hours limit |
| 14:00 | **Calligraphy:** the stroke and the dots | 20 (hand double), 22 (top shot) | The calligrapher writes the word for real, 10+ takes. Scan the best sheet at 1200 dpi. |
| 15:30 | **Foley session** (crew quiet) | P1 | Real slide, seal, lock, qalam on paper, ink drip. 96 kHz, 10+ takes each. |
| 16:30 | Light change, haze up | — | Pre-light the golden-hour wide |
| 17:00 | **Golden hour: child block 2** | 19, 21 | Haze for dust motes. Clean background plates for the Director comp. **About 40 min of usable light. Rehearse first.** |
| 18:00 | Clean plates · stills · BTS | P2, P3 | Product beauty stills for the portfolio |
| 19:00 | Wrap | | |

**Crew (lean, 10–12 people):**
- Director
- DOP
- 1st AC
- Gaffer plus 1 spark
- Art director/props
- Wardrobe/MUA
- Sound recordist (foley and guide)
- Calligrapher (consultant and hand double)
- PA
- BTS photographer
- **Child guardian** (mandatory)

**Kit:**
- Camera: cinema camera with 4K and 50p, plus 200p or more for shot 17 (e.g. Sony FX3/FX6 or RED Komodo; a Phantom only if the budget allows).
- Lenses: 24, 35, 50 and 85 mm, a 100 mm macro, and a probe lens (inkwell, seal).
- Grip: slider, top-down rig, tripod.
- Lighting: 600 W–1.2 kW daylight through the window (the "sun"), bounce and negative fill, haze machine, polariser and black flags (glass reflections).
- Practical effects: contact transducer and subwoofer (ripple), fan (curtain).

---

## 4. AI generation pipeline (exterior)

1. **Style lock.** One master style frame (teal-steel grade, long-lens compression, hard midday sun) is attached as a reference to every prompt.
2. **Keyframes:** Nano Banana, 3–4 variants per shot at 16:9 (`product_images/src/generate.py`, extended for storyboard frames once `GEMINI_API_KEY` is set).
3. **Character sheet** for the Director (front, 3/4, profile, holding the megaphone), used in shots 14 and 21.
4. **Image-to-video:** a current image-to-video model (e.g. Veo, Kling or Runway class). Write a motion prompt per shot from the shot list's *move/support* column, with 3–5 generations each.
5. **Selection:** pick on motion realism first, then continuity (direction of travel left/right; the bike must exit frame left in 5 and enter right in 12).
6. **Finishing:** upscale to UHD, add grain to match the live plates, and keep the two grades separate (teal city, gold interior).

**Rules:**
- No real brands, police or government livery.
- No recognisable real people.
- No Arabic text generated by AI (all text goes in as graphics in post).
- Disclose AI use where the platform or broadcaster requires it.

---

## 5. Post-production

| Step | Tool (or equivalent) | Notes |
|---|---|---|
| Edit | DaVinci Resolve / Premiere | Cut to the locked soundtrack. Markers at 16.0, 22.5, 24.0, 25.0, 26.3 and 32.4. |
| Composites | After Effects / Nuke | 4 and 19: AI city through the glass. 16: the airborne bike visible in the closing gap. 21: the Director outside. Add glass reflections over the comp for realism. |
| Ink-to-logo (22) | AE + fluid sim | Starts from the scanned calligraphy; resolves into the **vector** SAKINA logotype |
| End card (23) | Blender + AE | 3D SAKINA panel slides and seals, revealing the AL Mohib logo. Keyed to the sonic logo (slide 32.4, seal 32.95, chime 33.0). |
| Grade | Resolve | Two looks: teal-steel city, warm sand interior. The **grade turns at the seal.** |
| Sound | (soundtrack v2 sessions) | Swap the scratch VO for talent, swap synth foley for the P1 recordings where better, final mix to −23 LUFS (TV) and −14 LUFS (web) |

---

## 6. Budget (indicative, SAR; validate with local quotes)

| Line | Lean portfolio | Agency grade |
|---|---|---|
| Talent: grandfather, girl, calligrapher/hand double | 5,000–10,000 | 15,000–30,000 |
| DOP and camera crew (1 day) | 6,000–10,000 | 15,000–25,000 |
| Camera, lens, grip and lighting package | 4,000–8,000 | 12,000–25,000 |
| Location (penthouse, 1 day) | 2,000–5,000 | 8,000–20,000 |
| Art, props, wardrobe | 2,000–4,000 | 8,000–15,000 |
| AI generation (image and video credits, upscaling) | 1,000–3,000 | 3,000–8,000 |
| VO talent (AR and EN) and studio | 1,500–4,000 | 5,000–12,000 |
| Post: edit, comp, CG end card, grade | 8,000–20,000 | 40,000–90,000 |
| Music (keep the original synth score / commission a live re-record) | 0 | 15,000–40,000 |
| Production management, insurance, permits | 2,000–4,000 | 10,000–25,000 |
| Contingency, 10% | 3,000–7,000 | 13,000–29,000 |
| **Total** | **≈ 35,000–75,000** | **≈ 145,000–320,000** |

For comparison, the same film **fully live action** (stunt team, police vehicles, a helicopter, road closures) would likely cost **SAR 1–2M+**. The hybrid model delivers about 90% of the visual scale for about 5% of that cost. That trade-off is itself a strong portfolio talking point.

---

## 7. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| AI shots look "AI" (morphing, physics errors) | Cheapens the film | Short shots, motion blur and grain, a strict selection pass, and keep AI out of the hero moments |
| Golden-hour window too short (shots 19, 21) | Lose the emotional climax | Rehearse beforehand; lights pre-set; a fallback lamp-sun rig through the window |
| Child fatigue | Weak performance | Child blocks at 11:30 and 17:00 only; hand double covers every insert |
| Glass reflections show the crew | Unusable plates | Black flags, polariser, crew in black; remove in comp |
| Calligraphy quality | Credibility with an Arab audience | A professional khattat writes it for real; pick the best of 30+ rehearsal sheets |
| Logo is a raster AI-style render | Soft end card, no animation | **Vector redraw in week 1** (also fixes the brand for all future use) |
| Real brand on the rental window | Legal / confusion | Cover hardware marks; product identity added in post |
| Likeness and music rights | Portfolio takedown | Talent releases signed on set; the score is 100% original (we own it) |

---

## 8. Deliverables
| Asset | Spec |
|---|---|
| Hero 35 s (AR, EN) | ProRes 422 HQ, UHD 3840×2160 and HD 1920×1080, 25 fps, 48 kHz/24-bit, TV −23 LUFS |
| Cutdowns 15 s, 6 s | Same spec |
| Social 9:16 (35 s and 15 s) | H.264 1080×1920, −14 LUFS, burnt-in AR/EN subtitles |
| Textless and M&E | For re-versioning |
| Portfolio case study | 60–90 s BTS film (hybrid workflow breakdown), 10 product and production stills |

---

## Immediate next actions
1. **Add `GEMINI_API_KEY`** to unlock keyframes and the storyboard (weeks 1–2 depend on it).
2. **Brief a calligrapher.** Choose a style: Thuluth (majestic) or Diwani (flowing, intimate). **Diwani is recommended**, because its flow mirrors "the steady stroke".
3. **Logo vector redraw.**
4. **Location shortlist:** 3 Riyadh high-rises with west-facing floor-to-ceiling sliders.

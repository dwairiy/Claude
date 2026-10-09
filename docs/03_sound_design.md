# 03: Original Score and Sound Design: "SAKINA"

Every note and sound effect is **synthesized from code** (`audio/src/`): oscillators, noise and filters. No samples, libraries or third-party recordings are used. The soundtrack is 100% original and copyright-clean for the portfolio.

**Listen:** `audio/sakina_soundtrack_preview.mp4` (timeline with playhead) or `audio/mix/sakina_tvc35_temp_mix_web.mp3`

## Sonic concept
> **The window is the mute button.**

The reference ad shows silence; we **cause it**. For 24 seconds the city is loud, with heist score, sirens, a motorbike, a helicopter and horns. A hand slides the SAKINA sash closed. As the gap narrows, the world is filtered down to almost nothing (a 12 kHz to 1.5 kHz low-pass, −14 dB). On the **air-tight seal** it collapses to −40 dB and 140 Hz, and the scene goes from chaos to a breath of near-silence. Then the multipoint lock clicks shut. The product delivers the benefit on the soundtrack, in real time.

## Cue sheet (picture-locked to the 35 s structure)
| Time | Element | Detail |
|---|---|---|
| 0:00–0:24 | **Cue 1, "Rush Hour Heist"** | D minor, 120 BPM. Comic-tense heist score: Karplus-Strong pizzicato motif, driving saw bass ostinato, kit, brass stabs (from bar 5), spiccato strings and timpani (bars 9–11). Bar 12 builds with a snare/timpani roll, a chromatic string climb and a riser. |
| 0:00–0:25 | City SFX | Bank alarm bell, siren wail with a Doppler pass-by, horns, motorbike rev and pass (Doppler), tire screech, a yelp siren, jackhammer, a helicopter approaching, a second bike pass, horn lean. Traffic bed rises 6 dB across the act. |
| 0:23.88 | Breath | The roll stops an eighth note early, a gap so the hit lands |
| **0:24.00** | **Climax hit** | Tutti brass on D minor, timpani, crash, sub boom |
| 0:24.18 | Perspective cut | Cut to interior: outside −5 dB and starts muffling |
| 0:24.20–0:25.00 | **Window slide** (foley hero) | Roller rumble, brush-seal *shhh*, faint frame ring, panning left to right with the sash |
| **0:25.00** | **SEAL** | Low air-tight thump (97 to 52 Hz), gasket click, rubber puff. The outside world dies. |
| 0:25.45 | Multipoint lock | Three hook clicks and a handle clunk |
| 0:25.0–0:26.2 | Near-silence | Room tone at −52 dB, with a muffled ghost of the city fading out |
| 0:26.2–0:33 | **Cue 2, "Sakina"** | D major (the parallel major is the "light enters" moment). Felt piano with a warm pad: Dmaj9, Bm9, Gmaj7, Asus4. Long hall reverb. |
| 0:27.0–0:32.0 | **VO slot** | Kept clear: piano is sparse and the pad sits under the voice |
| 0:32.4–0:35 | **Sonic logo** | Soft slide, seal, then the rising **A–D–F#** "Sakina" chime, doubled on piano and resolving on D. Fade at 34.2 s. |

## Sonic logo: "slide · seal · Sakina"
`audio/sonic_logo/al_mohib_sakina_sonic_logo.wav` (3.6 s, −16 LUFS)
A three-part brand sound built from the product itself: the **slide** (motion), the **seal** (silence and protection), and a three-note rising major chime (calm and premium). It works as an end-card button, a social sting, a showroom door chime or an app sound.

## Deliverables
| Path | Content |
|---|---|
| `audio/mix/…_broadcast_-23LUFS.wav` | TV master, EBU R128: **−23.0 LUFS integrated**, true peak ≤ −1 dBTP, 48 kHz / 24-bit |
| `audio/mix/…_web_-14LUFS.wav` / `.mp3` | Online/social master, −14 LUFS, −1.4 dBTP |
| `audio/stems/` | 5 aligned stems (Act 1 music, exterior SFX, interior foley, Act 3 music, sonic logo), 35.000 s each, ready for the final dub |
| `audio/sfx/` | 14 standalone one-shots (sirens, bike, screech, horn, alarm, helicopter, jackhammer, traffic, whoosh, window slide, seal, lock, room tone) |
| `audio/mix/loudness_report.json` | Measured loudness per act |
| `audio/sakina_soundtrack_timeline.png` | Waveform and spectrogram with the act markers |

Measured (web master): Act 1 −13.7 LUFS → calm −26.2 LUFS. The **12 LU drop is the product benefit, made audible**.

## Compliance notes (KSA/GCC broadcast)
- **No gunshots** in the soundtrack. The reference's guns are a liability for GCC and family-slot clearance, so our chaos reads as an "urban storm", not violence. Picture should follow the same rule (chase, not shoot-out).
- Broadcast master is delivered at EBU R128 (−23 LUFS), the standard used by most GCC broadcasters. Confirm the exact delivery spec with the channel.

## Honest limitations and the upgrade path
- **I can't listen to audio.** Quality was checked by measurement: BS.1770 loudness, true peak, a per-segment balance check (e.g. the window slide sits about 7 dB over the muffled exterior), and spectrogram review. **Your ears are the final judge.** Tell me what to change: "more comic", "bigger hit", "warmer piano", and so on.
- Synthesized instruments are a strong **temp score**, not an orchestra. For the final film, hand `docs/03_sound_design.md` and the stems to a composer or session players (strings, brass, piano) and keep the structure, keys and sync points. The SFX design and the sonic logo can ship as they are, or be re-recorded as real foley of an actual sash closing.
- Timings follow the reference's 35 s structure. They will be re-conformed once our own script and storyboard are locked. Every sync point is a named constant at the top of `audio/src/build.py`.

## Regenerate
```bash
pip install numpy scipy soundfile matplotlib
python3 audio/src/build.py      # about 90 s; rebuilds everything above
```

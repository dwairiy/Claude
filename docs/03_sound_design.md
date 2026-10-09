# 03: Original Score and Sound Design: "SAKINA"

Every note and sound effect is **synthesized from code** (`audio/src/`): oscillators, noise and filters. No samples, libraries or third-party recordings are used. The soundtrack is 100% original and copyright-clean for the portfolio.

**Listen:** `audio/sakina_soundtrack_preview_AR.mp4` / `_EN.mp4` (timeline with playhead), or `audio/mix/sakina_tvc35_AR_web_-14LUFS.mp3` / `_EN_…mp3`

**Current version: v2.** Conformed to the script "The First Word" (doc 04). See the v2 changelog below.

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

## v2 changelog: script revisions (doc 04)
| TC | Revision | How |
|---|---|---|
| 05.0–07.5, 10.5–11.0, 15.5–17.0 | Interior cuts in Act 1 | Exterior −3 dB plus a 0.6 s room reverb (heard through the open window) |
| 05.4–06.3, 10.5 | First letter **س** and the wobble | Qalam scratches and a nib tap (mostly masked, felt more than heard) |
| 16.0 | **Ink blot** | Ink-drip "plip"; the score ducks −9 dB for 0.4 s (comic beat) |
| 22.5 | **Megaphone "Action!"** | One take serves both versions (KSA crews shout the loanword "أكشن"). Bullhorn chain: +2 st, band-limited 450–3800 Hz, horn drive and resonance, outdoor slap. |
| 26.3–28.85 | **Qalam on paper** (Act 3 hero foley) | Stick-slip friction synthesis driven by stroke speed, then 5 nib taps for the dots of سكينة (2 under ي, 1 over ن, 2 over ة) |
| 26.8–32.8 | **VO laid** (AR and EN) | Lines run back to back from 26.8 s; a guard fails the build if the VO would run past the logo's seal (32.95 s) |
| under the VO | **Side-chain** | Pad −3 dB and logo slide −6 dB while the voice speaks; piano untouched |

### VO timings (as laid)
| | Line 1 | Line 2 | Line 3 |
|---|---|---|---|
| **AR** | 26.80–29.22 *في الخارج… العالم لا يهدأ* | 29.52–31.50 *وفي الداخل… سكينة* | 31.75–32.79 *من المهيب* |
| **EN** | 26.80–28.80 *Outside, the world never stops.* | 29.20–30.31 *Inside… SAKINA.* | 30.66–31.56 *By AL Mohib.* |

### Scratch VO: how it was made and checked
- Piper neural TTS (Arabic: `ar_JO-kareem`, English: `en_US-ryan`). This is a **guide track for the edit**, not the final voice. The final mix uses cast talent.
- **Best-of-8 takes:** each line is generated 8 times. Whisper transcribes every take, and the most accurate one is kept, with the shortest winning ties. **All 7 lines scored 100% against the script.**
- Arabic is fully diacritised (e.g. *يَهْدَأُ*, *المُهِيبْ*) to force the right pronunciation.
- **In-mix check:** the English VO and the megaphone transcribe correctly from the finished mix. In the Arabic mix, Whisper hears *يهدأ* as "يهدو" (the final hamza is masked by the music) and *المهيب* as "المهيبة". I traced the second one: the isolated line transcribes correctly with every processing variant, so it is Whisper's language model guessing a feminine ending after "سكينة", not the audio. **Confirm both by ear.**

## Deliverables
| Path | Content |
|---|---|
| `audio/mix/sakina_tvc35_AR_broadcast_-23LUFS.wav` | **Arabic TV master**: −23.0 LUFS, ≤ −1 dBTP, 48 kHz / 24-bit |
| `audio/mix/sakina_tvc35_EN_broadcast_-23LUFS.wav` | English TV master |
| `audio/mix/sakina_tvc35_ME_broadcast_-23LUFS.wav` | **M&E** (music and effects, no dialogue) for re-voicing into any language |
| `audio/mix/…_{AR,EN}_web_-14LUFS.wav/.mp3` | Online/social masters, −14 LUFS, −1.4 dBTP |
| `audio/stems/` | 9 aligned stems (35.000 s): music ×2, exterior SFX, window foley, pen and ink foley, sonic logo, megaphone, VO AR, VO EN. Stems are pre-side-chain; the ducking happens in the mix. |
| `audio/vo/` | Selected scratch VO takes (22.05 kHz) |
| `audio/sfx/` | 17 one-shots (adds qalam stroke, nib tap, ink drip) |
| `audio/mix/loudness_report.json` | Loudness per version and act, VO timings, VO-over-music ratio |
| `audio/sakina_soundtrack_timeline_{AR,EN}.png` | Waveform and spectrogram with acts, VO lines and foley marked |

Measured (web masters): Act 1 −13.5 LUFS, post-seal −24.8, calm with VO −17.1 (AR) / −17.6 (EN). **The VO sits 9 LU over the music**, so dialogue stays clear without the music disappearing.

## Compliance notes (KSA/GCC broadcast)
- **No gunshots** in the soundtrack. The reference's guns are a liability for GCC and family-slot clearance, so our chaos reads as an "urban storm", not violence. Picture should follow the same rule (chase, not shoot-out).
- Broadcast master is delivered at EBU R128 (−23 LUFS), the standard used by most GCC broadcasters. Confirm the exact delivery spec with the channel.

## Honest limitations and the upgrade path
- **I can't listen to audio.** Quality was checked by measurement: BS.1770 loudness, true peak, a per-segment balance check (e.g. the window slide sits about 7 dB over the muffled exterior), and spectrogram review. **Your ears are the final judge.** Tell me what to change: "more comic", "bigger hit", "warmer piano", and so on.
- Synthesized instruments are a strong **temp score**, not an orchestra. For the final film, hand `docs/03_sound_design.md` and the stems to a composer or session players (strings, brass, piano) and keep the structure, keys and sync points. The SFX design and the sonic logo can ship as they are, or be re-recorded as real foley of an actual sash closing.
- Every sync point is a named constant at the top of `audio/src/build.py`, so re-conforming to the final picture edit is a one-line change per beat.

## Regenerate
```bash
pip install -r audio/requirements.txt
python3 audio/src/make_vo.py    # optional: re-record scratch VO (Piper + Whisper take selection)
python3 audio/src/build.py      # about 2.5 min; rebuilds all versions, stems, previews
```

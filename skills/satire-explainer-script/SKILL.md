---
name: satire-explainer-script
description: >
  Write a long-form YouTube satire explainer about money, status and excess: a fact-dense
  script with a deadpan broke-narrator voice, a joke every 10-15 seconds, and a paired
  ON-SCREEN column for visual gags. Formats: tier list, price ladder ("every level of"),
  second-person journey ("what happens when you..."), and big question ("what's the most...").
  Use when the user says "satire script", "tier list script", "every level of", "what happens
  when you", "money explainer", "write it like that rich-people channel", or wants a
  humorous long-form YouTube script in English, Hindi or Hinglish. Also covers infotainment
  mode for health and finance explainers ("health explainer", "finance explainer", "make
  this educational but funny").
user-invokable: true
argument-hint: "[topic] [format] [language]"
license: MIT
metadata:
  author: Regent Scale
  version: "0.1.0"
  category: content
  source-study: "Jackpockets channel, 5 of 11 transcripts (2026-11-05)"
---

# Satire Explainer Script

Writes scripts that learn from the mechanics of a proven channel (money satire, about 23x views per subscriber) without copying its jokes, entries or wording.

## File map (one job per file)
| File | Job |
|---|---|
| `references/joke-mechanics.md` | **What is funny.** The Jackpockets devices and structure. This is the foundation. |
| `references/voice-and-tts.md` | **How it sounds.** Rishabh Jain (Labour Law Advisor) rhythm, ElevenLabs tags, TTS formatting. |
| `references/hindi-humor.md` | **What is current.** Indian references and slang, updated by the user. |
| `references/channel-data.md` | Format and title evidence. |
| `references/visual-gag-map.md` | ON SCREEN column and editor brief. |
| `references/health-finance-rules-india.md`, `hindi-and-legal.md` | Safety check before publishing. |

Raw research (do not load into context; distilled into the files above): `D:\Regent Scale\youtube\research\` holds the jackpockets, labour-law-advisor and hindi-memes folders.

## Load only what you need
- `references/joke-mechanics.md`: always. The 14 devices plus the structural patterns.
- `references/channel-data.md`: only when choosing a format or a title.
- `references/visual-gag-map.md`: only when writing the ON-SCREEN column or briefing an editor.
- `references/hindi-and-legal.md`: always for Hindi or Hinglish, and for any script naming real Indian people.
- `references/health-finance-rules-india.md`: in infotainment mode, as a wording and brand-deal check only.
- `references/hindi-humor.md`: always for Hindi or Hinglish.
- `references/voice-and-tts.md`: always for Hindi or Hinglish voiceover. Jokes come from joke-mechanics; sentence rhythm and TTS formatting come from this file.

## Inputs
Topic, format, language (English, Hindi or Hinglish), target length, mode (satire or infotainment), and the narrator persona (default: middle-class broke narrator). Outside money and status topics, the formula needs a substitute engine: a big curiosity question, a stake the viewer feels (their money, their body, their parents) and a myth to bust.

## Infotainment mode (health, finance)
Modeled on the two biggest source videos, which are the most educational ones.
- **Ratio:** one teaching point per beat. A laugh every 20 to 30 seconds, not every 10 to 15. The facts are the product and the jokes are the glue.
- **Formats that fit:** escalation ladder ("What's the most dangerous food in your kitchen?"), game with a rule ("Could you retire on a Rs 30,000 salary?"), second-person journey ("What happens to your body when you stop sugar for 30 days?"), myth-bust ending.
- **Mandatory devices:** scale translation (device 15) on every big number, a myth-bust bookend, a sincere awe or care pivot (device 18).
- **Joke targets:** marketing, myths, systems, our own habits. Shock tags (device 10) are off.
- **We inform, we do not advise.** Content is proven, sourced findings and case studies, not instructions or tips. The rules file matters only where wording drifts into advice ("you should buy or eat X") and for paid brand integrations.
- **Hindi or Hinglish:** joke-mechanics.md is the foundation. Its devices, structure and level of execution stay the same as the source channel, in any language. `references/hindi-humor.md` is a culture-and-freshness layer: what Indian audiences laugh at today, references and current slang. Use it to localize a device, not to replace one. The user keeps adding current terms to it, so read its latest version every run.

## Workflow

**Research gate (mandatory, set by the user):** no script until two things exist and the user has approved them: (a) the tier list or ladder as a structure only, and (b) `facts.md`, a fact sheet with a source URL and a confidence grade (A primary, B reputable secondary, C clinic or marketing, ? unverified) for every fact. The script may use only facts from that sheet, need not use all of them, and never uses a "?" fact. Infotainment, not a lecture: pick the facts that make the best jokes and the clearest picture.

0. **Mirror the source first (mandatory).** Find the Jackpockets video whose format matches (levels = Every Level Of Watches; journey = Lottery; ladder = Most Expensive Thing; game = $1 Trillion; tier list = House Tier List). Read its first 60 lines from `D:\Regent Scale\youtube\research\jackpockets\transcripts\`, and write the new hook beat for beat on that skeleton (see "Format skeletons" in joke-mechanics.md). The voice file only changes how Hindi sentences join. It never changes the structure, the jokes or the tone.
1. **Pick the format and title.** Prefer question or second-person titles over tier lists (see channel-data.md). Write 5 title options and 3 hook options, then let the user choose.
2. **Fact file first, jokes second.** Gather 12 to 25 entries or steps, each with 3 or more checkable specifics (price, year, model, quote) and a source URL. About 70% of the script is real information. No fact, no joke. Save the facts as `facts.md` next to the script.
3. **Find the spine.**
   - Bookend: what extreme opens the video and returns at the end in a new light?
   - Long-game plant: who or what gets introduced warmly early and pays off late? (device 7)
   - Runner: which line repeats 3 times with an evolving meaning? (device 8)
   - Quiet thesis: what true idea about wealth or status does the ending land? (device 14)
4. **Order for rhythm.** Alternate long story entries (40 to 90s) with rapid-fire one-liners (3 to 6s). Put an open loop in the first 60 seconds (god-tier tease, "you will see why later"). Place the strongest story at about 60 to 70% of runtime.
5. **Draft the beats** in the two-column format below. For each entry: credential, surprising fact, escalation, twist or clip, verdict with a joke reason.
6. **Joke pass.** Tag every laugh beat with its device number. Check: one beat every 10 to 15 seconds, no device used twice in a row, at least 4 different devices per 2 minutes, and 2 or more clip-as-punchline moments per 5 minutes.
7. **Visual pass.** At least 40% of the laugh beats must be carried or doubled by the ON-SCREEN column. Mark every deliberate silence `[SIL 1-3s]`. Use the gag codes from visual-gag-map.md.
8. **Safety pass.** Punch up only. For India, apply every rule in hindi-and-legal.md. Flag each risky line with `[LEGAL]` and propose a safer version.
9. **Read-aloud pass.** Every sentence must be speakable in one breath. Cut any adjective that does not carry a fact or a laugh.
10. **Humanize.** No em dashes, no AI slop words (run the ig-human checks if available).

## Output format

```
TITLE: ...
HOOK OPTIONS: 1) ... 2) ... 3) ...
SPINE: bookend = ... | plant = ... | runner = ... | thesis = ...

| # | Time | VO (narration) | ON SCREEN | Gag | Source |
|---|------|----------------|-----------|-----|--------|
| 1 | 0:00 | From a ... to a ..., this is ... | range montage, cheapest to priciest | range hook | - |
| 2 | 0:06 | ... | CLIP: ... (2s) | D9 | [url] |
```

End with: a clip list for the footage researcher (source, timestamp, purpose), the `[LEGAL]` flags, and a laugh-beat count per minute.

## Never
- Reuse a joke, phrasing or entry from the source channel. Study the mechanism and rebuild it.
- Invent a fact, a quote or a number to set up a joke. Mock-precise numbers (device 12) must be obviously absurd.
- Analyze video frames to "see" gags. Visual knowledge comes from the user's annotations in visual-gag-map.md.

# Visual Gag Map (inferred from transcripts)

Each row below is a guess from the transcript: a silence gap, a sentence that stops mid-thought, or a line that only makes sense with an image. The "Actually on screen" column is still empty. To fill it, dissect the video with the `video-dissect` skill and look at that range with `frames` (only when a script needs it; ask the user before looking at many ranges). The user does not need to annotate by hand.

## Gag codes (use them in the ON SCREEN column)


- `LIT` literal image of the word just spoken
- `CUT` hard cut to a contradicting image or clip
- `MEME` meme or reaction image
- `CLIP` real interview, news or vlog clip delivering the punchline
- `SFX` sound effect or music sting carrying the joke
- `ZOOM` zoom or freeze frame on a detail
- `TEXT` on-screen text, label or caption joke
- `AI` AI-generated image
- `SIL` deliberate silence held for a beat

## Billionaire House Tier List (z_3LPJZXawE)
| Time | Line | Guess | Actually on screen |
|---|---|---|---|
| 00:02:48 | "has its own ZIP code" / "I'm too poor to even be looking" | narrator-reaction image | |
| 00:03:25 | "human experiments on children... S tier" | absurd image, instant S tier stamp | |
| 00:03:56-04:02 | Buffett "memories" then 6s gap | sentimental montage, then a CUT | |
| 00:04:08-04:11 | Ambani mansion "in the middle of the... hood" | aerial pullback to the slums | |
| 00:04:45-49 | Kanye "solving homelessness" / "they already have tents" | LIT tent city | |
| 00:05:07-14 | "100,000 acre city in the Middle... East" | gap, likely SFX or map | |
| 00:05:31-36 | Jack Ma criticizes government, 5s gap | ominous music, disappearance visual | |
| 00:05:51-55 | Jordan house "because it's in... Illinois" | gap, Illinois image or SFX | |
| 00:06:38-41 | Bezos "further from the... IRS" | gap, IRS logo | |
| 00:08:20-25 | "visuals will be made with AI. AI is a brilliant tool" | deliberately bad AI image | |
| 00:09:25 | "expensive psych ward" | LIT | |

## Celebrity Car Tier List (W3QZEobImTs)
| Time | Line | Guess | Actually on screen |
|---|---|---|---|
| 00:00:06-12 | DiCaprio "batteries... environment", gap, "F tier" | yacht or private jet CUT | |
| 00:00:41-44 | McLaren "no driver aids", gap | Mr. Bean clip | |
| 00:01:34-46 | "giant spider on my doorstep... Holy mackerel" | CLIP, likely a Ferrari spider reveal | |
| 00:03:06-08 | "children dying of hunger... Not enough." | CLIP reaction | |
| 00:05:08-11 | chocolate car "doing ad libs" | SFX Travis ad lib | |
| 00:06:09-14 | Mitsubishi "jump off a cliff" | LIT car off a cliff or stock crash chart | |
| 00:07:10-14 | "beating up Asians" | archive news | |
| 00:09:52-56 | Elvis shoots the car, gap, "bullet holes" | SFX gunshots | |
| 00:12:21-25 | RDJ charity, 4s gap | Iron Man clip | |
| 00:13:04-11 | Shaq smart car | CLIP | |
| 00:16:08 | 13s gap before MrBeast | montage or CLIP | |

## Billionaire Car Tier List (bu8zvWoYSkI)
| Time | Line | Guess | Actually on screen |
|---|---|---|---|
| 00:00:11-15 | gap, "the second car is a $1.4M Pagani" | CUT reveal | |
| 00:00:24-29 | Griffin "$200M on this... interesting assortment of paint" | painting, ZOOM | |
| 00:01:53 | Jay-Z car, 6s gap | car CLIP, SFX | |
| 00:02:05-12 | Ballmer Ford hand-delivered, 7s gap | CLIP | |
| 00:03:45-51 | "touching the truck's handle bestows frugality" | holy light, choir SFX | |
| 00:07:04-10 | "watch this" then the crash into an embankment | SFX crash, black screen | |

## Every Level Of Watches (WYKam9rBDtQ)
| Time | Line | Guess | Actually on screen |
|---|---|---|---|
| 00:01:19-23 | "maybe you should buy another... or maybe you shouldn't" | tone shift, Apple-ad parody | |
| 00:01:55-58 | "three colorful circles" | ZOOM on Activity rings | |
| 00:03:54-04:01 | Hamilton "sent in a pocket watch", gap | SIL or SFX | |
| 00:04:16-20 | "one giant leap for the Omega marketing team" | moon landing footage, TEXT | |
| 00:05:31-55 | Genta deadline "11:59 pm" | clock or student meme | |
| 00:08:24-26 | "they squished it" | LIT squish SFX | |
| 00:08:51-55 | "according to the Cartier marketing department", gap | record scratch | |
| 00:11:13-17 | "little African boys" | do not adapt (punch-down) | |

## What Happens When You Win The Lottery (XO5KrFb9yhM)
| Time | Line | Guess | Actually on screen |
|---|---|---|---|
| 00:00:36-41 | "lost your ticket... three of them didn't survive" | news headlines | |
| 00:01:45-49 | the boss calls, gap | ringtone SFX, phone UI | |
| 00:02:56-03:00 | "next to the reward for killing you" | giant check, WANTED poster | |
| 00:06:11 | "But one thing's missing. That's better." | a purely visual addition to the mansion | |
| 00:08:34 | "rich person parties, woman" | rapid image list | |
| 00:09:07-12 | "statistical glitch", 5s gap | glitch effect | |
| 00:10:00 | "Jason?" then the news clip | record scratch, CLIP | |
| 00:12:22-25 | "you were never... [cut]" | final cut | |

## Image library (tagged by Gemini)
- Library folder: `D:\Regent Scale\youtube\assets\images\` (the user drops images here, subfolders allowed).
- Tag new images with the global skill `image-tagger`: `tag-images.ps1 <folder> --dry-run`, then without `--dry-run` once the user agrees (it costs Gemini calls). It skips images already tagged.
- Index: `<folder>\_index.jsonl`, one JSON line per image (description, on_image_text, kind, meme_template, mood, tags, edit_uses, risky).
- When writing the ON SCREEN column, grep the index for the beat's mood and tags and cite the file, e.g. `IMG: reactions/shocked-uncle.jpg`. Never cite an image whose `risky` field is not empty without flagging it `[LEGAL]`.

# Voice and TTS Script Rules (Hindi / Hinglish)

Jokes come from joke-mechanics.md (Jackpockets). **How the sentences sound** comes from this file. It is modeled on Rishabh Jain (Labour Law Advisor). Study his rhythm only, never his jokes or lines. Source transcripts: `D:\Regent Scale\youtube\research\labour-law-advisor\transcripts\`.

## How Rishabh talks (observed patterns)

1. **Number first, then repeat it as a question.** "₹50 लाख। कितने? ₹50 लाख..." The repeat gives the ear a second chance and creates a pause.
2. **He asks the viewer's question out loud, then answers it.** "पता है क्यों?", "फर्म में कितना पैसा बचा?", "कितने परसेंट का? 12% का।", "क्यों चुना? स्पॉन्सर है इसलिए चुना।" Use about one every 20 to 30 seconds. This is the main thing that makes a script sound spoken, not written.
3. **Chained prerequisites.** "टैक्स समझने से पहले ये समझना पड़ेगा कि टैक्स लगता किस पे है, और उसको समझने से पहले..." The explanation is a staircase, one step per sentence.
4. **The last word starts the next sentence.** "इसमें एक कंडीशन है। कंडीशन ये है कि..."
5. **Jargon stays English, then gets defined immediately.** "Bifacial का मतलब, दोनों साइड पे सोलर सेल्स।" Hindi is the grammar glue. English is the nouns.
6. **Named, recurring people in examples.** "मान लो एक फर्म है मेरी और मनदीप की", "भोले भाले राहुल". The examples are about people, not "a person".
7. **Spoken glue words, used naturally:** देखो, यार, ना (mid-sentence: "हम सबकी ना..."), मान लो, तो, अब, बट, खैर, मतलब, यानी, ऑल इन ऑल. About one or two per 3 sentences, never two in a row.
8. **Short sentences.** 5 to 15 words. Fragments are fine ("तीन अंडे। इक्कीस रुपये।"). One idea per sentence.
9. **Honest, self-roasting asides.** "हम रह गए थोड़े गरीब।" "स्पॉन्सर है इसलिए चुना।" "दिमाग का दही हो जाएगा, लेकिन मज़ा बहुत आएगा।"
10. **Promise plus open loop at the start.** "किसकी कौन सी entity है, ये आगे बता दूँगा।" "इसका फायदा कुछ ही देर में पता चलेगा।"
11. **Personify the system.** "सरकार इतनी भी दयालु नहीं है।"
12. **Exact number, then the rounded one.** "₹22,50,000... मतलब लगभग साढ़े बाईस लाख।"

## AI tells to delete (from the user's feedback on draft 01)
- Written-Hindi connectors: "जिसमें ... के हिसाब से", "अब मज़ेदार बात यह है कि", "तीनों में एक ही चीज़ है". Real speakers say "और पता है इसमें क्या है?" instead.
- A punchline on every line. Real speech has plain, flat setup lines between the jokes.
- Perfectly symmetric triplets on every beat. Use the stinger list (device 2) at most once a minute.
- Acronyms and institutions normies don't know (ICMR, NIN, DIAAS). Say "सरकारी guidelines", "doctors", "एक बड़ी study".
- Weird or obscure "elite" items (bird's-nest soup, nursery rhymes). Elite means a smart *observation* about something everyone knows (eggs, dal, the gym bhaiya), not an obscure *object*.

## Rhythm must never cost fun (user feedback, draft 02)
Draft 02 sounded human but lost the laughs. The rhythm rules shape *how* a line is said. They never replace the joke density from joke-mechanics.md. In the hook, keep a laugh every 8 to 12 seconds. In the body, every 20 to 30 seconds (infotainment mode). If a rewrite for rhythm removes a joke, put the joke back in a spoken form.

## ElevenLabs v3 audio tags
v3 reads square-bracket tags as performance directions. It has no SSML, so tags plus punctuation do the work. Any descriptive word in brackets is attempted, but these are the documented ones:
- **Emotion and tone:** [sarcastic], [excited], [curious], [mischievously], [sad], [annoyed], [thoughtful], [surprised], [serious]
- **Delivery:** [whispers], [sighs], [laughs], [exhales], [deadpan]
- **Pace:** [rushed], [rapid-fire], [slows down], [deliberate], [drawn out]
- **Pauses:** [pause], [short pause], [continues after a beat], plus "..." and new lines

**Rules:**
1. One tag at the start of a line, at most two per line. A tag lasts until the next one, so reset with [neutral] or a new tag.
2. The default voice is dry and deadpan. Tags mark the *changes* (a sarcastic aside, a rushed list, a slow reveal). Do not tag every line.
3. Tags stay in English, even inside Devanagari text.
4. Hindi tag behavior is not documented by ElevenLabs. Test each new tag on one line before relying on it, and log what works here.
5. v3 works best with a designed voice or an instant voice clone. Pick the voice once and keep it for the whole channel.
6. Other tools: Narration Box also takes bracket emotion tags in Hindi.

## VoiceStudio (local, free; installed at D:\VoiceStudio)
Its default engine (OmniVoice) reads **unknown tags out loud as words**, so never paste an ElevenLabs-tagged script into it.
- **Works:** `[pause]` (350 ms), `[pause 500ms]`, `[pause 1s]` (up to 10 s), `[laughter]`, `[sigh]`.
- **Whisper** is a style setting in voice design, not an inline tag.
- **No emotion tags.** Delivery comes from punctuation, short lines and pauses. Keep the default voice deadpan.
- Write one master script with ElevenLabs tags, then make the VoiceStudio version by deleting emotion and pace tags and turning [pause] beats into `[pause Nms]`.

## TTS formatting rules
- **Script in Devanagari** for Hindi words, **English nouns in Latin** (protein, gym, label). Hindi in Roman script makes TTS mispronounce it.
- **Numbers as words**, the way you'd say them: "इक्कीस रुपये", "चार हज़ार", "सत्तर percent". Never "₹21" or "70%" in the TTS text.
- **Pauses:** "।" is a normal stop, "..." is a dramatic beat (about 0.7s), and a new line is a breath. Mark longer silences for the editor as `[SIL 1s]`. They are not read aloud.
- **Emphasis:** short sentences, not capitals. TTS ignores most styling.
- **Whispers and asides:** write `(धीरे से)` for the editor or voice settings, and keep the line under 8 words.
- Read every line aloud once. If you run out of breath, split it.

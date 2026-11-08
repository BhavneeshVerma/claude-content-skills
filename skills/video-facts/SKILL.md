---
name: video-facts
description: Research a YouTube video after the angle is picked and build facts.md - the list of entries (ways, tiers, levels), blind spots most viewers have never heard of, real dated cases and study data, real human stories, every line with a source URL and a grade (A, B, C, ?). Uses Reddit (through the user's Chrome), news and papers, parallel research agents and a verification pass that opens the original pages. Use when the user says "facts", "research this video", "build facts.md", "find blind spots", "real stories", "real cases", or after video-angle is approved and before satire-explainer-script.
---

# Video Facts

The script may only use what is in `facts.md`, so this file decides how good the video can be. Two failures to avoid, both from the user: facts that only repeat what everyone knows ("I did not learn anything new"), and facts that lecture or are flimsy. Every way or tier needs either a blind spot or a real case, and every line needs a source.

## Inputs
- `angle.md` approved (the chosen angle and skeleton) and the channel `audience.md`.
- The channel `CONTEXT.md` and `youtube/CONTEXT.md` (rules: inform never advise, sincere beat for deaths, jokes on our habits).
- The starting list in `topic-ideas.md`, if any.
- An earlier `facts.md` from the same channel as the format reference.

## Step 0: Tools first (before any long run)
Check the tools before spending time or tokens. If something needs setup, do it or tell the user the exact steps right away; never let an agent run for long on a broken tool.
- Reddit: `opencli profile list` must show a connected Chrome profile (OpenCLI lives in `~/.agent-reach/tools/npm-global`; if the extension says "reconnecting", run `opencli doctor` to start the helper). `agent-reach reddit search`, Reddit `.json` URLs, old.reddit, WebSearch on reddit.com and headless browsers are all blocked; only the user's Chrome works.
- Web search and page reading for news and papers.
- Ask before anything that costs credits (shared rule).

## Step 1: Brainstorm the long list
From the angle, topic ideas and your own knowledge, list 15-25 candidate entries. Mark each: obvious (the viewer already knows) or blind spot (most of the audience has not heard of it). Widen the topic to its culture, not only its literal meaning (the winter video took in bonfires, kangri, cough syrup season). Expect the user to cut a third.

## Step 2: Blind-spot scout (Reddit plus news)
Find what real people in the audience say, fear and get wrong. Run the script, read only the digest:
```
python -I <skill>/scripts/reddit_gather.py "angithi" "gas geyser fainted" "<hinglish term>" --threads 8 --skip "restaurant|zomato" --out <notes>/reddit-digest.md
python -I <skill>/scripts/reddit_gather.py --read <thread url> <thread url> --out <notes>/reddit-threads.md
```
- Search in English, Hinglish and Hindi words the audience uses (`audience.md`). Indian subreddits: india, delhi, indiasocial, AskIndia, mumbai, bangalore, twoxindiamums, IndianMedSchool (doctors' ER stories), trekkingIndia, plus city subs.
- Reddit rate-limits after about 30 pages: batch the searches, 5 seconds per page (the script does this), stop at 3 empty pages.
- A Reddit post is a lead, not a fact: find the news report or paper behind it, or mark it `?`.

## Step 3: Parallel research agents
Split the entries into 3-5 groups and send one background agent per group (`general-purpose`). Each agent gets the rules below, writes its full results to the shared notes folder, and returns only a ranked top 10. Cap each at about 20 minutes; a stuck agent is stopped, not waited on.
Each agent finds, per entry: the strongest number (official Indian data first: NCRB, MoRTH, IMD, ICMR, AIIMS, NHRC; then WHO, CDC, NHS; then peer-reviewed papers), 2-4 dated Indian cases with outlet and URL, and anything that contradicts the popular belief.

## Step 4: Verification pass
One or two agents open the original page (PDF, report table, paper abstract) for every headline number and every case date. They fix wrong years, wrong totals and citations that cannot be found. Known traps:
- One state's count used as a national count; say "sirf Gujarat mein" if that is all there is.
- Police "suspected" causes stated as final; the script says "police ke mutaabik".
- A foreign figure used as if it were Indian; say where it is from.
- Season fit: the thing must actually peak in this season (flu peaks in the monsoon in the plains, not winter).
- Viral videos and "N cigarettes a day" style headlines: grade C or drop.

## Step 5: Real stories pass
For each entry, find one human story the script could retell: survivors, near misses, a family's account, a doctor's case, a twist (the boy who slept in another room). Sources: long-form news features (ThePrint ground reports, Newslaundry, The News Minute, BBC Hindi, Scroll), Reddit first-person posts, YouTube interviews (YouTube search through agent-reach is mostly noise; search outlets by the person's name instead). Private people: first names only, or none.

## Step 6: Write facts.md
```
# <Title>: <N> Ways + Fact Sheet
Angle, target length, "the script may use only facts from this sheet".
Confidence key: A primary, B reputable secondary, C marketing or clinic, ? unverified.
## The <N> ways (structure only, no script)
| # | Way | Who it hits | Best proof | Rough time |   (★ = blind spot)
Curiosity gaps the script can use. Dropped (with the reason and source). Open user decisions.
## 1. <Way>
1.1 **<claim>:** numbers, who found it, year. Grade.
- URL
## Real stories (pick list for the script)
S<way>.<n> one paragraph, grade, URL. "No story found" list.
## Open before the script
Traps the script must not fall into; what is still unverified.
```
No em dashes. Keep the earlier numbering when entries are dropped (references like 12.5 stay valid); move dropped material to `_archive/old-drafts/`.

## Gate
The user approves `facts.md` (they will cut and add entries). Update the video's `status.md` and the channel `CONTEXT.md` video table. Log decisions and corrections in `youtube/feedback-log.md`. Do not write the script; that is `satire-explainer-script`, in a new session.

## Never
- Pad with facts everyone knows, or advice ("aapko yeh karna chahiye").
- Invent a national total, a date or a name to fill a gap; write the gap down instead.
- Keep an entry that does not happen to this audience's people (the user dropped "peanut in a child's lung" for this reason) or is not really tied to the topic (kite string was "rarely related to winters only").
- Let a research agent run on a broken tool, or read raw pages when a digest will do.

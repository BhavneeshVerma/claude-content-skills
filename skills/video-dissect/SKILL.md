---
name: video-dissect
description: >
  Break one video link into a research folder: stats (views, likes, comments, subscribers), top comments,
  the video, an MP3, a timestamped transcript (Gemini first), every cut with a keyframe, pauses, and a
  summary with words per minute and cuts per minute. Then look at any time range as frames, or have Gemini
  watch a range. Works for YouTube, public Instagram reels, X videos and Reddit threads. Use when the user
  pastes a video link and says "dissect", "break down", "study this video", "analyze this", "get the
  transcript", "download this", "what happens at 2:15", or "look at this part". For searching or finding
  posts across platforms, use agent-reach instead; this skill is for one link you already have.
user-invokable: true
argument-hint: "<link> | frames <folder> <start> <end> | describe <folder> <start> <end>"
license: MIT
metadata:
  author: Regent Scale
  version: "1.0.0"
  category: research
---

# Video Dissect

One command turns a link into everything needed to study its writing and its edit. Every download and cache stays on D:.

## Commands
Run with PowerShell. The launcher sits next to this file: `scripts/dissect.ps1`.

| Want | Command |
|---|---|
| Dissect a link | `scripts/dissect.ps1 <link> [--out DIR] [--no-video] [--max-comments 200]` |
| Look at a range yourself (Claude reads the images) | `scripts/dissect.ps1 frames <folder> <start> <end> [--max 30] [--mode scene\|uniform]` |
| Have Gemini watch a range (motion, sound, cuts) | `scripts/dissect.ps1 describe <folder> <start> <end> ["question"]` |

Times are `mm:ss` or `hh:mm:ss`. Default output: `D:\Regent Scale\_library\videos\<platform>-<title>\` (set `DISSECT_OUT` to change).

## What the folder holds
- `summary.md`: read this first. Stats, words per minute, cuts per minute, average shot length, longest pauses, first 30 seconds of transcript, top comments.
- `meta.json`, `comments.json`, `video.mp4` (720p), `audio.mp3`.
- `transcript.txt`: `[hh:mm:ss] line`. Its first line names the source.
- `shots.csv` and `keyframes/shot-NNN.jpg`: one image per cut.
- `frames-<start>-<end>/`: from the frames command, with a `transcript.txt` of what is said over those frames.
- `describe-<start>-<end>.md`: from the describe command.

## Rules
1. **Transcript order:** uploaded captions in the spoken language, then Gemini, then YouTube auto captions, then faster-whisper on this PC. On a 503 it tries the next newest Gemini model; on a 429 (quota) it stops.
2. **Looking at video costs tokens.** Default to `summary.md` and the transcript. Open keyframes or run `frames` only for the ranges the task needs, and keep `--max` at 30 or less unless the user asks for more. Use `describe` (Gemini) only when the user asks, or when motion or sound matters and frames cannot show it.
3. `scene` mode takes one frame per cut in the range (best for edit study); `uniform` spreads frames evenly (best for a talking head with few cuts).
4. Instagram and X work only for public posts; never log in with the user's main accounts.
5. The Gemini key comes from the `GEMINI_API_KEY` environment variable, else a `.env` in the current folder or its parents, else `D:\Regent Scale\.env`. Never print the key.

## Needs
`uv` on PATH. The launcher pulls yt-dlp, ffmpeg (bundled), PySceneDetect, google-genai and faster-whisper into `D:\dev-cache`.

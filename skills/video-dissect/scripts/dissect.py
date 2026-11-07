"""Dissect one video link into a research folder: stats, comments, video, mp3, transcript, cuts, keyframes, pauses.

Run through the launcher next to this file (keeps every download and cache on D:):
    dissect.ps1 <link> [--out DIR] [--no-video] [--max-comments 200]
    dissect.ps1 frames <folder> <start> <end> [--max 30] [--mode scene|uniform]   (frames for Claude to look at)
    dissect.ps1 describe <folder> <start> <end> ["question"]                      (Gemini watches the clip)

Works for YouTube, public Instagram reels and X videos (via yt-dlp), and Reddit threads (public .json, no login).

Transcript order: uploaded (human) captions > Gemini > auto captions > faster-whisper on this PC.
Gemini is used for the transcript only when there are no human captions, and for "describe" only when asked.
"""
import argparse, json, os, re, subprocess, sys, time, urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HOME_BASE = Path(r"D:\Regent Scale")  # holds .env and the library; override with GEMINI_API_KEY / DISSECT_OUT
DEFAULT_OUT = Path(os.environ.get("DISSECT_OUT") or HOME_BASE / "_library" / "videos")


def ffmpeg_exe() -> str:
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def slug(s: str, n: int = 50) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:n].strip("-") or "video"


def ts(sec: float) -> str:
    sec = int(sec)
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


# ---------- env and Gemini ----------
def load_env() -> dict:
    if os.environ.get("GEMINI_API_KEY"):
        return {"GEMINI_API_KEY": os.environ["GEMINI_API_KEY"], "GEMINI_MODEL": os.environ.get("GEMINI_MODEL", "")}
    f = next((d / ".env" for d in [Path.cwd(), *Path.cwd().parents, HOME_BASE] if (d / ".env").exists()), None)
    if not f:
        return {}
    return dict(l.strip().split("=", 1) for l in f.open(encoding="utf8") if "=" in l and not l.startswith("#"))


def gemini():
    env = load_env()
    if not env.get("GEMINI_API_KEY"):
        return None, None
    from google import genai
    client = genai.Client(api_key=env["GEMINI_API_KEY"])
    names = [m.name.split("/")[-1] for m in client.models.list()]
    flash = [n for n in names if re.fullmatch(r"gemini-\d+(\.\d+)?-flash", n)]
    model = max(flash, key=lambda n: float(re.findall(r"\d+(?:\.\d+)?", n)[0])) if flash else env.get("GEMINI_MODEL") or "gemini-flash-latest"
    client._flash_models = sorted(set(n for n in names if re.fullmatch(r"gemini-[\d.]+-(flash|flash-lite|pro)", n)),
                                  key=lambda n: (-float(re.findall(r"[\d.]+", n)[0]), "lite" in n))
    return client, model


def upload(client, path: Path):
    f = client.files.upload(file=str(path))
    while f.state and f.state.name == "PROCESSING":
        time.sleep(3)
        f = client.files.get(name=f.name)
    if f.state and f.state.name == "FAILED":
        raise RuntimeError("Gemini could not process the file")
    return f


TRANSCRIBE_PROMPT = """Transcribe this audio exactly as spoken, for a script writer studying delivery.
Return ONLY JSON: a list of {"t": "hh:mm:ss", "text": "..."} with one item per spoken sentence or short phrase (max ~12 words).
Rules: keep the original language. Hindi in Devanagari, English words in Latin script, as people actually mix them.
Mark music, laughter or sound effects in square brackets, e.g. [music], [laughs]. Mark unclear words [unclear]. Do not summarize or fix grammar."""


def transcribe_gemini(mp3: Path):
    client, model = gemini()
    if not client:
        raise RuntimeError("no GEMINI_API_KEY in .env")
    from google.genai import types
    f = upload(client, mp3)
    r, last = None, None
    chain = [model, model] + [m for m in client._flash_models if m != model][:4]
    for m in chain:  # retry once, then the next newest models this key can use (503 = overloaded)
        try:
            r = client.models.generate_content(model=m, contents=[f, TRANSCRIBE_PROMPT],
                                               config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1))
            model = m
            break
        except Exception as e:
            last = e
            print(f"  gemini {m}: {str(e)[:60]}")
            if "429" in str(e):
                break  # quota: do not burn more requests
            time.sleep(8)
    if r is None:
        raise last
    rows = json.loads(r.text)
    try:
        client.files.delete(name=f.name)
    except Exception:
        pass
    return [f"[{x['t']}] {x['text']}" for x in rows], f"gemini ({model})"


def transcribe_whisper(mp3: Path):
    from faster_whisper import WhisperModel
    try:
        m = WhisperModel("medium", device="cuda", compute_type="int8_float16")
    except Exception:
        m = WhisperModel("medium", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(str(mp3), vad_filter=True)
    return [f"[{ts(s.start)}] {s.text.strip()}" for s in segs], "faster-whisper medium (local)"


def vtt_to_lines(vtt: Path):
    out, last = [], None
    cur_t = None
    for line in vtt.read_text(encoding="utf8", errors="ignore").splitlines():
        m = re.match(r"(\d+):(\d\d):(\d\d)\.\d+ -->", line) or re.match(r"(\d\d):(\d\d)\.\d+ -->", line)
        if m:
            g = [int(x) for x in m.groups()]
            cur_t = g[0] * 3600 + g[1] * 60 + g[2] if len(g) == 3 else g[0] * 60 + g[1]
            continue
        text = re.sub(r"<[^>]+>", "", line).strip()
        if not text or cur_t is None or text == last or "-->" in text or text.startswith(("WEBVTT", "Kind:", "Language:")):
            continue
        out.append(f"[{ts(cur_t)}] {text}")
        last = text
    return out


# ---------- video steps ----------
def fetch(url: str, out: Path, args):
    import yt_dlp
    probe = yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}).extract_info(url, download=False)
    folder = out / f"{slug(probe.get('extractor_key', 'web'), 12)}-{slug(probe.get('title') or probe.get('id', 'video'))}"
    folder.mkdir(parents=True, exist_ok=True)
    opts = {
        "quiet": True, "no_warnings": True,
        "outtmpl": str(folder / "video.%(ext)s"),
        "format": "bv*[height<=720]+ba/b[height<=720]/b",
        "merge_output_format": "mp4",
        "ffmpeg_location": ffmpeg_exe(),
        "getcomments": args.max_comments > 0,
        "extractor_args": {"youtube": {"max_comments": [str(args.max_comments)], "comment_sort": ["top"]}},
        "skip_download": args.no_video,
    }
    info = yt_dlp.YoutubeDL(opts).extract_info(url, download=True)
    # captions in a separate pass, so a rate limit (429) never kills the run
    human = [l for l in (probe.get("subtitles") or {}) if l.split("-")[0] in ("en", "hi")]
    auto = [l for l in (probe.get("automatic_captions") or {}) if l.endswith("-orig")][:1]
    for langs in ([*human[:2]], auto):
        if not langs:
            continue
        try:
            yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True, "outtmpl": str(folder / "video.%(ext)s"),
                              "writesubtitles": bool(human), "writeautomaticsub": langs is auto,
                              "subtitleslangs": langs, "subtitlesformat": "vtt"}).download([url])
        except Exception as e:
            print("captions skipped:", str(e)[:120])
    keep = ["id", "title", "webpage_url", "channel", "uploader", "channel_follower_count", "upload_date", "duration",
            "view_count", "like_count", "comment_count", "tags", "categories", "chapters", "description", "language"]
    meta = {k: info.get(k) for k in keep if info.get(k) is not None}
    if probe.get("comment_count") is not None:
        meta["comment_count"] = probe["comment_count"]  # real total, not just the ones downloaded
    meta["human_captions"] = sorted((info.get("subtitles") or {}).keys())
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf8")
    comments = sorted(info.get("comments") or [], key=lambda c: c.get("like_count") or 0, reverse=True)
    (folder / "comments.json").write_text(json.dumps(
        [{"likes": c.get("like_count"), "author": c.get("author"), "text": c.get("text")} for c in comments],
        ensure_ascii=False, indent=1), encoding="utf8")
    return folder, meta


def video_file(folder: Path):
    return next((v for v in sorted(folder.glob("video.*")) if v.suffix in (".mp4", ".mkv", ".webm")), None)


def make_mp3(folder: Path):
    vid = video_file(folder)
    if not vid:
        return None
    mp3 = folder / "audio.mp3"
    if not mp3.exists():
        subprocess.run([ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(vid), "-vn", "-ac", "1", "-b:a", "64k", str(mp3)], check=True)
    return mp3


def transcript(folder: Path, meta: dict, mp3):
    vtts = sorted(folder.glob("video.*.vtt"))
    spoken = (meta.get("language") or "").split("-")[0]
    # uploaded captions count only if they are in the spoken language (an English track on a Hindi video is a translation)
    human = [v for v in vtts if v.name.split(".")[-2] in meta["human_captions"] and spoken and v.name.split(".")[-2].split("-")[0] == spoken]
    attempts = []
    if human:
        attempts.append(("uploaded captions", lambda: (vtt_to_lines(human[0]), f"uploaded captions ({human[0].name})")))
    if mp3:
        attempts.append(("gemini", lambda: transcribe_gemini(mp3)))
    auto = [v for v in vtts if v not in human]
    if auto:
        pick = next((v for v in auto if "orig" in v.name), auto[0])
        attempts.append(("auto captions", lambda: (vtt_to_lines(pick), f"YouTube auto captions ({pick.name})")))
    if mp3:
        attempts.append(("whisper", lambda: transcribe_whisper(mp3)))
    for name, fn in attempts:
        try:
            lines, src = fn()
            if lines:
                (folder / "transcript.txt").write_text(f"# source: {src}\n" + "\n".join(lines), encoding="utf8")
                print("transcript:", src)
                return lines
        except Exception as e:
            print(f"transcript via {name} failed: {str(e)[:150]}")
    return []


def cuts(folder: Path):
    vid = video_file(folder)
    if not vid:
        return []
    from scenedetect import detect, ContentDetector, open_video, save_images
    scenes = detect(str(vid), ContentDetector(threshold=27))
    kf = folder / "keyframes"
    kf.mkdir(exist_ok=True)
    if scenes:
        save_images(scenes, open_video(str(vid)), num_images=1, output_dir=str(kf),
                    image_name_template="shot-$SCENE_NUMBER", width=480)
    rows = [(i + 1, s.get_seconds(), e.get_seconds()) for i, (s, e) in enumerate(scenes)]
    with (folder / "shots.csv").open("w", encoding="utf8") as f:
        f.write("shot,start,end,length_s,keyframe\n")
        for n, s, e in rows:
            f.write(f"{n},{ts(s)},{ts(e)},{e - s:.1f},keyframes/shot-{n:03d}.jpg\n")
    return rows


def pauses(folder: Path, mp3):
    if not mp3:
        return []
    r = subprocess.run([ffmpeg_exe(), "-i", str(mp3), "-af", "silencedetect=noise=-32dB:d=0.6", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf8", errors="ignore")
    ends = re.findall(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", r.stderr)
    return [(float(e) - float(d), float(d)) for e, d in ends]


def summary(folder: Path, meta: dict, lines, shots, gaps):
    dur = meta.get("duration") or 0
    body = [re.sub(r"^\[[^\]]+\]\s*", "", l) for l in lines]
    words = sum(len(b.split()) for b in body)
    hook = [l for l in lines if (m := re.match(r"\[(\d+):(\d+):(\d+)\]", l)) and int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) < 30]
    top = json.loads((folder / "comments.json").read_text(encoding="utf8"))[:10]
    md = [f"# {meta.get('title', '')}", "",
          f"- Link: {meta.get('webpage_url', '')}",
          f"- Channel: {meta.get('channel') or meta.get('uploader', '')} ({meta.get('channel_follower_count', '?')} subscribers)",
          f"- Uploaded: {meta.get('upload_date', '?')} | Duration: {ts(dur)}",
          f"- Views {meta.get('view_count', '?')} | Likes {meta.get('like_count', '?')} | Comments {meta.get('comment_count', '?')}",
          ""]
    if dur:
        md += [f"- Speaking pace: {words / (dur / 60):.0f} words/min ({words} words)",
               f"- Cuts: {len(shots)} shots, {len(shots) / (dur / 60):.1f} cuts/min, average shot {dur / max(len(shots), 1):.1f}s"]
    md += [f"- Pauses over 0.6s: {len(gaps)}; longest: " + ", ".join(f"{ts(s)} ({d:.1f}s)" for s, d in sorted(gaps, key=lambda g: -g[1])[:5]), "",
           "## Hook (first 30 seconds)", *hook, "", "## Top comments"]
    md += [f"- ({c['likes']}) {(c['text'] or '').strip()[:200]}" for c in top]
    (folder / "summary.md").write_text("\n".join(md), encoding="utf8")


# ---------- reddit ----------
def reddit(url: str, out: Path):
    req = urllib.request.Request(url.split("?")[0].rstrip("/") + ".json?limit=200", headers={"User-Agent": "regent-scale-research/1.0"})
    data = json.loads(urllib.request.urlopen(req, timeout=30).read())
    post = data[0]["data"]["children"][0]["data"]
    folder = out / f"reddit-{slug(post['title'])}"
    folder.mkdir(parents=True, exist_ok=True)

    def walk(children, depth=0):
        for c in children:
            d = c.get("data", {})
            if c.get("kind") != "t1":
                continue
            yield {"depth": depth, "score": d.get("score"), "author": d.get("author"), "text": d.get("body")}
            rep = d.get("replies")
            if isinstance(rep, dict):
                yield from walk(rep["data"]["children"], depth + 1)

    comments = list(walk(data[1]["data"]["children"]))
    meta = {k: post.get(k) for k in ["title", "subreddit", "author", "score", "upvote_ratio", "num_comments", "created_utc", "url", "selftext"]}
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf8")
    (folder / "comments.json").write_text(json.dumps(comments, ensure_ascii=False, indent=1), encoding="utf8")
    top = sorted([c for c in comments if c["depth"] == 0], key=lambda c: -(c["score"] or 0))[:15]
    md = [f"# r/{meta['subreddit']}: {meta['title']}", f"- Score {meta['score']} ({meta['upvote_ratio']}), {meta['num_comments']} comments", "",
          (meta["selftext"] or "")[:2000], "", "## Top comments"] + [f"- ({c['score']}) {(c['text'] or '')[:300]}" for c in top]
    (folder / "summary.md").write_text("\n".join(md), encoding="utf8")
    print("saved", folder)


# ---------- describe a section with Gemini ----------
def describe(folder: Path, start: str, end: str, question: str):
    def secs(x):
        p = [int(v) for v in x.split(":")]
        return sum(v * 60 ** i for i, v in enumerate(reversed(p)))
    client, model = gemini()
    if not client:
        sys.exit("no GEMINI_API_KEY in .env")
    from google.genai import types
    vid = video_file(folder)
    clip = folder / f"clip-{secs(start)}-{secs(end)}.mp4"
    subprocess.run([ffmpeg_exe(), "-y", "-loglevel", "error", "-ss", str(secs(start)), "-to", str(secs(end)), "-i", str(vid),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "30", "-vf", "scale=-2:480", "-c:a", "aac", "-b:a", "64k", str(clip)], check=True)
    f = upload(client, clip)
    prompt = question or ("Describe this clip beat by beat for a comedy writer and editor: what is on screen, any text, "
                          "the cuts, music and sound effects, and exactly where and how each joke lands (picture, words, sound or the cut).")
    r = client.models.generate_content(model=model, contents=[f, prompt], config=types.GenerateContentConfig(temperature=0.3))
    out = folder / f"describe-{secs(start)}-{secs(end)}.md"
    out.write_text(f"# {start}-{end} ({model})\n\n{r.text}", encoding="utf8")
    try:
        client.files.delete(name=f.name)
    except Exception:
        pass
    clip.unlink(missing_ok=True)
    print(r.text)
    print("saved", out)


# ---------- focused frames for Claude to look at ----------
def frames(folder: Path, start: str, end: str, cap: int, mode: str):
    def secs(x):
        p = [float(v) for v in x.split(":")]
        return sum(v * 60 ** i for i, v in enumerate(reversed(p)))
    vid = video_file(folder)
    if not vid:
        sys.exit("no video in folder; run dissect on the link first (without --no-video)")
    a, b = secs(start), secs(end)
    times = []
    if mode == "scene" and (folder / "shots.csv").exists():
        starts = [secs(r.split(",")[1]) + 0.3 for r in (folder / "shots.csv").read_text(encoding="utf8").splitlines()[1:]]
        starts = [t for t in starts if a <= t <= b]
        times = starts if len(starts) <= cap else [starts[round(i * (len(starts) - 1) / (cap - 1))] for i in range(cap)]
    if not times:  # uniform, at most 2 frames per second
        n = max(1, min(cap, int((b - a) * 2)))
        times = [a + (b - a) * (i + 0.5) / n for i in range(n)]
    out = folder / f"frames-{ts(a).replace(':', '')}-{ts(b).replace(':', '')}"
    out.mkdir(exist_ok=True)
    for t in times:
        name = f"t{ts(t).replace(':', '')}.{int((t % 1) * 10)}.jpg"
        subprocess.run([ffmpeg_exe(), "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(vid), "-frames:v", "1",
                        "-vf", "scale=640:-2", str(out / name)], check=True)
    tr = folder / "transcript.txt"  # what is said over these frames
    if tr.exists():
        keep = []
        for l in tr.read_text(encoding="utf8").splitlines():
            m = re.match(r"\[(\d+):(\d+):(\d+)\]", l)
            if m and a - 2 <= int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) <= b:
                keep.append(l)
        (out / "transcript.txt").write_text("\n".join(keep), encoding="utf8")
    print(f"{len(times)} frames ({mode}) saved to {out}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "frames":
        ap = argparse.ArgumentParser()
        ap.add_argument("cmd"); ap.add_argument("folder"); ap.add_argument("start"); ap.add_argument("end")
        ap.add_argument("--max", type=int, default=30)
        ap.add_argument("--mode", choices=["uniform", "scene"], default="scene")
        a = ap.parse_args()
        return frames(Path(a.folder), a.start, a.end, a.max, a.mode)
    if len(sys.argv) > 1 and sys.argv[1] == "describe":
        ap = argparse.ArgumentParser()
        ap.add_argument("cmd"); ap.add_argument("folder"); ap.add_argument("start"); ap.add_argument("end")
        ap.add_argument("question", nargs="?", default="")
        a = ap.parse_args()
        return describe(Path(a.folder), a.start, a.end, a.question)
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--no-video", action="store_true", help="stats, comments and captions only")
    ap.add_argument("--max-comments", type=int, default=200)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if "reddit.com" in a.url:
        return reddit(a.url, out)
    folder, meta = fetch(a.url, out, a)
    print("saved", folder)
    mp3 = None if a.no_video else make_mp3(folder)
    lines = transcript(folder, meta, mp3)
    shots = [] if a.no_video else cuts(folder)
    gaps = pauses(folder, mp3)
    summary(folder, meta, lines, shots, gaps)
    print("done:", folder / "summary.md")


if __name__ == "__main__":
    main()

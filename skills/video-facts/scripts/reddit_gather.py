"""Search Reddit through the user's own Chrome (OpenCLI Browser Bridge) and write a short digest.

Why Chrome: Reddit blocks headless browsers, `.json` URLs (403) and old.reddit without login.
The user's real Chrome with the OpenCLI extension gets through. Only the digest is meant to be
read by Claude, so a run costs a few thousand tokens instead of raw pages.

Usage:
  python reddit_gather.py "angithi" "gas geyser fainted" --threads 8 --out digest.md
  python reddit_gather.py --read https://www.reddit.com/r/india/comments/abc123/ --out digest.md

Needs: OpenCLI in ~/.agent-reach/tools/npm-global, the OpenCLI extension connected in Chrome
(`opencli profile list` shows a connected profile). Read-only: no login, no posting, no voting.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

OPENCLI_DIR = os.path.expanduser(r"~/.agent-reach/tools/npm-global")
SESSION = "rg"
PAUSE = 5  # seconds per page; Reddit starts serving empty pages after about 30 fast reads

SEARCH_JS = r"""JSON.stringify([...new Set([...document.querySelectorAll('a[href*="/comments/"]')]
 .map(a=>a.href.split('?')[0]))].slice(0,12).map(h=>{const p=new URL(h).pathname;
 const a=[...document.querySelectorAll('a[href^="'+p+'"]')].find(x=>x.innerText.trim().length>10);
 return {title:a?a.innerText.trim().slice(0,140):'',url:h}}))"""

THREAD_JS = r"""(()=>{const p=document.querySelector('shreddit-post');if(!p)return JSON.stringify({empty:true});
 const b=p.querySelector('[slot=text-body]');
 const cs=[...document.querySelectorAll('shreddit-comment')].filter(c=>+c.getAttribute('depth')<=1).slice(0,%d)
  .map(c=>{const t=c.querySelector('[slot=comment]');return t?{d:+c.getAttribute('depth'),s:c.getAttribute('score'),
  t:t.innerText.replace(/\s+/g,' ').slice(0,450)}:null}).filter(x=>x&&x.t.length>=50);
 return JSON.stringify({title:p.getAttribute('post-title'),date:(p.getAttribute('created-timestamp')||'').slice(0,10),
  score:p.getAttribute('score'),comments:p.getAttribute('comment-count'),link:p.getAttribute('content-href'),
  body:(b?b.innerText:'').replace(/\s+/g,' ').slice(0,1800),top:cs})})()"""


def opencli(*args, timeout=60):
    env = dict(os.environ)
    env["PATH"] = OPENCLI_DIR + os.pathsep + env.get("PATH", "")
    exe = "opencli.cmd" if os.name == "nt" else "opencli"
    r = subprocess.run([exe, *args], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, timeout=timeout, shell=(os.name == "nt"))
    lines = [l for l in r.stdout.splitlines() if "Update available" not in l and "npm install" not in l]
    return "\n".join(lines).strip()


def open_page(url, wait_selector=None):
    opencli("browser", SESSION, "open", url, "--window", "background")
    if wait_selector:
        opencli("browser", SESSION, "wait", "selector", wait_selector, timeout=30)
    time.sleep(PAUSE)


def eval_json(js):
    out = opencli("browser", SESSION, "eval", js)
    m = re.search(r"(\{.*\}|\[.*\])", out, re.S)
    try:
        return json.loads(m.group(1)) if m else None
    except json.JSONDecodeError:
        return None


def check_connected():
    out = opencli("profile", "list", timeout=30)
    if "connected" not in out or "No Browser Bridge" in out:
        sys.exit("OpenCLI extension not connected. Open Chrome, click the OpenCLI extension, then run "
                 "`opencli doctor` (starts the helper). `opencli profile list` must show a connected profile.")


def search(q):
    open_page("https://www.reddit.com/search/?q=" + urllib.parse.quote(q) + "&type=posts")
    return eval_json(SEARCH_JS) or []


def read_thread(url, n_comments):
    open_page(url, wait_selector="shreddit-post")
    return eval_json(THREAD_JS % n_comments)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("queries", nargs="*", help="search terms; English, Hinglish, Hindi")
    ap.add_argument("--read", nargs="*", default=[], help="thread URLs to read directly")
    ap.add_argument("--threads", type=int, default=6, help="how many threads to open from search results")
    ap.add_argument("--comments", type=int, default=12)
    ap.add_argument("--subs", default="", help="comma list; keep only these subreddits (e.g. india,delhi)")
    ap.add_argument("--skip", default="", help="regex; drop titles that match (noise like restaurant names)")
    ap.add_argument("--out", default="reddit-digest.md")
    a = ap.parse_args()
    check_connected()

    subs = {s.strip().lower() for s in a.subs.split(",") if s.strip()}
    skip = re.compile(a.skip, re.I) if a.skip else None
    lines, picked = ["# Reddit digest", ""], []

    for q in a.queries:
        hits = search(q)
        keep = []
        for h in hits:
            m = re.search(r"/r/([^/]+)/comments/", h["url"])
            sub = m.group(1) if m else "?"
            if subs and sub.lower() not in subs:
                continue
            if skip and skip.search(h["title"]):
                continue
            keep.append((sub, h))
        lines.append(f"## search: {q} ({len(keep)} kept of {len(hits)})")
        lines += [f"- r/{s} | {h['title']} | {h['url']}" for s, h in keep] or ["- nothing"]
        lines.append("")
        picked += [h["url"] for _, h in keep]
        if not hits:
            lines.append("(empty result: Reddit may be rate-limiting; wait and rerun)\n")

    to_read = list(dict.fromkeys(a.read + picked[: a.threads]))
    empties = 0
    for url in to_read:
        t = read_thread(url, a.comments)
        lines.append(f"## thread: {url}")
        if not t or t.get("empty"):
            empties += 1
            lines.append("(page did not load)\n")
            if empties >= 3:
                lines.append("Stopped: 3 empty pages in a row, Reddit is rate-limiting. Rerun later.\n")
                break
            continue
        empties = 0
        lines.append(f"{t['title']} | {t['date']} | score {t['score']} | {t['comments']} comments")
        if t.get("link") and "reddit.com" not in (t["link"] or ""):
            lines.append(f"link: {t['link']}")
        if t.get("body"):
            lines.append(f"post: {t['body']}")
        for c in t.get("top", []):
            lines.append(("  " * c["d"]) + f"- [{c['s']}] {c['t']}")
        lines.append("")

    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {a.out}: {len(a.queries)} searches, {len(to_read)} threads")


if __name__ == "__main__":
    main()

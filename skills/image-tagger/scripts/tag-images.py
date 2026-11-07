"""Tag every image in a folder with Gemini, so scripts can pull the right image for an edit.

Usage (run the launcher next to this file; caches stay on D:):
    tag-images.ps1 <folder> [--limit 5] [--dry-run]

- Writes one line per image to <folder>/_index.jsonl. Already-tagged images (same content hash) are skipped,
  so you can drop new images in and rerun; renaming a file does not re-tag it.
- Images are shrunk to 768px on the long side before upload, which keeps each call cheap.
- On a quota error (429) it stops and tells you, instead of retrying and burning requests.
- --dry-run only counts what would be sent.
"""
import argparse, hashlib, io, json, re, sys, time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}

PROMPT = """You tag images for the editor of a Hindi/Hinglish satire explainer YouTube channel (health, skincare, money).
Return ONLY JSON with these keys:
"description": 2-3 plain sentences: what is in the image, who or what, the setting, the expression or mood,
"on_image_text": exact text written in the image, or "",
"kind": one of [reaction, meme_template, stock_photo, product, screenshot, news, chart, illustration, other],
"meme_template": the well-known meme or template name if it is one, else "",
"public_figure": name only if this is clearly a famous public figure or a famous meme face, else "",
"mood": list of 1-3 from [shock, disbelief, smug, sad, angry, confused, proud, awkward, cringe, happy, tired, deadpan, panic, judging],
"objects": list of key visible objects,
"tags": 8-15 lowercase search tags (English, plus Hinglish words an Indian viewer would use),
"edit_uses": list of 2-4 short ways an editor could use it, e.g. "reaction after a shocking price", "cutaway for 'no moisturizer'",
"india_specific": true or false,
"risky": "" or a short note if it shows nudity, gore, a private person, a watermark, or a logo that could cause a copyright or defamation issue.
Be literal. Do not guess names of people who are not famous."""


def load_env(start: Path) -> dict:
    import os
    if os.environ.get("GEMINI_API_KEY"):
        return {"GEMINI_API_KEY": os.environ["GEMINI_API_KEY"], "GEMINI_MODEL": os.environ.get("GEMINI_MODEL", "")}
    for d in [start, *start.parents, Path.cwd(), *Path.cwd().parents, Path(r"D:\Regent Scale")]:
        f = d / ".env"
        if f.exists():
            return dict(l.strip().split("=", 1) for l in f.open(encoding="utf8") if "=" in l and not l.startswith("#"))
    sys.exit("No GEMINI_API_KEY in the environment or in a .env file.")


def shrink(p: Path) -> bytes:
    from PIL import Image
    im = Image.open(p)
    im.seek(0)  # first frame of a gif
    im = im.convert("RGB")
    im.thumbnail((768, 768))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=85)
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    folder = Path(a.folder)
    index = folder / "_index.jsonl"
    done = set()
    if index.exists():
        done = {json.loads(l)["sha1"] for l in index.open(encoding="utf8") if l.strip()}

    todo = []
    for p in sorted(folder.rglob("*")):
        if p.suffix.lower() in EXTS and p.is_file():
            h = hashlib.sha1(p.read_bytes()).hexdigest()
            if h not in done:
                todo.append((p, h))
    if a.limit:
        todo = todo[: a.limit]
    print(f"{len(done)} already tagged, {len(todo)} to tag.")
    if a.dry_run or not todo:
        return

    from google import genai
    from google.genai import types
    env = load_env(Path(__file__).resolve().parent)
    client = genai.Client(api_key=env["GEMINI_API_KEY"])
    names = [m.name.split("/")[-1] for m in client.models.list()]
    flash = [n for n in names if re.fullmatch(r"gemini-\d+(\.\d+)?-flash", n)]
    model = max(flash, key=lambda n: float(re.findall(r"\d+(?:\.\d+)?", n)[0])) if flash else env.get("GEMINI_MODEL") or "gemini-flash-latest"
    print("model:", model)

    tok_in = tok_out = 0
    with index.open("a", encoding="utf8") as out:
        for i, (p, h) in enumerate(todo, 1):
            try:
                r = client.models.generate_content(
                    model=model,
                    contents=[types.Part.from_bytes(data=shrink(p), mime_type="image/jpeg"), PROMPT],
                    config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.3))
                data = json.loads(r.text)
            except Exception as e:
                msg = str(e)
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                    print(f"Quota hit after {i - 1} images. Rerun later; finished ones are saved.")
                    break
                print("failed", p.name, msg[:160])
                continue
            row = {"file": str(p.relative_to(folder)).replace("\\", "/"), "sha1": h, **data, "_model": model}
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            u = r.usage_metadata
            tok_in += u.prompt_token_count or 0
            tok_out += u.candidates_token_count or 0
            print(f"[{i}/{len(todo)}] {p.name}: {', '.join(data.get('tags', [])[:6])}")
            time.sleep(1)
    print(f"tokens in/out: {tok_in}/{tok_out}")


if __name__ == "__main__":
    main()

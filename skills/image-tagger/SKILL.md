---
name: image-tagger
description: >
  Tag every image in a folder with Gemini (description, on-image text, kind, meme template, mood, search
  tags, edit uses, legal risk) into one searchable index, then pull the right image for a script beat or an
  edit. Use when the user says "tag these images", "index my image folder", "find an image for this beat",
  "which reaction image fits", or drops images into the library. Only tags; it does not create images.
user-invokable: true
argument-hint: "<folder> [--limit N] [--dry-run]"
license: MIT
metadata:
  author: Regent Scale
  version: "1.0.0"
  category: production
---

# Image Tagger

## Commands
| Want | Command (PowerShell) |
|---|---|
| Count what would be tagged (free) | `scripts/tag-images.ps1 <folder> --dry-run` |
| Tag a small test batch | `scripts/tag-images.ps1 <folder> --limit 5` |
| Tag everything new | `scripts/tag-images.ps1 <folder>` |

Default library: `D:\Regent Scale\youtube\assets\images\` (subfolders allowed).

## The index
`<folder>\_index.jsonl`, one JSON line per image: `file`, `description`, `on_image_text`, `kind`, `meme_template`, `public_figure`, `mood`, `objects`, `tags`, `edit_uses`, `india_specific`, `risky`.

## Rules
1. **Costs Gemini calls.** Always run `--dry-run` first and tell the user the count; tag only after they agree. Images are shrunk to 768px first, already-tagged images (same content hash) are skipped, and a 429 (quota) stops the run with progress saved.
2. **Finding an image:** search the index (grep or read) for the beat's mood and tags, and cite the file path in the ON SCREEN column, e.g. `IMG: reactions/shocked-uncle.jpg`.
3. Any image with a non-empty `risky` field gets flagged `[LEGAL]` before it is used.
4. The Gemini key comes from `GEMINI_API_KEY`, else a `.env` near the script or the current folder, else `D:\Regent Scale\.env`. Never print it.

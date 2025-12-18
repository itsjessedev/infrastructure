#!/usr/bin/env python3
"""
Build Kometa collection YAML from local media using TMDB collections and curated fallbacks.

- Scans /media and /mnt/sdcard recursively for movie folders/files.
- Resolves TMDB IDs (search + year), then fetches belongs_to_collection to group franchises.
- Adds curated manual groups for franchises without TMDB collections (duologies, remakes, etc.).
- Emits a YAML file suitable for Kometa `collection_files`.

Usage:
  python scripts/build_collections.py \
    --tmdb-api-key $TMDB_API_KEY \
    --out generated/kometa/collections.yml
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import urllib.request
import urllib.parse


SCAN_ROOTS = [
    "/media/movies",
    "/media/movies-kids",
    "/mnt/sdcard/movies",
    "/mnt/sdcard/movies-kids",
]

# Simple cache to avoid hammering TMDB.
DEFAULT_CACHE = Path("generated/kometa/tmdb_cache.json")
DEFAULT_OUT = Path("generated/kometa/collections.yml")

YEAR_RE = re.compile(r"\s*\((\d{4})\)$")
ROMAN = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii", "xiii", "xiv", "xv"}
SEPARATORS = [":", " - ", " – ", " — "]
NUM_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
    "hundred": 100,
    "thousand": 1000,
}

# Manual collections for franchises that don't have clean TMDB collections.
CURATED_COLLECTIONS: Dict[str, List[str]] = {
    "Anchorman Collection": ["Anchorman"],
    "Joe Dirt Collection": ["Joe Dirt"],
    "Happy Gilmore Collection": ["Happy Gilmore"],
    "Grown Ups Collection": ["Grown Ups"],
    "George of the Jungle Collection": ["George of the Jungle"],
    "Hocus Pocus Collection": ["Hocus Pocus"],
    "Spider-Verse Collection": ["Spider-Man", "Spiderverse"],
    "101 Dalmatians Collection": ["101 Dalmatians", "One Hundred and One Dalmatians"],
}


@dataclass
class MediaItem:
    title: str
    year: Optional[int]
    path: Path


def words_to_number(words: List[str]) -> Optional[int]:
    total = 0
    current = 0
    found = False
    for w in words:
        if w not in NUM_WORDS:
            return None if not found else total + current
        found = True
        val = NUM_WORDS[w]
        if val == 100:
            current = max(1, current) * 100
        elif val == 1000:
            current = max(1, current) * 1000
            total += current
            current = 0
        else:
            current += val
    return total + current if found else None


def normalize_base(title: str) -> str:
    """Normalize a title for grouping (strip year, subtitles, and trailing numerals)."""
    t = YEAR_RE.sub("", title)
    for sep in SEPARATORS:
        if sep in t:
            t = t.split(sep)[0]
            break
    t = t.replace("&", "and")
    tokens = re.split(r"[\\s._-]+", t.lower())

    # Convert leading number words to digits.
    out: List[str] = []
    i = 0
    while i < len(tokens):
        if tokens[i] in NUM_WORDS:
            j = i
            seq: List[str] = []
            while j < len(tokens) and tokens[j] in NUM_WORDS:
                seq.append(tokens[j])
                j += 1
            num_val = words_to_number(seq)
            if num_val is not None:
                out.append(str(num_val))
                i = j
                continue
        out.append(tokens[i])
        i += 1

    while out and (out[-1].isdigit() or out[-1] in ROMAN):
        out.pop()
    return " ".join(out).strip()


def parse_title_year(name: str) -> Tuple[str, Optional[int]]:
    base = name
    year = None
    m = YEAR_RE.search(name)
    if m:
        year = int(m.group(1))
        base = YEAR_RE.sub("", name).strip()
    # Strip common quality/codec/resolution tokens tacked onto folder names.
    base = re.sub(r"\b(480p|720p|1080p|2160p|4k|x264|x265|h264|h265|bluray|webrip|web-dl|hdr|hevc|aac|dts|ac3)\b",
                  "", base, flags=re.IGNORECASE)
    base = re.sub(r"\s+", " ", base).strip()
    return base, year


def walk_media(paths: Iterable[str]) -> List[MediaItem]:
    exts = {".mkv", ".mp4", ".avi", ".mov", ".m4v"}
    found: List[MediaItem] = []
    for root in paths:
        p = Path(root)
        if not p.exists():
            continue
        for entry in p.rglob("*"):
            if entry.name.startswith("."):
                continue
            if entry.is_dir():
                title, year = parse_title_year(entry.name)
                found.append(MediaItem(title=title, year=year, path=entry))
            elif entry.is_file() and entry.suffix.lower() in exts:
                title, year = parse_title_year(entry.stem)
                found.append(MediaItem(title=title, year=year, path=entry))
    return found


def tmdb_get(url: str) -> dict:
    with urllib.request.urlopen(url) as resp:
        return json.load(resp)


def search_tmdb(api_key: str, title: str, year: Optional[int]) -> Optional[int]:
    query = urllib.parse.quote(title)
    year_param = f"&year={year}" if year else ""
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}{year_param}"
    data = tmdb_get(url)
    results = data.get("results") or []
    if not results:
        return None
    return results[0]["id"]


def tmdb_movie_details(api_key: str, movie_id: int) -> dict:
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    return tmdb_get(url)


def load_cache(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_cache(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def build_collections(api_key: str, items: List[MediaItem], cache_path: Path) -> Tuple[Dict[str, List[str]], dict]:
    cache = load_cache(cache_path)
    # cache schema: { "title|year|path": { "tmdb_id": int, "collection_id": int|null, "collection_name": str|null } }
    def cache_key(item: MediaItem) -> str:
        return f"{item.title}|{item.year or ''}|{item.path}"

    collections: Dict[str, List[str]] = defaultdict(list)

    for item in items:
        key = cache_key(item)
        entry = cache.get(key)
        tmdb_id = None
        collection = None

        if entry:
            tmdb_id = entry.get("tmdb_id")
            collection = entry.get("collection")
        if not tmdb_id:
            tmdb_id = search_tmdb(api_key, item.title, item.year)
        canonical_title = item.title
        if tmdb_id:
            details = tmdb_movie_details(api_key, tmdb_id)
            if details.get("title"):
                canonical_title = details["title"]
            belongs = details.get("belongs_to_collection")
            if belongs:
                collection = {"id": belongs.get("id"), "name": belongs.get("name")}
            cache[key] = {"tmdb_id": tmdb_id, "collection": collection}
        else:
            cache[key] = {"tmdb_id": None, "collection": None}

        if collection and collection.get("name"):
            collections[collection["name"]].append(canonical_title)

    # Add curated manual collections
    inventory_titles = {item.title for item in items}
    for coll_name, patterns in CURATED_COLLECTIONS.items():
        hits = []
        for title in inventory_titles:
            for pat in patterns:
                if pat.lower() in title.lower():
                    hits.append(title)
                    break
        if len(hits) >= 2:
            collections[coll_name].extend(sorted(set(hits)))

    save_cache(cache_path, cache)
    return collections, cache


def write_yaml(out_path: Path, holiday_block: str, collections: Dict[str, List[str]], min_items: int = 2) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append("collections:")
    # Holiday block already includes indentation relative to collections root
    for l in holiday_block.strip().splitlines():
        lines.append(f"  {l}")
    for name in sorted(collections.keys(), key=lambda x: x.lower()):
        titles = sorted(set(collections[name]))
        if len(titles) < min_items:
            continue
        lines.append(f"  {name}:")
        lines.append("    visible_library: true")
        lines.append("    collection_order: release")
        lines.append(f"    sort_title: \"{name}\"")
        lines.append("    plex_search:")
        lines.append("      any:")
        lines.append("        title:")
        for title in titles:
            lines.append(f"          - \"{title}\"")
        lines.append("")
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


HOLIDAY_BLOCK = """
  Sleighlist Spotlight:
    schedule: range(11/01-01/07)
    visible_home: true
    visible_shared: true
    visible_library: true
    delete_not_scheduled: true
    sync_mode: sync
    collection_order: release
    sort_title: "!00 Sleighlist Spotlight"
    summary: "Christmas picks auto-surface Nov 1 - Jan 7; pin in Plex Home to keep it first. Kids profiles only see kid-safe titles."
    plex_search:
      any:
        title:
          - "A Christmas Story"
          - "8-Bit Christmas"
          - "National Lampoon's Christmas Vacation"
          - "Christmas with the Kranks"
          - "The Nightmare Before Christmas"
          - "Jingle All the Way"
          - "Elf"
          - "Home Alone"
          - "Home Alone 2"
          - "Klaus"
          - "The Santa Clause"
          - "The Santa Clause 2"
          - "The Santa Clause 3"
          - "Four Christmases"
          - "The Holiday"
          - "Love Actually"
          - "Die Hard"
          - "The Night Before"
          - "Office Christmas Party"
          - "The Christmas Chronicles"
          - "The Christmas Chronicles 2"
          - "Deck the Halls"
          - "Fred Claus"
          - "A Charlie Brown Christmas"
          - "A Garfield Christmas Special"
          - "Christmas Comes But Once a Year"
          - "The Christmas Visitor"
          - "Pluto's Christmas Tree"
          - "Grandma Got Run Over by a Reindeer"
          - "Rudolph the Red-Nosed Reindeer"
          - "Frosty the Snowman"
          - "How the Grinch Stole Christmas"
          - "The Polar Express"
          - "Mickey's Once Upon a Christmas"
          - "Mickey's Twice Upon a Christmas"
          - "Arthur Christmas"
          - "Noelle"
          - "The Muppet Christmas Carol"
          - "Santa Claus Is Comin' to Town"
          - "The Grinch"
          - "Abominable"
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Kometa collection YAML from TMDB data.")
    parser.add_argument("--tmdb-api-key", dest="tmdb_api_key", default=os.getenv("TMDB_API_KEY"), required=True)
    parser.add_argument("--paths", nargs="*", default=SCAN_ROOTS, help="Paths to scan for media")
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--min-items", type=int, default=2, help="Minimum titles required to emit a collection")
    args = parser.parse_args()

    items = walk_media(args.paths)
    collections, cache = build_collections(args.tmdb_api_key, items, args.cache)
    write_yaml(args.out, HOLIDAY_BLOCK, collections, min_items=args.min_items)
    kept = sum(1 for v in collections.values() if len(set(v)) >= args.min_items)
    print(f"Found {kept} collections (after min_items filter); wrote {args.out}")
    print(f"Cache entries: {len(cache)} -> {args.cache}")


if __name__ == "__main__":
    sys.exit(main())

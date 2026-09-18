#!/usr/bin/env python3
"""Deduplicate wiki articles that share the same source URL."""
from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qs, urlparse, urlunparse

SKIP_NAMES = {"_index.md", "INDEX.md", "STATUS.md"}
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")


def normalize_source(url: str) -> str:
    url = url.strip().strip('"').strip("'")
    if not url:
        return ""
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower().removeprefix("www.")
    path = parsed.path.rstrip("/")
    if "youtube.com" in host or host == "youtu.be":
        if host == "youtu.be":
            vid = path.lstrip("/")
        else:
            vid = parse_qs(parsed.query).get("v", [""])[0]
        return f"youtube:{vid}" if vid else url
    return urlunparse((parsed.scheme.lower(), host, path, "", "", ""))


def parse_article(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = "", text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm, body = parts[1], parts[2]
    source = ""
    match = re.search(r"^source:\s*[\"']?(.*?)[\"']?\s*$", fm, re.M | re.I)
    if match:
        source = match.group(1).strip()
    title = ""
    match = re.search(r"^title:\s*[\"']?(.*?)[\"']?\s*$", fm, re.M)
    if match:
        title = match.group(1).strip()
    slug = path.stem
    garbage = bool(re.search(r"(?:^|-)e[0-9a-f]{2}(?:-e[0-9a-f]{2})+", slug))
    garbage = garbage or bool(re.search(r"guaxuan|nengli|zhen-deng", slug))
    ugly_long = len(slug) > 80 or bool(re.search(r"-[0-9a-f]{8}$", slug))
    return {
        "path": path,
        "text": text,
        "source": source,
        "norm": normalize_source(source),
        "title": title,
        "slug": slug,
        "topic": path.parent.name,
        "bytes": len(text),
        "links": body.count("[["),
        "bullets": len(re.findall(r"^\s*[-*]", body, re.M)),
        "garbage": garbage,
        "ugly_long": ugly_long,
        "mtime": path.stat().st_mtime,
    }


def content_score(article: dict) -> float:
    return article["links"] * 10 + article["bullets"] * 3 + min(article["bytes"], 8000) / 80


def slug_score(article: dict) -> float:
    score = 0.0
    if article["garbage"]:
        score -= 200
    if article["ugly_long"]:
        score -= 80
    score -= abs(len(article["slug"]) - 40) * 0.5
    score -= max(0, len(article["slug"]) - 55) * 2
    return score


def pick_keeper(group: list[dict]) -> tuple[dict, Path]:
    # Prefer denser content, but never promote garbage-slug bodies over clean ones.
    best_content = max(
        group,
        key=lambda a: (
            0 if a["garbage"] else 1,
            0 if a["ugly_long"] else 1,
            content_score(a),
            a["mtime"],
        ),
    )
    best_slug_art = max(group, key=lambda a: (slug_score(a), content_score(a)))
    return best_content, best_slug_art["path"]


def collect_articles(wiki_dir: Path) -> list[dict]:
    articles = []
    for path in wiki_dir.rglob("*.md"):
        if "hubs" in path.parts or path.name in SKIP_NAMES:
            continue
        articles.append(parse_article(path))
    return articles


def rewrite_links(wiki_dir: Path, redirects: dict[str, str]) -> int:
    changed_files = 0

    def rewrite_target(target: str) -> str | None:
        key = target.strip()
        return redirects.get(key)

    for path in wiki_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        changed = False

        def repl(match: re.Match[str]) -> str:
            nonlocal changed
            target, label = match.group(1), match.group(2)
            new_target = rewrite_target(target)
            if not new_target:
                return match.group(0)
            changed = True
            if label is not None:
                return f"[[{new_target}|{label}]]"
            return f"[[{new_target}]]"

        new_text = LINK_RE.sub(repl, text)
        if changed and new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed_files += 1
    return changed_files


def dedupe(wiki_dir: Path, *, dry_run: bool = False) -> None:
    articles = collect_articles(wiki_dir)
    by_norm: dict[str, list[dict]] = defaultdict(list)
    for article in articles:
        if article["norm"]:
            by_norm[article["norm"]].append(article)

    redirects: dict[str, str] = {}
    to_delete: list[Path] = []
    writes: list[tuple[Path, str]] = []

    groups = [(norm, group) for norm, group in by_norm.items() if len(group) >= 2]
    print(f"Duplicate groups: {len(groups)}")

    for _norm, group in sorted(groups, key=lambda item: -len(item[1])):
        content_art, keep_path = pick_keeper(group)
        keep_key = f"{keep_path.parent.name}/{keep_path.stem}"
        if content_art["path"] != keep_path:
            writes.append((keep_path, content_art["text"]))
        print(
            f"KEEP {keep_path.relative_to(wiki_dir)}"
            + (
                f"  (content from {content_art['path'].relative_to(wiki_dir)})"
                if content_art["path"] != keep_path
                else ""
            )
        )
        for article in group:
            if article["path"] == keep_path:
                continue
            key = f"{article['topic']}/{article['slug']}"
            redirects[key] = keep_key
            redirects[article["slug"]] = keep_key
            to_delete.append(article["path"])
            print(f" DEL {article['path'].relative_to(wiki_dir)}")
        print()

    print(f"Files to delete: {len(to_delete)}")
    print(f"Content moves: {len(writes)}")
    if dry_run:
        print("Dry run — no changes written.")
        return

    for path, text in writes:
        path.write_text(text, encoding="utf-8")
        print(f"WROTE content -> {path}")

    for path in to_delete:
        path.unlink()
        print(f"DELETED {path}")

    changed = rewrite_links(wiki_dir, redirects)
    print(f"Rewrote links in {changed} files")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wiki", default="newswiki/wiki")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    dedupe(Path(args.wiki), dry_run=args.dry_run)


if __name__ == "__main__":
    main()

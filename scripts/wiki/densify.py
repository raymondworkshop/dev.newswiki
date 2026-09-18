"""Deterministic wiki-link densification for richer Quartz backlinks/graph."""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from wiki.common import WIKI_LINK_RE, repo_root, resolve_path

INDEX_NAMES = {"_index.md", "INDEX.md"}
RELATED_HEADINGS = ("相关文章", "Related Articles", "Related")
FOOTER_SPLIT_RE = re.compile(r"\n---\n\*\*(?:Topics?|主题|主題)\*\*:", re.M)
TAG_RE = re.compile(r"#([a-zA-Z0-9][\w-]*)")
TITLE_RE = re.compile(r'^title:\s*"?(.*?)"?\s*$', re.M)
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.-]{2,}|[\u4e00-\u9fff]{2,}")

# High-signal entities that currently appear as unresolved [[links]] or plain text.
ENTITY_ALIASES: dict[str, tuple[str, ...]] = {
    "spacex": ("SpaceX", "spacex", "星舰", "Starship", "Starlink", "星链"),
    "nvidia": ("NVIDIA", "Nvidia", "NVDA", "英伟达"),
    "nebius": ("Nebius",),
    "coreweave": ("CoreWeave", "Coreweave"),
    "microsoft": ("Microsoft", "微软", "MSFT"),
    "ai-infrastructure": ("数据中心", "data center", "datacenter", "AI算力"),
}

# Key concepts (topic「关键技术」+ common investment/tech terms) → hubs/.
# Longer aliases first in each tuple; avoid ultra-generic 1–2 char tokens.
CONCEPT_ALIASES: dict[str, tuple[str, ...]] = {
    "ipo": ("首次公开募股", "IPO"),
    "valuation": ("估值", "valuation"),
    "interest-rates": ("interest rates", "interest rate", "利率"),
    "regulation": ("regulatory", "regulation", "监管"),
    "ai-investing": ("AI 投研", "AI投研"),
    "cash-flow": ("cash flow", "现金流", "FCF"),
    "leverage": ("leverage", "杠杆"),
    "risk-return": ("风险回报", "risk-return", "risk return"),
    "llm": ("大语言模型", "LLM"),
    "gpu": ("GPU",),
    "ai-agent": ("AI Agent", "AI智能体", "智能体"),
    "humanoid-robot": ("人形机器人", "humanoid robot", "humanoid"),
    "business-model": ("business model", "商业模式"),
    "geopolitics": ("geopolitics", "地缘政治"),
    "automation": ("automation", "自动化"),
    "career-path": ("职业路径", "career path"),
    "background-check": ("background check", "背调"),
    "demographics": ("人口结构", "demographics"),
    "consumer-habits": ("消费习惯",),
    "product-form": ("产品形态",),
    "ux": ("用户体验", "UX"),
    "open-source": ("开源与自建", "开源"),
}


def all_hub_aliases() -> dict[str, tuple[str, ...]]:
    """Company/entity hubs + concept hubs for mention linking and hub pages."""
    merged = dict(ENTITY_ALIASES)
    merged.update(CONCEPT_ALIASES)
    return merged


# Generic tokens that inflate Jaccard scores without semantic signal.
STOP_TOKENS = {
    "the", "and", "for", "with", "from", "that", "this", "are", "was", "were",
    "have", "has", "will", "into", "about", "after", "before", "over", "under",
    "https", "http", "www", "com", "articles", "mod", "cn", "wsj", "source",
    "title", "description", "published", "created", "author", "topics", "tags",
    "business", "finance", "career", "lifestyle", "design", "tech", "index",
    "key", "takeaways", "core", "view", "要点", "核心观点", "相关文章", "related",
}


@dataclass
class Article:
    path: Path
    rel: str
    slug_path: str
    title: str
    topics: list[str]
    tags: set[str] = field(default_factory=set)
    tokens: set[str] = field(default_factory=set)
    entities: set[str] = field(default_factory=set)
    text: str = ""
    body_text: str = ""


def _is_article(path: Path) -> bool:
    return (
        path.suffix == ".md"
        and path.name not in INDEX_NAMES
        and "hubs" not in path.parts
        and path.name != "articles.md"
    )


def _parse_front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    block = text[3:end]
    data: dict[str, str] = {}
    title_m = TITLE_RE.search(block)
    if title_m:
        data["title"] = title_m.group(1).strip().strip('"')
    topics: list[str] = []
    in_topics = False
    for line in block.splitlines():
        if line.startswith("topics:"):
            in_topics = True
            continue
        if in_topics:
            if line.startswith("  - "):
                topics.append(line[4:].strip())
            elif line and not line.startswith(" "):
                in_topics = False
    if topics:
        data["topics"] = ",".join(topics)
    return data


def _body_without_related(text: str) -> str:
    text = _strip_existing_related(text)
    match = FOOTER_SPLIT_RE.search(text)
    if match:
        return text[: match.start()]
    return text


def load_articles(wiki_dir: Path) -> list[Article]:
    articles: list[Article] = []
    for path in sorted(wiki_dir.rglob("*.md")):
        if not _is_article(path):
            continue
        text = path.read_text(encoding="utf-8")
        fm = _parse_front_matter(text)
        rel = path.relative_to(wiki_dir).as_posix()
        slug_path = rel[:-3]
        title = fm.get("title") or path.stem
        topics = [t for t in fm.get("topics", "").split(",") if t]
        if not topics and "/" in slug_path:
            topics = [slug_path.split("/", 1)[0]]
        body = _body_without_related(text)
        tags = set(TAG_RE.findall(text)) - {"hub", "business", "finance", "career", "lifestyle", "design", "tech"}
        tokens = {
            t.lower()
            for t in TOKEN_RE.findall(f"{title}\n{body}")
            if t.lower() not in STOP_TOKENS and len(t) > 1
        }
        entities = {
            slug
            for slug, aliases in all_hub_aliases().items()
            if any(alias in body or alias.lower() in tokens for alias in aliases)
        }
        articles.append(
            Article(
                path=path,
                rel=rel,
                slug_path=slug_path,
                title=title,
                topics=topics,
                tags=tags,
                tokens=tokens,
                entities=entities,
                text=text,
                body_text=body,
            )
        )
    return articles


def similarity(a: Article, b: Article) -> float:
    if a.slug_path == b.slug_path:
        return 0.0
    score = 0.0
    shared_entities = a.entities & b.entities
    tag_overlap = len(a.tags & b.tags)
    token_overlap = len(a.tokens & b.tokens)

    if shared_entities:
        score += 3.0 * len(shared_entities)
    if tag_overlap:
        score += 2.0 * tag_overlap
    if a.topics and b.topics and a.topics[0] == b.topics[0]:
        score += 0.5
    # Only count token overlap when there is already a thematic signal.
    if shared_entities or tag_overlap:
        score += min(token_overlap, 8) * 0.2
    return score


def pick_related(article: Article, pool: list[Article], *, limit: int = 4) -> list[Article]:
    ranked = sorted(
        ((similarity(article, other), other) for other in pool),
        key=lambda item: (-item[0], item[1].title),
    )
    picked: list[Article] = []
    for score, other in ranked:
        # Require entity or tag overlap — topic alone is not enough.
        if score < 2.0:
            break
        picked.append(other)
        if len(picked) >= limit:
            break
    return picked


def _related_section_markdown(related: list[Article], *, chinese: bool) -> str:
    heading = "## 相关文章" if chinese else "## Related Articles"
    lines = [heading, ""]
    for item in related:
        lines.append(f"- [[{item.slug_path}|{item.title}]]")
    lines.append("")
    return "\n".join(lines)


def _looks_chinese(text: str) -> bool:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff") >= 20


def _strip_existing_related(text: str) -> str:
    """Remove a prior related section without touching the Topics footer."""
    for heading in RELATED_HEADINGS:
        pattern = re.compile(
            rf"\n## {re.escape(heading)}\n.*?(?=\n---\n\*\*(?:Topics?|主题|主題)\*\*:|\n## |\Z)",
            re.S,
        )
        text = pattern.sub("\n", text, count=1)
    return text


def upsert_related_section(text: str, related: list[Article]) -> str:
    """Replace/insert related links. Preserve Topics footer; keep old related if none found."""
    if not related:
        return text
    text = _strip_existing_related(text)
    section = _related_section_markdown(related, chinese=_looks_chinese(text))
    match = FOOTER_SPLIT_RE.search(text)
    if match:
        return text[: match.start()].rstrip() + "\n\n" + section.strip() + "\n" + text[match.start() :]
    # Footer missing — append related, then a minimal separator for safety.
    return text.rstrip() + "\n\n" + section.strip() + "\n"


def render_hub_page(
    entity_slug: str,
    display: str,
    members: list[Article],
    *,
    kind: str = "entity",
) -> str:
    primary = members[0].topics[0] if members and members[0].topics else "business"
    blurb = (
        f"Curated hub for the concept 「{display}」."
        if kind == "concept"
        else f"Curated hub for articles related to {display}."
    )
    lines = [
        "---",
        f'title: "{display}"',
        f'description: "Hub page aggregating wiki articles related to {display}."',
        "topics:",
        f"  - {primary}",
        "---",
        "",
        f"# {display}",
        "",
        blurb,
        "",
        "## 相关文章",
        "",
    ]
    for article in sorted(members, key=lambda a: a.title):
        topic = article.topics[0] if article.topics else "wiki"
        lines.append(f"- [[{article.slug_path}|{article.title}]] · #{topic}")
    lines.append("")
    lines.append("---")
    lines.append(f"**Topics**: [[{primary}/_index|{primary.title()}]]  ")
    tag = "concept" if kind == "concept" else "hub"
    lines.append(f"**Tags**: #{entity_slug} #{tag}")
    lines.append("")
    return "\n".join(lines)


def rewrite_entity_links(text: str, entity_slug: str, aliases: tuple[str, ...]) -> str:
    """Point bare [[Alias]] links at hubs/entity_slug so Quartz can resolve them."""
    hub = f"hubs/{entity_slug}"

    def repl(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        display = match.group(2)
        bare = target.split("/")[-1]
        if target.startswith("hubs/"):
            return match.group(0)
        if bare.lower() == entity_slug or target in aliases or bare in aliases:
            label = display or bare
            return f"[[{hub}|{label}]]"
        return match.group(0)

    pattern = re.compile(r"\[\[([^\]|#]+)(?:\|([^\]]+))?\]\]")
    return pattern.sub(repl, text)


# Protect existing markup so plain-mention linking does not nest inside links/code.
_PROTECT_RE = re.compile(
    r"```[\s\S]*?```"
    r"|`[^`\n]+`"
    r"|\[\[[^\]]*\]\]"
    r"|\[[^\]]*\]\([^)]+\)"
)


def _alias_is_ascii(alias: str) -> bool:
    return all(ord(ch) < 128 for ch in alias)


def _mention_pattern(alias: str) -> re.Pattern[str]:
    escaped = re.escape(alias)
    if _alias_is_ascii(alias) and " " not in alias:
        # Word-ish boundary: avoid matching inside longer identifiers.
        return re.compile(rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_])")
    return re.compile(escaped)


def build_mention_alias_map(
    entity_aliases: dict[str, tuple[str, ...]] | None = None,
) -> list[tuple[str, str]]:
    """Return (alias, hub_slug) pairs sorted longest-first for greedy matching."""
    source = entity_aliases if entity_aliases is not None else all_hub_aliases()
    pairs: list[tuple[str, str]] = []
    for slug, aliases in source.items():
        for alias in aliases:
            if alias.strip():
                pairs.append((alias, slug))
    pairs.sort(key=lambda item: (-len(item[0]), item[0]))
    return pairs


def link_plain_mentions(
    text: str,
    *,
    alias_map: list[tuple[str, str]] | None = None,
    max_links: int = 12,
) -> tuple[str, int]:
    """Turn plain entity/concept mentions into [[hubs/slug|mention]] (Wikipedia-style).

    Caps: at most one new link per hub slug, and at most ``max_links`` total per doc.
    Existing wikilinks, markdown links, and code spans are left untouched.
    Front matter is not linked.
    """
    if max_links <= 0:
        return text, 0

    pairs = alias_map if alias_map is not None else build_mention_alias_map()
    if not pairs:
        return text, 0

    body_start = 0
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end >= 0:
            body_start = end + len("\n---")

    prefix, body = text[:body_start], text[body_start:]
    added = 0
    used_slugs: set[str] = set()

    def _protect(src: str) -> tuple[str, list[str]]:
        placeholders: list[str] = []

        def _stash(match: re.Match[str]) -> str:
            placeholders.append(match.group(0))
            return f"\0DENSIFY{len(placeholders) - 1}\0"

        return _PROTECT_RE.sub(_stash, src), placeholders

    def _restore(src: str, placeholders: list[str]) -> str:
        return re.sub(
            r"\0DENSIFY(\d+)\0",
            lambda m: placeholders[int(m.group(1))],
            src,
        )

    working, placeholders = _protect(body)

    for alias, slug in pairs:
        if added >= max_links:
            break
        if slug in used_slugs:
            continue
        pattern = _mention_pattern(alias)
        match = pattern.search(working)
        if not match:
            continue
        linked = f"[[hubs/{slug}|{match.group(0)}]]"
        working = working[: match.start()] + linked + working[match.end() :]
        used_slugs.add(slug)
        added += 1
        # Re-protect so later aliases cannot match inside the new wikilink path.
        working, placeholders = _protect(_restore(working, placeholders))

    return prefix + _restore(working, placeholders), added


_TOPIC_METRICS_LINE_RE = re.compile(
    r"^([ \t]*-[ \t]*\*\*(?:关键技术|关键技术/变量|关键技术／变量|關鍵技術|關鍵技術/變量|关键技術/變量|投資视角|投资视角)\*\*:[ \t]*)([^\n]*)$",
    re.MULTILINE,
)


def link_metrics_line_values(line_values: str, *, alias_map: list[tuple[str, str]] | None = None) -> str:
    """Link plain concept phrases inside a topic-index metrics value list."""
    wrapped = f"---\ntitle: x\n---\n{line_values}"
    out, _ = link_plain_mentions(
        wrapped,
        alias_map=alias_map if alias_map is not None else build_mention_alias_map(CONCEPT_ALIASES),
        max_links=20,
    )
    if out.startswith("---"):
        end = out.find("\n---", 3)
        if end >= 0:
            return out[end + len("\n---") :].lstrip("\n")
    return line_values


def link_topic_index_concepts(wiki_dir: Path, *, dry_run: bool = False) -> int:
    """Rewrite topic _index 关键技术 (and 投资视角) values to concept hub links."""
    alias_map = build_mention_alias_map(CONCEPT_ALIASES)
    updated = 0
    for path in sorted(wiki_dir.glob("*/_index.md")):
        text = path.read_text(encoding="utf-8")

        def _repl(match: re.Match[str]) -> str:
            prefix, values = match.group(1), match.group(2)
            linked = link_metrics_line_values(values, alias_map=alias_map)
            return prefix + linked

        new_text = _TOPIC_METRICS_LINE_RE.sub(_repl, text)
        if new_text != text:
            updated += 1
            if not dry_run:
                path.write_text(new_text, encoding="utf-8")
    return updated


def build_related_map(
    articles: list[Article],
    *,
    limit: int = 4,
) -> dict[str, list[Article]]:
    """Score related neighbors, then make edges bidirectional within ``limit``."""
    by_slug = {a.slug_path: a for a in articles}
    related_map: dict[str, list[Article]] = {
        article.slug_path: pick_related(article, articles, limit=limit) for article in articles
    }

    for a_slug, related in list(related_map.items()):
        a = by_slug[a_slug]
        for b in related:
            b_list = related_map.setdefault(b.slug_path, [])
            if not any(item.slug_path == a_slug for item in b_list):
                b_list.append(a)

    for slug, related in related_map.items():
        if len(related) <= limit:
            continue
        article = by_slug[slug]
        related_map[slug] = sorted(
            related,
            key=lambda other: (-similarity(article, other), other.title),
        )[:limit]

    return related_map


def densify_wiki(
    wiki_dir: Path,
    *,
    related_limit: int = 4,
    write_hubs: bool = True,
    link_mentions: bool = True,
    mention_budget: int = 12,
    dry_run: bool = False,
) -> dict[str, int]:
    hub_aliases = all_hub_aliases()
    articles = load_articles(wiki_dir)
    updated_articles = 0
    related_links_added = 0
    mention_links_added = 0

    # Snapshot hub membership from original body text before mutations.
    hub_members: dict[str, list[Article]] = {
        slug: [a for a in articles if slug in a.entities]
        for slug in hub_aliases
    }

    related_map = build_related_map(articles, limit=related_limit)
    alias_map = build_mention_alias_map(hub_aliases) if link_mentions else []

    for article in articles:
        related = related_map.get(article.slug_path, [])
        new_text = upsert_related_section(article.text, related)
        mentions = 0
        if link_mentions:
            new_text, mentions = link_plain_mentions(
                new_text,
                alias_map=alias_map,
                max_links=mention_budget,
            )
            mention_links_added += mentions
        if write_hubs:
            for hub_slug, aliases in hub_aliases.items():
                if hub_slug in article.entities:
                    new_text = rewrite_entity_links(new_text, hub_slug, aliases)
        if new_text != article.text:
            related_links_added += len(related)
            updated_articles += 1
            article.text = new_text
            if not dry_run:
                article.path.write_text(new_text, encoding="utf-8")

    hubs_written = 0
    if write_hubs:
        hubs_dir = wiki_dir / "hubs"
        if not dry_run:
            hubs_dir.mkdir(parents=True, exist_ok=True)
        for hub_slug, aliases in hub_aliases.items():
            members = hub_members.get(hub_slug, [])
            if len(members) < 2:
                continue
            display = aliases[0]
            kind = "concept" if hub_slug in CONCEPT_ALIASES else "entity"
            content = render_hub_page(hub_slug, display, members, kind=kind)
            hubs_written += 1
            if not dry_run:
                (hubs_dir / f"{hub_slug}.md").write_text(content, encoding="utf-8")

    topic_indexes_updated = 0
    if link_mentions:
        topic_indexes_updated = link_topic_index_concepts(wiki_dir, dry_run=dry_run)

    return {
        "articles_scanned": len(articles),
        "articles_updated": updated_articles,
        "related_links_added": related_links_added,
        "mention_links_added": mention_links_added,
        "hubs_written": hubs_written,
        "topic_indexes_updated": topic_indexes_updated,
    }


def graph_stats(wiki_dir: Path) -> dict[str, float | int]:
    articles = load_articles(wiki_dir)
    targets: dict[str, Path] = {}
    for path in wiki_dir.rglob("*.md"):
        if path.name in INDEX_NAMES:
            continue
        rel = path.relative_to(wiki_dir).as_posix()[:-3]
        targets[rel] = path
        targets[path.stem] = path

    outbound: list[int] = []
    backlinks: dict[str, set[str]] = defaultdict(set)
    unresolved = Counter()

    article_slugs = {a.slug_path for a in articles}
    for article in articles:
        links = WIKI_LINK_RE.findall(article.text)
        resolvable = 0
        for target in links:
            key = target.strip()
            if key in targets:
                resolvable += 1
                dest = targets[key].relative_to(wiki_dir).as_posix()[:-3]
                if dest in article_slugs or dest.startswith("hubs/"):
                    backlinks[dest].add(article.slug_path)
            else:
                unresolved[key] += 1
        outbound.append(resolvable)

    with_backlinks = sum(1 for s in article_slugs if backlinks.get(s))
    return {
        "articles": len(articles),
        "mean_outbound": round(sum(outbound) / max(len(outbound), 1), 2),
        "median_outbound": sorted(outbound)[len(outbound) // 2] if outbound else 0,
        "articles_with_backlink": with_backlinks,
        "backlink_coverage_pct": round(100 * with_backlinks / max(len(articles), 1), 1),
        "hub_pages": len(list((wiki_dir / "hubs").glob("*.md"))) if (wiki_dir / "hubs").exists() else 0,
        "top_unresolved": unresolved.most_common(5),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Densify wiki article cross-links and entity hubs.")
    parser.add_argument("--wiki", default="newswiki/wiki")
    parser.add_argument("--related-limit", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-hubs", action="store_true")
    parser.add_argument(
        "--no-mentions",
        action="store_true",
        help="Skip Wikipedia-style plain-text entity → hub linking",
    )
    parser.add_argument("--stats-only", action="store_true")
    args = parser.parse_args(argv)

    root = repo_root()
    wiki_dir = resolve_path(root, args.wiki)

    before = graph_stats(wiki_dir)
    print("[densify] before:", before)
    if args.stats_only:
        return 0

    result = densify_wiki(
        wiki_dir,
        related_limit=args.related_limit,
        write_hubs=not args.no_hubs,
        link_mentions=not args.no_mentions,
        dry_run=args.dry_run,
    )
    print("[densify] result:", result)
    after = graph_stats(wiki_dir) if not args.dry_run else before
    if not args.dry_run:
        print("[densify] after:", after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

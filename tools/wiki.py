#!/usr/bin/env python3
"""Helper CLI for LLM wikis. Standard library only (Python 3.8+).

Commands:
  search <query>   Rank wiki pages by relevance to the query terms.
  lint             Mechanical health checks (exit code 1 if errors).
  stats            Page counts, hub pages, recent log entries.
  pending          Raw files not yet ingested (not referenced by any source page).
  xlinks           Verify cross-wiki references [[wiki-id:slug]].
  log              Show the last N log entries.

Use --root to operate on another wiki (default: the repo containing this script).
"""

import argparse
import datetime as dt
import math
import os
import re
import sys
from collections import Counter, defaultdict

DEFAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECIAL_PAGES = {"index", "log"}
NO_ORPHAN_CHECK = {"index", "log", "overview"}
REQUIRED_FIELDS = ("title", "type", "created", "updated")
VALID_TYPES = {"source", "entity", "concept", "topic", "analysis", "overview", "meta"}
NEEDS_SOURCES = {"entity", "concept", "topic", "analysis"}

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOG_ENTRY_RE = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\] (setup|ingest|query|lint|link|refactor|schema) \| .+")


# --------------------------------------------------------------------------- parsing

def parse_scalar(value):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [parse_scalar(v) for v in inner.split(",")] if inner else []
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def strip_comment(line):
    # Remove trailing "# comment" outside quotes (good enough for our config files).
    in_quote = None
    for i, ch in enumerate(line):
        if ch in "\"'":
            in_quote = None if in_quote == ch else (in_quote or ch)
        elif ch == "#" and not in_quote and (i == 0 or line[i - 1].isspace()):
            return line[:i].rstrip()
    return line.rstrip()


def load_yaml(text):
    """Minimal YAML subset: nested maps, lists of scalars/maps, folded scalars."""
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text) or {}
    except ImportError:
        pass
    lines = [strip_comment(l) for l in text.splitlines()]
    lines = [l for l in lines if l.strip()]
    pos = 0

    def indent(l):
        return len(l) - len(l.lstrip(" "))

    def parse_block(level):
        nonlocal pos
        if pos < len(lines) and lines[pos].lstrip().startswith("- "):
            result = []
            while pos < len(lines) and indent(lines[pos]) == level and lines[pos].lstrip().startswith("- "):
                item = lines[pos].lstrip()[2:]
                if re.match(r"^[\w-]+:( |$)", item):
                    # map inside a list item: rewrite the line as a map at deeper indent
                    lines[pos] = " " * (level + 2) + item
                    result.append(parse_block(level + 2))
                else:
                    result.append(parse_scalar(item))
                    pos += 1
            return result
        result = {}
        while pos < len(lines) and indent(lines[pos]) == level:
            key, _, rest = lines[pos].strip().partition(":")
            rest = rest.strip()
            pos += 1
            if rest in (">", "|", ">-", "|-"):
                parts = []
                while pos < len(lines) and indent(lines[pos]) > level:
                    parts.append(lines[pos].strip())
                    pos += 1
                result[key] = " ".join(parts)
            elif rest:
                result[key] = parse_scalar(rest)
            elif pos < len(lines) and indent(lines[pos]) > level:
                result[key] = parse_block(indent(lines[pos]))
            elif pos < len(lines) and indent(lines[pos]) == level and lines[pos].lstrip().startswith("- "):
                result[key] = parse_block(level)
            else:
                result[key] = None
        return result

    return parse_block(0) if lines else {}


def split_frontmatter(text):
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    raw = text[3:end].strip("\n")
    body = text[end + 4:].lstrip("\n")
    try:
        fm = load_yaml(raw)
    except Exception:
        fm = {"__invalid__": True}
    return (fm if isinstance(fm, dict) else {"__invalid__": True}), body


def clean_for_links(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    return text


class Page:
    def __init__(self, root, path):
        self.path = path
        self.rel = os.path.relpath(path, root)
        self.slug = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as f:
            self.text = f.read()
        self.fm, self.body = split_frontmatter(self.text)
        links = WIKILINK_RE.findall(clean_for_links(self.body))
        self.links = [l.strip() for l in links if ":" not in l]
        self.xlinks = [l.strip() for l in links if ":" in l]

    @property
    def title(self):
        if self.fm and self.fm.get("title"):
            return str(self.fm["title"])
        m = re.search(r"^# (.+)$", self.body, re.M)
        return m.group(1).strip() if m else self.slug

    @property
    def type(self):
        return (self.fm or {}).get("type")


class Wiki:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.wiki_dir = os.path.join(self.root, "wiki")
        self.raw_dir = os.path.join(self.root, "raw")
        if not os.path.isdir(self.wiki_dir):
            sys.exit("error: no wiki/ directory under %s" % self.root)
        cfg_path = os.path.join(self.root, "wiki.config.yaml")
        self.config = {}
        if os.path.exists(cfg_path):
            with open(cfg_path, encoding="utf-8") as f:
                self.config = load_yaml(f.read()) or {}
        self.pages = []
        for dirpath, dirnames, filenames in os.walk(self.wiki_dir):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for fn in sorted(filenames):
                if fn.endswith(".md"):
                    self.pages.append(Page(self.root, os.path.join(dirpath, fn)))
        self.by_slug = defaultdict(list)
        for p in self.pages:
            self.by_slug[p.slug].append(p)

    def page(self, slug):
        found = self.by_slug.get(slug)
        return found[0] if found else None

    def inbound(self):
        inbound = defaultdict(set)
        for p in self.pages:
            for target in p.links:
                inbound[target].add(p.slug)
        return inbound

    def linked_wikis(self):
        return {w.get("id"): w for w in (self.config.get("linked_wikis") or []) if isinstance(w, dict)}


# --------------------------------------------------------------------------- commands

def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def cmd_search(wiki, args):
    terms = [t for t in tokenize(args.query) if len(t) > 1]
    if not terms:
        sys.exit("error: empty query")
    docs = {}
    for p in wiki.pages:
        if p.slug in SPECIAL_PAGES:
            continue
        aliases = " ".join(str(a) for a in ((p.fm or {}).get("aliases") or []))
        docs[p.slug] = (p, Counter(tokenize(p.body)), set(tokenize(p.title + " " + p.slug + " " + aliases)))
    n = len(docs) or 1
    df = Counter()
    for _, counts, head in docs.values():
        for t in set(terms):
            if counts[t] or t in head:
                df[t] += 1
    results = []
    for slug, (p, counts, head) in docs.items():
        score, matched = 0.0, 0
        for t in terms:
            if counts[t] or t in head:
                matched += 1
                idf = math.log(1 + n / (1 + df[t]))
                score += idf * (math.log(1 + counts[t]) + (3.0 if t in head else 0.0))
        if matched:
            score *= matched / len(terms)
            results.append((score, p))
    results.sort(key=lambda r: -r[0])
    for score, p in results[: args.limit]:
        snippet = ""
        for line in p.body.splitlines():
            if any(t in line.lower() for t in terms) and not line.startswith("#"):
                snippet = line.strip()[:160]
                break
        print("%6.2f  [[%s]]  %s  (%s)" % (score, p.slug, p.title, p.rel))
        if snippet:
            print("        %s" % snippet)
    if not results:
        print("no matches")


def cmd_lint(wiki, args):
    errors, warnings, infos = [], [], []
    inbound = wiki.inbound()
    index = wiki.page("index")
    index_links = set(index.links) if index else set()
    if not index:
        errors.append("wiki/index.md is missing")

    for slug, pages in wiki.by_slug.items():
        if len(pages) > 1:
            errors.append("duplicate slug '%s': %s" % (slug, ", ".join(p.rel for p in pages)))

    missing = defaultdict(set)
    for p in wiki.pages:
        if not SLUG_RE.match(p.slug):
            warnings.append("%s: file name is not kebab-case" % p.rel)
        for target in p.links:
            if not wiki.page(target):
                missing[target].add(p.slug)
        if p.slug in SPECIAL_PAGES:
            continue
        if p.fm is None:
            errors.append("%s: missing frontmatter" % p.rel)
            continue
        if p.fm.get("__invalid__"):
            errors.append("%s: unparseable frontmatter" % p.rel)
            continue
        for field in REQUIRED_FIELDS:
            if not p.fm.get(field):
                errors.append("%s: frontmatter missing '%s'" % (p.rel, field))
        if p.type and p.type not in VALID_TYPES:
            errors.append("%s: unknown type '%s'" % (p.rel, p.type))
        if p.type in NEEDS_SOURCES:
            cites = [l for l in p.links if l.startswith("src-")]
            if not p.fm.get("sources") and not cites:
                warnings.append("%s: no source citations" % p.rel)
        if p.slug not in index_links:
            warnings.append("%s: not listed in index.md" % p.rel)
        if p.slug not in NO_ORPHAN_CHECK and p.type != "meta" and not (inbound.get(p.slug, set()) - {"index", "log"}):
            warnings.append("%s: orphan (no inbound links besides index/log)" % p.rel)

    for target, sources in sorted(missing.items()):
        msg = "missing page [[%s]] linked from %s" % (target, ", ".join(sorted(sources)))
        (errors if "index" in sources else warnings).append(msg)

    known = wiki.linked_wikis()
    for p in wiki.pages:
        for x in p.xlinks:
            wid = x.split(":", 1)[0]
            if wid not in known:
                errors.append("%s: cross-wiki link [[%s]] uses unregistered wiki id '%s'" % (p.rel, x, wid))

    log = os.path.join(wiki.wiki_dir, "log.md")
    if os.path.exists(log):
        with open(log, encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if line.startswith("## ") and not LOG_ENTRY_RE.match(line):
                    warnings.append("wiki/log.md:%d: malformed entry header" % i)

    if not args.quick:
        days = int(((wiki.config.get("lint") or {}).get("stale_after_days")) or 180)
        today = dt.date.today()
        for p in wiki.pages:
            updated = (p.fm or {}).get("updated")
            try:
                d = dt.date.fromisoformat(str(updated))
            except ValueError:
                continue
            if (today - d).days > days and p.type not in ("meta",):
                infos.append("%s: not updated for %d days" % (p.rel, (today - d).days))
            if (p.fm or {}).get("status") == "disputed":
                infos.append("%s: status disputed" % p.rel)
        for f in pending_raw(wiki):
            infos.append("raw file not ingested: %s" % f)

    for label, items in (("ERROR", errors), ("WARN", warnings), ("INFO", infos)):
        for item in items:
            print("%-5s %s" % (label, item))
    print("\n%d errors, %d warnings, %d info (%d pages)" % (len(errors), len(warnings), len(infos), len(wiki.pages)))
    return 1 if errors else 0


def pending_raw(wiki):
    if not os.path.isdir(wiki.raw_dir):
        return []
    corpus = "\n".join(p.text for p in wiki.pages if p.type == "source" or p.rel.startswith(os.path.join("wiki", "sources")))
    pending = []
    for dirpath, dirnames, filenames in os.walk(wiki.raw_dir):
        rel_dir = os.path.relpath(dirpath, wiki.raw_dir)
        if rel_dir.split(os.sep)[0] == "assets":
            continue
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fn in sorted(filenames):
            if fn.startswith("."):
                continue
            if fn not in corpus:
                pending.append(os.path.relpath(os.path.join(dirpath, fn), wiki.root))
    return pending


def cmd_pending(wiki, args):
    files = pending_raw(wiki)
    for f in files:
        print(f)
    if not files:
        print("nothing pending")


def cmd_stats(wiki, args):
    types = Counter(p.type or "(none)" for p in wiki.pages)
    print("Wiki: %s (%s)" % (wiki.config.get("name", "?"), wiki.config.get("id", "?")))
    print("Pages: %d" % len(wiki.pages))
    for t, c in sorted(types.items()):
        print("  %-10s %d" % (t, c))
    links = sum(len(p.links) for p in wiki.pages)
    print("Wikilinks: %d  Cross-wiki links: %d" % (links, sum(len(p.xlinks) for p in wiki.pages)))
    inbound = wiki.inbound()
    hubs = sorted(((len(v - {"index", "log"}), k) for k, v in inbound.items() if wiki.page(k) and k not in SPECIAL_PAGES), reverse=True)
    print("Top hubs (inbound links):")
    for c, slug in hubs[: args.top]:
        print("  %3d  [[%s]]" % (c, slug))
    print("Pending raw files: %d" % len(pending_raw(wiki)))
    print("Linked wikis: %s" % (", ".join(k for k in wiki.linked_wikis() if k) or "none"))


def cmd_xlinks(wiki, args):
    known = wiki.linked_wikis()
    status = 0
    cache = {}
    found_any = False
    for p in wiki.pages:
        for x in p.xlinks:
            found_any = True
            wid, slug = x.split(":", 1)
            w = known.get(wid)
            if not w:
                print("ERROR %s: [[%s]] unknown wiki id" % (p.rel, x))
                status = 1
                continue
            path = os.path.normpath(os.path.join(wiki.root, str(w.get("path") or "")))
            if not w.get("path") or not os.path.isdir(os.path.join(path, "wiki")):
                print("SKIP  %s: [[%s]] wiki '%s' not available locally (%s)" % (p.rel, x, wid, path))
                continue
            if wid not in cache:
                cache[wid] = Wiki(path)
            target = cache[wid].page(slug.strip())
            if target:
                print("OK    %s: [[%s]] -> %s" % (p.rel, x, os.path.join(w.get("path"), target.rel)))
            else:
                print("ERROR %s: [[%s]] page not found in %s" % (p.rel, x, path))
                status = 1
    if not found_any:
        print("no cross-wiki links")
    for wid, w in known.items():
        path = os.path.normpath(os.path.join(wiki.root, str(w.get("path") or "")))
        state = "available" if os.path.isdir(os.path.join(path, "wiki")) else "NOT FOUND"
        print("wiki %-20s %s (%s)" % (wid, state, path))
    return status


def cmd_log(wiki, args):
    path = os.path.join(wiki.wiki_dir, "log.md")
    with open(path, encoding="utf-8") as f:
        entries = [l.rstrip() for l in f if l.startswith("## [")]
    for e in entries[-args.n:]:
        print(e)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=DEFAULT_ROOT, help="wiki repo root (default: this repo)")
    sub = parser.add_subparsers(dest="cmd")
    s = sub.add_parser("search", help="search wiki pages")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=10)
    l = sub.add_parser("lint", help="mechanical health checks")
    l.add_argument("--quick", action="store_true", help="skip stale/pending checks")
    st = sub.add_parser("stats", help="wiki statistics")
    st.add_argument("--top", type=int, default=10)
    sub.add_parser("pending", help="raw files not yet ingested")
    sub.add_parser("xlinks", help="verify cross-wiki links")
    lg = sub.add_parser("log", help="last log entries")
    lg.add_argument("-n", type=int, default=10)
    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 0
    wiki = Wiki(args.root)
    handler = {"search": cmd_search, "lint": cmd_lint, "stats": cmd_stats,
               "pending": cmd_pending, "xlinks": cmd_xlinks, "log": cmd_log}[args.cmd]
    return handler(wiki, args) or 0


if __name__ == "__main__":
    sys.exit(main())

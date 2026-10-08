#!/usr/bin/env python3
"""Apply the AnxietyFreePups article template (task 17) to one page.

Adds, without touching the rest of the page:
  1. <link> to /css/article-kit.css (also fixes the phone menu covering the hamburger)
  2. "Quick answer" box right under the hero (text from the spec, written in Saad's ChatGPT chat)
  3. Table of contents from the page's H2s (only when the page has 4+ H2s); H2s get ids
  4. "Our top pick" product box with an Amazon button + disclosure line, placed before the 2nd H2
  5. In-body "Related reading" block (2-4 links) before the 4th H2 (or the last H2)
  6. Author / last-updated box at the end of the article body, and JSON-LD dateModified

Every block is optional and idempotent (re-running skips blocks already present).

Usage:
  python3 scripts/apply_article_template.py PAGE.html SPEC.json [--dry-run]
  python3 scripts/apply_article_template.py PAGE.html --kit-only   # CSS link + TOC + author box only

SPEC.json example:
{
  "quick_answer": {"text": "One or two sentences that answer the search question.",
                   "bullets": ["optional point", "optional point"]},
  "product": {"name": "KONG Classic Dog Toy",
              "url": "https://www.amazon.com/dp/B0002AR0I8?tag=anxietyfreepu-20",
              "why": "One line on why it fits this problem.",
              "img": "optional /images/... path", "label": "Our top pick"},
  "related": [{"href": "/guides/separation-anxiety", "text": "Separation anxiety: the full guide"}],
  "updated": "2026-10-08"
}
"""
import datetime, html, json, re, sys

TAG = "anxietyfreepu-20"
MARK = "afp-kit"


def slugify(t):
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t).lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:60] or "section"


def div_end(s, start, tag="div"):
    """Index just after the </tag> that closes the <tag ...> starting at `start` (div, main or section)."""
    depth = 0
    for m in re.finditer(rf"<{tag}\b|</{tag}>", s[start:]):
        depth += 1 if m.group(0) == f"<{tag}" else -1
        if depth == 0:
            return start + m.end()
    raise ValueError(f"unbalanced {tag}")


def content_bounds(s):
    m = re.search(r'<(div|main) class="content"[^>]*>', s)
    if not m:
        raise ValueError('no <div class="content"> or <main class="content">')
    tag = m.group(1)
    end = div_end(s, m.start(), tag)
    return m.end(), end - len(f"</{tag}>")


def check_amazon(url):
    if "amazon.com" not in url or f"tag={TAG}" not in url or "chewy" in url.lower():
        raise ValueError(f"product url must be amazon.com with tag={TAG}: {url}")


def apply(s, spec, kit_only=False):
    done = []
    # 1. stylesheet
    if "/css/article-kit.css" not in s:
        s = s.replace("</head>", '<link rel="stylesheet" href="/css/article-kit.css">\n</head>', 1)
        done.append("css")
    # 2. quick answer
    qa = spec.get("quick_answer")
    if qa and not kit_only and 'class="quick-answer"' not in s:
        m = re.search(r'<(div|section) class="hero-article"', s)
        pos = div_end(s, m.start(), m.group(1)) if m else content_bounds(s)[0]
        body = f'<p>{qa["text"]}</p>'
        if qa.get("bullets"):
            body += "<ul>" + "".join(f"<li>{b}</li>" for b in qa["bullets"]) + "</ul>"
        block = (f'\n<!-- {MARK}:quick-answer -->\n<div class="quick-answer" role="note">'
                 f'<div class="qa-label">Quick answer</div>{body}</div>\n')
        s = s[:pos] + block + s[pos:]
        done.append("quick-answer")
    # 3. H2 ids + TOC
    cs, ce = content_bounds(s)
    content = s[cs:ce]
    used = set()

    def add_id(m):
        attrs, inner = m.group(1), m.group(2)
        if "id=" in attrs:
            used.add(re.search(r'id="([^"]+)"', attrs).group(1))
            return m.group(0)
        sid = slugify(inner)
        base, n = sid, 2
        while sid in used:
            sid, n = f"{base}-{n}", n + 1
        used.add(sid)
        return f'<h2{attrs} id="{sid}">{inner}</h2>'

    content = re.sub(r"<h2([^>]*)>(.*?)</h2>", add_id, content, flags=re.S)
    h2s = re.findall(r'<h2[^>]*id="([^"]+)"[^>]*>(.*?)</h2>', content, flags=re.S)
    if len(h2s) >= 4 and 'class="toc"' not in content:
        items = "".join(f'<li><a href="#{i}">{re.sub(r"<[^>]+>", "", t).strip()}</a></li>' for i, t in h2s)
        toc = (f'\n<!-- {MARK}:toc -->\n<details class="toc" open><summary>On this page</summary>'
               f"<ol>{items}</ol></details>\n")
        content = toc + content
        done.append(f"toc({len(h2s)})")
    # 4. product box before 2nd H2
    p = spec.get("product")
    if p and not kit_only and 'class="product-box"' not in content:
        check_amazon(p["url"])
        img = (f'<div class="pb-img"><img src="{p["img"]}" alt="{html.escape(p["name"])}" '
               f'width="110" height="110" loading="lazy"></div>') if p.get("img") else ""
        box = (f'\n<!-- {MARK}:product-box -->\n<div class="product-box">{img}<div class="pb-body">'
               f'<div class="pb-label">{p.get("label", "Our top pick")}</div><h4>{p["name"]}</h4>'
               f'<p>{p["why"]}</p><a class="amz-btn" href="{p["url"]}" target="_blank" '
               f'rel="noopener noreferrer nofollow sponsored">Check price on Amazon</a>'
               f'<p class="disclosure-line">We earn a small commission if you buy through this link, at no extra cost to you. '
               f'<a href="/resources/affiliate-disclosure">Disclosure</a></p></div></div>\n')
        heads = [m.start() for m in re.finditer(r"<h2[\s>]", content)]
        at = heads[1] if len(heads) >= 2 else (heads[0] if heads else 0)
        content = content[:at] + box + content[at:]
        done.append("product-box")
    # 5. related block before 4th H2 (or last H2)
    rel = spec.get("related")
    if rel and not kit_only and 'class="related-block"' not in content:
        if not 2 <= len(rel) <= 4:
            raise ValueError("related needs 2-4 links")
        lis = "".join(f'<li><a href="{r["href"]}">{r["text"]}</a></li>' for r in rel)
        blk = (f'\n<!-- {MARK}:related -->\n<div class="related-block"><div class="rb-label">Related reading</div>'
               f"<ul>{lis}</ul></div>\n")
        heads = [m.start() for m in re.finditer(r"<h2[\s>]", content)]
        at = heads[3] if len(heads) >= 4 else (heads[-1] if heads else len(content))
        content = content[:at] + blk + content[at:]
        done.append("related")
    # 6. author box at end of content
    updated = spec.get("updated") or datetime.date.today().isoformat()
    nice = datetime.date.fromisoformat(updated).strftime("%-d %B %Y")
    if 'class="author-box"' not in content:
        ab = (f'\n<!-- {MARK}:author -->\n<div class="author-box"><div class="ab-icon">AP</div><div>'
              f'<div class="ab-name">AnxietyFreePups editorial team</div>'
              f'<div class="ab-meta">Last updated <time datetime="{updated}">{nice}</time></div>'
              f'<p>General information for dog owners, not veterinary advice. If your dog panics, hurts itself '
              f'or stops eating when alone, talk to your vet. We earn from qualifying Amazon purchases; '
              f'<a href="/resources/affiliate-disclosure">how that works</a>.</p></div></div>\n')
        content = content + ab
        done.append("author-box")
    s = s[:cs] + content + s[ce:]
    if "author-box" in done:
        s = re.sub(r'"dateModified":"[0-9-]+"', f'"dateModified":"{updated}"', s)
    return s, done


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    kit_only, dry = "--kit-only" in sys.argv, "--dry-run" in sys.argv
    if not a:
        sys.exit(__doc__)
    page = a[0]
    spec = json.load(open(a[1])) if len(a) > 1 else {}
    src = open(page, encoding="utf-8").read()
    out, done = apply(src, spec, kit_only)
    print(page, "->", ", ".join(done) or "nothing to do")
    if not dry and out != src:
        open(page, "w", encoding="utf-8").write(out)


if __name__ == "__main__":
    main()

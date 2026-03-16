#!/usr/bin/env python3
"""
link_article.py — Wires a blog article into the site (no LLM needed).

Does exactly 3 file edits:
  1. breeds/[breed-slug].html  — injects scaffold if needed, inserts article card
  2. index.html                — prepends card to .articles-grid, rotates out last if >= 6
  3. sitemap.xml               — adds new URL entry

Usage:
    python3 scripts/link_article.py \
        --breed-slug "beagle" \
        --article-slug "puppy-crate-training" \
        --title "Beagle Puppy Crate Training: Stop the Howling in 7 Nights" \
        --desc "7-night protocol to stop Beagle puppy crate howling for good" \
        --emoji "🐾" \
        --date "2026-03-17"
"""

import argparse
import os
import re
import sys
from datetime import date as date_cls

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(REPO_ROOT, ".claude", "agent-memory", "linker", "MEMORY.md")


# ── Slug → Display Name ───────────────────────────────────────────────────────

def slug_to_name(slug):
    """Convert breed-slug to Breed Name (e.g. golden-retriever → Golden Retriever)."""
    return " ".join(word.capitalize() for word in slug.split("-"))


# ── Memory helpers ────────────────────────────────────────────────────────────

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def is_scaffolded(breed_slug):
    memory = load_memory()
    return f"- {breed_slug} (" in memory


def save_scaffolded(breed_slug, today):
    memory = load_memory()
    entry = f"- {breed_slug} ({today})\n"
    if "## Scaffolded Breeds" in memory:
        memory = memory.replace("## Scaffolded Breeds\n", f"## Scaffolded Breeds\n{entry}")
    else:
        memory += f"\n## Scaffolded Breeds\n{entry}"
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.write(memory)


def save_rotated_card(today, href, title):
    memory = load_memory()
    entry = f"- {today}: {href} — \"{title}\"\n"
    if "## Rotated Homepage Cards" in memory:
        memory = memory.replace("## Rotated Homepage Cards\n", f"## Rotated Homepage Cards\n{entry}")
    else:
        memory += f"\n## Rotated Homepage Cards\n{entry}"
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.write(memory)


# ── HTML templates ────────────────────────────────────────────────────────────

def breed_page_scaffold(breed_name):
    return f"""<section class="blog-articles-section" style="background:var(--cream);border-top:1px solid var(--sand-light);padding:3rem 5vw">
  <div style="max-width:760px;margin:0 auto">
    <h2 style="font-family:'Playfair Display',Georgia,serif;font-size:1.8rem;font-weight:700;color:var(--bark);margin-bottom:1.5rem">{breed_name} Deep-Dive Articles</h2>
    <div id="blog-list" style="display:flex;flex-direction:column;gap:1rem">
    <!-- BLOG_LIST_START -->
    <!-- BLOG_LIST_END -->
    </div>
  </div>
</section>
"""


def breed_page_card(breed_slug, article_slug, emoji, title, desc):
    return f"""    <a href="/blogs/{breed_slug}-{article_slug}" style="display:flex;gap:1rem;background:var(--warm-white);border:1px solid var(--sand-light);border-radius:12px;padding:1.2rem;text-decoration:none;transition:all .2s" onmouseover="this.style.borderColor='var(--moss)'" onmouseout="this.style.borderColor='var(--sand-light)'">
      <span style="font-size:2rem;flex-shrink:0">{emoji}</span>
      <div>
        <div style="font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--moss);font-weight:600;margin-bottom:.3rem">DEEP-DIVE</div>
        <div style="font-weight:600;color:var(--bark);font-size:.95rem;margin-bottom:.3rem">{title}</div>
        <div style="font-size:.82rem;color:var(--text-muted)">{desc}</div>
      </div>
    </a>"""


def homepage_card(breed_slug, article_slug, emoji, title, desc):
    return f"""    <a href="blogs/{breed_slug}-{article_slug}" class="article-card reveal">
      <div class="article-thumb" style="background:linear-gradient(135deg,var(--sand),var(--bark-light));display:flex;align-items:center;justify-content:center;position:relative"><span style="font-size:3.5rem;line-height:1;z-index:1">{emoji}</span><span class="card-cat">BREED GUIDE</span></div>
      <div class="article-body"><h3>{title}</h3><p>{desc}</p></div>
    </a>"""


# ── Task 1: Update breed page ─────────────────────────────────────────────────

def update_breed_page(breed_slug, article_slug, emoji, title, desc, today):
    path = os.path.join(REPO_ROOT, "breeds", f"{breed_slug}.html")
    if not os.path.exists(path):
        print(f"WARNING: Breed page not found: {path}", file=sys.stderr)
        print(f"  Skipping breed page update.", file=sys.stderr)
        return False, False

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    breed_name = slug_to_name(breed_slug)
    scaffold_injected = False

    # Inject scaffold if not present
    if "<!-- BLOG_LIST_START -->" not in content:
        scaffold = breed_page_scaffold(breed_name)
        # Insert before <section class="related-section"
        if '<section class="related-section"' in content:
            content = content.replace(
                '<section class="related-section"',
                scaffold + '<section class="related-section"',
                1
            )
        elif '<div class="related-section"' in content:
            content = content.replace(
                '<div class="related-section"',
                scaffold + '<div class="related-section"',
                1
            )
        else:
            # Fallback: insert before </body>
            content = content.replace("</body>", scaffold + "</body>", 1)
        scaffold_injected = True
        save_scaffolded(breed_slug, today)
        print(f"  Scaffold injected into {path}", file=sys.stderr)

    # Insert article card after <!-- BLOG_LIST_START -->
    card = breed_page_card(breed_slug, article_slug, emoji, title, desc)
    content = content.replace(
        "    <!-- BLOG_LIST_START -->",
        f"    <!-- BLOG_LIST_START -->\n{card}",
        1
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  breeds/{breed_slug}.html updated", file=sys.stderr)
    return True, scaffold_injected


# ── Task 2: Update homepage ───────────────────────────────────────────────────

def update_homepage(breed_slug, article_slug, emoji, title, desc, today):
    path = os.path.join(REPO_ROOT, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Count existing article cards
    cards = re.findall(r'<a\s[^>]*class="article-card[^"]*"', content)
    card_count = len(cards)

    rotated_href = None
    rotated_title = None

    # Rotate out last card if >= 6
    if card_count >= 6:
        # Find the last article-card anchor and remove it
        # Pattern: find last <a ... class="article-card...">...</a>
        last_card_pattern = r'(\s*<a\s[^>]*class="article-card[^"]*"[^>]*>.*?</a>)(?=\s*\n\s*</div>)'
        matches = list(re.finditer(r'\s*<a\s[^>]*class="article-card[^"]*"[^>]*>.*?</a>', content, re.DOTALL))
        if matches:
            last = matches[-1]
            last_html = last.group(0)
            # Extract href for logging
            href_match = re.search(r'href="([^"]+)"', last_html)
            title_match = re.search(r'<h3>(.*?)</h3>', last_html, re.DOTALL)
            rotated_href = href_match.group(1) if href_match else "unknown"
            rotated_title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else "unknown"
            content = content[:last.start()] + content[last.end():]
            save_rotated_card(today, rotated_href, rotated_title)
            print(f"  Rotated out: {rotated_href} — {rotated_title}", file=sys.stderr)

    # Prepend new card after <div class="articles-grid">
    new_card = homepage_card(breed_slug, article_slug, emoji, title, desc)
    grid_pattern = r'(<div class="articles-grid">)'
    if re.search(grid_pattern, content):
        content = re.sub(
            grid_pattern,
            f'\\1\n{new_card}',
            content,
            count=1
        )
    else:
        print("WARNING: .articles-grid not found in index.html", file=sys.stderr)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  index.html updated (cards before: {card_count})", file=sys.stderr)
    return rotated_href, rotated_title


# ── Task 3: Update sitemap ────────────────────────────────────────────────────

def update_sitemap(breed_slug, article_slug, date_str):
    path = os.path.join(REPO_ROOT, "sitemap.xml")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    url = f"https://www.anxietyfreepups.com/blogs/{breed_slug}-{article_slug}"
    new_entry = f'  <url><loc>{url}</loc><lastmod>{date_str}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>\n'

    # Insert after opening <urlset tag
    content = re.sub(
        r'(<urlset[^>]*>)',
        f'\\1\n{new_entry}',
        content,
        count=1
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  sitemap.xml updated — added {url}", file=sys.stderr)
    return url


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Wire a blog article into the AnxietyFreePups site")
    parser.add_argument("--breed-slug", required=True, help='e.g. "beagle"')
    parser.add_argument("--article-slug", required=True, help='e.g. "puppy-crate-training"')
    parser.add_argument("--title", required=True, help="Full article title")
    parser.add_argument("--desc", required=True, help="One-line description")
    parser.add_argument("--emoji", required=True, help="Single emoji")
    parser.add_argument("--date", default=str(date_cls.today()), help="YYYY-MM-DD (default: today)")
    args = parser.parse_args()

    os.chdir(REPO_ROOT)
    today = args.date

    print(f"\nLinking: {args.breed_slug}-{args.article_slug}", file=sys.stderr)
    print(f"  Title: {args.title}", file=sys.stderr)

    # Task 1
    breed_ok, scaffold_injected = update_breed_page(
        args.breed_slug, args.article_slug, args.emoji, args.title, args.desc, today
    )

    # Task 2
    rotated_href, rotated_title = update_homepage(
        args.breed_slug, args.article_slug, args.emoji, args.title, args.desc, today
    )

    # Task 3
    new_url = update_sitemap(args.breed_slug, args.article_slug, today)

    # Summary
    print(f"\n✓ Linker complete: {args.breed_slug}-{args.article_slug}", file=sys.stderr)
    print(f"  breeds/{args.breed_slug}.html — scaffold={'injected' if scaffold_injected else 'existing'}, card added", file=sys.stderr)
    print(f"  index.html — new card prepended, rotated={'none' if not rotated_href else rotated_href}", file=sys.stderr)
    print(f"  sitemap.xml — {new_url}", file=sys.stderr)


if __name__ == "__main__":
    main()

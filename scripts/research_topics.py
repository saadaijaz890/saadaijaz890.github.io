#!/usr/bin/env python3
"""
research_topics.py — Uses OpenAI to research and rank article topics for a given dog breed.

Usage:
    python3 scripts/research_topics.py \
        --breed "Australian Shepherd" \
        --breed-slug "australian-shepherd"

    python3 scripts/research_topics.py \
        --breed "Chihuahua" \
        --breed-slug "chihuahua" \
        --no-memory-update

Requires: pip install openai>=1.30.0
API key:  export OPENAI_API_KEY=sk-...
"""

import argparse
import glob
import os
import re
import sys
import warnings

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_PATH = os.path.join(REPO_ROOT, ".claude", "agent-memory", "researcher", "MEMORY.md")
MEMORY_MAX_LINES = 195  # trim if over this


# ── Inventory ─────────────────────────────────────────────────────────────────

def inventory_existing_coverage(breed_slug: str) -> tuple[list[str], str]:
    """Return (existing_slugs, breed_page_summary)."""
    # Existing blog slugs for this breed
    pattern = os.path.join(REPO_ROOT, "blogs", f"{breed_slug}-*.html")
    existing_files = glob.glob(pattern)
    existing_slugs = []
    for f in existing_files:
        base = os.path.basename(f).replace(".html", "")
        existing_slugs.append(base)

    # Breed page summary
    breed_page_path = os.path.join(REPO_ROOT, "breeds", f"{breed_slug}.html")
    breed_page_summary = ""
    if os.path.exists(breed_page_path):
        with open(breed_page_path, "r", encoding="utf-8") as fh:
            html = fh.read()
        headings = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', html, re.DOTALL)
        headings = [re.sub(r'<[^>]+>', '', h).strip() for h in headings if h.strip()]
        breed_page_summary = "Headings on breed page: " + ", ".join(headings[:12]) if headings else ""
    else:
        breed_page_summary = f"No breed page found at breeds/{breed_slug}.html"

    return existing_slugs, breed_page_summary


def load_memory() -> str:
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "r", encoding="utf-8") as fh:
            return fh.read()
    return ""


# ── Prompt ────────────────────────────────────────────────────────────────────

def build_research_prompt(breed: str, breed_slug: str, breed_page_summary: str,
                           existing_slugs: list[str], memory_content: str) -> str:
    existing_str = "\n".join(f"  - {s}" for s in existing_slugs) if existing_slugs else "  (none)"
    guides_str = """\
  - guides/calming-chews.html
  - guides/thundershirt-review.html
  - guides/nighttime-anxiety.html
  - guides/leash-reactivity.html
  - guides/separation-anxiety.html
  - guides/vet-visit-anxiety.html
  - guides/car-travel-anxiety.html
  - guides/grooming-anxiety.html
  - guides/rescue-dog-anxiety.html
  - guides/noise-phobia.html
  - guides/enrichment-for-anxiety.html"""

    memory_section = f"\n## Prior Research Memory\n{memory_content}" if memory_content.strip() else ""

    return f"""\
You are a content researcher for AnxietyFreePups.com, a dog anxiety affiliate content site.
Your task is to identify the 5 best NEW article topics for the **{breed}** breed.

## Context

**Breed slug**: {breed_slug}
**Breed page coverage** (topics already addressed):
{breed_page_summary}

**Existing blog articles for this breed** (do NOT suggest any of these):
{existing_str}

**Cross-breed guides already on site** (do NOT suggest duplicates of these):
{guides_str}
{memory_section}

## Search Instructions

Please search the web for the following (3 targeted searches):
1. `"{breed} anxiety" site:reddit.com` — recurring questions in Reddit posts/comments
2. `"{breed} anxiety" "how to"` — PAA-style how-to queries
3. `"{breed} separation anxiety" OR "{breed} crate training" OR "{breed} thunderstorm"` — high-affiliate topics

Analyze results to identify the most frequently asked, unanswered breed-specific questions.

## Scoring Dimensions (1–5 each, max 15)

| Dimension | Description |
|---|---|
| PAA Volume | How often does this question appear across Reddit / search results? |
| Affiliate Potential | Does it naturally lead to product recommendations (calming chews, ThunderShirt, crate covers, etc.)? |
| Novelty | Is this NOT already covered in the breed page or cross-breed guides above? |

## Slug Rules
- Lowercase, hyphens only, no articles ("a", "the")
- Max 5 words after the breed prefix
- Full slug format: `{breed_slug}-[article-slug]`
- Must be unique — not in the existing blog articles list above

## Few-Shot Example Row (format reference only — do not copy this content)
| 1 | Golden Retriever Puppy Crate Anxiety: 7-Night Protocol | golden-retriever-puppy-crate-anxiety | 5 | 5 | 5 | 15 | Dozens of dedicated forum threads; breed page has zero crate content; strong affiliate (crate, KONG, calming chews) |

## Required Output Format

Return EXACTLY this markdown table with 5 rows, sorted by Score descending, followed by the footer lines.
Do not include any other text before or after.

## {breed} — Top 5 Article Topics

| # | Title | Slug | PAA | Affiliate | Novelty | Score | Why Now |
|---|---|---|---|---|---|---|---|
| 1 | [Compelling article title] | [{breed_slug}-article-slug] | 5 | 5 | 4 | 14 | [1-sentence rationale] |
| 2 | ... | ... | ... | ... | ... | ... | ... |
| 3 | ... | ... | ... | ... | ... | ... | ... |
| 4 | ... | ... | ... | ... | ... | ... | ... |
| 5 | ... | ... | ... | ... | ... | ... | ... |

**Top Pick**: Row 1 — [brief reason why this is the strongest choice]
**Coverage Gaps Found**: [list topics already in breeds/ or guides/ that disqualified candidates]
"""


# ── OpenAI calls ──────────────────────────────────────────────────────────────

def call_openai_responses_api(client, prompt: str) -> str:
    """Primary path: gpt-4o with web_search_preview tool."""
    response = client.responses.create(
        model="gpt-4o",
        tools=[{"type": "web_search_preview"}],
        input=prompt,
    )
    # Extract text output from response items
    for item in response.output:
        if hasattr(item, "content"):
            for block in item.content:
                if hasattr(block, "text"):
                    return block.text
        if hasattr(item, "text"):
            return item.text
    return str(response.output)


def call_openai_chat_fallback(client, prompt: str) -> str:
    """Fallback path: gpt-4o chat completions without web search."""
    print("WARNING: Responses API unavailable — falling back to chat completions (no live web search).",
          file=sys.stderr)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": (
                "You are a content researcher for AnxietyFreePups.com. "
                "Use your training knowledge to identify high-demand, unanswered breed-specific "
                "anxiety topics. Follow the output format exactly as specified."
            )},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content


# ── Memory update ─────────────────────────────────────────────────────────────

def parse_table(raw_output: str) -> list[dict]:
    """Extract rows from the markdown table for memory update."""
    rows = []
    in_table = False
    for line in raw_output.splitlines():
        line = line.strip()
        if line.startswith("| #") or line.startswith("|---|"):
            in_table = True
            continue
        if in_table and line.startswith("|") and not line.startswith("|---|"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 7 and parts[0].isdigit():
                rows.append({
                    "rank": parts[0],
                    "title": parts[1],
                    "slug": parts[2],
                    "paa": parts[3],
                    "affiliate": parts[4],
                    "novelty": parts[5],
                    "score": parts[6],
                    "why": parts[7] if len(parts) > 7 else "",
                })
        elif in_table and not line.startswith("|"):
            in_table = False
    return rows


def update_memory(breed: str, breed_slug: str, existing_slugs: list[str],
                  topics: list[dict]) -> None:
    """Append/replace Coverage Gaps section in MEMORY.md."""
    memory = load_memory()

    # Build new section
    lines = [f"## Coverage Gaps Confirmed ({breed})"]
    for t in topics:
        lines.append(f"- {t['title']} — slug: `{t['slug']}`, score: {t['score']}/15")
    if existing_slugs:
        lines.append(f"\n## Topics Already Written ({breed_slug})")
        for s in existing_slugs:
            lines.append(f"- {s}")
    new_section = "\n".join(lines)

    # Remove old section for this breed if present
    pattern = rf"## Coverage Gaps Confirmed \({re.escape(breed)}\).*?(?=\n## |\Z)"
    memory = re.sub(pattern, "", memory, flags=re.DOTALL).rstrip()

    # Also remove old "Topics Already Written" section for this breed
    pattern2 = rf"## Topics Already Written \({re.escape(breed_slug)}\).*?(?=\n## |\Z)"
    memory = re.sub(pattern2, "", memory, flags=re.DOTALL).rstrip()

    # Append new section
    memory = memory + "\n\n" + new_section + "\n"

    # Trim if over line limit
    mem_lines = memory.splitlines()
    if len(mem_lines) > MEMORY_MAX_LINES:
        # Keep header + last N lines
        keep = mem_lines[:5] + mem_lines[-(MEMORY_MAX_LINES - 5):]
        memory = "\n".join(keep) + "\n"

    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    with open(MEMORY_PATH, "w", encoding="utf-8") as fh:
        fh.write(memory)
    print(f"Memory updated: {MEMORY_PATH}", file=sys.stderr)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Research article topics via OpenAI for a dog breed")
    parser.add_argument("--breed", required=True, help='Breed name e.g. "Australian Shepherd"')
    parser.add_argument("--breed-slug", required=True, help='Breed slug e.g. "australian-shepherd"')
    parser.add_argument("--no-memory-update", action="store_true",
                        help="Skip writing results to MEMORY.md")
    args = parser.parse_args()

    # ── Check API key ──────────────────────────────────────────────────────────
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        print("  Set it with: export OPENAI_API_KEY=sk-...", file=sys.stderr)
        sys.exit(1)

    # ── Check openai package ───────────────────────────────────────────────────
    try:
        import openai
    except ImportError:
        print("ERROR: openai package not installed.", file=sys.stderr)
        print("  Run: pip install openai", file=sys.stderr)
        sys.exit(1)

    # Runtime version warning
    try:
        from packaging.version import Version
        if Version(openai.__version__) < Version("1.30.0"):
            print(f"WARNING: openai {openai.__version__} detected; >=1.30.0 recommended.",
                  file=sys.stderr)
    except ImportError:
        pass  # packaging not installed — skip version check

    from openai import OpenAI

    # ── Inventory ──────────────────────────────────────────────────────────────
    print(f"Inventorying existing coverage for {args.breed}...", file=sys.stderr)
    existing_slugs, breed_page_summary = inventory_existing_coverage(args.breed_slug)
    memory_content = load_memory()

    print(f"  Existing articles: {existing_slugs or '(none)'}", file=sys.stderr)

    # ── Build prompt ───────────────────────────────────────────────────────────
    prompt = build_research_prompt(
        breed=args.breed,
        breed_slug=args.breed_slug,
        breed_page_summary=breed_page_summary,
        existing_slugs=existing_slugs,
        memory_content=memory_content,
    )

    # ── Call OpenAI ────────────────────────────────────────────────────────────
    client = OpenAI(api_key=api_key)

    print(f"Calling OpenAI Responses API (web search) for: {args.breed}", file=sys.stderr)
    raw_output = None
    try:
        raw_output = call_openai_responses_api(client, prompt)
    except Exception as e:
        err_str = str(e)
        if "400" in err_str or "404" in err_str or "web_search" in err_str.lower():
            try:
                raw_output = call_openai_chat_fallback(client, prompt)
            except Exception as e2:
                print(f"ERROR calling OpenAI API: {e2}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"ERROR calling OpenAI API: {e}", file=sys.stderr)
            sys.exit(1)

    if not raw_output:
        print("ERROR: Empty response from OpenAI.", file=sys.stderr)
        sys.exit(1)

    # ── Print table to stdout ──────────────────────────────────────────────────
    print(raw_output)

    # ── Update memory ──────────────────────────────────────────────────────────
    if not args.no_memory_update:
        topics = parse_table(raw_output)
        if topics:
            update_memory(args.breed, args.breed_slug, existing_slugs, topics)
        else:
            print("WARNING: Could not parse table rows — MEMORY.md not updated.", file=sys.stderr)


if __name__ == "__main__":
    main()

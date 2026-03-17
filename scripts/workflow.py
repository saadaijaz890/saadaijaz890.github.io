#!/usr/bin/env python3
"""
workflow.py — Unified CLI for the AnxietyFreePups content pipeline.

Runs all 4 phases without Claude:

    python3 scripts/workflow.py research --breed "Australian Shepherd" --breed-slug "australian-shepherd"
    python3 scripts/workflow.py write --breed "..." --breed-slug "..." --title "..." --slug "..." --date "..." --breed-file "..." --output-file "..."
    python3 scripts/workflow.py link --breed-slug "..." --article-slug "..." --title "..." --desc "..." --emoji "..." --date "..."
    python3 scripts/workflow.py publish --files file1 file2 file3 file4 --message "..."
"""

import argparse
import sys
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cmd_research(args):
    sys.argv = [
        "research_topics.py",
        "--breed", args.breed,
        "--breed-slug", args.breed_slug,
    ]
    if args.no_memory_update:
        sys.argv.append("--no-memory-update")
    from scripts.research_topics import main
    main()


def cmd_write(args):
    sys.argv = [
        "generate_article.py",
        "--breed", args.breed,
        "--breed-slug", args.breed_slug,
        "--dog-ceo-path", args.dog_ceo_path,
        "--title", args.title,
        "--slug", args.slug,
        "--date", args.date,
        "--breed-file", args.breed_file,
        "--guide-file", args.guide_file,
        "--output-file", args.output_file,
    ]
    from scripts.generate_article import main
    main()


def cmd_link(args):
    sys.argv = [
        "link_article.py",
        "--breed-slug", args.breed_slug,
        "--article-slug", args.article_slug,
        "--title", args.title,
        "--desc", args.desc,
        "--emoji", args.emoji,
        "--date", args.date,
    ]
    from scripts.link_article import main
    main()


def cmd_publish(args):
    sys.argv = ["publish_articles.py", "--files"] + args.files + ["--message", args.message]
    from scripts.publish_articles import main
    main()


def main():
    parser = argparse.ArgumentParser(
        description="AnxietyFreePups content pipeline — run any phase directly"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── research ──────────────────────────────────────────────────────────────
    p_research = sub.add_parser("research", help="Phase 1: Research article topics")
    p_research.add_argument("--breed", required=True)
    p_research.add_argument("--breed-slug", required=True)
    p_research.add_argument("--no-memory-update", action="store_true")

    # ── write ─────────────────────────────────────────────────────────────────
    p_write = sub.add_parser("write", help="Phase 2: Generate article HTML")
    p_write.add_argument("--breed", required=True)
    p_write.add_argument("--breed-slug", required=True)
    p_write.add_argument("--dog-ceo-path", required=True)
    p_write.add_argument("--title", required=True)
    p_write.add_argument("--slug", required=True)
    p_write.add_argument("--date", required=True)
    p_write.add_argument("--breed-file", required=True)
    p_write.add_argument("--guide-file", default="guides/separation-anxiety.html")
    p_write.add_argument("--output-file", required=True)

    # ── link ──────────────────────────────────────────────────────────────────
    p_link = sub.add_parser("link", help="Phase 3: Wire article into site")
    p_link.add_argument("--breed-slug", required=True)
    p_link.add_argument("--article-slug", required=True)
    p_link.add_argument("--title", required=True)
    p_link.add_argument("--desc", required=True)
    p_link.add_argument("--emoji", required=True)
    p_link.add_argument("--date", required=True)

    # ── publish ───────────────────────────────────────────────────────────────
    p_publish = sub.add_parser("publish", help="Phase 4: Commit and push files")
    p_publish.add_argument("--files", nargs="+", required=True,
                           help="Exact file paths to stage and commit")
    p_publish.add_argument("--message", required=True, help="Commit message")

    args = parser.parse_args()

    # Add repo root to path so script imports work
    sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

    dispatch = {
        "research": cmd_research,
        "write": cmd_write,
        "link": cmd_link,
        "publish": cmd_publish,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()

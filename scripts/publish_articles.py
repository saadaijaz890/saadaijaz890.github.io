#!/usr/bin/env python3
"""
publish_articles.py — Stages specific files, commits, and pushes to remote.

Usage:
    python3 scripts/publish_articles.py \
        --files blogs/beagle-puppy-crate-training.html breeds/beagle.html index.html sitemap.xml \
        --message "Add Beagle articles: 5 deep-dive guides" \
        --remote calmxx

Safety:
  - Never stages .claude/settings.local.json
  - Never uses --force or git add -A
  - Handles diverged history with rebase
"""

import argparse
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Files that must NEVER be committed (contain secrets)
EXCLUDED_FILES = [
    ".claude/settings.local.json",
    ".env",
]


def run(cmd, check=True, capture=False):
    """Run a shell command in the repo root."""
    result = subprocess.run(
        cmd, shell=True, cwd=REPO_ROOT,
        capture_output=capture, text=True
    )
    if check and result.returncode != 0:
        stderr = result.stderr.strip() if result.stderr else ""
        stdout = result.stdout.strip() if result.stdout else ""
        print(f"ERROR running: {cmd}", file=sys.stderr)
        if stdout:
            print(f"  stdout: {stdout}", file=sys.stderr)
        if stderr:
            print(f"  stderr: {stderr}", file=sys.stderr)
        sys.exit(1)
    return result


def main():
    parser = argparse.ArgumentParser(description="Git stage, commit, push for AnxietyFreePups")
    parser.add_argument("--files", nargs="+", required=True, help="Files to stage and commit")
    parser.add_argument("--message", required=True, help="Commit message")
    parser.add_argument("--remote", default="calmxx", help="Git remote name (default: calmxx)")
    parser.add_argument("--branch", default="main", help="Branch to push (default: main)")
    args = parser.parse_args()

    os.chdir(REPO_ROOT)

    # ── Safety: unstage excluded files ───────────────────────────────────────
    for excluded in EXCLUDED_FILES:
        result = run(f'git diff --cached --name-only', capture=True, check=False)
        if excluded in (result.stdout or ""):
            print(f"  Unstaging excluded file: {excluded}", file=sys.stderr)
            run(f'git restore --staged "{excluded}"', check=False)

    # ── Filter out excluded files from the list ───────────────────────────────
    safe_files = []
    for f in args.files:
        norm = f.replace("\\", "/").lstrip("./")
        if any(excl in norm for excl in EXCLUDED_FILES):
            print(f"  Skipping excluded file: {f}", file=sys.stderr)
        else:
            safe_files.append(f)

    if not safe_files:
        print("ERROR: No safe files to commit.", file=sys.stderr)
        sys.exit(1)

    # ── Verify files exist ────────────────────────────────────────────────────
    missing = []
    for f in safe_files:
        full = os.path.join(REPO_ROOT, f.replace("/", os.sep))
        # For deleted files, they won't exist on disk — that's OK
        # Check git status instead

    # ── Confirm branch ────────────────────────────────────────────────────────
    result = run("git branch --show-current", capture=True)
    current_branch = result.stdout.strip()
    if current_branch != args.branch:
        print(f"ERROR: Expected branch '{args.branch}', currently on '{current_branch}'", file=sys.stderr)
        sys.exit(1)
    print(f"  Branch: {current_branch}", file=sys.stderr)

    # ── Stage files ───────────────────────────────────────────────────────────
    files_str = " ".join(f'"{f}"' for f in safe_files)
    print(f"\nStaging {len(safe_files)} files...", file=sys.stderr)
    run(f"git add {files_str}")

    # Verify staged
    result = run("git diff --cached --name-only", capture=True)
    staged = result.stdout.strip().splitlines()
    print(f"  Staged: {staged}", file=sys.stderr)

    if not staged:
        print("ERROR: No files staged. Nothing to commit.", file=sys.stderr)
        sys.exit(1)

    # ── Commit ────────────────────────────────────────────────────────────────
    # Write message to a temp file to avoid shell escaping issues
    msg_file = os.path.join(REPO_ROOT, ".git", "_publish_msg.txt")
    with open(msg_file, "w", encoding="utf-8") as f:
        f.write(args.message + "\n\nCo-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>")

    print(f"\nCommitting: {args.message}", file=sys.stderr)
    run(f'git commit -F "{msg_file}"')

    # Clean up temp file
    try:
        os.remove(msg_file)
    except OSError:
        pass

    # Verify commit
    result = run("git log --oneline -1", capture=True)
    commit_hash = result.stdout.strip()
    print(f"  Commit: {commit_hash}", file=sys.stderr)

    # ── Push ──────────────────────────────────────────────────────────────────
    print(f"\nPushing to {args.remote}/{args.branch}...", file=sys.stderr)
    push_result = run(f"git push {args.remote} {args.branch}", check=False, capture=True)

    if push_result.returncode != 0:
        stderr = push_result.stderr or ""
        if "rejected" in stderr and "non-fast-forward" in stderr:
            print("  Push rejected — rebasing...", file=sys.stderr)
            run(f"git pull --rebase {args.remote} {args.branch}")
            run(f"git push {args.remote} {args.branch}")
        else:
            print(f"ERROR pushing: {stderr}", file=sys.stderr)
            sys.exit(1)

    print(f"\n✓ Published successfully!", file=sys.stderr)
    print(f"  Commit: {commit_hash}", file=sys.stderr)
    print(f"  Remote: {args.remote}/{args.branch}", file=sys.stderr)
    print(f"  Files: {', '.join(safe_files)}", file=sys.stderr)


if __name__ == "__main__":
    main()

# Content Publisher Agent Memory

## Published Articles (all guides/)
- leash-reactivity.html — "Leash Reactivity: The 3-Step Fix" (pre-existing)
- calming-chews.html — "Calming Chews: Which Work Fastest?" (pre-existing)
- thundershirt-review.html — "Thundershirt Review: Does Pressure Therapy Work?" (pre-existing)
- separation-anxiety.html — "Separation Anxiety: The 3-Layer Protocol" (pre-existing)
- nighttime-anxiety.html — "Nighttime Anxiety Guide" (pre-existing)
- vet-visit-anxiety.html — "How to Calm a Dog Terrified of the Vet" (published 2026-03-09)
- car-travel-anxiety.html — "Why Your Dog Panics in the Car — 3-Step Fix" (published 2026-03-09)
- grooming-anxiety.html — "Dog Scared of the Groomer? Desensitization Plan" (published 2026-03-09)
- rescue-dog-anxiety.html — "New Rescue Dog Won't Settle? 3-3-3 Rule" (published 2026-03-09)
- noise-phobia.html — "Beyond Thunderstorms: Vacuums and Everyday Noises" (published 2026-03-09)
- enrichment-for-anxiety.html — "Anxious Dog Enrichment Plan: 5 Puzzle Toys" (published 2026-03-09)

## Internal Linking Patterns
- calming-chews.html is linked from almost every guide (universal relevance)
- separation-anxiety.html is linked from rescue-dog-anxiety and enrichment-for-anxiety
- vet-visit-anxiety.html is linked from grooming-anxiety and car-travel-anxiety
- All new guides cross-link to each other where relevant

## Affiliate Products Used
- VetriScience Composure Chews (Amazon) — vet visits, car travel, grooming
- Adaptil Spray (Amazon) — vet visits, car travel, grooming
- Thundershirt (Amazon) — vet visits, noise phobia
- Zylkene (Amazon) — vet visits, grooming
- Sleepypod Clickit Sport harness (Amazon) — car travel
- Kong Classic (Amazon) — rescue dog, enrichment
- Midwest iCrate (Amazon) — rescue dog
- Adaptil Diffuser (Amazon) — rescue dog
- LectroFan white noise machine (Amazon) — noise phobia
- Through a Dog's Ear speaker (Amazon) — noise phobia
- Paw5 Snuffle Mat (Amazon) — enrichment
- Nina Ottosson Dog Tornado puzzle (Amazon) — enrichment
- LickiMat Classic Buddy (Amazon) — enrichment
- Himalayan Yak Chews (Amazon) — enrichment

## Git Push Notes
- Remote divergence happened once during session (Article 3). Fixed with: git stash, git pull --rebase, git stash pop, git push
- Use `git stash` approach if pull --rebase fails due to unstaged changes

## HTML Patterns That Work Well
- Stat/timeline bar: dark bark background, 3-column grid, sand-colored values
- Phase blocks, step blocks, strategy cards: warm-white background with sand-light border, 16px radius
- Trigger grids: auto-fill minmax(200px) for 2-3 across on desktop
- Product rows: flex layout, 2rem icon, moss CTA button
- Tip/warning boxes: left border colored, 0 12px 12px 0 radius
- All new articles use `id="heroImg"` for dog.ceo API injection

## Canonical URL Note
Existing guides in sitemap use .html extension (e.g. guides/leash-reactivity.html).
New articles follow same pattern in sitemap but canonical tags use no .html extension.
This matches the pattern in the pre-existing vet-visit-anxiety.html file.

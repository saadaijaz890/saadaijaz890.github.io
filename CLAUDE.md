# AnxietyFreePups — Orchestrator Instructions

You are the Orchestrator for the AnxietyFreePups content publishing system. Your job is to coordinate 4 specialized sub-agents through a gated 4-phase workflow. **Stop for user confirmation between each phase.**

## Site Context

- **URL**: https://www.anxietyfreepups.com
- **Repo**: github.com/saadaijaz890/calmpaw (branch: main)
- **Local path**: C:\Users\Saad\Downloads\calmpaw
- **Hosting**: GitHub Pages + Cloudflare

## Directory Layout

```
index.html               ← homepage (.articles-grid inside #guides section)
guides/                  ← cross-breed topic guides
breeds/                  ← 18 authoritative breed pages
blogs/                   ← NEW: breed-specific deep-dive articles
resources/               ← about, privacy, affiliate-disclosure, contact
sitemap.xml              ← updated on every publish
```

## Breed Slug Reference (18 breeds)

| Breed Name | Slug (file basename) | dog.ceo API path |
|---|---|---|
| Golden Retriever | golden-retriever | retriever-golden |
| Labrador Retriever | labrador-retriever | retriever-labrador |
| German Shepherd | german-shepherd | germanshepherd |
| Poodle | poodle | poodle |
| French Bulldog | french-bulldog | bulldog-french |
| Beagle | beagle | beagle |
| Dachshund | dachshund | dachshund |
| Corgi | corgi | corgi-cardigan |
| Australian Shepherd | australian-shepherd | australian-shepherd |
| Husky | husky | husky |
| Border Collie | border-collie | collie-border |
| Yorkshire Terrier | yorkshire-terrier | yorkshire |
| Chihuahua | chihuahua | chihuahua |
| Pug | pug | pug |
| Pitbull | pitbull | pitbull |
| Cavalier King Charles Spaniel | cavalier-king-charles-spaniel | spaniel-cocker |
| Doberman | doberman | doberman |
| Weimaraner | weimaraner | weimaraner |

## Design System

**CSS Variables** (all pages use these):
```css
--cream:#FAF7F2  --warm-white:#FFFEF9  --bark:#2C1A0E  --bark-light:#5C3D2A
--moss:#3D5A3E   --moss-light:#6B8F6C  --sand:#D4A96A  --sand-light:#EDD9B0
--text:#1A1208   --text-muted:#6B5A4A
```

**Fonts**: `'Playfair Display',Georgia,serif` (headings 700/900) + `'DM Sans',system-ui,-apple-system,sans-serif` (body 400/500)
**Font loading**: async preload + onload pattern with noscript fallback
**Breakpoints**: mobile `max-width:768px`, tablet `min-width:769px and max-width:1100px`

## Schema Requirements (all blog articles)

1. `Article` — with `ImageObject` (1200×630), author, datePublished
2. `BreadcrumbList` — Home → Breed page → Article
3. `FAQPage` — minimum 3 Q&A pairs

## Affiliate Rules

- Amazon Associates links only, always with `tag=anxietyfreepu-20` (no Chewy or other retailers)
- All affiliate links: `rel="noopener noreferrer nofollow sponsored"`
- Disclosure in every page footer + link to `resources/affiliate-disclosure.html`

## 4-Phase Workflow

### Phase 1 — Research (STOP for confirmation)

Invoke `@researcher` with the breed name.

```
@researcher: Research [BREED NAME]
```

Agent returns a 5-row markdown table of article topics ranked by score. **Present table to user, wait for them to pick a topic before proceeding.**

---

### Phase 2 — Write (STOP for review)

Once user confirms a topic, invoke `@writer`:

```
@writer: Write article for [BREED NAME] | title: [CHOSEN TITLE] | slug: [target-slug]
```

The slug becomes the filename: `blogs/[breed-slug]-[target-slug].html`

Agent creates the full HTML file. **Show user the file path and word count, ask them to review before proceeding.**

---

### Phase 3 — Link (STOP for deploy approval)

Once user approves the draft, invoke `@linker`:

```
@linker: breed=[breed-slug] | article=[article-slug] | title=[Article Title] | desc=[one-line description] | emoji=[single emoji] | date=[YYYY-MM-DD]
```

Agent updates 3 files: `breeds/[breed].html`, `index.html`, `sitemap.xml`. **Show user a summary of all 3 edits and ask for deploy approval.**

---

### Phase 4 — Publish

Once user approves deploy, invoke `@publisher`:

```
@publisher: Publish [blogs/breed-slug-article-slug.html] + [breeds/breed-slug.html] + [index.html] + [sitemap.xml]
```

Agent stages exactly those 4 files, commits, and pushes. **Report the live URL to user.**

## Critical File Paths

- Design template for @writer: `breeds/golden-retriever.html`
- Structure reference for @writer: `guides/separation-anxiety.html`
- Homepage grid target for @linker: `.articles-grid` inside `<section id="guides">` in `index.html`
- Sitemap: `sitemap.xml`

## Blog Section Scaffold

@linker injects this into a breed page (before `.related-section`) the first time an article is added for that breed:

```html
<section class="blog-articles-section" style="background:var(--cream);border-top:1px solid var(--sand-light);padding:3rem 5vw">
  <div style="max-width:760px;margin:0 auto">
    <h2 style="font-family:'Playfair Display',Georgia,serif;font-size:1.8rem;font-weight:700;color:var(--bark);margin-bottom:1.5rem">[Breed] Deep-Dive Articles</h2>
    <div id="blog-list" style="display:flex;flex-direction:column;gap:1rem">
    <!-- BLOG_LIST_START -->
    <!-- BLOG_LIST_END -->
    </div>
  </div>
</section>
```

## Article Card Template (inserted by @linker after `<!-- BLOG_LIST_START -->`)

```html
    <a href="/blogs/[breed-slug]-[article-slug]" style="display:flex;gap:1rem;background:var(--warm-white);border:1px solid var(--sand-light);border-radius:12px;padding:1.2rem;text-decoration:none;transition:all .2s" onmouseover="this.style.borderColor='var(--moss)'" onmouseout="this.style.borderColor='var(--sand-light)'">
      <span style="font-size:2rem;flex-shrink:0">[EMOJI]</span>
      <div>
        <div style="font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--moss);font-weight:600;margin-bottom:.3rem">DEEP-DIVE</div>
        <div style="font-weight:600;color:var(--bark);font-size:.95rem;margin-bottom:.3rem">[ARTICLE TITLE]</div>
        <div style="font-size:.82rem;color:var(--text-muted)">[ONE-LINE DESCRIPTION]</div>
      </div>
    </a>
```

## Homepage Article Card Template (prepended by @linker to `.articles-grid`)

```html
    <a href="blogs/[breed-slug]-[article-slug]" class="article-card reveal">
      <div class="article-thumb" style="background:linear-gradient(135deg,var(--sand),var(--bark-light));display:flex;align-items:center;justify-content:center;position:relative"><span style="font-size:3.5rem;line-height:1;z-index:1">[EMOJI]</span><span class="card-cat">BREED GUIDE</span></div>
      <div class="article-body"><h3>[ARTICLE TITLE]</h3><p>[ONE-LINE DESCRIPTION]</p></div>
    </a>
```

## Safety Rules

- Never skip the STOP gates — each phase requires explicit user confirmation
- @publisher stages **specific file paths only** — never `git add -A`
- @linker logs every rotated homepage card to its memory file
- No agent uses `--no-verify` or `--force` on git commands

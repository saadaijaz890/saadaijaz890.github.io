#!/usr/bin/env python3
"""
generate_article.py — Uses OpenAI gpt-4o to generate a complete blog article HTML
for AnxietyFreePups.com.

Usage:
    python3 scripts/generate_article.py \
        --breed "Beagle" \
        --breed-slug "beagle" \
        --dog-ceo-path "beagle" \
        --title "Beagle Separation Anxiety: 5-Step Protocol 2026" \
        --slug "beagle-separation-anxiety-protocol" \
        --date "2026-03-17" \
        --breed-file "breeds/beagle.html" \
        --guide-file "guides/separation-anxiety.html" \
        --output-file "blogs/beagle-separation-anxiety-protocol.html"

Requires: pip install openai
API key:  export OPENAI_API_KEY=sk-...
"""

import argparse
import os
import re
import sys

# ── Site-wide CSS (copied from breeds/golden-retriever.html) ──────────────────
CSS = """    :root{--cream:#FAF7F2;--warm-white:#FFFEF9;--bark:#2C1A0E;--bark-light:#5C3D2A;--moss:#3D5A3E;--moss-light:#6B8F6C;--sand:#D4A96A;--sand-light:#EDD9B0;--text:#1A1208;--text-muted:#6B5A4A;--shadow:0 4px 32px rgba(44,26,14,.10)}
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    html{scroll-behavior:smooth}
    body{font-family:'DM Sans',system-ui,-apple-system,sans-serif;background:var(--cream);color:var(--text)}
    header{position:sticky;top:0;z-index:100;background:rgba(250,247,242,.98);backdrop-filter:blur(12px);border-bottom:1px solid var(--sand-light);padding:0 5vw;display:flex;align-items:center;justify-content:space-between;height:64px}
    .logo{font-family:'Playfair Display',Georgia,serif;font-size:1.5rem;font-weight:900;color:var(--bark);text-decoration:none}.logo span{color:var(--moss)}
    nav{display:flex;gap:2rem}nav a{text-decoration:none;color:var(--text-muted);font-size:.9rem;font-weight:500}nav a:hover{color:var(--moss)}
    .nav-cta{background:var(--moss);color:white!important;padding:.5rem 1.2rem;border-radius:100px}
    .breadcrumb{padding:1.2rem 5vw;font-size:.82rem;color:var(--text-muted)}.breadcrumb a{color:var(--moss);text-decoration:none}
    .hero-article{background:linear-gradient(135deg,#EDD9B0 0%,#FAF7F2 60%);padding:4rem 5vw 3rem}
    .article-tag{display:inline-block;background:var(--bark);color:var(--sand-light);padding:.3rem .9rem;border-radius:100px;font-size:.72rem;font-weight:500;letter-spacing:.06em;margin-bottom:1.2rem}
    h1{font-family:'Playfair Display',Georgia,serif;font-size:clamp(2rem,4vw,3rem);font-weight:900;color:var(--bark);line-height:1.1;max-width:760px;margin-bottom:1rem}
    .lead{font-size:1.1rem;color:var(--text-muted);max-width:680px;line-height:1.7;margin-bottom:1.5rem}
    .meta{display:flex;gap:2rem;font-size:.82rem;color:var(--text-muted)}
    .content{max-width:760px;margin:0 auto;padding:3rem 5vw}
    h2{font-family:'Playfair Display',Georgia,serif;font-size:1.8rem;font-weight:700;color:var(--bark);margin:2.5rem 0 1rem}
    h3{font-family:'Playfair Display',Georgia,serif;font-size:1.3rem;font-weight:700;color:var(--bark);margin:1.5rem 0 .8rem}
    p{font-size:1rem;color:var(--text-muted);line-height:1.75;margin-bottom:1.2rem}
    .breed-facts{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:1.5rem 0}
    .fact{background:var(--warm-white);border:1px solid var(--sand-light);border-radius:12px;padding:1.2rem;text-align:center}
    .fact .val{font-family:'Playfair Display',Georgia,serif;font-size:1.8rem;font-weight:700;color:var(--moss)}
    .fact .label{font-size:.78rem;color:var(--text-muted);margin-top:.3rem}
    .product-row{background:var(--warm-white);border:1px solid var(--sand-light);border-radius:16px;padding:1.5rem;margin:1rem 0;display:flex;gap:1rem;align-items:center}
    .product-row .emoji{font-size:2rem;flex-shrink:0}
    .product-row h4{font-weight:600;color:var(--bark);margin-bottom:.2rem}
    .product-row p{font-size:.82rem;color:var(--text-muted);margin:0}
    .product-row a{display:inline-block;background:var(--moss);color:white;padding:.4rem 1rem;border-radius:100px;text-decoration:none;font-size:.78rem;font-weight:500;margin-top:.5rem;transition:all .2s}
    .product-row a:hover{background:var(--bark)}
    .tip-box{background:rgba(61,90,62,.08);border-left:4px solid var(--moss);border-radius:0 12px 12px 0;padding:1.2rem 1.5rem;margin:1.5rem 0;font-size:.9rem;color:var(--text-muted)}
    .tip-box strong{color:var(--moss)}
    .warning-box{background:rgba(212,169,106,.12);border-left:4px solid var(--sand);border-radius:0 12px 12px 0;padding:1.2rem 1.5rem;margin:1.5rem 0;font-size:.9rem;color:var(--text-muted)}
    .warning-box strong{color:var(--bark-light)}
    .faq-section{background:var(--warm-white);padding:3rem 5vw;margin-top:3rem}
    .faq-container{max-width:760px;margin:0 auto}
    .faq-item{background:var(--cream);border-radius:16px;padding:1.8rem;border:1px solid var(--sand-light);margin-bottom:1rem}
    .faq-q{font-family:'Playfair Display',Georgia,serif;font-size:1.1rem;font-weight:700;color:var(--bark);margin-bottom:.8rem;line-height:1.3}
    .faq-a{font-size:.9rem;color:var(--text-muted);line-height:1.6}
    .faq-a strong{color:var(--moss)}
    .back-btn{display:inline-block;margin-bottom:2rem;color:var(--moss);text-decoration:none;font-size:.9rem;font-weight:500}
    .back-btn:hover{text-decoration:underline}
    footer{background:var(--bark);color:rgba(255,255,255,.5);padding:3rem 5vw;display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:3rem}
    footer .logo{color:var(--sand-light);display:block;margin-bottom:.8rem}footer p{font-size:.82rem;line-height:1.65}
    footer h4{color:white;font-size:.85rem;font-weight:600;margin-bottom:1rem}footer ul{list-style:none}footer ul li{margin-bottom:.5rem}
    footer ul a{color:rgba(255,255,255,.5);text-decoration:none;font-size:.82rem}footer ul a:hover{color:var(--sand)}
    .footer-bottom{background:rgba(0,0,0,.2);padding:1.2rem 5vw;text-align:center;font-size:.75rem;color:rgba(255,255,255,.6)}
    .affiliate-note{background:rgba(212,169,106,.1);border:1px solid rgba(212,169,106,.2);border-radius:8px;padding:1rem;margin-top:2rem;font-size:.75rem;color:rgba(255,255,255,.65)}
    .related-section{background:var(--warm-white);border-top:1px solid var(--sand-light);padding:3rem 5vw;margin-top:2rem}
    .related-section h3{font-family:'Playfair Display',Georgia,serif;font-size:1.5rem;color:var(--bark);margin-bottom:1.5rem}
    .related-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1rem;max-width:760px}
    .related-card{background:var(--cream);border:1px solid var(--sand-light);border-radius:12px;padding:1.2rem;text-decoration:none;display:block;transition:all .2s}
    .related-card:hover{border-color:var(--moss);transform:translateY(-2px)}
    .related-card .rc-tag{font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;color:var(--moss);font-weight:600;margin-bottom:.4rem}
    .related-card .rc-title{font-size:.9rem;font-weight:600;color:var(--bark);line-height:1.3}
    .breed-hero-img{width:120px;height:120px;border-radius:50%;object-fit:cover;border:4px solid rgba(255,255,255,.3);box-shadow:0 8px 32px rgba(0,0,0,.2);margin-bottom:1.2rem;display:block}
    .hamburger{display:none;flex-direction:column;gap:5px;cursor:pointer;padding:.5rem;background:none;border:none;z-index:200}
    .hamburger span{display:block;width:22px;height:2px;background:var(--bark);border-radius:2px;transition:all .3s}
    .hamburger.open span:nth-child(1){transform:rotate(45deg) translate(5px,5px)}
    .hamburger.open span:nth-child(2){opacity:0}
    .hamburger.open span:nth-child(3){transform:rotate(-45deg) translate(5px,-5px)}
    .mobile-menu{display:none;position:fixed;inset:0;background:var(--cream);z-index:150;padding:80px 2rem 2rem;flex-direction:column;overflow-y:auto}
    .mobile-menu.open{display:flex}
    .mobile-menu a{font-size:1.1rem;font-weight:500;color:var(--bark);text-decoration:none;padding:1rem 0;border-bottom:1px solid var(--sand-light);transition:color .2s}
    .mobile-menu a:hover{color:var(--moss)}
    .mobile-menu .mob-cta{background:var(--moss);color:white!important;border-radius:100px;text-align:center;padding:.9rem 1.5rem;margin-top:1.5rem;border:none}
    @media(max-width:768px){nav{display:none}footer{grid-template-columns:1fr 1fr}}
    @media(max-width:768px){.hamburger{display:flex}}"""


def build_system_prompt():
    # Use a placeholder instead of f-string to avoid conflicts with JS/JSON curly braces
    template = """You are the content writer for AnxietyFreePups.com, a dog anxiety affiliate site. Your task is to produce one complete, publish-ready HTML page for a breed-specific deep-dive blog article.

## ABSOLUTE RULES
1. Output ONLY valid HTML. No markdown code fences, no explanations, no commentary. The raw output is saved directly as an .html file.
2. Use ONLY the CSS classes listed below — do NOT invent new class names.
3. Every affiliate link MUST include: rel="noopener noreferrer nofollow sponsored" and target="_blank"
4. Affiliate links format: https://www.amazon.com/s?k=[search+terms]&tag=anxietyfree-20 OR https://www.chewy.com/s?query=[terms]
5. Include ALL 3 required JSON-LD schemas: Article, BreadcrumbList, FAQPage
6. Write 1,500–2,000 words of body copy (not counting HTML/CSS boilerplate) — use 5-6 H2 sections, each with 2-3 detailed paragraphs
7. Every paragraph must reference the specific breed — no generic "your dog" advice

## EXACT CSS TO USE
Place this inside <style> tags verbatim:
__CSS_BLOCK__

## EXACT FONT LOADING PATTERN
```
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@400;500&display=swap" as="style" onload="this.onload=null;this.rel='stylesheet'"><noscript><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet"></noscript>
```

## EXACT HEADER HTML (reproduce verbatim)
```
<header><a href="/" class="logo">AnxietyFree<span>Pups</span></a><nav><a href="/#guides">Breed Guides</a><a href="/#products">Top Products</a><a href="/#faq">FAQ</a><a href="/#products" class="nav-cta">Shop Now</a></nav><button class="hamburger" id="menuToggle" aria-label="Menu" onclick="var m=document.getElementById('mobileNav');m.classList.toggle('open');this.classList.toggle('open')"><span></span><span></span><span></span></button></header>
```

## EXACT FOOTER HTML (reproduce verbatim)
```
<footer>
  <div><a href="/" class="logo">AnxietyFree<span style="color:var(--sand)">Pups</span></a><p>Helping anxious dogs find calm since 2024. All recommendations independently researched.</p><div class="affiliate-note">⚠️ <strong>Affiliate Disclosure:</strong> We earn commissions from qualifying purchases at no extra cost to you. <a href="/resources/affiliate-disclosure" style="color:rgba(255,255,255,.7)">Full disclosure</a></div></div>
  <div><h4>Top Guides</h4><ul><li><a href="/guides/calming-chews">Calming Chews</a></li><li><a href="/guides/thundershirt-review">Thundershirt Review</a></li><li><a href="/guides/separation-anxiety">Separation Anxiety</a></li><li><a href="/guides/nighttime-anxiety">Nighttime Anxiety</a></li></ul></div>
  <div><h4>By Breed</h4><ul><li><a href="/breeds/pug">Pug</a></li><li><a href="/breeds/corgi">Corgi</a></li><li><a href="/breeds/chihuahua">Chihuahua</a></li><li><a href="/breeds/golden-retriever">Golden Retriever</a></li><li><a href="/breeds/border-collie">Border Collie</a></li></ul></div>
  <div><h4>Resources</h4><ul><li><a href="/resources/about">About</a></li><li><a href="/resources/affiliate-disclosure">Affiliate Disclosure</a></li><li><a href="/resources/contact">Contact</a></li></ul></div>
</footer>
<div class="footer-bottom">© 2026 AnxietyFreePups.com — Not a substitute for veterinary advice.</div>
```

## EXACT MOBILE MENU (reproduce verbatim)
```
<div class="mobile-menu" id="mobileNav"><a href="/#guides" onclick="document.getElementById('mobileNav').classList.remove('open');document.getElementById('menuToggle').classList.remove('open')">Breed Guides</a><a href="/#products" onclick="document.getElementById('mobileNav').classList.remove('open');document.getElementById('menuToggle').classList.remove('open')">Top Products</a><a href="/#faq" onclick="document.getElementById('mobileNav').classList.remove('open');document.getElementById('menuToggle').classList.remove('open')">FAQ</a><a href="/#products" class="mob-cta" onclick="document.getElementById('mobileNav').classList.remove('open');document.getElementById('menuToggle').classList.remove('open')">Shop Now</a></div>
```

## DOG IMAGE LAZY-LOAD PATTERN
Use this exact pattern (fill in BREED and DOG_CEO_PATH):
```
<img id="breed-hero" class="breed-hero-img" src="" alt="[BREED] dog" loading="lazy">
<script>
fetch('https://dog.ceo/api/breed/[DOG_CEO_PATH]/images/random')
  .then(r=>r.json()).then(d=>{if(d.status==='success')document.getElementById('breed-hero').src=d.message})
  .catch(()=>{});
</script>
```

## FULL PAGE STRUCTURE

```
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🐾</text></svg>">
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>[Article Title] | AnxietyFreePups</title>
  <meta name="description" content="[150-160 chars including breed name and primary keyword]"/>
  <link rel="canonical" href="https://www.anxietyfreepups.com/blogs/[slug]"/>
  <meta property="og:type" content="article"/>
  <meta property="og:url" content="https://www.anxietyfreepups.com/blogs/[slug]"/>
  <meta property="og:title" content="[title]"/>
  <meta property="og:description" content="[description]"/>
  <meta property="og:image" content="https://images.dog.ceo/breeds/[dog-ceo-path]/random.jpg"/>
  <meta name="twitter:card" content="summary_large_image"/>
  <meta name="twitter:title" content="[title]"/>
  <meta name="twitter:description" content="[short description]"/>
  <meta name="twitter:image" content="https://images.dog.ceo/breeds/[dog-ceo-path]/random.jpg"/>
  [FONT LOADING]
  <style>[FULL CSS]</style>
  <script type="application/ld+json">[Article schema]</script>
  <script type="application/ld+json">[BreadcrumbList schema]</script>
  <script type="application/ld+json">[FAQPage schema — must match FAQ HTML]</script>
</head>
<body>
[HEADER]
<nav class="breadcrumb"><a href="/">Home</a> › <a href="/breeds/[breed-slug]">[Breed] Anxiety Guide</a> › [Short Article Title]</nav>
<div class="hero-article">
  <span class="article-tag">DEEP DIVE</span>
  [DOG IMAGE + SCRIPT]
  <h1>[Full Article Title]</h1>
  <p class="lead">[2-3 sentence breed-specific hook, 40-60 words]</p>
  <div class="meta"><span>🔬 Vet-reviewed</span><span>📅 Updated [YEAR]</span><span>⏱ 7 min read</span></div>
</div>
<div class="content">
  <a href="/breeds/[breed-slug]" class="back-btn">← [Breed] Complete Anxiety Guide</a>
  [3-4 H2 content sections, each with 2-3 breed-specific paragraphs]
  [1-2 .tip-box elements with <strong> highlights]
  [1-2 .warning-box elements with <strong> highlights]
  [2-3 .product-row cards]
  [1 internal link to a relevant guide using <a href="/guides/[guide]">]
</div>
<section class="faq-section">
  <div class="faq-container">
    <h2>Frequently Asked Questions: [Breed] [Topic]</h2>
    [3-5 .faq-item > .faq-q + .faq-a]
  </div>
</section>
<section class="related-section">
  <div style="max-width:760px;margin:0 auto">
    <h3>Related Reading</h3>
    <div class="related-grid">
      <a href="/breeds/[breed-slug]" class="related-card">
        <div class="rc-tag">Breed Guide</div>
        <div class="rc-title">[Breed] Complete Anxiety Guide</div>
      </a>
      <a href="/guides/[relevant-guide]" class="related-card">
        <div class="rc-tag">Guide</div>
        <div class="rc-title">[Relevant Guide Title]</div>
      </a>
    </div>
  </div>
</section>
[FOOTER]
[MOBILE MENU]
</body>
</html>
```

## REQUIRED SCHEMAS

Article:
{{"@context":"https://schema.org","@type":"Article","headline":"[title]","description":"[meta description]","author":{{"@type":"Organization","name":"AnxietyFreePups"}},"publisher":{{"@type":"Organization","name":"AnxietyFreePups","url":"https://www.anxietyfreepups.com"}},"datePublished":"[YYYY-MM-DD]","dateModified":"[YYYY-MM-DD]","url":"https://www.anxietyfreepups.com/blogs/[slug]","image":{{"@type":"ImageObject","url":"https://images.dog.ceo/breeds/[dog-ceo-path]/random.jpg","width":1200,"height":630}}}}

BreadcrumbList:
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"https://www.anxietyfreepups.com/"}},{{"@type":"ListItem","position":2,"name":"[Breed] Guide","item":"https://www.anxietyfreepups.com/breeds/[breed-slug]"}},{{"@type":"ListItem","position":3,"name":"[Article Title]","item":"https://www.anxietyfreepups.com/blogs/[slug]"}}]}}

FAQPage: Build from the actual FAQ items in the HTML. Minimum 3 Q&A pairs.

## PRODUCT CARD FORMAT
```
<div class="product-row">
  <div class="emoji">[emoji]</div>
  <div>
    <h4>[Product Name]</h4>
    <p>[1-line breed-specific benefit]</p>
    <a href="https://www.amazon.com/s?k=[search+terms]&tag=anxietyfree-20" target="_blank" rel="noopener noreferrer nofollow sponsored">View on Amazon →</a>
  </div>
</div>
```

## CONTENT STANDARDS
- Tone: warm, practical, evidence-based — knowledgeable dog owner writing for peers
- Structure: H2 for major sections, H3 for sub-points. NO second H1.
- Tip boxes: pro training tips, positive advice
- Warning boxes: medical cautions, safety notes
- FAQ answers: 2-4 sentences, breed-specific, include <strong> on key terms
"""
    return template.replace("__CSS_BLOCK__", CSS)


def build_user_prompt(breed, breed_slug, dog_ceo_path, title, slug, date, breed_context, products_to_avoid):
    year = date[:4]
    avoid_str = ", ".join(products_to_avoid) if products_to_avoid else "none listed"

    return f"""Write the complete blog article HTML for these parameters:

- Breed: {breed}
- Breed slug: {breed_slug}
- Dog.ceo API path: {dog_ceo_path}
- Article title: {title}
- URL slug: {slug}
- Canonical URL: https://www.anxietyfreepups.com/blogs/{slug}
- Date published: {date}
- Year: {year}

BREED CONTEXT (from the {breed} breed page — use these facts, do not contradict them):
{breed_context}

PRODUCTS ALREADY ON THE BREED PAGE (do not duplicate these exact products in your article):
{avoid_str}

Output a single complete HTML document starting with <!DOCTYPE html> and ending with </html>.
No markdown. No code fences. No explanation text. HTML only."""


def extract_breed_context(html_content, breed):
    """Extract key breed facts from the breed page HTML."""
    if not html_content:
        return f"No breed page found — use general {breed} anxiety knowledge."

    # Extract fact card values + labels
    vals = re.findall(r'class="val"[^>]*>(.*?)</div>', html_content)
    labels = re.findall(r'class="label"[^>]*>(.*?)</div>', html_content)

    # Extract headings
    headings = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', html_content)
    headings = [re.sub(r'<[^>]+>', '', h).strip() for h in headings if h.strip()]

    # Extract text from first content paragraphs (breed context area)
    content_match = re.search(r'class="content">(.*?)</div>', html_content, re.DOTALL)
    paragraphs = []
    if content_match:
        raw = content_match.group(1)
        paras = re.findall(r'<p[^>]*>(.*?)</p>', raw, re.DOTALL)
        paragraphs = [re.sub(r'<[^>]+>', '', p).strip() for p in paras if len(p.strip()) > 80][:4]

    parts = []
    if vals and labels:
        stats = [f"{v}: {l}" for v, l in zip(vals[:3], labels[:3])]
        parts.append("Key breed stats: " + " | ".join(stats))
    if headings:
        parts.append("Topics on breed page: " + ", ".join(headings[:8]))
    if paragraphs:
        parts.append("Breed facts already stated:\n" + "\n".join(f"- {p[:220]}" for p in paragraphs))

    return "\n".join(parts) if parts else f"Breed page found but no structured facts extracted — write breed-accurate {breed} content."


def extract_products(html_content):
    """Extract product h4 names from the breed page to avoid duplicates."""
    return re.findall(r'<h4>(.*?)</h4>', html_content)


def strip_code_fences(text):
    """Remove markdown code fences if the model wrapped its output."""
    text = text.strip()
    # Strip opening fence
    text = re.sub(r'^```html?\s*\n?', '', text, flags=re.IGNORECASE)
    # Strip closing fence
    text = re.sub(r'\n?```\s*$', '', text)
    return text.strip()


def count_words(html_content):
    """Rough word count of visible text (strips tags)."""
    text = re.sub(r'<[^>]+>', ' ', html_content)
    text = re.sub(r'\s+', ' ', text)
    return len(text.split())


def main():
    parser = argparse.ArgumentParser(description="Generate blog article HTML via OpenAI gpt-4o")
    parser.add_argument("--breed", required=True, help='Breed name, e.g. "Beagle"')
    parser.add_argument("--breed-slug", required=True, help='Breed slug, e.g. "beagle"')
    parser.add_argument("--dog-ceo-path", required=True, help='dog.ceo API path, e.g. "beagle"')
    parser.add_argument("--title", required=True, help="Full article title")
    parser.add_argument("--slug", required=True, help='Full URL slug, e.g. "beagle-separation-anxiety-protocol"')
    parser.add_argument("--date", required=True, help="Publication date YYYY-MM-DD")
    parser.add_argument("--breed-file", required=True, help="Path to breed page HTML file")
    parser.add_argument("--guide-file", required=True, help="Path to guide HTML for structure reference")
    parser.add_argument("--output-file", required=True, help="Output file path, e.g. blogs/beagle-separation-anxiety-protocol.html")
    args = parser.parse_args()

    # ── Check API key ──────────────────────────────────────────────────────────
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        print("  Set it with: export OPENAI_API_KEY=sk-...", file=sys.stderr)
        sys.exit(1)

    # ── Check openai is installed ──────────────────────────────────────────────
    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: openai package not installed.", file=sys.stderr)
        print("  Run: pip install openai", file=sys.stderr)
        sys.exit(1)

    # ── Read reference files ───────────────────────────────────────────────────
    breed_html = ""
    breed_file = args.breed_file
    if os.path.exists(breed_file):
        with open(breed_file, "r", encoding="utf-8") as f:
            breed_html = f.read()
        print(f"Read breed file: {breed_file}", file=sys.stderr)
    else:
        fallback = "breeds/golden-retriever.html"
        if os.path.exists(fallback):
            with open(fallback, "r", encoding="utf-8") as f:
                breed_html = f.read()
            print(f"Breed file not found, using fallback: {fallback}", file=sys.stderr)
        else:
            print(f"Warning: breed file not found: {breed_file}", file=sys.stderr)

    # ── Extract context ────────────────────────────────────────────────────────
    breed_context = extract_breed_context(breed_html, args.breed)
    products_to_avoid = extract_products(breed_html)

    # ── Build prompts ──────────────────────────────────────────────────────────
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(
        breed=args.breed,
        breed_slug=args.breed_slug,
        dog_ceo_path=args.dog_ceo_path,
        title=args.title,
        slug=args.slug,
        date=args.date,
        breed_context=breed_context,
        products_to_avoid=products_to_avoid,
    )

    # ── Call OpenAI ────────────────────────────────────────────────────────────
    print(f"Calling OpenAI gpt-4o: {args.title}", file=sys.stderr)

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=12000,
        )
    except Exception as e:
        print(f"ERROR calling OpenAI API: {e}", file=sys.stderr)
        sys.exit(1)

    html_output = response.choices[0].message.content
    html_output = strip_code_fences(html_output)

    # ── Write output file ──────────────────────────────────────────────────────
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(html_output)

    word_count = count_words(html_output)
    print(f"SUCCESS: Written to {args.output_file} ({word_count} words)", file=sys.stderr)
    print(f"Tokens used: prompt={response.usage.prompt_tokens}, completion={response.usage.completion_tokens}", file=sys.stderr)


if __name__ == "__main__":
    main()

"""
SEO Prompt Template — Master prompt used for Gemini article generation.
Enforces SEO best practices, your site's editorial style, Kadence block HTML, and internal linking.
"""
import os
import json

# Scheme category slugs matching kisanportal.org pillar URLs (for WordPress category assignment)
SCHEME_CATEGORY_SLUGS = [
    "pm-kisan-samman-nidhi", "pmfby", "kisan-credit-card", "kisan-vikas-patra",
    "enam-scheme", "kisan-karz-mochan-yojana", "rythu-bharosa", "soil-health-card",
    "pm-kisan-tractor-scheme", "e-crop", "pm-dhan-dhaanya-krishi-yojana",
    "dalhan-aatmanirbharta-mission-scheme", "e-panta", "pik-vima-scheme-maharashtra",
]
# For prompt: same list + "news" for unrelated topics
CATEGORY_MAPPING = SCHEME_CATEGORY_SLUGS + ["news"]

# Topic/keyword phrases → WordPress category slug. First match wins; otherwise "news".
# Order matters: more specific phrases should come before broad ones (e.g. "PM Kisan Tractor" before "PM Kisan").
KEYWORDS_TO_CATEGORY = [
    # (list of phrases to match in topic title or matched_keyword, slug)
    (["pm kisan tractor", "tractor scheme", "tractor subsidy"], "pm-kisan-tractor-scheme"),
    (["pm kisan", "pm-kisan", "samman nidhi", "kisan samman"], "pm-kisan-samman-nidhi"),
    (["pmfby", "fasal bima", "crop insurance", "pradhan mantri fasal bima"], "pmfby"),
    (["kisan credit card", "kcc"], "kisan-credit-card"),
    (["kisan vikas patra", "kvp"], "kisan-vikas-patra"),
    (["enam", "e-nam", "e nam", "national agricultural market"], "enam-scheme"),
    (["kisan karz mochan", "karz mochan"], "kisan-karz-mochan-yojana"),
    (["rythu bharosa", "rythu bandhu", "rythu bharosa scheme"], "rythu-bharosa"),
    (["soil health card", "soil health"], "soil-health-card"),
    (["e-crop", "e crop", "ecrop"], "e-crop"),
    (["pm dhan dhaanya", "dhaanya krishi", "pm dhan"], "pm-dhan-dhaanya-krishi-yojana"),
    (["dalhan", "aatmanirbharta mission", "dalhan aatmanirbharta"], "dalhan-aatmanirbharta-mission-scheme"),
    (["e-panta", "e panta", "e panta andhra", "panta andhra"], "e-panta"),
    (["pik vima", "pik vima maharashtra", "pik vima scheme"], "pik-vima-scheme-maharashtra"),
]


def get_category_for_topic(topic_title, matched_keyword=""):
    """
    Return the WordPress category slug for this topic.
    If the topic or matched_keyword matches one of the scheme categories, return that slug.
    Otherwise return "news".
    """
    if not topic_title and not matched_keyword:
        return "news"
    combined = f" {((topic_title or '') + ' ' + (matched_keyword or '')).lower()} "
    for phrases, slug in KEYWORDS_TO_CATEGORY:
        for phrase in phrases:
            if phrase.lower() in combined:
                return slug
    return "news"

# Verified kisanportal.org POST URLs for internal linking (real published pages — no 404s).
# Category slugs (SCHEME_CATEGORY_SLUGS) are used only for WordPress category assignment, not for links.
BASE_URL = "https://kisanportal.org"

# Each entry: exact URL as published on site, topic label, and suggested anchor text. Use ONLY these URLs.
INTERNAL_LINKS_PILLARS = [
    {"url": f"{BASE_URL}/pm-kisan/", "topic": "PM Kisan", "anchors": ["PM Kisan", "PM-Kisan scheme", "farmer income support"]},
    {"url": f"{BASE_URL}/pm-kisan-status-check/", "topic": "PM Kisan Status Check", "anchors": ["PM Kisan status check", "check PM Kisan status", "beneficiary status"]},
    {"url": f"{BASE_URL}/pm-kisan-beneficiary-list/", "topic": "PM Kisan Beneficiary List", "anchors": ["PM Kisan beneficiary list", "beneficiary list"]},
    {"url": f"{BASE_URL}/pm-kisan-ekyc-guide/", "topic": "PM Kisan eKYC", "anchors": ["PM Kisan eKYC", "eKYC for PM Kisan"]},
    {"url": f"{BASE_URL}/pm-kisan-22nd-installment-date-2026/", "topic": "PM Kisan 22nd Installment", "anchors": ["PM Kisan 22nd installment", "22nd kist date"]},
    {"url": f"{BASE_URL}/pm-kisan-21st-installment-released/", "topic": "PM Kisan 21st Installment", "anchors": ["PM Kisan 21st installment", "21st kist"]},
    {"url": f"{BASE_URL}/pm-kisan-20th-installment/", "topic": "PM Kisan 20th Installment", "anchors": ["PM Kisan 20th installment"]},
    {"url": f"{BASE_URL}/pmfby-guide/", "topic": "PMFBY Guide", "anchors": ["PMFBY", "Pradhan Mantri Fasal Bima Yojana", "crop insurance guide"]},
    {"url": f"{BASE_URL}/pmfby-rabi-enrollment/", "topic": "PMFBY Rabi Enrollment", "anchors": ["PMFBY Rabi enrollment", "crop insurance enrollment"]},
    {"url": f"{BASE_URL}/kisan-credit-card-scheme/", "topic": "Kisan Credit Card Scheme", "anchors": ["Kisan Credit Card", "KCC", "farm credit scheme"]},
    {"url": f"{BASE_URL}/kisan-vikas-patra-guide/", "topic": "Kisan Vikas Patra Guide", "anchors": ["Kisan Vikas Patra", "KVP", "KVP guide"]},
    {"url": f"{BASE_URL}/enam-guide/", "topic": "eNAM Guide", "anchors": ["eNAM", "eNAM guide", "National Agricultural Market"]},
    {"url": f"{BASE_URL}/enam-2.0-registration-complete-guide/", "topic": "eNAM 2.0 Registration", "anchors": ["eNAM 2.0", "eNAM registration"]},
    {"url": f"{BASE_URL}/kisan-karz-mochan/", "topic": "Kisan Karz Mochan Yojana", "anchors": ["Kisan Karz Mochan", "debt relief for farmers"]},
    {"url": f"{BASE_URL}/rythu-bharosa-guide/", "topic": "Rythu Bharosa Guide", "anchors": ["Rythu Bharosa", "Rythu Bandhu", "farmer support"]},
    {"url": f"{BASE_URL}/soil-health-card-guide/", "topic": "Soil Health Card Guide", "anchors": ["Soil Health Card", "soil health card guide"]},
    {"url": f"{BASE_URL}/pm-tractor-scheme/", "topic": "PM Tractor Scheme", "anchors": ["PM Kisan Tractor Scheme", "tractor subsidy", "tractor scheme"]},
    {"url": f"{BASE_URL}/e-crop-registration/", "topic": "E-Crop Registration", "anchors": ["E-Crop registration", "e-Crop", "crop registration"]},
    {"url": f"{BASE_URL}/e-crop-status-ap/", "topic": "E-Crop Status AP", "anchors": ["E-Crop status", "e-Crop status check"]},
    {"url": f"{BASE_URL}/pm-dhan-dhaanya-krishi-yojana-pmddky/", "topic": "PM Dhan Dhaanya Krishi Yojana", "anchors": ["PM Dhan Dhaanya", "PMDDKY", "Krishi Yojana"]},
    {"url": f"{BASE_URL}/dalhan-aatmanirbharta-mission/", "topic": "Dalhan Aatmanirbharta Mission", "anchors": ["Dalhan Aatmanirbharta", "oil seeds mission"]},
    {"url": f"{BASE_URL}/e-panta-login-app-registration/", "topic": "e-Panta Login & Registration", "anchors": ["e-Panta", "e Panta registration", "e Panta login"]},
    {"url": f"{BASE_URL}/e-panta-status-check/", "topic": "e-Panta Status Check", "anchors": ["e-Panta status", "e Panta status check"]},
    {"url": f"{BASE_URL}/e-panta-ekyc/", "topic": "e-Panta eKYC", "anchors": ["e-Panta eKYC", "e Panta eKYC"]},
    {"url": f"{BASE_URL}/e-chasa-ap/", "topic": "e-Chasa AP", "anchors": ["e-Chasa", "e Chasa AP", "Andhra crop registration"]},
    {"url": f"{BASE_URL}/maharashtra-rabi-pik-virma/", "topic": "Maharashtra Rabi Pik Vima", "anchors": ["Pik Vima Maharashtra", "Maharashtra crop insurance", "Rabi Pik Vima"]},
]

INTERNAL_LINKS = {
    "pillars": INTERNAL_LINKS_PILLARS,
    "home": {"url": f"{BASE_URL}/", "anchor": "Kisan Portal Home"},
}

# File to store URLs of posts published by this agent — used as internal links in future articles.
PUBLISHED_POSTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "published_posts.json")


def _load_published_posts():
    """Load list of agent-published post URLs (for internal linking). Returns list of {url, topic, anchors}."""
    if not os.path.exists(PUBLISHED_POSTS_FILE):
        return []
    try:
        with open(PUBLISHED_POSTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        out = []
        for entry in data:
            url = (entry.get("url") or "").strip()
            if not url or not url.startswith("http"):
                continue
            title = (entry.get("title") or "").strip() or "Article"
            slug = (entry.get("slug") or "").strip()
            anchors = [title]
            if slug:
                anchors.append(slug.replace("-", " "))
            out.append({"url": url.rstrip("/") + "/", "topic": title, "anchors": anchors})
        return out
    except Exception:
        return []


def get_internal_links_for_prompt():
    """
    Return full list of internal link options: static pillars + agent-published posts.
    Newly published posts are listed first so they are preferred as the best reference for future articles.
    """
    static_urls = {p["url"].rstrip("/") for p in INTERNAL_LINKS_PILLARS}
    published = _load_published_posts()
    # Prepend published posts (most recent first if we stored in order), avoid duplicate URLs
    combined = []
    for p in published:
        u = (p["url"] or "").rstrip("/")
        if u and u not in static_urls:
            combined.append(p)
            static_urls.add(u)
    return combined + INTERNAL_LINKS_PILLARS


def add_published_post(post_url, title, slug=""):
    """
    Register a newly published post so it can be used for internal linking in future articles.
    Call this after successfully publishing to WordPress.
    """
    if not post_url or not title:
        return
    post_url = (post_url or "").strip().rstrip("/")
    if not post_url.startswith("http"):
        return
    try:
        data = []
        if os.path.exists(PUBLISHED_POSTS_FILE):
            with open(PUBLISHED_POSTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        # Avoid duplicate URL
        existing_urls = {e.get("url", "").rstrip("/") for e in data}
        if post_url.rstrip("/") in existing_urls:
            return
        data.append({"url": post_url, "title": (title or "").strip()[:200], "slug": (slug or "").strip()[:100]})
        with open(PUBLISHED_POSTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def build_article_prompt(topic_title, source_texts, matched_keyword=""):
    """
    Build the master SEO prompt for Gemini article generation.
    """
    # Build source context block
    sources_block = ""
    for i, src in enumerate(source_texts[:5], 1):
        sources_block += f"""
--- SOURCE {i} ({src.get('source_domain', 'Unknown')}) ---
{src.get('text', '')[:2000]}
"""

    # Build internal links list: agent-published posts first (best reference), then static pillars
    pillars_for_prompt = get_internal_links_for_prompt()
    links_context = "INTERNAL LINKING (use only these exact URLs):\n"
    for p in pillars_for_prompt:
        links_context += f"  - {p['topic']}\n"
        links_context += f"    - URL: {p['url']}\n"
        links_context += f"    - Anchors: {', '.join(p['anchors'])}\n"
    
    cat_mapping_str = ", ".join(CATEGORY_MAPPING)

    prompt = f"""You are a world-class SEO strategist and Indian agriculture journalist for kisanportal.org.
Your mission is to create a "Pillar Page" or highly-relevant "Cluster Article" that ranks for E-E-A-T and provides immense value to farmers.

TASK: Write a complete, publish-ready guide about: {topic_title}
PRIMARY KEYWORD: {matched_keyword or topic_title}

─── SOURCE MATERIAL ───
{sources_block}

─── SEO & CONTENT STRATEGY ───

**1. INTERNAL LINKING (FOOLPROOF — NO 404s):**
- You MUST include exactly 2-3 internal links. Use ONLY the exact URLs in the list below.
- Copy each URL character-for-character. Do NOT invent, modify, or guess any URL. Any link not from this list will cause a 404.
- Use standard HTML: <a href="EXACT_URL">anchor text</a>. Anchor text can be from the "anchors" list or the topic name.
- Available links (includes newly published articles and verified pages on kisanportal.org; prefer the most relevant):
{links_context}
- Every internal link href in your article MUST be exactly one of the URLs listed above. No exceptions.

**2. NO SEARCH METRICS:**
- ABSOLUTELY NO mentions of "Google Trends", "spike", "search volume", or "percentages".
- This is a factual portal for farmers.

**4. HTML FORMATTING:**
- Use ## for H2 headers and ### for H3 headers.
- Use * for bulleted lists.
- Bold important agriculture terms using **term**.

─── ARTICLE STRUCTURE ───
1. TITLE: Catchy SEO title (No markdown, no quotes, max 60 chars).
2. META_DESCRIPTION: Professional summary (150 chars).
3. SLUG: lowercase-kebab-case (No markdown).
4. TAGS: CSV list of 5 tags.
5. CATEGORY: ONE exact slug from: {cat_mapping_str}. Use "news" only when the topic does not match any of the scheme categories above (e.g. general agri news, policy roundups).
6. ---CONTENT_START---
   [Intro Paragraph]
   
   ## [Main Topic H2]
   [Detailed explanation with bullet points if helpful]
   
   ## [Section H2]
   [More details]
   
   ## Frequently Asked Questions
   
   <!-- wp:kadence/accordion {{"id":"3"}} -->
   <div class="wp-block-kadence-accordion kt-accordion-id_3">
     <!-- wp:kadence/pane {{"id":"3a","title":"Question 1?"}} -->
     <div class="wp-block-kadence-pane kt-accordion-pane-3a"><div class="kt-accordion-panel"><div class="kt-accordion-panel-inner">
       <!-- wp:paragraph --><p>Answer 1.</p><!-- /wp:paragraph -->
     </div></div></div>
     <!-- /wp:kadence/pane -->
     <!-- wp:kadence/pane {{"id":"3b","title":"Question 2?"}} -->
     <div class="wp-block-kadence-pane kt-accordion-pane-3b"><div class="kt-accordion-panel"><div class="kt-accordion-panel-inner">
       <!-- wp:paragraph --><p>Answer 2.</p><!-- /wp:paragraph -->
     </div></div></div>
     <!-- /wp:kadence/pane -->
   </div>
   <!-- /wp:kadence/accordion -->
7. ---CONTENT_END---
8. ---FAQ_START---
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "Insert Question 1",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "Insert detailed answer 1."
      }}
    }}
  ]
}}
</script>
9. ---FAQ_END---
"""
    return prompt


def build_image_prompt(topic_title, article_content_snippet=""):
    """
    Build a cinematic prompt for Gemini Imagen.
    """
    prompt = f"""Cinematic editorial photography of: {topic_title}.
Setting: Lush Indian agricultural landscape, vibrant green fields, professional lighting, 8k resolution.
Main subject: A thriving crop field or a professional farmer using digital tools.
Style: Professional National Geographic style, highly detailed, photorealistic.

CRITICAL: 
- ABSOLUTELY NO TEXT, NO LOGOS, NO LETTERS.
- NO cartoon or animation.
- High quality stock photography feel.
"""

    return prompt

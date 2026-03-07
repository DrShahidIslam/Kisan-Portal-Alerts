"""
SEO Prompt Template - Master prompt used for Gemini article generation.
Enforces SEO best practices, your site's editorial style, Kadence block HTML, and internal linking.
"""
import os
import json
from detection.scheme_registry import get_category_slug_for_text

# Scheme category slugs matching kisanportal.org pillar URLs (for WordPress category assignment)
SCHEME_CATEGORY_SLUGS = [
    "pm-kisan-samman-nidhi", "pmfby", "kisan-credit-card", "kisan-vikas-patra",
    "enam-scheme", "kisan-karz-mochan-yojana", "rythu-bharosa", "soil-health-card",
    "pm-kisan-tractor-scheme", "e-crop", "pm-dhan-dhaanya-krishi-yojana",
    "dalhan-aatmanirbharta-mission-scheme", "e-panta", "pik-vima-scheme-maharashtra",
    "pm-kusum-yojana", "rkvy-scheme", "pm-fme-scheme", "pm-matsya-sampada-yojana",
    "national-livestock-mission", "midh-horticulture", "smam-mechanization",
    "national-bamboo-mission", "pm-kisan-maandhan", "nfsm-food-security",
    "ladli-behna-yojana", "kalia-yojana", "krishak-bandhu-scheme",
    "paramparagat-krishi-organic", "rashtriya-gokul-mission",
    "rajiv-gandhi-kisan-nyay", "meri-fasal-mera-byora",
]
CATEGORY_MAPPING = SCHEME_CATEGORY_SLUGS + ["news"]

KEYWORDS_TO_CATEGORY = [
    (["pm kisan tractor", "tractor scheme", "tractor subsidy"], "pm-kisan-tractor-scheme"),
    (["pm kisan maandhan", "farmer pension"], "pm-kisan-maandhan"),
    (["pm kisan", "pm-kisan", "samman nidhi", "kisan samman"], "pm-kisan-samman-nidhi"),
    (["pmfby", "fasal bima", "crop insurance", "pradhan mantri fasal bima"], "pmfby"),
    (["kisan credit card", "kcc"], "kisan-credit-card"),
    (["kisan vikas patra", "kvp"], "kisan-vikas-patra"),
    (["enam", "e-nam", "e nam", "national agricultural market"], "enam-scheme"),
    (["kisan karz mochan", "karz mochan", "farm loan waiver"], "kisan-karz-mochan-yojana"),
    (["rythu bharosa", "rythu bandhu", "rythu bharosa scheme", "ysr rythu"], "rythu-bharosa"),
    (["soil health card", "soil health"], "soil-health-card"),
    (["e-crop", "e crop", "ecrop", "crop survey"], "e-crop"),
    (["pm dhan dhaanya", "dhaanya krishi", "pm dhan", "pmddky"], "pm-dhan-dhaanya-krishi-yojana"),
    (["dalhan", "aatmanirbharta mission", "dalhan aatmanirbharta", "oilseeds mission"], "dalhan-aatmanirbharta-mission-scheme"),
    (["e-panta", "e panta", "e panta andhra", "panta andhra"], "e-panta"),
    (["pik vima", "pik vima maharashtra", "pik vima scheme"], "pik-vima-scheme-maharashtra"),
    (["pm kusum", "kusum yojana", "solar pump"], "pm-kusum-yojana"),
    (["rkvy", "rashtriya krishi vikas", "rkvy-raftaar"], "rkvy-scheme"),
    (["pm fme", "micro food", "odop", "one district one product"], "pm-fme-scheme"),
    (["pmmsy", "matsya sampada", "fisheries subsidy"], "pm-matsya-sampada-yojana"),
    (["national livestock mission", "nlm", "goat farming", "poultry scheme"], "national-livestock-mission"),
    (["midh", "horticulture mission", "horticulture subsidy"], "midh-horticulture"),
    (["smam", "farm machinery subsidy", "custom hiring", "agricultural mechanization"], "smam-mechanization"),
    (["national bamboo mission", "bamboo plantation", "nbm"], "national-bamboo-mission"),
    (["nfsm", "national food security mission", "food security"], "nfsm-food-security"),
    (["ladli behna", "ladli bahan"], "ladli-behna-yojana"),
    (["kalia yojana", "kalia odisha"], "kalia-yojana"),
    (["krishak bandhu", "krishak bandhu west bengal"], "krishak-bandhu-scheme"),
    (["paramparagat krishi", "pkvy", "organic farming mission"], "paramparagat-krishi-organic"),
    (["rashtriya gokul mission", "gokul mission", "cattle breeding"], "rashtriya-gokul-mission"),
    (["rajiv gandhi kisan nyay", "kisan nyay chhattisgarh"], "rajiv-gandhi-kisan-nyay"),
    (["meri fasal mera byora", "haryana farmer registration"], "meri-fasal-mera-byora"),
]


def get_category_for_topic(topic_title, matched_keyword=""):
    """Return WordPress category slug from master scheme registry; fallback to static mapping."""
    if not topic_title and not matched_keyword:
        return "news"

    slug = get_category_slug_for_text(topic_title, matched_keyword)
    if slug and slug != "news":
        return slug

    combined = f" {((topic_title or '') + ' ' + (matched_keyword or '')).lower()} "
    for phrases, static_slug in KEYWORDS_TO_CATEGORY:
        for phrase in phrases:
            if phrase.lower() in combined:
                return static_slug
    return "news"


BASE_URL = "https://kisanportal.org"

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

PUBLISHED_POSTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "published_posts.json")


def _load_published_posts():
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
    try:
        static_urls = {p.get("url", "").rstrip("/") for p in INTERNAL_LINKS_PILLARS if p.get("url")}
        published = _load_published_posts()
        combined = []
        for p in published:
            u = (p.get("url") or "").rstrip("/")
            if u and u not in static_urls:
                combined.append(p)
                static_urls.add(u)
        return combined + INTERNAL_LINKS_PILLARS
    except Exception:
        return list(INTERNAL_LINKS_PILLARS)


def add_published_post(post_url, title, slug="", published_at=""):
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
        existing_urls = {e.get("url", "").rstrip("/") for e in data}
        if post_url.rstrip("/") in existing_urls:
            return
        data.append({
            "url": post_url,
            "title": (title or "").strip()[:200],
            "slug": (slug or "").strip()[:100],
            "published_at": (published_at or "")[:40],
        })
        with open(PUBLISHED_POSTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def infer_content_template(topic_title, content_angle=""):
    """Map topic intent to a stable article template."""
    angle = (content_angle or "").strip().lower()
    title = (topic_title or "").strip().lower()
    combined = f"{angle} {title}"

    if any(token in combined for token in ["installment", "kist", "payment release", "payment update", "amount credited"]):
        return "installment_update"
    if any(token in combined for token in ["ekyc", "e-kyc", "e kyc", "kyc update"]):
        return "ekyc_update"
    if any(token in combined for token in ["status", "beneficiary list", "payment status", "application status", "check online"]):
        return "status_check"
    if any(token in combined for token in ["eligibility", "eligible", "how to apply", "application process", "documents required"]):
        return "eligibility_guide"
    if any(token in combined for token in ["breaking", "latest news", "announcement", "released", "deadline extended", "government decision"]):
        return "breaking_news"
    return "generic_guide"


TEMPLATE_LABELS = {
    "installment_update": "Installment Update",
    "ekyc_update": "eKYC Update",
    "status_check": "Status Check",
    "eligibility_guide": "Eligibility Guide",
    "breaking_news": "Breaking News",
    "generic_guide": "General Scheme Guide",
}


def get_template_rules(template_name, primary_keyword):
    rules = {
        "installment_update": f"""
CONTENT TEMPLATE RULES: INSTALLMENT UPDATE
- Focus on installment date, expected amount, beneficiary impact, and official status.
- The intro should say whether the installment is released, expected, delayed, or under verification.
- Add clear sections for release date, amount, eligibility for this installment, status check steps, and common payment failure reasons.
- Use headings similar to: "{primary_keyword} installment date", "who will get payment", "how to check status", and "why payment may be delayed".
- FAQ should cover installment date, amount, status check, and payment not received.
""",
        "ekyc_update": f"""
CONTENT TEMPLATE RULES: EKYC UPDATE
- Focus on whether eKYC is mandatory, deadline, who needs to do it, and what happens if it is not completed.
- Add clear sections for eKYC last date, online and offline eKYC steps, required documents, and common OTP/Aadhaar issues.
- Use headings similar to: "{primary_keyword} eKYC last date", "how to complete eKYC", and "problems farmers face during eKYC".
- FAQ should cover mandatory status, last date, OTP problems, and failed verification.
""",
        "status_check": f"""
CONTENT TEMPLATE RULES: STATUS CHECK
- Focus on the exact steps to check status, where to click, what details are needed, and what each result means.
- Add clear sections for official portal, step-by-step status check, meaning of common status messages, and next action if status is pending or rejected.
- Use headings similar to: "how to check {primary_keyword} status", "status meanings", and "what to do if status is pending".
- FAQ should cover portal link, required details, pending status, and rejected status.
""",
        "eligibility_guide": f"""
CONTENT TEMPLATE RULES: ELIGIBILITY GUIDE
- Focus on who can apply, who cannot apply, required documents, and practical steps.
- Add clear sections for eligibility criteria, ineligible cases, documents list, application process, and mistakes to avoid.
- Use headings similar to: "{primary_keyword} eligibility", "documents required", and "how to apply".
- FAQ should cover age, land or income rules, documents, and application mode.
""",
        "breaking_news": f"""
CONTENT TEMPLATE RULES: BREAKING NEWS
- Lead with the key update immediately and explain why it matters to farmers today.
- Add sections for what changed, who is affected, official source details, and what farmers should do next.
- Keep the article factual, fresh, and easy to quote in AI answers.
- Use headings similar to: "what changed", "who is affected", and "next steps for farmers".
- FAQ should cover the update summary, affected users, date, and action steps.
""",
        "generic_guide": f"""
CONTENT TEMPLATE RULES: GENERAL SCHEME GUIDE
- Explain the scheme/update in a practical way with useful sections for benefits, eligibility, steps, and latest guidance.
- Use straightforward H2s that match search intent and keep the article tightly focused on {primary_keyword}.
""",
    }
    return rules.get(template_name, rules["generic_guide"]).strip()


def get_language_rules(target_lang):
    rules = {
        "en": """
LANGUAGE-SPECIFIC SEO RULES: ENGLISH
- Write in simple Indian English that sounds helpful, not robotic.
- Put the main keyword naturally in the title, meta, first paragraph, and one H2.
- Prefer direct search phrases such as status check, installment date, last date, eligibility, and documents required.
- Keep sentences crisp so AI summaries can quote them cleanly.
""",
        "hi": """
LANGUAGE-SPECIFIC SEO RULES: HINDI
- Write in clear, natural Devanagari Hindi for farmers. Avoid heavy Hinglish.
- Keep official scheme names in their official form, but explain the update in simple Hindi.
- Put the main keyword naturally in the title, meta, first paragraph, and one H2 in Hindi usage form.
- Use familiar Hindi search phrases such as स्टेटस चेक, किस्त, लाभार्थी सूची, पात्रता, दस्तावेज, आवेदन प्रक्रिया.
- Keep wording easy enough for voice search and AI summaries.
""",
        "te": """
LANGUAGE-SPECIFIC SEO RULES: TELUGU
- Write in clear, natural Telugu script for farmers. Avoid mixing too much English unless it is an official portal or scheme term.
- Keep official scheme names accurate, but explain the update in simple Telugu.
- Put the main keyword naturally in the title, meta, first paragraph, and one H2 in Telugu usage form.
- Use familiar Telugu search phrases such as స్టేటస్ చెక్, విడత, అర్హత, దరఖాస్తు విధానం, అవసరమైన పత్రాలు.
- Keep the language conversational, trustworthy, and easy for summaries and voice-style answers.
""",
    }
    return rules.get(target_lang, rules["en"]).strip()


def build_article_prompt(topic_title, source_texts, matched_keyword="", target_lang="en", content_angle=""):
    """Build the master SEO prompt for Gemini article generation."""
    sources_block = ""
    for i, src in enumerate(source_texts[:5], 1):
        sources_block += f"""
--- SOURCE {i} ({src.get('source_domain', 'Unknown')}) ---
{src.get('text', '')[:2000]}
"""

    pillars_for_prompt = get_internal_links_for_prompt()
    links_context = "ALLOWED INTERNAL LINKS:\n"
    for p in pillars_for_prompt:
        links_context += f"  - Title: {p['topic']}\n"
        links_context += f"    - EXACT URL TO USE: {p['url']}\n"
        links_context += f"    - Allowed Anchors: {', '.join(p['anchors'])}\n"

    cat_mapping_str = ", ".join(CATEGORY_MAPPING)
    primary_keyword = (matched_keyword or topic_title).strip()

    lang_labels = {"en": "English", "hi": "Hindi", "te": "Telugu"}
    target_lang = (target_lang or "en").lower()
    if target_lang not in lang_labels:
        target_lang = "en"

    template_name = infer_content_template(topic_title, content_angle)
    template_label = TEMPLATE_LABELS.get(template_name, "General Scheme Guide")
    template_rules = get_template_rules(template_name, primary_keyword)
    language_rules = get_language_rules(target_lang)

    prompt = f"""You are a world-class SEO strategist and Indian agriculture journalist for kisanportal.org.
Your mission is to create a highly useful article that ranks in search, answers questions directly, and is suitable for AI overviews, answer engines, and generative search experiences.

TASK: Write a complete, publish-ready guide about: {topic_title}
PRIMARY KEYWORD / FOCUS KEYWORD: {primary_keyword}
TARGET LANGUAGE: {lang_labels[target_lang]} ({target_lang})
CONTENT TEMPLATE: {template_label}

SOURCE MATERIAL
{sources_block}

SEO / AEO / GEO STRATEGY

1. INTERNAL LINKING (STRICT)
- You MUST include exactly 2 to 3 internal links inside the body text.
- Use ONLY the exact URLs from the allowed internal links list below.
- Never invent, guess, or modify a URL.
- Format: <a href="EXACT_URL_FROM_LIST">anchor text</a>.
- {links_context}

2. LANGUAGE REQUIREMENT
- The full article content must be in TARGET LANGUAGE only: {lang_labels[target_lang]} ({target_lang}).
- Do not mix languages except official scheme names.
- Set LANG field exactly to: {target_lang}.
- {language_rules}

3. SEO REQUIREMENTS
- PRIMARY KEYWORD / FOCUS KEYWORD is: "{primary_keyword}".
- The TITLE must contain the PRIMARY KEYWORD exactly or the closest exact scheme phrase.
- The META_DESCRIPTION must contain the PRIMARY KEYWORD naturally and include a strong click hook such as latest update, status, installment, last date, amount, eligibility, apply process, documents, or payment update.
- The first 120 words must include the PRIMARY KEYWORD naturally.
- The first paragraph must hook the reader by explaining what changed, why it matters now, and what the farmer should do next.
- Use the PRIMARY KEYWORD naturally in at least one H2 and in the closing guidance.
- Keep the article tightly focused on the PRIMARY KEYWORD. Do not drift into broad agriculture commentary.

4. AEO / GEO REQUIREMENTS
- Answer the main search query early, clearly, and directly in 2 to 4 sentences near the top.
- Write in a way that can be quoted by AI overviews and answer engines: clear facts, clean phrasing, and no fluff.
- Add question-based subheadings where useful, such as eligibility, status check, installment date, eKYC, documents, amount, or how to apply.
- Use short paragraphs, bullets, and step-based explanations so the article is easy to scan.
- If the topic is a fresh update, clearly mark what is new and what remains unchanged.
- The article structure must match the selected content template.
- {template_rules}

5. DO NOT DO THIS
- Do not mention Google Trends, search volume, spike score, or keyword metrics.
- Do not write filler introductions.
- Do not write generic motivational text.
- Do not invent facts beyond the source material.
- Do not stuff keywords unnaturally.

6. HTML FORMATTING
- Use ## for H2 headers and ### for H3 headers.
- Use * for bulleted lists.
- Bold important agriculture terms using **term**.

ARTICLE STRUCTURE
CRITICAL: TITLE is the article H1 and must be a real search-friendly headline.
CRITICAL: META_DESCRIPTION should be attractive, factual, and click-worthy.
CRITICAL: The intro must say what changed, who is affected, and what action the reader should take.
CRITICAL: The article must feel helpful for search users first, then strong enough for AI summaries.

1. TITLE: Maximum 60 characters. Must contain the PRIMARY KEYWORD. No markdown or quotes.
2. META_DESCRIPTION: 140 to 155 characters. Must contain the PRIMARY KEYWORD naturally and a strong hook.
3. SLUG: 3 to 6 words, lowercase, hyphens only, max 50 chars.
4. TAGS: Exactly 5 tags, comma-separated.
5. CATEGORY: ONE slug from: {cat_mapping_str}. Use "news" only if topic does not match a scheme.
6. LANG: The 2-letter ISO language code of this article's text. Use exactly {target_lang}.
7. ---CONTENT_START---
- Start with a short direct-answer intro of 2 to 4 sentences.
- Follow with well-structured H2/H3 sections that match the selected template.
- Add at least 2 bullet lists where useful.
- Include a short FAQ section at the end with 4 to 6 real questions farmers may ask.
- Keep the tone practical, trustworthy, and easy to understand.
8. ---CONTENT_END---
9. ---FAQ_START---
REQUIRED: Output FAQPage JSON-LD schema with 3 to 4 real questions and real answers.
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{ "@type": "Question", "name": "What is [write actual question here]?", "acceptedAnswer": {{ "@type": "Answer", "text": "[Write 2 to 4 sentence answer here.]" }} }},
    {{ "@type": "Question", "name": "How do I [write actual question]?", "acceptedAnswer": {{ "@type": "Answer", "text": "[Write answer.]" }} }},
    {{ "@type": "Question", "name": "[Third actual question]?", "acceptedAnswer": {{ "@type": "Answer", "text": "[Write answer.]" }} }}
  ]
}}
</script>
10. ---FAQ_END---

Return ONLY this exact structure:
TITLE: ...
META_DESCRIPTION: ...
SLUG: ...
TAGS: tag1, tag2, tag3, tag4, tag5
CATEGORY: ...
LANG: {target_lang}
---CONTENT_START---
[full article in markdown]
---CONTENT_END---
---FAQ_START---
[FAQPage JSON-LD]
---FAQ_END---
"""
    return prompt

def build_image_prompt(topic_title, article_content_snippet=""):
    """Build a clear, editorial-style prompt for AI image generation."""
    prompt = f"""Professional editorial photograph for an Indian agriculture news article. Topic: {topic_title}.
Scene: Lush Indian farm landscape, green fields or crops, natural daylight, photorealistic.
Style: High-quality stock photo, National Geographic style, no people in frame (or distant farmer in field).
Rules: No text, no logos, no watermarks, no cartoons. Landscape orientation, 16:9 suitable for featured image."""

    return prompt



"""
Quality gate checks before publishing articles.
"""
import re
from writer.seo_prompt import get_required_sections


GENERIC_KEYWORDS = {
    "agriculture", "farming", "farmers", "scheme", "schemes", "news", "india", "kisan"
}

TREND_TALK_PATTERNS = (
    r"google trends",
    r"trending on google",
    r"rising search",
    r"search volume",
    r"searched a lot",
    r"people are searching",
    r"popular in searches",
)


def _normalize_text(value):
    value = (value or "").lower()
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"[^a-z0-9\u0900-\u097f\u0c00-\u0c7f\s]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _keyword_density(text, keyword):
    text = _normalize_text(text)
    keyword = _normalize_text(keyword)
    if not text or not keyword:
        return 0.0
    words = text.split()
    kw_words = keyword.split()
    if not words or not kw_words:
        return 0.0
    joined = " ".join(words)
    occurrences = len(re.findall(rf'(?<!\w){re.escape(keyword)}(?!\w)', joined))
    return (occurrences * len(kw_words) / max(len(words), 1)) * 100


def validate_article_for_publish(article, min_words=700):
    issues = []
    warnings = []

    article = article or {}
    title = article.get("title", "").strip()
    seo_title = (article.get("seo_title") or title).strip()
    meta = article.get("meta_description", "").strip()
    image_alt = (article.get("image_alt") or "").strip()
    full_content = article.get("full_content") or article.get("content_html") or ""
    content_text = re.sub(r"<[^>]+>", " ", full_content)
    words = [w for w in content_text.split() if w.strip()]
    intro_text = " ".join(words[:120])
    focus_keyword = (article.get("focus_keyword") or article.get("matched_keyword") or article.get("title") or "").strip()
    category = (article.get("category") or "").strip().lower()
    source_quality = article.get("source_quality") or {}
    source_count = int(source_quality.get("source_count") or 0)
    official_count = int(source_quality.get("official_count") or 0)
    source_domains = source_quality.get("source_domains") or []
    keyword_plan = article.get("keyword_plan") or {}
    secondary_keywords = article.get("secondary_keywords") or keyword_plan.get("secondary") or []
    supporting_keywords = article.get("supporting_keywords") or keyword_plan.get("supporting") or []
    template_name = article.get("template_name") or "generic_guide"

    normalized_keyword = _normalize_text(focus_keyword)
    normalized_title = _normalize_text(title)
    normalized_seo_title = _normalize_text(seo_title)
    normalized_meta = _normalize_text(meta)
    normalized_intro = _normalize_text(intro_text)
    normalized_alt = _normalize_text(image_alt)
    normalized_content = _normalize_text(content_text)

    if len(title) < 35:
        warnings.append("Title is short; improve clarity for search CTR")
    if len(title) > 65:
        issues.append("Title is too long (recommended <= 65 characters)")

    if len(seo_title) < 45:
        warnings.append("SEO title is short; target 50-65 characters")
    if len(seo_title) > 70:
        issues.append("SEO title is too long (recommended <= 70 characters)")

    if len(meta) < 140:
        warnings.append("Meta description is short; target 140-155 characters")
    if len(meta) > 165:
        issues.append("Meta description is too long (recommended <= 165 characters)")
    if meta and not re.search(r'[.!?]$' , meta):
        warnings.append("Meta description may be cut off or not end cleanly")

    if len(words) < min_words:
        issues.append(f"Article is thin ({len(words)} words); needs at least {min_words} words")

    internal_links = len(re.findall(r'<a\s+[^>]*href="https://kisanportal\.org/', full_content, flags=re.IGNORECASE))
    if internal_links < 2:
        issues.append("Internal linking is weak (needs at least 2 internal links)")

    h2_count = len(re.findall(r"<h2\b", full_content, flags=re.IGNORECASE))
    if h2_count < 3:
        issues.append("Content structure is weak (needs at least 3 H2 sections)")

    bullet_count = len(re.findall(r"<(ul|ol)\b", full_content, flags=re.IGNORECASE))
    if bullet_count < 2:
        warnings.append("Scannable structure is weak; add more bullet or step lists")

    if len(intro_text) < 260:
        warnings.append("Intro is weak; add a clearer hook and early answer")

    if normalized_keyword and len(normalized_keyword) >= 4:
        if normalized_keyword not in normalized_title:
            issues.append("Focus keyword is missing from title")
        if normalized_keyword not in normalized_seo_title:
            issues.append("Focus keyword is missing from SEO title")
        if normalized_keyword not in normalized_meta:
            warnings.append("Focus keyword is missing from meta description")
        if normalized_keyword not in normalized_intro:
            issues.append("Focus keyword is missing from the first 120 words")
        if not re.search(rf'<h2[^>]*>[^<]*{re.escape(focus_keyword)}[^<]*</h2>', full_content, flags=re.IGNORECASE):
            warnings.append("Focus keyword is missing from H2 headings")

    if normalized_keyword in GENERIC_KEYWORDS or len(normalized_keyword.split()) < 2:
        issues.append("Focus keyword is too broad; use a stronger long-tail keyword")

    density = _keyword_density(normalized_content, normalized_keyword)
    if density and density < 0.4:
        warnings.append(f"Focus keyword density is low ({density:.2f}%)")
    if density > 2.5:
        issues.append(f"Focus keyword density is too high ({density:.2f}%); looks stuffed")

    if not image_alt:
        issues.append("Featured image alt text is missing")
    elif normalized_keyword and normalized_keyword not in normalized_alt:
        warnings.append("Featured image alt text does not include the focus keyword")
    elif _normalize_text(title) == normalized_alt:
        warnings.append("Featured image alt text is identical to the title; make it more descriptive")

    if category == "news" and any(token in normalized_keyword for token in ["status", "eligibility", "apply", "documents", "ekyc", "installment"]):
        warnings.append("This looks like a scheme-intent article but is categorized as news")

    is_news_like = (
        category == "news" or
        any(token in normalized_keyword for token in ["latest update", "news", "announcement", "released", "deadline"])
    )
    if source_count < 2:
        if is_news_like:
            issues.append("Source coverage is too thin for a news-style article; require at least 2 distinct source domains")
        else:
            warnings.append("Source coverage is thin; enrich with more supporting sources if available")
    if is_news_like and official_count < 1:
        issues.append("News-style article is missing an official source")

    if re.search(r'what this means for farmers|kisan portal analysis', normalized_content) is None and any(token in normalized_keyword for token in ["latest update", "news", "announcement"]):
        warnings.append("News article is missing a value-add analysis section")

    if re.search(r"official source|official website|official notification|official portal", normalized_content) is None and official_count > 0:
        warnings.append("Article uses official sources but does not clearly surface that context for readers")

    trend_talk = any(re.search(pattern, normalized_content) for pattern in TREND_TALK_PATTERNS)
    if trend_talk:
        issues.append("Article mentions search/trend metrics instead of focusing on user value")

    if len(secondary_keywords) < 3:
        warnings.append("Keyword plan is weak; include at least 3 strong secondary keywords")
    else:
        covered_secondary = sum(1 for kw in secondary_keywords if _normalize_text(kw) in normalized_content)
        if covered_secondary < min(3, len(secondary_keywords)):
            warnings.append("Secondary keyword coverage is weak across the article body")

    if len(supporting_keywords) < 3:
        warnings.append("Supporting keyword plan is thin; broaden related subtopics")
    else:
        covered_supporting = sum(1 for kw in supporting_keywords if _normalize_text(kw) in normalized_content)
        if covered_supporting < min(2, len(supporting_keywords)):
            warnings.append("Supporting subtopics are not covered deeply enough in the article")

    required_sections = get_required_sections(template_name, focus_keyword or article.get("title", ""))
    covered_sections = 0
    for section in required_sections:
        section_tokens = [tok for tok in _normalize_text(section).split() if len(tok) > 2]
        if not section_tokens:
            continue
        if sum(1 for tok in section_tokens if tok in normalized_content) >= max(1, min(2, len(section_tokens))):
            covered_sections += 1
    if covered_sections < max(3, len(required_sections) - 1):
        warnings.append("Article structure does not fully cover the required intent blueprint")

    if "FAQPage" not in full_content:
        warnings.append("FAQ schema missing; rich result chance reduced")

    if not re.search(r"frequently asked questions|faq", content_text, flags=re.IGNORECASE):
        warnings.append("FAQ section heading is missing")

    return {
        "ok": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "word_count": len(words),
        "internal_links": internal_links,
        "h2_count": h2_count,
        "focus_keyword": focus_keyword,
        "keyword_density": round(density, 2),
        "seo_title": seo_title,
        "image_alt": image_alt,
        "source_count": source_count,
        "official_source_count": official_count,
        "secondary_keyword_count": len(secondary_keywords),
        "supporting_keyword_count": len(supporting_keywords),
        "template_name": template_name,
        "blueprint_sections_covered": covered_sections,
    }

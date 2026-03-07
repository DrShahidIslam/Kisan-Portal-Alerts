"""
Quality gate checks before publishing articles.
"""
import re


def validate_article_for_publish(article, min_words=700):
    issues = []
    warnings = []

    title = (article or {}).get("title", "").strip()
    meta = (article or {}).get("meta_description", "").strip()
    full_content = (article or {}).get("full_content") or (article or {}).get("content_html") or ""
    content_text = re.sub(r"<[^>]+>", " ", full_content)
    words = [w for w in content_text.split() if w.strip()]

    if len(title) < 35:
        warnings.append("Title is short; improve clarity for search CTR")
    if len(title) > 65:
        issues.append("Title is too long (recommended <= 65 characters)")

    if len(meta) < 120:
        warnings.append("Meta description is short; target 120-155 characters")
    if len(meta) > 165:
        issues.append("Meta description is too long (recommended <= 165 characters)")

    if len(words) < min_words:
        issues.append(f"Article is thin ({len(words)} words); needs at least {min_words} words")

    internal_links = len(re.findall(r"<a\s+[^>]*href=\"https://kisanportal\.org/", full_content, flags=re.IGNORECASE))
    if internal_links < 2:
        issues.append("Internal linking is weak (needs at least 2 internal links)")

    if "FAQPage" not in full_content:
        warnings.append("FAQ schema missing; rich result chance reduced")

    return {
        "ok": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "word_count": len(words),
        "internal_links": internal_links,
    }

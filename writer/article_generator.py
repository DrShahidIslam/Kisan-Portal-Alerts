"""
Article Generator - Uses Gemini to write SEO-optimized articles
from source material gathered by the source fetcher.
"""
import logging
import re

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from writer.source_fetcher import fetch_multiple_sources
from writer.seo_prompt import build_article_prompt, get_category_for_topic, build_image_alt_text
from detection.language_router import normalize_lang
from gemini_client import generate_content_with_fallback

logger = logging.getLogger(__name__)


OFFICIAL_SOURCE_SUFFIXES = (".gov.in", ".nic.in", ".gov", ".edu", ".ac.in")


def _is_official_domain(domain):
    domain = (domain or "").lower().strip()
    return bool(domain) and domain.endswith(OFFICIAL_SOURCE_SUFFIXES)


def _summarize_source_quality(source_texts):
    domains = []
    official_domains = []
    for src in source_texts or []:
        domain = (src.get("source_domain") or "").strip().lower()
        if not domain:
            continue
        if domain not in domains:
            domains.append(domain)
        if (src.get("is_official") or _is_official_domain(domain)) and domain not in official_domains:
            official_domains.append(domain)
    return {
        "source_domains": domains,
        "official_domains": official_domains,
        "source_count": len(domains),
        "official_count": len(official_domains),
    }


def _derive_focus_keyword(topic_title, matched_keyword="", content_angle=""):
    """Turn a broad scheme/topic name into a stronger long-tail focus keyword."""
    topic_title = (topic_title or "").strip()
    matched_keyword = (matched_keyword or "").strip()
    content_angle = (content_angle or "").strip().lower()
    base = matched_keyword or topic_title
    title_lower = topic_title.lower()

    if any(token in title_lower or token in content_angle for token in ["status", "beneficiary"]):
        return f"{base} status check 2026".strip()
    if any(token in title_lower or token in content_angle for token in ["ekyc", "e-kyc", "aadhaar"]):
        return f"{base} eKYC update 2026".strip()
    if any(token in title_lower or token in content_angle for token in ["installment", "kist", "payment"]):
        return f"{base} installment date 2026".strip()
    if any(token in title_lower or token in content_angle for token in ["eligibility", "eligible"]):
        return f"{base} eligibility 2026".strip()
    if any(token in title_lower or token in content_angle for token in ["apply", "registration"]):
        return f"{base} apply online 2026".strip()
    if any(token in title_lower or token in content_angle for token in ["documents", "document"]):
        return f"{base} required documents 2026".strip()
    if any(token in title_lower or token in content_angle for token in ["rejected", "failed", "error"]):
        return f"{base} rejected payment fix".strip()
    if any(token in title_lower or token in content_angle for token in ["news", "update", "announcement", "released"]):
        return f"{base} latest update 2026".strip()
    return (topic_title or base).strip()


def _search_news_for_trend(keyword):
    """Search Google News RSS and NewsAPI to find background context for a trending keyword."""
    urls = []

    try:
        import feedparser
        import urllib.parse
        encoded_kw = urllib.parse.quote(keyword)
        rss_url = f"https://news.google.com/rss/search?q={encoded_kw}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:3]:
            if entry.link and entry.link not in urls:
                urls.append(entry.link)
    except Exception as e:
        logger.warning(f"Failed to fetch Google News RSS for trend: {e}")

    try:
        from newsapi import NewsApiClient
        from datetime import datetime, timedelta
        newsapi = NewsApiClient(api_key=config.NEWS_API_KEY)
        from_date = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")
        results = newsapi.get_everything(
            q=keyword,
            language="en",
            sort_by="relevancy",
            from_param=from_date,
            page_size=5,
        )
        if results.get("status") == "ok":
            for article in results.get("articles", [])[:3]:
                url = article.get("url")
                if url and url not in urls:
                    urls.append(url)
    except Exception as e:
        logger.warning(f"Failed to fetch NewsAPI for trend: {e}")

    return urls


def generate_article(topic, source_urls=None):
    """Generate a complete SEO-optimized article for a trending topic."""
    logger.info(f"Generating article for: {topic.get('topic', 'Unknown')}")

    if source_urls is None:
        source_urls = []
        for story in topic.get("stories", []):
            url = story.get("url", "")
            if url and url.startswith("http"):
                source_urls.append(url)

    top_url = topic.get("top_url", "")
    if top_url and top_url not in source_urls:
        source_urls.insert(0, top_url)

    is_pure_trend = True if not source_urls else all("trends.google.com" in url for url in source_urls)
    if is_pure_trend:
        keyword = topic.get("matched_keyword") or topic.get("topic", "").replace("Rising search:", "").strip()
        logger.info(f"Pure trend detected. Searching active news for: '{keyword}'")
        found_urls = _search_news_for_trend(keyword)
        if found_urls:
            source_urls.extend(found_urls)
            logger.info(f"Found {len(found_urls)} background articles for context.")

    logger.info(f"Fetching {len(source_urls)} source URLs...")
    source_texts = fetch_multiple_sources(source_urls, max_sources=8)

    if not source_texts:
        logger.warning("No source material could be extracted. Using topic summary only.")
        source_texts = [{
            "title": topic.get("topic", ""),
            "text": "\n".join(s.get("summary", "") for s in topic.get("stories", [])),
            "source_domain": "aggregated_summaries",
            "url": "",
            "is_official": False,
        }]

    source_quality = _summarize_source_quality(source_texts)
    content_angle = (topic.get("content_angle") or "").strip().lower()
    topic_title_lower = (topic.get("topic") or "").strip().lower()
    is_news_like = any(token in f"{content_angle} {topic_title_lower}" for token in [
        "breaking", "news", "announcement", "released", "latest update", "deadline"
    ])
    is_summary_only = (
        len(source_texts) == 1 and
        source_texts[0].get("source_domain") == "aggregated_summaries" and
        not source_texts[0].get("url")
    )
    if is_summary_only:
        logger.warning("Skipping generation because only aggregated summary text is available.")
        return None
    if source_quality["source_count"] < 2:
        logger.warning("Skipping generation because fewer than 2 distinct source domains were available.")
        return None
    if is_news_like and source_quality["official_count"] < 1:
        logger.warning("Skipping generation for news-like topic because no official source was found.")
        return None

    target_lang = normalize_lang(topic.get("lang", "en"))

    try:
        prompt = build_article_prompt(
            topic_title=topic.get("topic", "Agriculture News Update"),
            source_texts=source_texts,
            matched_keyword=topic.get("matched_keyword", ""),
            target_lang=target_lang,
            content_angle=topic.get("content_angle", ""),
        )
    except Exception as e:
        logger.error(f"Failed to build prompt: {e}")
        return None

    try:
        logger.info("Calling Gemini API...")
        response = generate_content_with_fallback(model=config.GEMINI_MODEL, contents=prompt)
        raw_output = (getattr(response, "text", None) or "").strip()
        if not raw_output:
            logger.error("Gemini returned empty or blocked content (no text).")
            return None
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return None

    article = _parse_article_output(
        raw_output,
        matched_keyword=topic.get("matched_keyword", ""),
        topic_title=topic.get("topic", ""),
        content_angle=topic.get("content_angle", ""),
    )

    if not article:
        logger.error("Failed to parse Gemini output.")
        return None

    if len(article.get("content", "") or "") < 100:
        logger.warning("Parsed content too short; treating as parse failure.")
        return None

    article["sources_used"] = [s.get("source_domain", "") for s in source_texts]
    article["source_quality"] = source_quality
    article["has_official_source"] = source_quality["official_count"] > 0
    article["word_count"] = len(article.get("content_html", "").split())
    article["category"] = get_category_for_topic(topic.get("topic", ""), topic.get("matched_keyword", ""))
    article["focus_keyword"] = (
        article.get("focus_keyword")
        or _derive_focus_keyword(topic.get("topic", ""), topic.get("matched_keyword", ""), topic.get("content_angle", ""))
    )
    article["matched_keyword"] = article.get("focus_keyword")
    article["seo_title"] = article.get("seo_title") or article.get("title", "")
    article["image_alt"] = article.get("image_alt") or build_image_alt_text(
        topic.get("topic", ""), article.get("focus_keyword", ""), article.get("category", "")
    )
    article["lang"] = target_lang if target_lang in ("en", "hi", "te") else article.get("lang", "en")
    logger.info(f"Article generated: '{article['title']}' (category: {article['category']})")
    return article


def _parse_article_output(raw_text, matched_keyword="", topic_title="", content_angle=""):
    """Parse the structured output from Gemini into article components."""
    try:
        result = {}

        def clean_meta(val):
            if not val:
                return ""
            return re.sub(r'[*_#`"]', '', val).strip()

        def match_field(pattern):
            m = re.search(pattern, raw_text, re.IGNORECASE | re.DOTALL)
            return clean_meta(m.group(1)) if m else ""

        MAX_TITLE_LEN = 60
        result["title"] = match_field(r'(?:1\.|TITLE:)\s*(.+?)(?:\n|2\.|SEO_TITLE:|3\.|META_DESCRIPTION:|---|$)')
        if not result["title"]:
            lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
            result["title"] = clean_meta(lines[0]) if lines else "Agriculture Update"
        if len(result["title"]) > MAX_TITLE_LEN:
            result["title"] = result["title"][:MAX_TITLE_LEN].rsplit(" ", 1)[0] or result["title"][:MAX_TITLE_LEN]

        result["seo_title"] = match_field(r'(?:2\.|SEO_TITLE:)\s*(.+?)(?:\n|3\.|META_DESCRIPTION:|4\.|FOCUS_KEYWORD:|---|$)') or result["title"]
        result["meta_description"] = match_field(r'(?:3\.|META_DESCRIPTION:)\s*(.+?)(?:\n|4\.|FOCUS_KEYWORD:|5\.|IMAGE_ALT:|6\.|SLUG:|---|$)')
        result["focus_keyword"] = match_field(r'(?:4\.|FOCUS_KEYWORD:)\s*(.+?)(?:\n|5\.|IMAGE_ALT:|6\.|SLUG:|---|$)')
        result["image_alt"] = match_field(r'(?:5\.|IMAGE_ALT:)\s*(.+?)(?:\n|6\.|SLUG:|7\.|TAGS:|---|$)')

        MAX_SLUG_LEN = 50
        slug_match = re.search(r'(?:6\.|SLUG:)\s*([a-z0-9-]+)', raw_text, re.IGNORECASE)
        if slug_match:
            result["slug"] = re.sub(r'-+', '-', clean_meta(slug_match.group(1).lower()).strip('-'))
        else:
            result["slug"] = re.sub(r'[^a-z0-9]+', '-', result["title"].lower()).strip('-')
        result["slug"] = result["slug"][:MAX_SLUG_LEN].rstrip('-')

        tags_match = re.search(r'(?:7\.|TAGS:)\s*(.+?)(?:\n|8\.|CATEGORY:|---|$)', raw_text, re.IGNORECASE | re.DOTALL)
        result["tags"] = [clean_meta(t) for t in tags_match.group(1).split(',') if t.strip()] if tags_match else ["agriculture", "india"]

        category_match = re.search(r'(?:8\.|CATEGORY:)\s*([a-z0-9-]+)', raw_text, re.IGNORECASE)
        result["category"] = clean_meta(category_match.group(1).lower()) if category_match else "news"

        final_kw = matched_keyword if matched_keyword else clean_meta(topic_title)
        if not result["focus_keyword"]:
            result["focus_keyword"] = _derive_focus_keyword(topic_title, final_kw, content_angle)
        result["matched_keyword"] = result["focus_keyword"]

        lang_match = re.search(r'(?:9\.|LANG:)\s*([a-z]{2})', raw_text, re.IGNORECASE)
        result["lang"] = clean_meta(lang_match.group(1).lower()) if lang_match else "en"

        content_block_match = re.search(r'---CONTENT_START---(.*?)---CONTENT_END---', raw_text, re.DOTALL)
        if content_block_match:
            result["content"] = content_block_match.group(1).strip()
        else:
            fuzzy_parts = re.split(r'(?:10\.|---CONTENT_START---).*?\n', raw_text, maxsplit=1, flags=re.IGNORECASE | re.DOTALL)
            if len(fuzzy_parts) > 1:
                result["content"] = fuzzy_parts[1].split("---CONTENT_END---")[0].strip()
            else:
                lines = raw_text.split("\n")
                result["content"] = "\n".join(lines[9:]).strip() if len(lines) > 9 else raw_text
        if not result["content"]:
            result["content"] = raw_text

        md = (result.get("meta_description") or result["title"]).strip()[:155]
        if len(md) < 100 and result["content"]:
            first = result["content"].split(".")[0].strip()[:120]
            if first:
                md = (md + " " + first).strip()[:155]
        result["meta_description"] = md or result["title"][:155]
        result["seo_title"] = (result.get("seo_title") or result["title"])[:65].strip()
        if not result.get("image_alt"):
            result["image_alt"] = build_image_alt_text(topic_title, result.get("focus_keyword", ""), result.get("category", ""))

        result["faq_html"] = ""
        faq_block = re.search(r'---FAQ_START---(.*?)---FAQ_END---', raw_text, re.DOTALL)
        if faq_block:
            result["faq_html"] = re.sub(r'<!--.*?-->', '', faq_block.group(1), flags=re.DOTALL).strip()
        if not result["faq_html"]:
            schema_match = re.search(r'<script\s+type=["\']application/ld\+json["\'].*?FAQPage.*?</script>', raw_text, re.DOTALL | re.IGNORECASE)
            if schema_match:
                result["faq_html"] = schema_match.group(0).strip()
        if result["faq_html"] and not re.search(r'<script\b', result["faq_html"], re.IGNORECASE):
            result["faq_html"] = '<script type="application/ld+json">\n' + result["faq_html"] + '\n</script>'

        # Remove markdown code blocks that Gemini might wrap around JSON
        result["faq_html"] = re.sub(r'^```[a-zA-Z]*\s*', '', result["faq_html"], flags=re.MULTILINE)
        result["faq_html"] = re.sub(r'```\s*$', '', result["faq_html"], flags=re.MULTILINE).strip()

        placeholder_phrases = (
            "Insert Question",
            "Insert detailed answer",
            "First real question in full",
            "Second real question?",
            "Third real question?",
            "[write actual question]",
            "[Write 2 to 4 sentence answer",
            "[Write answer.]",
        )
        if result["faq_html"] and any(p in result["faq_html"] for p in placeholder_phrases):
            result["faq_html"] = ""
        if result["faq_html"] and '"name":' in result["faq_html"]:
            if not re.search(r'"name":\s*"[^"]*\?"', result["faq_html"]):
                result["faq_html"] = ""

        import markdown
        result["content_html"] = markdown.markdown(result["content"], extensions=['nl2br', 'sane_lists'])

        def _build_faq_from_schema(faq_html_str):
            import json as _json
            script_body = re.search(r'<script[^>]*>([\s\S]*?)</script>', faq_html_str, re.IGNORECASE)
            if not script_body:
                return None
            raw_json_str = script_body.group(1).strip()
            # Clean up markdown code blocks if present
            raw_json_str = re.sub(r'^```[a-zA-Z]*\s*', '', raw_json_str, flags=re.MULTILINE)
            raw_json_str = re.sub(r'```\s*$', '', raw_json_str, flags=re.MULTILINE).strip()
            data = _json.loads(raw_json_str)
            entities = data.get("mainEntity") or []
            qa_list = []
            for ent in entities:
                if not isinstance(ent, dict):
                    continue
                name = (ent.get("name") or "").strip()
                ans = ent.get("acceptedAnswer") or {}
                text = (ans.get("text") if isinstance(ans, dict) else "") or ""
                if name and "?" in name:
                    qa_list.append((name, text))
            if not qa_list:
                return None
            parts = []
            for q, a in qa_list:
                q_esc = (q or "").replace("<", "&lt;").replace(">", "&gt;").strip()
                a_esc = (a or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                parts.append(f'<!-- wp:heading {{"level":3}} -->\n<h3>{q_esc}</h3>\n<!-- /wp:heading -->')
                parts.append(f'<!-- wp:paragraph -->\n<p>{a_esc}</p>\n<!-- /wp:paragraph -->')
            return "\n".join(parts)

        has_visible_faq = bool(re.search(r'<h[234][^>]*>[^<]*\?[^<]*</h[234]>', result["content_html"]))
        if not has_visible_faq and result.get("faq_html") and "FAQPage" in result["faq_html"]:
            try:
                faq_list_html = _build_faq_from_schema(result["faq_html"])
                if faq_list_html:
                    faq_heading_match = re.search(r'(<h2[^>]*>.*?Frequently Asked Questions.*?</h2>)', result["content_html"], re.IGNORECASE | re.DOTALL)
                    if faq_heading_match:
                        new_section = faq_heading_match.group(0) + "\n\n" + faq_list_html
                        result["content_html"] = result["content_html"].replace(faq_heading_match.group(0), new_section, 1)
                    else:
                        result["content_html"] += "\n\n<!-- wp:heading {\"level\":2} -->\n<h2>Frequently Asked Questions</h2>\n<!-- /wp:heading -->\n\n" + faq_list_html
            except Exception as faq_e:
                logger.debug(f"FAQ list build failed: {faq_e}")

        wrapped_body = f'<div class="kisan-article-body entry-content-wrap" style="padding: 1.5rem;">\n{result["content_html"]}\n</div>'
        faq_block_output = ""
        if result["faq_html"]:
            hidden_schema = (
                '<div class="kisan-faq-schema" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);clip-path:inset(50%);white-space:nowrap;" aria-hidden="true">'
                + result["faq_html"]
                + '</div>'
            )
            faq_block_output = "\n\n<!-- wp:html -->\n" + hidden_schema + "\n<!-- /wp:html -->"

        result["faq_schema"] = result.get("faq_html", "")
        result["full_content"] = wrapped_body + faq_block_output
        return result
    except Exception:
        logger.exception("Parse error")
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_topic = {
        "topic": "PM Kisan Beneficiary Status 2026",
        "matched_keyword": "pm-kisan-samman-nidhi",
        "stories": [{"summary": "Latest updates on PM Kisan scheme for farmers."}],
    }
    article = generate_article(test_topic)
    if article:
        print(f"TITLE: {article['title']}")
        print(f"CONTENT PREVIEW: {article['full_content'][:500]}...")

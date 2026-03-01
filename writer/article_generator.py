"""
Article Generator — Uses Gemini to write SEO-optimized articles
from source material gathered by the source fetcher.
"""
import logging
import re
import time

from google import genai

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from writer.source_fetcher import fetch_multiple_sources
from writer.seo_prompt import build_article_prompt
from gemini_client import generate_content_with_fallback

logger = logging.getLogger(__name__)

# Gemini retry handled by gemini_client


def _search_news_for_trend(keyword):
    """Search Google News RSS and NewsAPI to find background context for a trending keyword."""
    urls = []
    
    # 1. Google News RSS
    try:
        import feedparser
        import urllib.parse
        encoded_kw = urllib.parse.quote(keyword)
        rss_url = f"https://news.google.com/rss/search?q={encoded_kw}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:3]:
            if entry.link and entry.link not in urls:
                urls.append(entry.link)
    except Exception as e:
        logger.warning(f"Failed to fetch Google News RSS for trend: {e}")

    # 2. NewsAPI
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
            page_size=5
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
    """
    Generate a complete SEO-optimized article for a trending topic.
    """
    logger.info(f"📝 Generating article for: {topic.get('topic', 'Unknown')}")

    # ── Step 1: Gather source material ────────────────────────────
    if source_urls is None:
        source_urls = []
        for story in topic.get("stories", []):
            url = story.get("url", "")
            if url and url.startswith("http"):
                source_urls.append(url)

    # Also add the top_url if available
    top_url = topic.get("top_url", "")
    if top_url and top_url not in source_urls:
        source_urls.insert(0, top_url)

    # Check if this is a pure trend alert
    is_pure_trend = True
    if not source_urls:
        is_pure_trend = True
    else:
        for url in source_urls:
            if "trends.google.com" not in url:
                is_pure_trend = False
                break
                
    if is_pure_trend:
        keyword = topic.get("matched_keyword") or topic.get("topic", "").replace("Rising search:", "").strip()
        logger.info(f"  🔍 Pure trend detected. Searching active news for: '{keyword}'")
        found_urls = _search_news_for_trend(keyword)
        if found_urls:
            source_urls.extend(found_urls)
            logger.info(f"  ✅ Found {len(found_urls)} background articles for context.")

    logger.info(f"  Fetching {len(source_urls)} source URLs...")
    source_texts = fetch_multiple_sources(source_urls, max_sources=8)

    if not source_texts:
        logger.warning("  ⚠️ No source material could be extracted. Using topic summary only.")
        source_texts = [{
            "title": topic.get("topic", ""),
            "text": "\n".join(s.get("summary", "") for s in topic.get("stories", [])),
            "source_domain": "aggregated_summaries",
            "url": "",
        }]

    # ── Step 2: Build the prompt ──────────────────────────────────
    prompt = build_article_prompt(
        topic_title=topic.get("topic", "Agriculture News Update"),
        source_texts=source_texts,
        matched_keyword=topic.get("matched_keyword", "")
    )

    # ── Step 3: Call Gemini ───────────────────────────────────────
    try:
        logger.info("  🤖 Calling Gemini API...")
        response = generate_content_with_fallback(
            model=config.GEMINI_MODEL,
            contents=prompt
        )
        raw_output = response.text
        logger.info(f"  ✅ Gemini responded ({len(raw_output)} chars)")
        logger.debug(f"RAW AI OUTPUT:\n{raw_output}")

    except Exception as e:
        logger.error(f"  ❌ Gemini API error: {e}")
        return None

    # ── Step 4: Parse structured output ───────────────────────────
    article = _parse_article_output(
        raw_output, 
        matched_keyword=topic.get("matched_keyword", ""), 
        topic_title=topic.get("topic", "")
    )

    if article:
        article["sources_used"] = [s.get("source_domain", "") for s in source_texts]
        article["word_count"] = len(article.get("content_html", "").split())
        logger.info(f"  ✅ Article generated: '{article['title']}'")
    else:
        logger.error("  ❌ Failed to parse Gemini output")

    return article


def _parse_article_output(raw_text, matched_keyword="", topic_title=""):
    """
    Parse the structured output from Gemini into article components.
    Includes robust fallback logic for when AI omits labels or markers.
    """
    try:
        result = {}
        
        # Helper to strip markdown and excessive punctuation
        def clean_meta(val):
            if not val: return ""
            # Strip markdown artifacts and quotes
            return re.sub(r'[*_#`"]', '', val).strip()

        # ── 1. TITLE ──
        # Best: 1. TITLE: or TITLE:
        title_match = re.search(r'(?:1\.|TITLE:)\s*(.+?)(?:\n|2\.|META_DESCRIPTION:|---|$)', raw_text, re.IGNORECASE | re.DOTALL)
        if title_match:
            result["title"] = clean_meta(title_match.group(1))
        else:
            # Fallback: First non-empty line
            lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
            result["title"] = clean_meta(lines[0]) if lines else "Agriculture Update"

        # ── 2. META_DESCRIPTION ──
        meta_match = re.search(r'(?:2\.|META_DESCRIPTION:)\s*(.+?)(?:\n|3\.|SLUG:|---|$)', raw_text, re.IGNORECASE | re.DOTALL)
        if meta_match:
            result["meta_description"] = clean_meta(meta_match.group(1))
        else:
            # Fallback: second line if it looks like a description (long)
            lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
            if len(lines) > 1 and len(lines[1]) > 50:
                result["meta_description"] = clean_meta(lines[1])
            else:
                result["meta_description"] = result["title"][:155]

        # ── 3. SLUG ──
        slug_match = re.search(r'(?:3\.|SLUG:)\s*([a-z0-9-]+)', raw_text, re.IGNORECASE)
        if slug_match:
            result["slug"] = clean_meta(slug_match.group(1).lower())
        else:
            result["slug"] = re.sub(r'[^a-z0-0]+', '-', result["title"].lower()).strip('-')

        # ── 4. TAGS ──
        tags_match = re.search(r'(?:4\.|TAGS:)\s*(.+?)(?:\n|5\.|CATEGORY:|---|$)', raw_text, re.IGNORECASE | re.DOTALL)
        if tags_match:
            result["tags"] = [clean_meta(t) for t in tags_match.group(1).split(",") if t.strip()]
        else:
            result["tags"] = ["agriculture", "india"]

        # ── 5. CATEGORY ──
        category_match = re.search(r'(?:5\.|CATEGORY:)\s*([a-z0-9-]+)', raw_text, re.IGNORECASE)
        result["category"] = clean_meta(category_match.group(1).lower()) if category_match else "news"
        # Use provided keyword or title as fallback to avoid NameError if local lookup fails
        final_kw = matched_keyword if matched_keyword else clean_meta(topic_title)
        result["matched_keyword"] = final_kw

        # ── 6. CONTENT ──
        content_block_match = re.search(r'---CONTENT_START---(.*?)---CONTENT_END---', raw_text, re.DOTALL)
        if content_block_match:
            result["content"] = content_block_match.group(1).strip()
        else:
            # Fuzzy: look for anything after the Category/5 line or marked 6.
            fuzzy_parts = re.split(r'(?:6\.|---CONTENT_START---).*?\n', raw_text, maxsplit=1, flags=re.IGNORECASE | re.DOTALL)
            if len(fuzzy_parts) > 1:
                result["content"] = fuzzy_parts[1].split("---CONTENT_END---")[0].strip()
            else:
                # Absolute fallback: Everything after the first 3 lines
                lines = raw_text.split("\n")
                result["content"] = "\n".join(lines[3:]).strip() if len(lines) > 3 else raw_text

        # ── 7. FAQ ──
        faq_match = re.search(r'---FAQ_START---(.*?)---FAQ_END---', raw_text, re.DOTALL)
        if faq_match:
            result["faq_html"] = re.sub(r'<!--.*?-->', '', faq_match.group(1), flags=re.DOTALL).strip()
        else:
            schema_match = re.search(r'<script type="application/ld\+json">.*?</script>', raw_text, re.DOTALL)
            result["faq_html"] = schema_match.group(0) if schema_match else ""

        # Markdown to HTML Force Conversion
        import markdown
        result["content_html"] = markdown.markdown(
            result["content"], 
            extensions=['nl2br', 'sane_lists']
        )

        # Assembly
        result["full_content"] = result["content_html"]
        if result["faq_html"]:
            result["full_content"] += "\n\n" + result["faq_html"]

        return result

    except Exception as e:
        logger.error(f"  ❌ Parse error: {e}")
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_topic = {
        "topic": "PM Kisan Beneficiary Status 2026",
        "matched_keyword": "pm-kisan-samman-nidhi",
        "stories": [{"summary": "Latest updates on PM Kisan scheme for farmers."}]
    }
    article = generate_article(test_topic)
    if article:
        print(f"TITLE: {article['title']}")
        print(f"CONTENT PREVIEW: {article['full_content'][:500]}...")

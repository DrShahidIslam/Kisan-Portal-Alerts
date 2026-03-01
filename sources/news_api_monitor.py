"""
NewsAPI Monitor — Fetches top headlines and everything matching agriculture keywords.
Uses the free tier of newsapi.org (100 requests/day).
"""
import logging
import hashlib
from datetime import datetime, timedelta

from newsapi import NewsApiClient

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

logger = logging.getLogger(__name__)


def _hash_story(title, url):
    """Create a unique hash for a story."""
    raw = f"{title.strip().lower()}|{url.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def fetch_news_headlines():
    """
    Fetch agriculture-related headlines from NewsAPI.
    Uses both top-headlines and everything endpoints for maximum coverage.
    Returns a list of story dicts.

    Note: Free tier only allows 100 requests/day, so we use them wisely.
    """
    stories = []

    try:
        newsapi = NewsApiClient(api_key=config.NEWS_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize NewsAPI client: {e}")
        return stories

    # ── Query 1: Top headlines for agriculture in India ──────────────
    try:
        logger.info("NewsAPI: Fetching top headlines for 'agriculture india'")
        top = newsapi.get_top_headlines(
            q="agriculture OR farming",
            country="in",
            page_size=20
        )

        if top.get("status") == "ok":
            for article in top.get("articles", []):
                title = article.get("title", "")
                if not title or title == "[Removed]":
                    continue

                story = {
                    "title": title.strip(),
                    "summary": (article.get("description") or "").strip()[:500],
                    "url": article.get("url", ""),
                    "source": f"NewsAPI/{article.get('source', {}).get('name', 'Unknown')}",
                    "source_type": "newsapi",
                    "matched_keyword": "agriculture",
                    "published_at": _parse_date(article.get("publishedAt")),
                    "story_hash": _hash_story(title, article.get("url", "")),
                    "image_url": article.get("urlToImage", ""),
                }
                stories.append(story)

    except Exception as e:
        logger.error(f"NewsAPI top headlines error: {e}")

    # ── Query 1b: Top business headlines in India (agri-related) ──────
    try:
        logger.info("NewsAPI: Fetching top business headlines in India")
        sports_top = newsapi.get_top_headlines(
            category="business",
            country="in",
            page_size=20
        )

        if sports_top.get("status") == "ok":
            for article in sports_top.get("articles", []):
                title = article.get("title", "")
                if not title or title == "[Removed]":
                    continue

                story = {
                    "title": title.strip(),
                    "summary": (article.get("description") or "").strip()[:500],
                    "url": article.get("url", ""),
                    "source": f"NewsAPI/{article.get('source', {}).get('name', 'Unknown')}",
                    "source_type": "newsapi",
                    "matched_keyword": "india business",
                    "published_at": _parse_date(article.get("publishedAt")),
                    "story_hash": _hash_story(title, article.get("url", "")),
                    "image_url": article.get("urlToImage", ""),
                }
                stories.append(story)

    except Exception as e:
        logger.error(f"NewsAPI business headlines error: {e}")

    # ── Query 2: Everything endpoint for scheme-specific and regional coverage ───────
    search_queries = [
        # Central schemes
        "PM Kisan",
        "PMFBY crop insurance",
        "Kisan Credit Card",
        "eNAM agriculture India",
        "Soil Health Card scheme",
        "MSP minimum support price farmers",
        "agriculture minister India",
        "farmer scheme India",
        "agriculture budget India",
        "Agriculture Infrastructure Fund India",
        "Namo Drone Didi farmers",
        "Natural Farming India",
        # State schemes (all corners of India)
        "Rythu Bharosa Rythu Bandhu",
        "e Panta Andhra farmers",
        "Kalia Yojana Odisha",
        "Krishak Bandhu West Bengal",
        "Shetkari Sanman Nidhi Maharashtra",
        "Bhavantar Bhugtan Yojana",
        "Pik Vima Maharashtra crop insurance",
        "e-Chasa Andhra crop",
        "farmer protest India",
        "FPO farmer producer organisation India",
        "procurement MSP mandi India",
        "kharif rabi crop India",
    ]

    for query in search_queries:
        try:
            logger.info(f"NewsAPI: Searching everything for '{query}'")
            from_date = (datetime.utcnow() - timedelta(hours=24)).strftime("%Y-%m-%d")

            results = newsapi.get_everything(
                q=query,
                language="en",
                sort_by="publishedAt",
                from_param=from_date,
                page_size=10
            )

            if results.get("status") == "ok":
                for article in results.get("articles", []):
                    title = article.get("title", "")
                    if not title or title == "[Removed]":
                        continue

                    story = {
                        "title": title.strip(),
                        "summary": (article.get("description") or "").strip()[:500],
                        "url": article.get("url", ""),
                        "source": f"NewsAPI/{article.get('source', {}).get('name', 'Unknown')}",
                        "source_type": "newsapi",
                        "matched_keyword": query.lower(),
                        "published_at": _parse_date(article.get("publishedAt")),
                        "story_hash": _hash_story(title, article.get("url", "")),
                        "image_url": article.get("urlToImage", ""),
                    }
                    stories.append(story)

        except Exception as e:
            logger.error(f"NewsAPI everything error for '{query}': {e}")
            continue

    # Deduplicate by hash
    seen_hashes = set()
    unique_stories = []
    for story in stories:
        if story["story_hash"] not in seen_hashes:
            seen_hashes.add(story["story_hash"])
            unique_stories.append(story)

    # Exclusion filter — remove cricket, rugby, etc.
    exclude_kws = getattr(config, "EXCLUDE_KEYWORDS", [])
    filtered = []
    excluded = 0
    for story in unique_stories:
        text = f"{story.get('title', '')} {story.get('summary', '')}".lower()
        if any(kw.lower() in text for kw in exclude_kws):
            excluded += 1
            continue
        filtered.append(story)

    if excluded > 0:
        logger.info(f"NewsAPI Monitor: Excluded {excluded} irrelevant stories (cricket/rugby/etc.)")

    logger.info(f"NewsAPI Monitor: Found {len(filtered)} relevant stories (from {len(stories)} total)")
    return filtered


def _parse_date(date_str):
    """Parse ISO date string from NewsAPI."""
    if not date_str:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return datetime.utcnow()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    stories = fetch_news_headlines()
    for s in stories[:15]:
        print(f"[{s['source']}] {s['title']}")
        print(f"  {s['summary'][:120]}...")
        print(f"  URL: {s['url'][:80]}")
        print()

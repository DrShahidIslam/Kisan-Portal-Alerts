"""
Telegram Bot â€” Sends formatted notifications with interactive buttons.
Handles both sending alerts and receiving commands (/write_article, /ignore).
"""
import logging
import asyncio
import requests

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

logger = logging.getLogger(__name__)


def _get_base_url():
    """Build Telegram API URL at call time (not import time) so env vars are loaded."""
    token = config.TELEGRAM_BOT_TOKEN
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN is not set!")
        logger.error("TELEGRAM_BOT_TOKEN is not set!")
        return None
    return f"https://api.telegram.org/bot{token}"


def send_trending_alert(topic):
    """
    Send a rich trending topic alert to Telegram.
    Uses plain text to avoid MarkdownV2 escaping issues with dynamic content.
    """
    score = topic.get("score", 0)
    factors = topic.get("factors", [])
    sources = topic.get("sources", [])
    top_url = topic.get("top_url", "")
    story_count = topic.get("story_count", 1)

    # Score to emoji
    if score >= 80:
        fire = "ðŸ”¥ðŸ”¥ðŸ”¥"
    elif score >= 50:
        fire = "ðŸ”¥ðŸ”¥"
    else:
        fire = "ðŸ”¥"

    lines = [
        f"{fire} TRENDING: {topic['topic']}",
        "â”" * 30,
        f"ðŸ“Š Score: {score} | {story_count} source{'s' if story_count > 1 else ''}",
        f"ðŸ“° Sources: {', '.join(sources[:5])}",
        f"ðŸ·ï¸ Keyword: {topic.get('matched_keyword', 'N/A')}",
        "",
        "ðŸ“ Why it's trending:",
    ]

    for f in factors[:5]:
        lines.append(f"  â€¢ {f}")

    if top_url:
        lines.append(f"\nðŸ”— Source: {top_url}")

    # Add story summaries
    stories = topic.get("stories", [])
    if stories:
        lines.append("\nðŸ“° Coverage:")
        for s in stories[:3]:
            source_name = s.get("source", "Unknown")
            title = s.get("title", "")[:80]
            url = s.get("url", "")
            lines.append(f"  â€¢ [{source_name}] {title}")
            if url:
                lines.append(f"    {url}")

    message = "\n".join(lines)

    # Try to grab the hash from the topic, or fallback to generic
    story_hash = topic.get("story_hash")
    if not story_hash and topic.get("stories"):
        story_hash = topic.get("stories")[0].get("story_hash")
    
    cb_data = f"write_{story_hash[:40]}" if story_hash else "write_article"

    # Use inline keyboard buttons for actions
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "âœï¸ Generate Article", "callback_data": cb_data},
                {"text": "ðŸš« Ignore", "callback_data": "ignore"},
            ]
        ]
    }
    return _send_message(message, reply_markup=keyboard)


def send_simple_message(text):
    """Send a simple text message (no markdown)."""
    return _send_message(text)


def send_status_update(status_text):
    """Send a status update about the agent's activity."""
    message = f"ðŸ¤– Agent Status\n{'â”' * 20}\n{status_text}"
    return _send_message(message)


def send_article_preview(article_data, quality=None):
    """Send an article preview for human review, including quality findings when available."""
    title = article_data.get("title", "Untitled")
    meta = article_data.get("meta_description", "")
    slug = article_data.get("slug", "")
    word_count = article_data.get("word_count", 0)
    content_preview = article_data.get("content", "")[:800]
    quality = quality or {}
    issues = quality.get("issues", [])
    warnings = quality.get("warnings", [])
    has_findings = bool(issues or warnings)

    lines = [
        "ARTICLE READY FOR REVIEW",
        "-" * 30,
        "",
        f"Title: {title}",
        f"Slug: /{slug}",
        f"Meta: {meta}",
        f"Words: {word_count}",
    ]

    if quality:
        lines.extend([
            f"Focus keyword: {quality.get('focus_keyword', article_data.get('focus_keyword', ''))}",
            f"Internal links: {quality.get('internal_links', 0)} | H2s: {quality.get('h2_count', 0)}",
        ])
        if quality.get("keyword_density") is not None:
            lines.append(f"Keyword density: {quality.get('keyword_density', 0)}%")

    if has_findings:
        lines.extend(["", "Weaknesses:"])
        if issues:
            lines.extend(f"- {issue}" for issue in issues[:5])
        if warnings:
            lines.extend(f"- {warning}" for warning in warnings[:4])

    lines.extend([
        "",
        "Preview:",
        f"{content_preview}...",
    ])

    message = "\n".join(lines)

    if has_findings:
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Continue Draft", "callback_data": "quality_continue_draft"},
                    {"text": "Continue Live", "callback_data": "quality_continue_publish"},
                ],
                [
                    {"text": "Regenerate", "callback_data": "write_article"},
                    {"text": "Reject", "callback_data": "reject"},
                ],
            ]
        }
    else:
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Save Draft Only", "callback_data": "approve"},
                    {"text": "Publish Live", "callback_data": "publish_live"},
                ],
                [
                    {"text": "Regenerate", "callback_data": "write_article"},
                    {"text": "Reject", "callback_data": "reject"},
                ],
            ]
        }

    return _send_message(message, reply_markup=keyboard)

def send_quality_gate_decision(article_data, quality, requested_status="draft"):
    """Ask the user whether to continue with a quality-gate flagged article."""
    title = article_data.get("title", "Untitled")
    requested_status = (requested_status or "draft").lower()
    issues = quality.get("issues", [])
    warnings = quality.get("warnings", [])

    lines = [
        "QUALITY CHECK FLAGGED THIS ARTICLE",
        "-" * 34,
        "",
        f"Title: {title}",
        f"Requested action: {'Publish live' if requested_status == 'publish' else 'Save as draft'}",
        f"Words: {quality.get('word_count', 0)}",
        f"Internal links: {quality.get('internal_links', 0)}",
        f"H2 sections: {quality.get('h2_count', 0)}",
        "",
        "Blocking issues:",
    ]

    if issues:
        lines.extend(f"- {issue}" for issue in issues[:6])
    else:
        lines.append("- None")

    if warnings:
        lines.append("")
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in warnings[:4])

    lines.extend([
        "",
        "Choose whether to keep this as a draft, publish it live, or reject it.",
    ])

    message = "\n".join(lines)

    if requested_status == "publish":
        primary_button = {"text": "Continue Live", "callback_data": "quality_continue_publish"}
        secondary_button = {"text": "Save as Draft", "callback_data": "quality_continue_draft"}
    else:
        primary_button = {"text": "Continue and Save Draft", "callback_data": "quality_continue_draft"}
        secondary_button = {"text": "Publish Live Instead", "callback_data": "quality_continue_publish"}

    keyboard = {
        "inline_keyboard": [
            [primary_button, secondary_button],
            [
                {"text": "Regenerate", "callback_data": "write_article"},
                {"text": "Reject", "callback_data": "reject"},
            ],
        ]
    }

    return _send_message(message, reply_markup=keyboard)

def send_publish_confirmation(post_url, post_title, post_id=None, status="publish"):
    """Send confirmation that an article was published or saved as draft."""
    if status.lower() == "draft":
        status_text = "âœ… SAVED AS DRAFT"
        bottom_text = "The post is saved as a draft on your site\\."
    else:
        status_text = "ðŸš€ PUBLISHED LIVE"
        bottom_text = "The post is now live on your site\\."

    message = f"""{status_text}
{'â”' * 30}

ðŸ“„ *Title:* {_escape_md(post_title)}
ðŸ”— [View Post]({post_url})

{bottom_text}"""

    # Add inline button to publish the draft directly from Telegram
    keyboard = None
    if status.lower() == "draft" and post_id:
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "ðŸš€ Publish Live Now", "callback_data": f"publish_draft_{post_id}"}
                ]
            ]
        }

    return _send_message(message, parse_mode="MarkdownV2", reply_markup=keyboard)


def _format_factors(factors):
    """Format spike factors into a bulleted list."""
    if not factors:
        return "â€¢ General coverage increase"
    return "\n".join(f"â€¢ {_escape_md(f)}" for f in factors[:5])


def _escape_md(text):
    """Escape special characters for Telegram MarkdownV2."""
    if not text:
        return ""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def send_generating_status(topic_title):
    """Send a status message that an article is being generated."""
    message = f"ðŸ“ Generating article for:\n{topic_title}\n\nThis may take 1-2 minutes..."
    return _send_message(message)


def send_generation_confirmation(topic):
    """Send an 'Are you sure?' confirmation before starting article generation."""
    title = topic.get("topic", "Unknown Topic")
    story_hash = topic.get("story_hash", "none")

    text = (
        f"â“ *Confirm Article Generation*\n\n"
        f"Do you want to generate a full article for:\n"
        f"ðŸ‘‰ *{title}*?\n\n"
        f"This will use Gemini API and may take a moment."
    )

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "âœ… Yes, Generate", "callback_data": f"confirm_write_{story_hash}"},
                {"text": "âŒ Cancel", "callback_data": "cancel_write"},
            ]
        ]
    }
    return _send_message(text, parse_mode="Markdown", reply_markup=keyboard)


def send_image_preview(image_path, article_title):
    """
    Send a generated featured image to Telegram for approval.

    Args:
        image_path: Local path to the image file
        article_title: Article title for the caption

    Returns:
        int: Message ID, or None if failed
    """
    import json

    base_url = _get_base_url()
    if not base_url:
        return None

    chat_id = config.TELEGRAM_CHAT_ID
    if not chat_id:
        return None

    caption = f"ðŸ–¼ï¸ Featured Image Preview\nâ”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n{article_title}"

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "âœ… Use Image (in next job)", "callback_data": "approve_image"},
                {"text": "ðŸ”„ Regenerate Image (in next job)", "callback_data": "regenerate_image"},
            ],
            [
                {"text": "ðŸš« Skip Image", "callback_data": "skip_image"},
            ],
        ]
    }

    try:
        with open(image_path, "rb") as f:
            files = {"photo": f}
            data = {
                "chat_id": chat_id,
                "caption": caption,
                "reply_markup": json.dumps(keyboard),
            }
            response = requests.post(f"{base_url}/sendPhoto", data=data, files=files, timeout=30)

        result = response.json()
        if result.get("ok"):
            message_id = result["result"]["message_id"]
            logger.info(f"Telegram: Image sent (ID: {message_id})")
            return message_id
        else:
            logger.error(f"Telegram sendPhoto error: {result.get('description', 'Unknown')}")
            return None

    except Exception as e:
        logger.error(f"Telegram image send error: {e}")
        return None


def _send_message(text, parse_mode=None, reply_markup=None):
    """Send a message via Telegram Bot API."""
    base_url = _get_base_url()
    if not base_url:
        print("TELEGRAM ERROR: Cannot send message â€” bot token not configured")
        return None

    chat_id = config.TELEGRAM_CHAT_ID
    if not chat_id:
        print("TELEGRAM ERROR: Cannot send message â€” chat ID not configured")
        return None

    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": False,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        response = requests.post(f"{base_url}/sendMessage", json=payload, timeout=30)
        result = response.json()

        if result.get("ok"):
            message_id = result["result"]["message_id"]
            logger.info(f"Telegram: Message sent (ID: {message_id})")
            print(f"TELEGRAM OK: Message sent (ID: {message_id})")
            return message_id
        else:
            error_desc = result.get("description", "Unknown error")
            logger.error(f"Telegram API error: {error_desc}")
            print(f"TELEGRAM API ERROR: {error_desc}")

            # If MarkdownV2 fails, retry without formatting
            if parse_mode and "parse" in error_desc.lower():
                logger.info("Retrying without markdown formatting...")
                import re
                plain_text = re.sub(r'\\(.)', r'\1', text)
                plain_text = re.sub(r'\*([^*]+)\*', r'\1', plain_text)
                plain_text = re.sub(r'_([^_]+)_', r'\1', plain_text)
                return _send_message(plain_text, parse_mode=None)

            return None

    except requests.exceptions.Timeout:
        logger.error("Telegram: Request timed out")
        print("TELEGRAM ERROR: Request timed out")
        return None
    except Exception as e:
        logger.error(f"Telegram send error: {e}")
        print(f"TELEGRAM ERROR: {e}")
        return None


def get_updates(offset=None):
    """
    Get new messages/commands sent to the bot.
    Used for handling /write_article, /approve, /reject commands.
    """
    base_url = _get_base_url()
    if not base_url:
        return []

    params = {"timeout": 5}
    if offset:
        params["offset"] = offset

    try:
        response = requests.get(f"{base_url}/getUpdates", params=params, timeout=10)
        result = response.json()

        if result.get("ok"):
            return result.get("result", [])
        return []

    except Exception as e:
        logger.error(f"Telegram getUpdates error: {e}")
        return []


def answer_callback_query(callback_query_id, text=""):
    """Acknowledge a callback query (inline button press)."""
    base_url = _get_base_url()
    if not base_url:
        return False

    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text

    try:
        response = requests.post(f"{base_url}/answerCallbackQuery", json=payload, timeout=10)
        return response.json().get("ok", False)
    except Exception as e:
        logger.error(f"answerCallbackQuery error: {e}")
        return False


def test_connection():
    """Test the Telegram bot connection with a generous timeout."""
    base_url = _get_base_url()
    if not base_url:
        return False, None

    try:
        response = requests.get(f"{base_url}/getMe", timeout=20)
        result = response.json()
        if result.get("ok"):
            bot_name = result["result"].get("username", "Unknown")
            logger.info(f"Telegram bot connected: @{bot_name}")
            return True, bot_name
        return False, None
    except Exception as e:
        logger.error(f"Telegram connection test failed: {e}")
        return False, None


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Test connection
    ok, name = test_connection()
    if ok:
        print(f"âœ… Bot connected: @{name}")

        # Send a test message
        mid = send_simple_message(f"ðŸ§ª Connection test successful! @{name} is ready for Kisan Portal.")
        if mid:
            print(f"âœ… Test message sent (ID: {mid})")
        else:
            print("âŒ Failed to send test message")
    else:
        print("âŒ Bot connection failed. Check your TELEGRAM_BOT_TOKEN.")



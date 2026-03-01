"""
Central configuration for the Kisan Portal Alerts App.
All settings, keywords, RSS feeds, and thresholds are defined here.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ──────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

_gemini_keys_env = os.getenv("GEMINI_API_KEYS", os.getenv("GEMINI_API_KEY", ""))
GEMINI_API_KEYS = [k.strip() for k in _gemini_keys_env.split(",") if k.strip()]
GEMINI_API_KEY = GEMINI_API_KEYS[0] if GEMINI_API_KEYS else None

WP_URL = os.getenv("WP_URL", "https://kisanportal.org")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

# ── RSS Feeds ─────────────────────────────────────────────────────────
# Use active, working feeds. Feeds in AGRI_ONLY_FEEDS below: accept all entries (no keyword filter).
RSS_FEEDS = {
    "Rural Voice (Latest)": "https://eng.ruralvoice.in/rss/latest-posts",
    "Rural Voice (National)": "https://eng.ruralvoice.in/rss/category/national",
    "Rural Voice (Agribusiness)": "https://eng.ruralvoice.in/rss/category/agribusiness",
    "PIB Press Releases": "https://pib.gov.in/RssMain.aspx?ModId=6&LangId=1",
    "Krishi Jagran": "https://krishijagran.com/feed/",
    "Financial Express Industry": "https://www.financialexpress.com/industry/feed/",
    "The Hindu Agriculture": "https://www.thehindu.com/sci-tech/agriculture/feeder/default.rss",
}
# Feeds that are 100% agriculture — accept every entry (still apply EXCLUDE_KEYWORDS). Ensures RSS shows in alerts.
AGRI_ONLY_FEEDS = [
    "Rural Voice (Latest)", "Rural Voice (National)", "Rural Voice (Agribusiness)",
    "PIB Press Releases", "Krishi Jagran", "Financial Express Industry", "The Hindu Agriculture",
]

# ── Keyword Watchlists ────────────────────────────────────────────────
# Central Government Schemes
CENTRAL_SCHEMES = [
    "PM Kisan", "PM-Kisan", "Pradhan Mantri Kisan Samman Nidhi",
    "PMFBY", "Pradhan Mantri Fasal Bima Yojana", "Crop Insurance",
    "Kisan Credit Card", "KCC", "eNAM", "mKisan",
    "MSP", "Minimum Support Price", "Soil Health Card",
    "PM Krishi Sinchai Yojana", "PMKSY", "Agricultural Infrastructure Fund",
    "Fertilizer Subsidy", "Panchayati Raj", "Namo Drone Didi",
    "Lakhpati Didi", "PM Vishwakarma",
]

# State Specific Schemes (Topical Authority)
STATE_SCHEMES = [
    "Rythu Bharosa", "Rythu Bandhu", "Pik Vima", "e Panta", 
    "e-Chasa", "Kalia Yojana", "Bhavantar Bhugpaye",
    "Krishak Bandhu", "Mukhyamantri Krishi Ashirwad Yojana",
    "Ladli Behna", "Shetkari Sanman Nidhi",
]

# General Agricultural Keywords
GENERAL_AGRI_KEYWORDS = [
    "Agriculture", "Farming", "Farmers", "Kisan", "Crop",
    "Harvest", "Monsoon", "Irrigation", "Pesticide", "Organic Farming",
    "Organic Fertilizer", "Seed Subsidy", "Agriculture Minister",
    "Krishi Bhawan", "Agri Startup", "Horticulture", "Livestock",
    "Dairy Farming", "Poultry", "Fisheries",
]

# Exclusion keywords — stories/trends containing these are discarded
EXCLUDE_KEYWORDS = [
    # Sports
    "football", "soccer", "world cup",
    "cricket", "t20", "ipl", "odi", "test match",
    "icc", "wpl", "tennis", "rugby", "f1", "golf",
    # Entertainment/Politics (non-agri)
    "bollywood", "movie review", "box office", "celebrity",
    "election campaign", "political rally", "stock market rally",
    "crypto", "bitcoin",
]

# Combined master list for filtering
ALL_KEYWORDS = CENTRAL_SCHEMES + STATE_SCHEMES + GENERAL_AGRI_KEYWORDS

# ── Detection Settings ────────────────────────────────────────────────
SPIKE_THRESHOLD = 2.0           # 2x above the rolling average = spike
SPIKE_MIN_SCORE = 40            # Minimum spike score to trigger alert
ROLLING_WINDOW_HOURS = 24       # Baseline window for comparison
SCAN_INTERVAL_MINUTES = 60      # How often the agent scans
DEDUP_WINDOW_HOURS = 168        # Don't re-alert about the same story within 7 days

# ── Google Trends Settings ────────────────────────────────────────────
TRENDS_GEO = "IN"               # India (Crucial to avoid US trends)
TRENDS_KEYWORDS_PER_BATCH = 5   # pytrends allows max 5 keywords per request

# ── WordPress Settings ────────────────────────────────────────────────
WP_DEFAULT_CATEGORY = "Uncategorized"
WP_DEFAULT_STATUS = "draft"     # 'draft', 'pending', or 'publish'

# ── Article Generation Settings ────────────────────────────────────────
ARTICLE_MIN_WORDS = 800
ARTICLE_MAX_WORDS = 1500
GEMINI_MODEL = "gemini-2.5-flash"
IMAGEN_MODEL = os.getenv("IMAGEN_MODEL", "imagen-3.0-generate-002")
# Set to True to skip AI image generation (saves quota; article publishes without featured image)
SKIP_AI_IMAGE = os.getenv("SKIP_AI_IMAGE", "false").lower() in ("true", "1", "yes")
# Imagen is paid-only; set True only if you have a paid Gemini plan. Free tier uses Gemini Flash → source → Pollinations → placeholder.
USE_GEMINI_IMAGEN = os.getenv("USE_GEMINI_IMAGEN", "false").lower() in ("true", "1", "yes")

# ── Logging ───────────────────────────────────────────────────────────
LOG_FILE = "agent.log"
LOG_LEVEL = "INFO"

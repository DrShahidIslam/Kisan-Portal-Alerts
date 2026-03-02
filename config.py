"""
Central configuration for the Kisan Portal Alerts App.
All settings, keywords, RSS feeds, and thresholds are defined here.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root so it works regardless of current working directory
_PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(_PROJECT_ROOT / ".env")

# ── API Keys ──────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Collect all Gemini/Google AI keys for rotation (rate-limit fallback). Order: GEMINI_API_KEYS, then GEMINI_API_KEY, then GOOGLE_API_KEY.
_gemini_keys_list = []
for env_name in ("GEMINI_API_KEYS", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
    val = os.getenv(env_name, "").strip()
    if not val:
        continue
    for k in val.split(","):
        k = k.strip()
        if k and k not in _gemini_keys_list:
            _gemini_keys_list.append(k)
GEMINI_API_KEYS = _gemini_keys_list
GEMINI_API_KEY = GEMINI_API_KEYS[0] if GEMINI_API_KEYS else None

WP_URL = os.getenv("WP_URL", "https://kisanportal.org")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

# Optional: Unsplash API for high-quality stock photos (50 req/hr free). If set, we try Unsplash before AI image gen.
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "").strip() or None

# ── RSS Feeds ─────────────────────────────────────────────────────────
# Use active, working feeds. Feeds in AGRI_ONLY_FEEDS: accept all entries (still apply EXCLUDE_KEYWORDS).
# Others (ET, IE, etc.): require keyword match for agriculture/farmer/scheme relevance.
RSS_FEEDS = {
    # Rural Voice — farmer/scheme-focused; all accepted as agri-only
    "Rural Voice (Latest)": "https://eng.ruralvoice.in/rss/latest-posts",
    "Rural Voice (National)": "https://eng.ruralvoice.in/rss/category/national",
    "Rural Voice (States)": "https://eng.ruralvoice.in/rss/category/state",
    "Rural Voice (Opinion)": "https://eng.ruralvoice.in/rss/category/opinion",
    "Rural Voice (Agribusiness)": "https://eng.ruralvoice.in/rss/category/agribusiness",
    "Rural Voice (Latest News)": "https://eng.ruralvoice.in/rss/category/latest-news",
    "Rural Voice (Agritech)": "https://eng.ruralvoice.in/rss/category/agritech",
    "Rural Voice (Cooperatives)": "https://eng.ruralvoice.in/rss/category/cooperatives",
    "Rural Voice (Agri Diplomacy)": "https://eng.ruralvoice.in/rss/category/agri-diplomacy",
    "Rural Voice (International)": "https://eng.ruralvoice.in/rss/category/international",
    "Rural Voice (Rural Dialogue)": "https://eng.ruralvoice.in/rss/category/rural-dialogue",
    "Rural Voice (Ground Report)": "https://eng.ruralvoice.in/rss/category/ground-report",
    "Rural Voice (Agri Start-Ups)": "https://eng.ruralvoice.in/rss/category/agri-start-ups",
    "Rural Voice (Rural Connect)": "https://eng.ruralvoice.in/rss/category/rural-connect",
    # Government & agri-focused outlets
    "PIB Press Releases": "https://pib.gov.in/RssMain.aspx?ModId=6&LangId=1",
    "Krishi Jagran": "https://krishijagran.com/feed/",
    "The Hindu Agriculture": "https://www.thehindu.com/sci-tech/agriculture/feeder/default.rss",
    "Financial Express Industry": "https://www.financialexpress.com/industry/feed/",
    # Broad outlets — keyword-filtered (not in AGRI_ONLY_FEEDS)
    "ET Economy": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",
    "ET Industry": "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms",
    "ET India News": "https://economictimes.indiatimes.com/news/india/rssfeeds/81582957.cms",
    "ET Environment": "https://economictimes.indiatimes.com/news/environment/rssfeeds/2647163.cms",
    "Indian Express India": "https://indianexpress.com/section/india/feed/",
    "Indian Express Economy": "https://indianexpress.com/section/business/economy/feed/",
    "Indian Express Commodities": "https://indianexpress.com/section/business/commodities/feed/",
    "Down to Earth Top Stories": "https://www.downtoearth.org.in/rssfeedstopstories.cms",
    "Down to Earth Environment": "https://www.downtoearth.org.in/rssfeeds/1221656.cms",
    # Leading Indian news — keyword-filtered for scheme/agri relevance
    "Zee News Nation": "https://zeenews.india.com/rss/india-national-news.xml",
    "Zee News States": "https://zeenews.india.com/rss/india-news.xml",
    "Zee News Business": "https://zeenews.india.com/rss/business.xml",
    "Zee News Science & Environment": "https://zeenews.india.com/rss/science-environment-news.xml",
    "Hindustan Times Economy": "https://www.hindustantimes.com/feeds/rss/ht-insight/economy/rssfeed.xml",
    "Hindustan Times Climate": "https://www.hindustantimes.com/feeds/rss/ht-insight/climate-change/rssfeed.xml",
    "Livemint Economy & Politics": "https://www.livemint.com/rss/economy_politics",
    "NDTV Business": "https://feeds.feedburner.com/ndtvkhabar-business",
}
# Feeds that are 100% agriculture/rural — accept every entry (still apply EXCLUDE_KEYWORDS).
AGRI_ONLY_FEEDS = [
    "Rural Voice (Latest)", "Rural Voice (National)", "Rural Voice (States)", "Rural Voice (Opinion)",
    "Rural Voice (Agribusiness)", "Rural Voice (Latest News)", "Rural Voice (Agritech)",
    "Rural Voice (Cooperatives)", "Rural Voice (Agri Diplomacy)", "Rural Voice (International)",
    "Rural Voice (Rural Dialogue)", "Rural Voice (Ground Report)", "Rural Voice (Agri Start-Ups)",
    "Rural Voice (Rural Connect)",
    "PIB Press Releases", "Krishi Jagran", "The Hindu Agriculture", "Financial Express Industry",
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

# High-value content angles: stories matching these get a scoring boost and a clearer article title
HIGH_VALUE_AGRI_KEYWORDS = [
    "installment", "instalment", "ekyc", "e-kyc", "eKYC", "last date", "deadline",
    "eligibility", "status check", "new scheme", "enrollment", "enrolment",
    "how to apply", "beneficiary", "released", "announced", "registration",
    "last date", "extended", "apply online", "portal", "pm kisan", "pmfby",
]

# Priority content ideas when there are few or no spike topics.
# Covers all schemes on the site (central + state) and farmer/agri angles. Rotated by day.
# Topic = article headline; matched_keyword used for category assignment.
CONTENT_IDEAS = [
    # PM Kisan
    {"topic": "PM Kisan eKYC Deadline 2026: How to Complete and Check Status", "matched_keyword": "PM Kisan"},
    {"topic": "PM Kisan Latest Installment Date and Payment Status 2026", "matched_keyword": "PM Kisan"},
    {"topic": "PM Kisan Beneficiary List and Status Check Online", "matched_keyword": "PM Kisan"},
    # PMFBY & crop insurance
    {"topic": "PMFBY Rabi Enrollment 2025-26: Last Date and How to Apply", "matched_keyword": "PMFBY"},
    {"topic": "PMFBY Claim Status Check and Crop Insurance Guide", "matched_keyword": "PMFBY"},
    # KCC, KVP, e-NAM
    {"topic": "Kisan Credit Card (KCC) Scheme: Eligibility and Application Process", "matched_keyword": "Kisan Credit Card"},
    {"topic": "Kisan Vikas Patra (KVP): Interest Rate and How to Open", "matched_keyword": "Kisan Vikas Patra"},
    {"topic": "e-NAM 2.0 Registration and Mandi Prices: Complete Guide", "matched_keyword": "eNAM"},
    # Soil Health, Kisan Karz Mochan, Tractor
    {"topic": "Soil Health Card: How to Download and Use for Farmers", "matched_keyword": "Soil Health Card"},
    {"topic": "Kisan Karz Mochan Yojana: Eligibility and Debt Relief for Farmers", "matched_keyword": "Kisan Karz Mochan"},
    {"topic": "PM Kisan Tractor Scheme: Subsidy and How to Apply", "matched_keyword": "PM Kisan Tractor"},
    # e-Crop, e-Panta, e-Chasa (AP/Telangana)
    {"topic": "e-Crop Registration and Status Check AP: Complete Guide", "matched_keyword": "e-Crop"},
    {"topic": "e-Panta Login, Registration and Status Check Andhra Pradesh", "matched_keyword": "e Panta"},
    {"topic": "e-Panta eKYC and Beneficiary Status 2026", "matched_keyword": "e Panta"},
    {"topic": "e-Chasa AP: Crop Registration and Farmer Portal Guide", "matched_keyword": "e-Chasa"},
    # PM Dhan Dhaanya, Dalhan, oilseeds
    {"topic": "PM Dhan Dhaanya Krishi Yojana (PMDDKY): Eligibility and Benefits", "matched_keyword": "PM Dhan Dhaanya"},
    {"topic": "Dalhan Aatmanirbharta Mission: Oilseeds and Farmer Support", "matched_keyword": "Dalhan Aatmanirbharta"},
    # State: Rythu Bharosa, Pik Vima, Kalia, Krishak Bandhu, others
    {"topic": "Rythu Bharosa / Rythu Bandhu: Eligibility and Payment Status", "matched_keyword": "Rythu Bharosa"},
    {"topic": "Pik Vima Maharashtra: Rabi Crop Insurance and Enrollment", "matched_keyword": "Pik Vima"},
    {"topic": "KALIA Yojana Odisha: Eligibility and Payment Status", "matched_keyword": "Kalia Yojana"},
    {"topic": "Krishak Bandhu West Bengal: Farmer Assistance and Status Check", "matched_keyword": "Krishak Bandhu"},
    {"topic": "Shetkari Sanman Nidhi Maharashtra: Eligibility and How to Apply", "matched_keyword": "Shetkari Sanman Nidhi"},
    {"topic": "Bhavantar Bhugtan Yojana: Price Deficiency Payment for Farmers", "matched_keyword": "Bhavantar Bhugpaye"},
    # MSP, FPO, general agri
    {"topic": "MSP and Procurement: Rabi Crops Minimum Support Price 2025-26", "matched_keyword": "MSP"},
    {"topic": "FPO Registration and Farmer Producer Organisation Benefits", "matched_keyword": "FPO"},
    {"topic": "Agriculture Infrastructure Fund: Eligibility and How to Apply", "matched_keyword": "Agricultural Infrastructure Fund"},
    {"topic": "Namo Drone Didi Scheme: Subsidy and Training for Women", "matched_keyword": "Namo Drone Didi"},
    {"topic": "Natural Farming in India: Schemes and Benefits for Farmers", "matched_keyword": "Natural Farming"},
]

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

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
    # Additional agri-focused outlets
    "Gaon Connection": "https://www.gaonconnection.com/feed",
    "Agriculture Today": "https://www.agriculturetoday.in/feed/",
    "Krishak Jagat": "https://www.krishakjagat.org/feed/",
    # Government scheme portals & agri news
    "PIB Agriculture": "https://pib.gov.in/RssMain.aspx?ModId=3&LangId=1",
    "PIB Rural": "https://pib.gov.in/RssMain.aspx?ModId=63&LangId=1",
    "ICAR News": "https://icar.org.in/rss.xml",
    # Broad outlets — keyword-filtered (not in AGRI_ONLY_FEEDS)
    "ET Economy": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",
    "ET Industry": "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms",
    "ET India News": "https://economictimes.indiatimes.com/news/india/rssfeeds/81582957.cms",
    "ET Environment": "https://economictimes.indiatimes.com/news/environment/rssfeeds/2647163.cms",
    "ET Agriculture": "https://economictimes.indiatimes.com/news/economy/agriculture/rssfeeds/1373380680.cms",
    "Indian Express India": "https://indianexpress.com/section/india/feed/",
    "Indian Express Economy": "https://indianexpress.com/section/business/economy/feed/",
    "Indian Express Commodities": "https://indianexpress.com/section/business/commodities/feed/",
    "Down to Earth Top Stories": "https://www.downtoearth.org.in/rssfeedstopstories.cms",
    "Down to Earth Environment": "https://www.downtoearth.org.in/rssfeeds/1221656.cms",
    "Down to Earth Agriculture": "https://www.downtoearth.org.in/rssfeeds/agriculture",
    # Leading Indian news — keyword-filtered for scheme/agri relevance
    "Zee News Nation": "https://zeenews.india.com/rss/india-national-news.xml",
    "Zee News States": "https://zeenews.india.com/rss/india-news.xml",
    "Zee News Business": "https://zeenews.india.com/rss/business.xml",
    "Zee News Science & Environment": "https://zeenews.india.com/rss/science-environment-news.xml",
    "Hindustan Times Economy": "https://www.hindustantimes.com/feeds/rss/ht-insight/economy/rssfeed.xml",
    "Hindustan Times Climate": "https://www.hindustantimes.com/feeds/rss/ht-insight/climate-change/rssfeed.xml",
    "Livemint Economy & Politics": "https://www.livemint.com/rss/economy_politics",
    "NDTV Business": "https://feeds.feedburner.com/ndtvkhabar-business",
    "Swarajya Magazine": "https://swarajyamag.com/rss",
}
# Feeds that are 100% agriculture/rural — accept every entry (still apply EXCLUDE_KEYWORDS).
AGRI_ONLY_FEEDS = [
    "Rural Voice (Latest)", "Rural Voice (National)", "Rural Voice (States)", "Rural Voice (Opinion)",
    "Rural Voice (Agribusiness)", "Rural Voice (Latest News)", "Rural Voice (Agritech)",
    "Rural Voice (Cooperatives)", "Rural Voice (Agri Diplomacy)", "Rural Voice (International)",
    "Rural Voice (Rural Dialogue)", "Rural Voice (Ground Report)", "Rural Voice (Agri Start-Ups)",
    "Rural Voice (Rural Connect)",
    "PIB Press Releases", "PIB Agriculture", "PIB Rural", "ICAR News",
    "Krishi Jagran", "The Hindu Agriculture", "Financial Express Industry",
    "Gaon Connection", "Agriculture Today", "Krishak Jagat",
    "Down to Earth Agriculture",
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
    # Additional central schemes
    "Paramparagat Krishi Vikas Yojana", "PKVY", "Organic Farming Mission",
    "RKVY", "Rashtriya Krishi Vikas Yojana",
    "NMSA", "National Mission Sustainable Agriculture",
    "Sub-Mission Agricultural Mechanization", "SMAM",
    "PM FME", "PM Formalization of Micro Food",
    "AGMARKNET", "Agricultural Marketing",
    "MIDH", "Mission Integrated Development Horticulture",
    "National Bamboo Mission", "NBM",
    "Pradhan Mantri Matsya Sampada Yojana", "PMMSY",
    "National Livestock Mission", "NLM",
    "Dairy Development", "NDDB", "Rashtriya Gokul Mission",
    "PM Kisan Maandhan", "Farmer Pension",
    "PM Dhan Dhaanya", "PMDDKY",
    "Dalhan Aatmanirbharta", "Oilseeds Mission",
    "PM KUSUM", "Solar Pump", "Kusum Yojana",
    "e-Crop", "Crop Survey",
    "National Food Security Mission", "NFSM",
    "Interest Subvention Scheme", "Farm Loan",
    "Vivad Se Vishwas",
    "National Bee Honey Mission", "Beekeeping",
]

# State Specific Schemes (Topical Authority)
STATE_SCHEMES = [
    "Rythu Bharosa", "Rythu Bandhu", "Pik Vima", "e Panta",
    "e-Chasa", "Kalia Yojana", "Bhavantar Bhugpaye",
    "Krishak Bandhu", "Mukhyamantri Krishi Ashirwad Yojana",
    "Ladli Behna", "Shetkari Sanman Nidhi",
    # Additional state schemes
    "YSR Rythu Bharosa", "Annadata Sukhibhava",
    "Pallishree", "Krushak Assistance",
    "Kisan Samman Nidhi UP", "UP Kisan",
    "Meri Fasal Mera Byora", "Haryana Farmer",
    "Karnataka Raitha Siri", "Raitha Siri",
    "Tamil Nadu Uzhavar", "Uzhavar Pathukappu",
    "PM Kisan Telangana", "Rytu Bandhu Telangana",
    "Gujarat Kisan", "Kisan Sahay Gujarat",
    "Rajiv Gandhi Kisan Nyay Yojana", "Chhattisgarh Kisan",
    "Mahatma Jyotirao Phule Shetkari Karz Mukti",
    "Punjab Kisan", "Debt Waiver Punjab",
    "MP Kisan Kalyan Yojana", "Mukhyamantri Kisan Kalyan",
    "Bihar Kisan", "Kisan Samman Nidhi Bihar",
    "Krishi Input Subsidy", "Crop Damage Relief",
    "Jharkhand Kisan", "Mukhyamantri Krishi Ashirwad",
]

# General Agricultural Keywords
GENERAL_AGRI_KEYWORDS = [
    "Agriculture", "Farming", "Farmers", "Kisan", "Crop",
    "Harvest", "Monsoon", "Irrigation", "Pesticide", "Organic Farming",
    "Organic Fertilizer", "Seed Subsidy", "Agriculture Minister",
    "Krishi Bhawan", "Agri Startup", "Horticulture", "Livestock",
    "Dairy Farming", "Poultry", "Fisheries",
    # Additional agri keywords for wider coverage
    "Mandi Price", "APMC", "Agri Market", "Procurement",
    "Kharif", "Rabi", "Zaid", "Sowing Season",
    "Fertilizer Price", "DAP", "Urea Price",
    "Farm Mechanization", "Tractor Subsidy",
    "FPO", "Farmer Producer Organisation",
    "Agri Budget", "Agriculture Budget",
    "Crop Loan", "Farm Credit", "Crop Damage",
    "Flood Relief Farmer", "Drought Relief",
    "Agri Export", "Spice Board", "Cotton Price",
    "Sugarcane Price", "Wheat Procurement", "Paddy Procurement",
    "Cold Storage", "Warehouse", "Food Processing",
    "Silk Farming", "Sericulture", "Mushroom Farming",
    "PM Kisan Helpline", "Agriculture Extension",
    "Soil Testing", "Water Conservation",
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
    "extended", "apply online", "portal", "pm kisan", "pmfby",
    # Rule changes, updates, and freshness triggers
    "rule change", "new rule", "guideline change", "updated", "revised",
    "notification", "gazette", "circular", "amendment",
    "increased", "hiked", "reduced", "disbursed", "credited",
    "beneficiary list", "rejection", "rejected", "ineligible",
    "aadhaar link", "bank link", "land record", "land seeding",
    "direct benefit transfer", "DBT", "payment status",
    "premium rate", "claim settlement", "insurance claim",
    "mandi rate", "msp hike", "procurement price",
    "subsidy amount", "subsidy rate", "interest rate",
    "kist", "kist date", "next installment",
]

# Priority content ideas when there are few or no spike topics.
# Covers all schemes on the site (central + state) and farmer/agri angles. Rotated across cycles.
# Topic = article headline; matched_keyword used for category assignment.
# IMPORTANT: Each idea covers a SPECIFIC ANGLE — eligibility, eKYC, status check, rule change,
# deadline, how-to-apply, installment update, beneficiary list, etc. — NOT just the scheme introduction.
CONTENT_IDEAS = [
    # ══════ PM Kisan — Multiple Angles ══════
    {"topic": "PM Kisan eKYC Deadline 2026: How to Complete and Check Status", "matched_keyword": "PM Kisan"},
    {"topic": "PM Kisan Latest Installment Date and Payment Status 2026", "matched_keyword": "PM Kisan"},
    {"topic": "PM Kisan Beneficiary List 2026: How to Check Your Name Online", "matched_keyword": "PM Kisan"},
    {"topic": "PM Kisan Eligibility Criteria 2026: Who Can and Cannot Apply", "matched_keyword": "PM Kisan"},
    {"topic": "PM Kisan Aadhaar Linking: How to Link and Fix Errors", "matched_keyword": "PM Kisan"},
    {"topic": "PM Kisan Land Seeding Problem: How to Fix and Update Records", "matched_keyword": "PM Kisan"},
    {"topic": "PM Kisan Rejected List 2026: Common Reasons and How to Fix", "matched_keyword": "PM Kisan"},
    {"topic": "PM Kisan Bank Account Change: How to Update Bank Details", "matched_keyword": "PM Kisan"},
    {"topic": "PM Kisan New Registration 2026: Step-by-Step Online Process", "matched_keyword": "PM Kisan"},
    {"topic": "PM Kisan Mobile Number Update: How to Change on Portal", "matched_keyword": "PM Kisan"},
    {"topic": "PM Kisan Helpline Number and Complaint Registration Guide", "matched_keyword": "PM Kisan"},
    {"topic": "PM Kisan DBT Payment Not Received: Troubleshooting Guide", "matched_keyword": "PM Kisan"},
    # ══════ PMFBY & Crop Insurance — Multiple Angles ══════
    {"topic": "PMFBY Rabi Enrollment 2025-26: Last Date and How to Apply", "matched_keyword": "PMFBY"},
    {"topic": "PMFBY Claim Status Check: How to Track Crop Insurance Claim", "matched_keyword": "PMFBY"},
    {"topic": "PMFBY Premium Rates 2026: Crop-Wise Insurance Premium Chart", "matched_keyword": "PMFBY"},
    {"topic": "PMFBY Eligibility: Which Farmers and Crops Are Covered", "matched_keyword": "PMFBY"},
    {"topic": "PMFBY Claim Rejection Reasons and How to Reapply", "matched_keyword": "PMFBY"},
    {"topic": "PMFBY Kharif Season 2026: Enrollment Dates and Crop List", "matched_keyword": "PMFBY"},
    {"topic": "PMFBY vs Restructured Weather Based Crop Insurance: Comparison", "matched_keyword": "PMFBY"},
    {"topic": "How to File PMFBY Crop Loss Intimation Within 72 Hours", "matched_keyword": "PMFBY"},
    # ══════ KCC — Multiple Angles ══════
    {"topic": "Kisan Credit Card (KCC) Eligibility 2026: Who Can Apply", "matched_keyword": "Kisan Credit Card"},
    {"topic": "KCC Loan Interest Rate 2026: Subvention and Repayment Rules", "matched_keyword": "Kisan Credit Card"},
    {"topic": "KCC Application Process: Documents Required and How to Apply", "matched_keyword": "Kisan Credit Card"},
    {"topic": "KCC Renewal Process 2026: How to Renew Your Kisan Credit Card", "matched_keyword": "Kisan Credit Card"},
    {"topic": "KCC Loan Limit Enhancement: How to Increase Credit Limit", "matched_keyword": "Kisan Credit Card"},
    {"topic": "KCC for Fisheries and Animal Husbandry: New Rules 2026", "matched_keyword": "Kisan Credit Card"},
    # ══════ eNAM — Multiple Angles ══════
    {"topic": "e-NAM 2.0 Registration: Step-by-Step Guide for Farmers", "matched_keyword": "eNAM"},
    {"topic": "e-NAM Mandi Prices Today: How to Check Live Rates Online", "matched_keyword": "eNAM"},
    {"topic": "e-NAM App Download and Features: Complete Farmer Guide", "matched_keyword": "eNAM"},
    {"topic": "How to Sell Crops on e-NAM: Online Bidding Process Explained", "matched_keyword": "eNAM"},
    # ══════ Soil Health Card ══════
    {"topic": "Soil Health Card Download: How to Get and Read Your Report", "matched_keyword": "Soil Health Card"},
    {"topic": "Soil Health Card Scheme 2026: Benefits and How to Apply", "matched_keyword": "Soil Health Card"},
    {"topic": "How to Use Soil Health Card Recommendations for Better Yield", "matched_keyword": "Soil Health Card"},
    # ══════ Kisan Vikas Patra ══════
    {"topic": "Kisan Vikas Patra Interest Rate 2026: Current Rate and Maturity", "matched_keyword": "Kisan Vikas Patra"},
    {"topic": "KVP vs FD vs PPF: Best Savings Option for Farmers Compared", "matched_keyword": "Kisan Vikas Patra"},
    # ══════ Kisan Karz Mochan ══════
    {"topic": "Kisan Karz Mochan Yojana: Eligibility and How to Check Status", "matched_keyword": "Kisan Karz Mochan"},
    {"topic": "Farm Loan Waiver 2026: State-Wise Status and Latest Updates", "matched_keyword": "Kisan Karz Mochan"},
    # ══════ PM Kisan Tractor ══════
    {"topic": "PM Kisan Tractor Yojana 2026: Subsidy Amount and How to Apply", "matched_keyword": "PM Kisan Tractor"},
    {"topic": "Tractor Subsidy Scheme: State-Wise Eligibility and Benefits", "matched_keyword": "PM Kisan Tractor"},
    # ══════ e-Crop, e-Panta, e-Chasa (AP/Telangana) ══════
    {"topic": "e-Crop Registration AP 2026: How to Register and Check Status", "matched_keyword": "e-Crop"},
    {"topic": "e-Crop Survey: Purpose, Process and Common Issues", "matched_keyword": "e-Crop"},
    {"topic": "e-Panta Login and Registration: Step-by-Step Guide AP", "matched_keyword": "e Panta"},
    {"topic": "e-Panta eKYC 2026: How to Complete and Verify Status", "matched_keyword": "e Panta"},
    {"topic": "e-Panta Beneficiary Status Check: Payment and Eligibility", "matched_keyword": "e Panta"},
    {"topic": "e-Chasa AP Crop Registration: Complete Guide for Farmers", "matched_keyword": "e-Chasa"},
    {"topic": "e-Chasa vs e-Crop: Differences and Which to Use in AP", "matched_keyword": "e-Chasa"},
    # ══════ PM Dhan Dhaanya, Dalhan ══════
    {"topic": "PM Dhan Dhaanya Krishi Yojana: Eligibility and How to Apply", "matched_keyword": "PM Dhan Dhaanya"},
    {"topic": "PMDDKY Benefits: Financial Assistance and District-Wise Coverage", "matched_keyword": "PM Dhan Dhaanya"},
    {"topic": "Dalhan Aatmanirbharta Mission: Oilseed Farmer Benefits 2026", "matched_keyword": "Dalhan Aatmanirbharta"},
    {"topic": "Pulses and Oilseeds Subsidy 2026: Government Support for Farmers", "matched_keyword": "Dalhan Aatmanirbharta"},
    # ══════ Rythu Bharosa / Rythu Bandhu ══════
    {"topic": "Rythu Bharosa Payment Status 2026: How to Check Online", "matched_keyword": "Rythu Bharosa"},
    {"topic": "Rythu Bharosa Eligibility 2026: Updated Rules and Who Qualifies", "matched_keyword": "Rythu Bharosa"},
    {"topic": "Rythu Bandhu Cheque Status: How to Track Payment in Telangana", "matched_keyword": "Rythu Bandhu"},
    {"topic": "YSR Rythu Bharosa vs Rythu Bandhu: Differences Explained", "matched_keyword": "Rythu Bharosa"},
    # ══════ Pik Vima (Maharashtra) ══════
    {"topic": "Pik Vima Maharashtra Rabi 2025-26: Enrollment and Premium", "matched_keyword": "Pik Vima"},
    {"topic": "Pik Vima Claim Status: How to Check and Track Your Claim", "matched_keyword": "Pik Vima"},
    {"topic": "Pik Vima Kharif 2026: Crop List, Dates and How to Apply", "matched_keyword": "Pik Vima"},
    # ══════ KALIA Yojana (Odisha) ══════
    {"topic": "KALIA Yojana Payment Status 2026: Check Odisha Farmer Aid", "matched_keyword": "Kalia Yojana"},
    {"topic": "KALIA Yojana Eligibility: Who Can Apply and Required Documents", "matched_keyword": "Kalia Yojana"},
    {"topic": "KALIA Yojana New Beneficiary List 2026: How to Check Name", "matched_keyword": "Kalia Yojana"},
    # ══════ Krishak Bandhu (West Bengal) ══════
    {"topic": "Krishak Bandhu Status Check 2026: Payment and Beneficiary List", "matched_keyword": "Krishak Bandhu"},
    {"topic": "Krishak Bandhu Death Benefit: Insurance Amount and Claim Process", "matched_keyword": "Krishak Bandhu"},
    # ══════ Shetkari Sanman Nidhi (Maharashtra) ══════
    {"topic": "Shetkari Sanman Nidhi Eligibility and Payment Status 2026", "matched_keyword": "Shetkari Sanman Nidhi"},
    {"topic": "Shetkari Sanman Nidhi How to Apply: Registration Guide", "matched_keyword": "Shetkari Sanman Nidhi"},
    # ══════ Bhavantar Bhugtan ══════
    {"topic": "Bhavantar Bhugtan Yojana: How Price Deficiency Payment Works", "matched_keyword": "Bhavantar Bhugpaye"},
    # ══════ MSP & Procurement ══════
    {"topic": "MSP Rabi Crops 2025-26: Complete Price List for All Crops", "matched_keyword": "MSP"},
    {"topic": "MSP Kharif Crops 2026: Expected Rates and Government Announcement", "matched_keyword": "MSP"},
    {"topic": "Wheat Procurement 2026: MSP Rate, Centers, and How to Sell", "matched_keyword": "MSP"},
    {"topic": "Paddy Procurement Season: MSP Rate and Mandi Registration", "matched_keyword": "MSP"},
    {"topic": "How MSP Is Calculated: Formula and Factors Explained", "matched_keyword": "MSP"},
    # ══════ FPO ══════
    {"topic": "FPO Registration 2026: How to Form a Farmer Producer Organisation", "matched_keyword": "FPO"},
    {"topic": "FPO Benefits: Government Grants and Support for Farmer Groups", "matched_keyword": "FPO"},
    {"topic": "How FPOs Help Farmers Get Better Prices: Success Stories", "matched_keyword": "FPO"},
    # ══════ Agriculture Infrastructure Fund ══════
    {"topic": "Agriculture Infrastructure Fund: Eligibility, Interest Rate and How to Apply", "matched_keyword": "Agricultural Infrastructure Fund"},
    {"topic": "AIF Loan for Cold Storage and Warehouse: Complete Guide", "matched_keyword": "Agricultural Infrastructure Fund"},
    # ══════ Namo Drone Didi ══════
    {"topic": "Namo Drone Didi Scheme 2026: Eligibility, Training and Subsidy", "matched_keyword": "Namo Drone Didi"},
    {"topic": "Drone Farming in India: How Namo Drone Didi Is Changing Agriculture", "matched_keyword": "Namo Drone Didi"},
    # ══════ PM KUSUM / Solar Pump ══════
    {"topic": "PM KUSUM Yojana 2026: Solar Pump Subsidy and How to Apply", "matched_keyword": "PM KUSUM"},
    {"topic": "PM KUSUM Component A B C: Which Is Right for You", "matched_keyword": "PM KUSUM"},
    {"topic": "Solar Pump Subsidy for Farmers: State-Wise Schemes 2026", "matched_keyword": "PM KUSUM"},
    # ══════ PM Kisan Maandhan (Farmer Pension) ══════
    {"topic": "PM Kisan Maandhan Yojana: Pension for Farmers and How to Enroll", "matched_keyword": "PM Kisan Maandhan"},
    {"topic": "Farmer Pension Scheme: Monthly Pension, Eligibility and Benefits", "matched_keyword": "PM Kisan Maandhan"},
    # ══════ RKVY ══════
    {"topic": "RKVY Scheme 2026: Rashtriya Krishi Vikas Yojana Benefits", "matched_keyword": "RKVY"},
    {"topic": "RKVY-RAFTAAR: Agri Startup Funding and How to Apply", "matched_keyword": "RKVY"},
    # ══════ PMFME (Micro Food Enterprise) ══════
    {"topic": "PM FME Scheme: Subsidy for Food Processing and How to Apply", "matched_keyword": "PM FME"},
    {"topic": "One District One Product (ODOP): Food Processing and Subsidy", "matched_keyword": "PM FME"},
    # ══════ Organic Farming ══════
    {"topic": "Paramparagat Krishi Vikas Yojana: Organic Farming Support 2026", "matched_keyword": "Paramparagat Krishi Vikas Yojana"},
    {"topic": "Natural Farming vs Organic Farming: Differences and Government Support", "matched_keyword": "Natural Farming"},
    {"topic": "Zero Budget Natural Farming: Benefits and How to Start", "matched_keyword": "Natural Farming"},
    # ══════ Fisheries & Livestock ══════
    {"topic": "PM Matsya Sampada Yojana 2026: Fisheries Subsidy and Benefits", "matched_keyword": "PMMSY"},
    {"topic": "National Livestock Mission: Dairy, Poultry and Goat Farming Support", "matched_keyword": "National Livestock Mission"},
    {"topic": "Rashtriya Gokul Mission: Cattle Breeding and Dairy Development", "matched_keyword": "Rashtriya Gokul Mission"},
    # ══════ Horticulture ══════
    {"topic": "MIDH Scheme: Horticulture Subsidy for Fruits, Vegetables and Flowers", "matched_keyword": "MIDH"},
    {"topic": "National Bamboo Mission: Subsidy for Bamboo Plantation 2026", "matched_keyword": "National Bamboo Mission"},
    # ══════ Agricultural Mechanization ══════
    {"topic": "SMAM Scheme: Farm Machinery Subsidy and Custom Hiring Centers", "matched_keyword": "SMAM"},
    {"topic": "Farm Equipment Subsidy 2026: State-Wise List and How to Apply", "matched_keyword": "Farm Mechanization"},
    # ══════ State-Specific Deep Dives ══════
    {"topic": "Rajiv Gandhi Kisan Nyay Yojana Chhattisgarh: Status and Benefits", "matched_keyword": "Rajiv Gandhi Kisan Nyay Yojana"},
    {"topic": "MP Mukhyamantri Kisan Kalyan Yojana: Payment Status 2026", "matched_keyword": "MP Kisan Kalyan Yojana"},
    {"topic": "Meri Fasal Mera Byora Haryana: Registration and Benefits", "matched_keyword": "Meri Fasal Mera Byora"},
    {"topic": "Tamil Nadu Uzhavar Pathukappu: Farmer Protection Scheme Guide", "matched_keyword": "Tamil Nadu Uzhavar"},
    {"topic": "Karnataka Raitha Siri: Farmer Assistance Eligibility and Benefits", "matched_keyword": "Karnataka Raitha Siri"},
    {"topic": "Gujarat Kisan Sahay Yojana: Crop Damage Compensation 2026", "matched_keyword": "Kisan Sahay Gujarat"},
    {"topic": "Ladli Behna Yojana: Eligibility, Payment Status and Latest Update", "matched_keyword": "Ladli Behna"},
    {"topic": "Mukhyamantri Krishi Ashirwad Yojana Jharkhand: Benefits and Status", "matched_keyword": "Mukhyamantri Krishi Ashirwad Yojana"},
    # ══════ Seasonal & Timely Content ══════
    {"topic": "Kharif Season 2026: Sowing Calendar, Crop Selection and Tips", "matched_keyword": "Kharif"},
    {"topic": "Rabi Crop Season Guide: Best Crops, Dates and Subsidy", "matched_keyword": "Rabi"},
    {"topic": "Fertilizer Subsidy 2026: Current Rates for Urea, DAP and MOP", "matched_keyword": "Fertilizer Subsidy"},
    {"topic": "Agriculture Budget 2026-27: Key Announcements for Farmers", "matched_keyword": "Agri Budget"},
    {"topic": "Crop Damage Compensation: How to Apply After Natural Disaster", "matched_keyword": "Crop Damage"},
    {"topic": "Crop Loan Interest Subvention 2026: Reduced Rate for Farmers", "matched_keyword": "Interest Subvention Scheme"},
    # ══════ How-To & Informational Guides ══════
    {"topic": "How to Check Any Government Scheme Status Online: Complete Guide", "matched_keyword": "agriculture"},
    {"topic": "Top 10 Government Schemes for Small and Marginal Farmers 2026", "matched_keyword": "agriculture"},
    {"topic": "Central vs State Farmer Schemes: Complete Comparison Guide", "matched_keyword": "agriculture"},
    {"topic": "Aadhaar Seeding for Farmer Schemes: Why It Matters and How to Fix", "matched_keyword": "agriculture"},
    {"topic": "All India Farmer Schemes List 2026: Central and State Combined", "matched_keyword": "agriculture"},
    {"topic": "How to Register on Farmer Portal: CSC, Mobile App and Online", "matched_keyword": "agriculture"},
    {"topic": "Digital Agriculture: Top Government Apps for Indian Farmers", "matched_keyword": "agriculture"},
    {"topic": "Mandi Prices Today: How to Check Commodity Rates in Your Area", "matched_keyword": "Mandi Price"},
    {"topic": "FPO vs SHG: Which Group Is Better for Farmers and Why", "matched_keyword": "FPO"},
    {"topic": "Beekeeping Subsidy in India: Government Support for Honey Farming", "matched_keyword": "National Bee Honey Mission"},
    {"topic": "Cold Storage and Warehouse Subsidy: NABARD and AIF Schemes 2026", "matched_keyword": "Agricultural Infrastructure Fund"},
    {"topic": "Food Processing Subsidy for Farmers: PMFME and ODOP Benefits", "matched_keyword": "PM FME"},
    {"topic": "Agri Export Opportunities 2026: Government Policies and Subsidies", "matched_keyword": "Agri Export"},
]

# ── Detection Settings ────────────────────────────────────────────────
SPIKE_THRESHOLD = 2.0           # 2x above the rolling average = spike
SPIKE_MIN_SCORE = 25            # Minimum spike score to trigger alert (lowered to catch 2-source stories)
ROLLING_WINDOW_HOURS = 24       # Baseline window for comparison
SCAN_INTERVAL_MINUTES = 60      # How often the agent scans
DEDUP_WINDOW_HOURS = 72         # Don't re-alert about the same story within 3 days (was 7, reduced for freshness)

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
# When all image sources fail: if False (default), publish without featured image; if True, use green placeholder with title text.
USE_PLACEHOLDER_IMAGE = os.getenv("USE_PLACEHOLDER_IMAGE", "false").lower() in ("true", "1", "yes")

# ── Logging ───────────────────────────────────────────────────────────
LOG_FILE = "agent.log"
LOG_LEVEL = "INFO"

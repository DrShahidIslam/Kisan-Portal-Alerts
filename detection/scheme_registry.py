"""
Master registry for India agriculture schemes and reusable coverage logic.
"""
from datetime import datetime
import re


# Central + state scheme registry used by detection, categorization, and coverage planning.
SCHEME_REGISTRY = [
    {"id": "pm_kisan", "name": "PM Kisan", "level": "central", "state": "", "priority": 10,
     "category_slug": "pm-kisan-samman-nidhi", "aliases": ["pm-kisan", "pradhan mantri kisan samman nidhi", "kisan samman nidhi"]},
    {"id": "pmfby", "name": "PMFBY", "level": "central", "state": "", "priority": 9,
     "category_slug": "pmfby", "aliases": ["pradhan mantri fasal bima yojana", "crop insurance"]},
    {"id": "kcc", "name": "Kisan Credit Card", "level": "central", "state": "", "priority": 9,
     "category_slug": "kisan-credit-card", "aliases": ["kcc", "farm credit card"]},
    {"id": "enam", "name": "eNAM", "level": "central", "state": "", "priority": 8,
     "category_slug": "enam-scheme", "aliases": ["e-nam", "national agricultural market"]},
    {"id": "pm_kusum", "name": "PM KUSUM", "level": "central", "state": "", "priority": 8,
     "category_slug": "pm-kusum-yojana", "aliases": ["kusum yojana", "solar pump scheme"]},
    {"id": "soil_health", "name": "Soil Health Card", "level": "central", "state": "", "priority": 7,
     "category_slug": "soil-health-card", "aliases": ["soil card"]},
    {"id": "rkvy", "name": "RKVY", "level": "central", "state": "", "priority": 7,
     "category_slug": "rkvy-scheme", "aliases": ["rashtriya krishi vikas yojana"]},
    {"id": "pm_fme", "name": "PM FME", "level": "central", "state": "", "priority": 7,
     "category_slug": "pm-fme-scheme", "aliases": ["pm formalization of micro food", "odop"]},
    {"id": "pm_matsya", "name": "PM Matsya Sampada Yojana", "level": "central", "state": "", "priority": 7,
     "category_slug": "pm-matsya-sampada-yojana", "aliases": ["pmmsy", "matsya sampada"]},
    {"id": "nlm", "name": "National Livestock Mission", "level": "central", "state": "", "priority": 7,
     "category_slug": "national-livestock-mission", "aliases": ["livestock mission"]},
    {"id": "midh", "name": "MIDH", "level": "central", "state": "", "priority": 6,
     "category_slug": "midh-horticulture", "aliases": ["horticulture mission"]},
    {"id": "smam", "name": "SMAM", "level": "central", "state": "", "priority": 6,
     "category_slug": "smam-mechanization", "aliases": ["farm machinery subsidy", "mechanization"]},
    {"id": "bamboo", "name": "National Bamboo Mission", "level": "central", "state": "", "priority": 6,
     "category_slug": "national-bamboo-mission", "aliases": ["nbm", "bamboo mission"]},
    {"id": "nfsm", "name": "NFSM", "level": "central", "state": "", "priority": 6,
     "category_slug": "nfsm-food-security", "aliases": ["national food security mission"]},
    {"id": "pm_maandhan", "name": "PM Kisan Maandhan", "level": "central", "state": "", "priority": 6,
     "category_slug": "pm-kisan-maandhan", "aliases": ["farmer pension"]},
    {"id": "aif", "name": "Agricultural Infrastructure Fund", "level": "central", "state": "", "priority": 6,
     "category_slug": "agricultural-infrastructure-fund", "aliases": ["aif", "agri infrastructure fund", "warehouse subsidy", "cold storage subsidy"]},
    {"id": "fpo", "name": "FPO", "level": "central", "state": "", "priority": 6,
     "category_slug": "fpo", "aliases": ["farmer producer organisation", "farmer producer organization"]},
    {"id": "msp", "name": "MSP", "level": "central", "state": "", "priority": 7,
     "category_slug": "msp", "aliases": ["minimum support price", "procurement price", "wheat procurement", "paddy procurement"]},
    {"id": "drone_didi", "name": "Namo Drone Didi", "level": "central", "state": "", "priority": 5,
     "category_slug": "namo-drone-didi", "aliases": ["drone didi", "drone subsidy"]},
    {"id": "gokul", "name": "Rashtriya Gokul Mission", "level": "central", "state": "", "priority": 5,
     "category_slug": "rashtriya-gokul-mission", "aliases": ["gokul mission", "cattle breeding mission"]},
    {"id": "bee_honey", "name": "National Bee Honey Mission", "level": "central", "state": "", "priority": 5,
     "category_slug": "national-bee-honey-mission", "aliases": ["beekeeping subsidy", "bee keeping", "honey mission"]},
    {"id": "natural_farming", "name": "Natural Farming", "level": "central", "state": "", "priority": 5,
     "category_slug": "natural-farming", "aliases": ["zero budget natural farming", "zbnf"]},
    {"id": "interest_subvention", "name": "Interest Subvention Scheme", "level": "central", "state": "", "priority": 5,
     "category_slug": "interest-subvention-scheme", "aliases": ["crop loan interest subvention", "interest subsidy farm loan"]},
    {"id": "rythu_bharosa", "name": "Rythu Bharosa", "level": "state", "state": "Andhra Pradesh", "priority": 8,
     "category_slug": "rythu-bharosa", "aliases": ["rythu bandhu", "ysr rythu bharosa"]},
    {"id": "e_panta", "name": "e-Panta", "level": "state", "state": "Andhra Pradesh", "priority": 8,
     "category_slug": "e-panta", "aliases": ["e panta", "panta"]},
    {"id": "e_crop", "name": "e-Crop", "level": "state", "state": "Andhra Pradesh", "priority": 8,
     "category_slug": "e-crop", "aliases": ["e crop", "ecrop"]},
    {"id": "kalia", "name": "KALIA Yojana", "level": "state", "state": "Odisha", "priority": 7,
     "category_slug": "kalia-yojana", "aliases": ["kalia"]},
    {"id": "krishak_bandhu", "name": "Krishak Bandhu", "level": "state", "state": "West Bengal", "priority": 7,
     "category_slug": "krishak-bandhu-scheme", "aliases": ["krishak bandhu scheme"]},
    {"id": "ladli_behna", "name": "Ladli Behna Yojana", "level": "state", "state": "Madhya Pradesh", "priority": 6,
     "category_slug": "ladli-behna-yojana", "aliases": ["ladli bahan"]},
    {"id": "rajiv_kisan_nyay", "name": "Rajiv Gandhi Kisan Nyay Yojana", "level": "state", "state": "Chhattisgarh", "priority": 6,
     "category_slug": "rajiv-gandhi-kisan-nyay", "aliases": ["kisan nyay yojana"]},
    {"id": "meri_fasal", "name": "Meri Fasal Mera Byora", "level": "state", "state": "Haryana", "priority": 6,
     "category_slug": "meri-fasal-mera-byora", "aliases": ["mfmb"]},
    {"id": "pik_vima", "name": "Pik Vima", "level": "state", "state": "Maharashtra", "priority": 6,
     "category_slug": "pik-vima-scheme-maharashtra", "aliases": ["pik vima yojana"]},
    {"id": "kisan_karz_mochan", "name": "Kisan Karz Mochan Yojana", "level": "state", "state": "Uttar Pradesh", "priority": 6,
     "category_slug": "kisan-karz-mochan-yojana", "aliases": ["farm loan waiver"]},
    {"id": "pm_tractor", "name": "PM Kisan Tractor Scheme", "level": "central", "state": "", "priority": 5,
     "category_slug": "pm-kisan-tractor-scheme", "aliases": ["tractor subsidy"]},
    {"id": "dalhan_mission", "name": "Dalhan Aatmanirbharta Mission", "level": "central", "state": "", "priority": 5,
     "category_slug": "dalhan-aatmanirbharta-mission-scheme", "aliases": ["oilseeds mission"]},
    {"id": "pm_dhan_dhaanya", "name": "PM Dhan Dhaanya Krishi Yojana", "level": "central", "state": "", "priority": 5,
     "category_slug": "pm-dhan-dhaanya-krishi-yojana", "aliases": ["pmddky"]},
    {"id": "paramparagat", "name": "Paramparagat Krishi Vikas Yojana", "level": "central", "state": "", "priority": 5,
     "category_slug": "paramparagat-krishi-organic", "aliases": ["pkvy", "organic farming mission"]},
    {"id": "shetkari_sanman", "name": "Shetkari Sanman Nidhi", "level": "state", "state": "Maharashtra", "priority": 5,
     "category_slug": "shetkari-sanman-nidhi", "aliases": ["maharashtra kisan samman nidhi"]},
    {"id": "bhavantar", "name": "Bhavantar Bhugtan Yojana", "level": "state", "state": "Madhya Pradesh", "priority": 5,
     "category_slug": "bhavantar-bhugtan-yojana", "aliases": ["bhavantar bhugpaye", "price deficiency payment"]},
    {"id": "mp_kisan_kalyan", "name": "MP Mukhyamantri Kisan Kalyan Yojana", "level": "state", "state": "Madhya Pradesh", "priority": 5,
     "category_slug": "mp-kisan-kalyan-yojana", "aliases": ["mukhyamantri kisan kalyan yojana", "mp kisan kalyan"]},
    {"id": "krishi_ashirwad", "name": "Mukhyamantri Krishi Ashirwad Yojana", "level": "state", "state": "Jharkhand", "priority": 5,
     "category_slug": "mukhyamantri-krishi-ashirwad-yojana", "aliases": ["krishi ashirwad yojana", "jharkhand kisan scheme"]},
    {"id": "kisan_sahay_gujarat", "name": "Gujarat Kisan Sahay Yojana", "level": "state", "state": "Gujarat", "priority": 5,
     "category_slug": "gujarat-kisan-sahay-yojana", "aliases": ["kisan sahay gujarat", "gujarat crop damage compensation"]},
    {"id": "raitha_siri", "name": "Karnataka Raitha Siri", "level": "state", "state": "Karnataka", "priority": 4,
     "category_slug": "karnataka-raitha-siri", "aliases": ["raitha siri"]},
    {"id": "uzhavar", "name": "Tamil Nadu Uzhavar Pathukappu", "level": "state", "state": "Tamil Nadu", "priority": 4,
     "category_slug": "tamil-nadu-uzhavar-pathukappu", "aliases": ["tamil nadu uzhavar", "uzhavar pathukappu"]},
]

DEFAULT_ANGLES = [
    "installment_update",
    "status_check",
    "ekyc_update",
    "eligibility",
    "apply_process",
    "documents_required",
    "rejection_fixes",
    "latest_news",
]

ANGLE_TOPIC_TEMPLATES = {
    "installment_update": "{name} latest installment update {year}: date, amount, status",
    "status_check": "{name} status check {year}: payment, beneficiary and pending status",
    "ekyc_update": "{name} eKYC update {year}: deadline, process, common errors",
    "eligibility": "{name} eligibility criteria {year}: who can apply and who cannot",
    "apply_process": "{name} online apply process {year}: step-by-step farmer guide",
    "documents_required": "{name} required documents {year}: complete checklist",
    "rejection_fixes": "{name} rejected or payment failed: reasons and how to fix",
    "latest_news": "{name} latest news update {year}: official announcements and changes",
}

ANGLE_PATTERNS = [
    ("installment_update", [r"\binstallment\b", r"\bkist\b", r"\bpayment\b"]),
    ("status_check", [r"\bstatus\b", r"\bbeneficiary\b", r"\bcheck\b"]),
    ("ekyc_update", [r"\bekyc\b", r"\be-kyc\b", r"\baadhaar\b"]),
    ("eligibility", [r"\beligib", r"\bwho can apply\b"]),
    ("apply_process", [r"\bhow to apply\b", r"\bregistration\b", r"\bapply online\b"]),
    ("documents_required", [r"\bdocument", r"\brequired papers\b"]),
    ("rejection_fixes", [r"\breject", r"\bfailed\b", r"\berror\b"]),
]


def get_registry():
    return list(SCHEME_REGISTRY)


def get_trends_keywords(limit=40):
    rows = sorted(SCHEME_REGISTRY, key=lambda x: x.get("priority", 0), reverse=True)
    intent_suffixes = [
        "status check",
        "eligibility",
        "how to apply",
        "last date",
        "payment status",
        "beneficiary list",
        "required documents",
        "ekyc",
    ]
    out = []
    for row in rows:
        out.append(row["name"])
        out.extend(row.get("aliases", []))
        if row.get("priority", 0) >= 6:
            seed_name = row["name"].strip()
            for suffix in intent_suffixes:
                out.append(f"{seed_name} {suffix}")
    dedup = []
    seen = set()
    for kw in out:
        k = kw.strip()
        if not k:
            continue
        key = k.lower()
        if key in seen:
            continue
        seen.add(key)
        dedup.append(k)
        if len(dedup) >= limit:
            break
    return dedup


def build_watchlist_keywords():
    return get_trends_keywords(limit=200)


def find_best_scheme(text):
    blob = (text or "").lower()
    best = None
    best_score = -1
    for scheme in SCHEME_REGISTRY:
        score = 0
        for phrase in [scheme["name"]] + scheme.get("aliases", []):
            p = phrase.lower().strip()
            if p and p in blob:
                score += max(2, len(p.split()))
        if score > best_score:
            best = scheme
            best_score = score
    return best if best_score > 0 else None


def infer_content_angle(text):
    blob = (text or "").lower()
    for angle, patterns in ANGLE_PATTERNS:
        for pat in patterns:
            if re.search(pat, blob):
                return angle
    return "latest_news"


def get_category_slug_for_text(topic_title, matched_keyword=""):
    scheme = find_best_scheme(f"{topic_title or ''} {matched_keyword or ''}")
    if scheme:
        return scheme.get("category_slug", "news")
    return "news"


def build_angle_topic(scheme, angle, year=None):
    year = year or datetime.utcnow().year
    tmpl = ANGLE_TOPIC_TEMPLATES.get(angle, ANGLE_TOPIC_TEMPLATES["latest_news"])
    return tmpl.format(name=scheme["name"], year=year)

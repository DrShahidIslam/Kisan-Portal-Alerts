"""
SEO Prompt Template — Master prompt used for Gemini article generation.
Enforces SEO best practices, your site's editorial style, Kadence block HTML, and internal linking.
"""

# Categorization rules for the prompt
CATEGORY_MAPPING = [
    "pm-kisan-samman-nidhi", "pmfby", "kisan-credit-card", "kisan-vikas-patra",
    "enam-scheme", "kisan-karz-mochan-yojana", "rythu-bharosa", "soil-health-card",
    "pm-kisan-tractor-scheme", "e-crop", "pm-dhan-dhaanya-krishi-yojana",
    "dalhan-aatmanirbharta-mission-scheme", "e-panta", "pik-vima-scheme-maharashtra"
]

# Internal pages on kisanportal.org for professional Pillar-Cluster linking
INTERNAL_LINKS = {
    "pillars": [
        {"url": "https://kisanportal.org/pm-kisan-st-check/", "topic": "PM Kisan Status Check", "anchors": ["PM Kisan beneficiary status check", "check PM Kisan status online", "PM-Kisan status verify"]},
        {"url": "https://kisanportal.org/pmfby-rabi-registration-open-crop-insurance-guide/", "topic": "PMFBY Crop Insurance", "anchors": ["PMFBY crop insurance registration", "Pradhan Mantri Fasal Bima Yojana Guide", "apply for crop insurance 2026"]},
        {"url": "https://kisanportal.org/pm-tractor-hi/", "topic": "Tractor Subsidy", "anchors": ["PM Kisan Tractor Scheme", "tractor subsidy for farmers", "agricultural machinery scheme"]},
        {"url": "https://kisanportal.org/pm-kisan-samman-nidhi-22vi-kist-kab-aaegi/", "topic": "PM Kisan Installments", "anchors": ["PM Kisan 22nd installment updates", "PM-Kisan payment dates 2026", "next PM Kisan kist news"]},
    ],
    "home": {"url": "https://kisanportal.org/", "anchor": "Kisan Portal Home"}
}


def build_article_prompt(topic_title, source_texts, matched_keyword=""):
    """
    Build the master SEO prompt for Gemini article generation.
    """
    # Build source context block
    sources_block = ""
    for i, src in enumerate(source_texts[:5], 1):
        sources_block += f"""
--- SOURCE {i} ({src.get('source_domain', 'Unknown')}) ---
{src.get('text', '')[:2000]}
"""

    # Build professional internal links suggestion
    links_context = "STRATEGIC INTERNAL LINKING (Pillar-Cluster Model):\n"
    for p in INTERNAL_LINKS["pillars"]:
        links_context += f"  - Pillar Content: {p['topic']}\n"
        links_context += f"    - Target URL: {p['url']}\n"
        links_context += f"    - Recommended Anchors: {', '.join(p['anchors'])}\n"
    
    cat_mapping_str = ", ".join(CATEGORY_MAPPING)

    prompt = f"""You are a world-class SEO strategist and Indian agriculture journalist for kisanportal.org.
Your mission is to create a "Pillar Page" or highly-relevant "Cluster Article" that ranks for E-E-A-T and provides immense value to farmers.

TASK: Write a complete, publish-ready guide about: {topic_title}
PRIMARY KEYWORD: {matched_keyword or topic_title}

─── SOURCE MATERIAL ───
{sources_block}

─── SEO & CONTENT STRATEGY ───

**1. REQUIRED STRATEGIC INTERNAL LINKING:**
- You MUST include exactly 2-3 internal links from the list below.
- Integrate them naturally. Use standard HTML: <a href="URL">anchor</a>.
- Available Pillars:
{links_context}

**2. NO SEARCH METRICS:**
- ABSOLUTELY NO mentions of "Google Trends", "spike", "search volume", or "percentages".
- This is a factual portal for farmers.

**4. HTML FORMATTING:**
- Use ## for H2 headers and ### for H3 headers.
- Use * for bulleted lists.
- Bold important agriculture terms using **term**.

─── ARTICLE STRUCTURE ───
1. TITLE: Catchy SEO title (No markdown, no quotes, max 60 chars).
2. META_DESCRIPTION: Professional summary (150 chars).
3. SLUG: lowercase-kebab-case (No markdown).
4. TAGS: CSV list of 5 tags.
5. CATEGORY: ONE exact slug from: {cat_mapping_str}.
6. ---CONTENT_START---
   [Intro Paragraph]
   
   ## [Main Topic H2]
   [Detailed explanation with bullet points if helpful]
   
   ## [Section H2]
   [More details]
   
   ## Frequently Asked Questions
   
   <!-- wp:kadence/accordion {{"id":"3"}} -->
   <div class="wp-block-kadence-accordion kt-accordion-id_3">
     <!-- wp:kadence/pane {{"id":"3a","title":"Question 1?"}} -->
     <div class="wp-block-kadence-pane kt-accordion-pane-3a"><div class="kt-accordion-panel"><div class="kt-accordion-panel-inner">
       <!-- wp:paragraph --><p>Answer 1.</p><!-- /wp:paragraph -->
     </div></div></div>
     <!-- /wp:kadence/pane -->
     <!-- wp:kadence/pane {{"id":"3b","title":"Question 2?"}} -->
     <div class="wp-block-kadence-pane kt-accordion-pane-3b"><div class="kt-accordion-panel"><div class="kt-accordion-panel-inner">
       <!-- wp:paragraph --><p>Answer 2.</p><!-- /wp:paragraph -->
     </div></div></div>
     <!-- /wp:kadence/pane -->
   </div>
   <!-- /wp:kadence/accordion -->
7. ---CONTENT_END---
8. ---FAQ_START---
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "Insert Question 1",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "Insert detailed answer 1."
      }}
    }}
  ]
}}
</script>
9. ---FAQ_END---
"""
    return prompt


def build_image_prompt(topic_title, article_content_snippet=""):
    """
    Build a cinematic prompt for Gemini Imagen.
    """
    prompt = f"""Cinematic editorial photography of: {topic_title}.
Setting: Lush Indian agricultural landscape, vibrant green fields, professional lighting, 8k resolution.
Main subject: A thriving crop field or a professional farmer using digital tools.
Style: Professional National Geographic style, highly detailed, photorealistic.

CRITICAL: 
- ABSOLUTELY NO TEXT, NO LOGOS, NO LETTERS.
- NO cartoon or animation.
- High quality stock photography feel.
"""

    return prompt

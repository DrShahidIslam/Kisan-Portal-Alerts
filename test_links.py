import os
from dotenv import load_dotenv

load_dotenv()

from writer.article_generator import generate_article
from writer.seo_prompt import get_internal_links_for_prompt

topic = {
    'topic': 'PM Kisan 23rd Installment Date Expected Next Month',
    'story_hash': 'test1234',
    'matched_keyword': 'pm kisan installment'
}

print("Generating Article...")
art = generate_article(topic)

print("\n--- RESULT ---")
if art:
    print('External Links Added:', art.get('full_content', '').count('target="_blank"'))
    print('Internal links:', art.get('quality_snapshot', {}).get('internal_links', 'N/A'))
else:
    print("Article generation failed")

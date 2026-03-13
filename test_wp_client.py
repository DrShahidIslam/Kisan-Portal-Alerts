import sys
import os
from dotenv import load_dotenv

load_dotenv()

from publisher.wordpress_client import create_post, update_post_status

# Test with a mock article
article = {
    'title': 'Test Article For internal links appended ' + os.urandom(4).hex(),
    'content': 'This is a test article content here. It has 2 to 3 internal links.',
    'slug': 'test-article-internal-links-' + os.urandom(4).hex(),
    'category': 'news',
    'status': 'publish'
}

print(f"Creating article: {article['title']}")
result = create_post(article, status='publish')

if result:
    print("Success create_post!")
    print(result)
else:
    print("Failed create_post.")

print("\n--- Checking published_posts.json ---")
try:
    with open('published_posts.json', 'r') as f:
        print(f.read()[-300:])
except Exception as e:
    print(e)

import json
import logging

import requests
from django.conf import settings

logger = logging.getLogger('autobiz')

API_URL = 'https://api.openai.com/v1/chat/completions'


class OpenAIClient:
    """Thin wrapper around the OpenAI Chat Completions API."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL or 'gpt-4o'

    def chat(self, user_message: str, system_message: str = '', max_tokens: int = 4096) -> str:
        """Send a single-turn chat request and return the assistant's text ('' on failure)."""
        if not self.api_key or self.api_key == 'YOUR_OPENAI_API_KEY_HERE':
            logger.warning('[OpenAIClient] No API key set — returning stub response.')
            return self._stub_response(system_message)

        messages = []
        if system_message:
            messages.append({'role': 'system', 'content': system_message})
        messages.append({'role': 'user', 'content': user_message})

        try:
            resp = requests.post(
                API_URL,
                headers={'Authorization': f'Bearer {self.api_key}'},
                json={
                    'model': self.model,
                    'messages': messages,
                    'max_tokens': max_tokens,
                    'temperature': 0.7,
                },
                timeout=120,
            )
            body = resp.json()
        except (requests.RequestException, ValueError) as e:
            logger.error('[OpenAIClient] HTTP request failed: %s', e)
            return ''

        if 'error' in body:
            logger.error('[OpenAIClient] API error: %s', (body['error'] or {}).get('message', 'unknown'))
            return ''

        try:
            return body['choices'][0]['message']['content'] or ''
        except (KeyError, IndexError, TypeError):
            return ''

    # ── Local-dev stubs (used when no API key is configured) ───────────────

    def _stub_response(self, system_message: str) -> str:
        # Agents that want JSON say so in their system message; the Design agent wants HTML.
        if 'json' not in system_message.lower():
            return STUB_HTML

        return json.dumps({
            'business_summary': 'A beloved local restaurant serving authentic cuisine.',
            'target_audience': 'Families and food lovers in the local area.',
            'branding_notes': 'Warm, inviting, community-focused branding.',
            'usp': 'Fresh ingredients, family recipes, unbeatable hospitality.',
            'tone': 'friendly',
            'color_palette': '#FF6B35, #F7C59F, #EFEFD0',
            'keywords': ['local restaurant', 'fresh food', 'family dining', 'authentic cuisine', 'best restaurant'],
            'hero_headline': 'Taste the Tradition',
            'hero_subheadline': 'Fresh, local, and made with love every single day.',
            'about_text': 'We have been serving our community for years with passion.',
            'menu_teaser': [
                {'name': 'Signature Biryani', 'description': 'Aromatic rice with tender meat'},
                {'name': 'Tandoori Platter', 'description': 'Smoky grilled favourites'},
                {'name': 'Mango Lassi', 'description': 'Refreshing traditional drink'},
            ],
            'cta_text': 'Reserve a Table',
            'footer_tagline': 'Good food. Good mood.',
            'page_title': 'Stub Restaurant — Best Food in Town',
        })


STUB_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stub Restaurant</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-white text-gray-800">
  <header class="bg-orange-600 text-white py-20 text-center">
    <h1 class="text-5xl font-bold">Taste the Tradition</h1>
    <p class="mt-4 text-xl">Fresh, local, and made with love every single day.</p>
    <a href="#contact" class="mt-8 inline-block bg-white text-orange-600 font-bold py-3 px-8 rounded-full">Reserve a Table</a>
  </header>
  <section class="py-16 px-8 max-w-4xl mx-auto">
    <h2 class="text-3xl font-bold mb-4">About Us</h2>
    <p class="text-gray-600">We have been serving our community for years with passion and fresh ingredients.</p>
  </section>
  <section class="bg-gray-50 py-16 px-8 text-center">
    <h2 class="text-3xl font-bold mb-8">Featured Dishes</h2>
    <div class="grid grid-cols-3 gap-8 max-w-4xl mx-auto">
      <div class="bg-white shadow p-6 rounded-lg">
        <img src="https://placehold.co/400x300" class="w-full rounded mb-4" alt="Dish">
        <h3 class="font-bold text-lg">Signature Biryani</h3>
        <p class="text-gray-500 text-sm">Aromatic rice with tender meat</p>
      </div>
      <div class="bg-white shadow p-6 rounded-lg">
        <img src="https://placehold.co/400x300" class="w-full rounded mb-4" alt="Dish">
        <h3 class="font-bold text-lg">Tandoori Platter</h3>
        <p class="text-gray-500 text-sm">Smoky grilled favourites</p>
      </div>
      <div class="bg-white shadow p-6 rounded-lg">
        <img src="https://placehold.co/400x300" class="w-full rounded mb-4" alt="Dish">
        <h3 class="font-bold text-lg">Mango Lassi</h3>
        <p class="text-gray-500 text-sm">Refreshing traditional drink</p>
      </div>
    </div>
  </section>
  <footer id="contact" class="bg-orange-600 text-white py-12 text-center">
    <p class="text-2xl font-bold">Good food. Good mood.</p>
    <p class="mt-2">Call us: +91-9876543210 | 123 Main Street</p>
  </footer>
</body>
</html>"""

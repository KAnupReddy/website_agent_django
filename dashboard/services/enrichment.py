import logging

from ..models import Business, Enrichment
from .openai_client import OpenAIClient
from .utils import parse_json_response

logger = logging.getLogger('autobiz')


class EnrichmentAgent:
    """Uses GPT to enrich business data with branding, audience, and business insights."""

    def __init__(self):
        self.ai = OpenAIClient()

    def enrich(self, business_id: int) -> bool:
        business = Business.objects.filter(pk=business_id).first()
        if not business:
            logger.error('[EnrichmentAgent] Business #%s not found.', business_id)
            return False

        logger.info('[EnrichmentAgent] Enriching: %s', business.name)

        response = self.ai.chat(
            self._build_prompt(business),
            'You are a business branding strategist. Respond only in valid JSON.',
        )
        parsed = parse_json_response(response)
        if not parsed:
            logger.error('[EnrichmentAgent] Failed to parse GPT response for #%s', business_id)
            return False

        keywords = parsed.get('keywords')
        if keywords is not None and not isinstance(keywords, list):
            keywords = [keywords]

        Enrichment.objects.create(
            business=business,
            business_summary=parsed.get('business_summary'),
            target_audience=parsed.get('target_audience'),
            branding_notes=parsed.get('branding_notes'),
            usp=parsed.get('usp'),
            tone=parsed.get('tone'),
            color_palette=parsed.get('color_palette'),
            keywords=','.join(str(k) for k in keywords) if keywords is not None else None,
            raw_gpt_response=response,
        )

        business.status = Business.Status.ENRICHED
        business.save(update_fields=['status', 'updated_at'])
        return True

    def _build_prompt(self, b: Business) -> str:
        def v(x):
            return '' if x is None else x

        return f"""Analyze this business and return a JSON object with these fields:
- business_summary: 2-3 sentence description of the business
- target_audience: who their ideal customers are
- branding_notes: visual/tone branding suggestions
- usp: unique selling proposition (1 sentence)
- tone: one word tone (e.g. friendly, luxurious, professional, vibrant)
- color_palette: suggested 3 hex colors as a string, e.g. "#FF5733, #C70039, #900C3F"
- keywords: array of 5 SEO keywords

Business data:
Name: {b.name}
Type: {v(b.business_type)}
Category / Niche: {v(b.category)}
Location: {b.location}
Rating: {v(b.rating)} ({b.review_count} reviews)
Address: {v(b.address)}"""

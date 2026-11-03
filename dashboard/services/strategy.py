import logging

from ..models import Business, Enrichment
from .openai_client import OpenAIClient
from .utils import parse_json_response

logger = logging.getLogger('autobiz')


class StrategyAgent:
    """Generates website content strategy (headlines, copy, sections) per business."""

    def __init__(self):
        self.ai = OpenAIClient()

    def strategize(self, business_id: int):
        """Return the content strategy dict consumed by the DesignAgent, or None."""
        business = Business.objects.filter(pk=business_id).first()
        enrichment = Enrichment.objects.filter(business_id=business_id).order_by('id').first()

        if not business or not enrichment:
            logger.error('[StrategyAgent] Missing data for business #%s', business_id)
            return None

        logger.info('[StrategyAgent] Building content strategy for: %s', business.name)

        response = self.ai.chat(
            self._build_prompt(business, enrichment),
            'You are a business website copywriter. Respond only in valid JSON.',
        )
        return parse_json_response(response)

    def _build_prompt(self, b: Business, e: Enrichment) -> str:
        def v(x):
            return '' if x is None else x

        return f"""Create website content for this business. Return a JSON object with:
- hero_headline: punchy main headline (max 8 words)
- hero_subheadline: supporting subtitle (max 15 words)
- about_text: 2 paragraphs about the business
- services_teaser: 3-4 featured services or products with one-line descriptions
- cta_text: call-to-action button text (e.g. "Book a Consultation", "Order Now", "Get a Quote")
- footer_tagline: short brand tagline
- page_title: SEO page title

Business: {b.name}
Type: {v(b.business_type)}
Category: {v(b.category)}
Location: {b.location}
USP: {v(e.usp)}
Tone: {v(e.tone)}
Audience: {v(e.target_audience)}
Keywords: {v(e.keywords)}"""

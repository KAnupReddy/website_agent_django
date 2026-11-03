import html
import logging
import re
from urllib.parse import urlparse

import requests

from ..models import Business, Design, Enrichment
from .design_styles import STYLES
from .openai_client import OpenAIClient
from .utils import text

logger = logging.getLogger('autobiz')

SYSTEM_PROMPT = (
    'You are an elite full-stack developer and UI/UX designer whose work rivals Stripe, Linear, and Vercel. '
    'You build stunning, production-quality websites that clients pay $15,000+ for. '
    'CRITICAL RULES: (1) Use ONLY CSS variables (var(--*)) for all colors — zero hardcoded hex in your CSS. '
    '(2) Build EVERY section in the page blueprint — no shortcuts, no omissions, no placeholder sections. '
    '(3) Make the hero visually spectacular: large h1, layered elements, depth, decorative backgrounds. '
    '(4) Zero Lorem ipsum — every word must be real business content. '
    '(5) The JS script block is pre-written — paste it VERBATIM before </body>. '
    'Output ONLY raw HTML starting with <!DOCTYPE html>. No markdown, no code fences, no explanations.'
)

JS_BLOCK = """<script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/vanilla-tilt/1.8.0/vanilla-tilt.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
  AOS.init({duration:800, once:true, easing:'ease-out-cubic', offset:80});

  var tiltEls = document.querySelectorAll('.tilt-card');
  if (tiltEls.length) VanillaTilt.init(tiltEls, {max:10, speed:400, glare:true, 'max-glare':0.12});

  gsap.registerPlugin(ScrollTrigger);

  var navEl = document.querySelector('nav, header');
  if (navEl) gsap.from(navEl, {y:-60, opacity:0, duration:0.6, ease:'power2.out'});

  var hero = document.querySelector('section');
  if (hero) {
    var heroEls = hero.querySelectorAll('h1, h2, p, a, button, .chip, .eyebrow, .tag, .ed-label, .label-sm');
    if (heroEls.length) gsap.from(heroEls, {y:40, opacity:0, duration:0.8, stagger:0.1, ease:'power2.out', delay:0.3});
  }

  document.querySelectorAll('.counter[data-target]').forEach(function(el) {
    var tgt = parseFloat(el.getAttribute('data-target'));
    var sfx = el.getAttribute('data-suffix') || '';
    ScrollTrigger.create({
      trigger: el, start: 'top 85%', once: true,
      onEnter: function() {
        gsap.to({val:0}, {val:tgt, duration:2.2, ease:'power1.out', onUpdate: function() {
          var v = Math.round(this.targets()[0].val);
          el.textContent = (v >= 1000 ? v.toLocaleString() : v) + sfx;
        }});
      }
    });
  });

  window.addEventListener('scroll', function() {
    var sy = window.scrollY;
    var n = document.querySelector('nav, header');
    if (n) {
      n.style.boxShadow = sy > 50 ? '0 2px 24px rgba(0,0,0,0.12)' : '';
      n.style.backdropFilter = sy > 80 ? 'blur(20px)' : '';
      n.style.webkitBackdropFilter = sy > 80 ? 'blur(20px)' : '';
    }
    if (sy < window.innerHeight) {
      document.querySelectorAll('[data-parallax]').forEach(function(el) {
        el.style.transform = 'translateY(' + (sy * (parseFloat(el.getAttribute('data-parallax')) || 0.12)) + 'px)';
      });
    }
  });

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
      });
    }, {threshold: 0.12});
    document.querySelectorAll('.anim-in').forEach(function(el) { io.observe(el); });
  }
});
</script>"""


class DesignAgent:
    """Generates one complete single-page website per style in STYLES."""

    styles = STYLES

    def __init__(self):
        self.ai = OpenAIClient()

    def generate(self, business_id: int, content: dict) -> list[int]:
        """Create a draft Design per style and return the new design IDs."""
        business = Business.objects.filter(pk=business_id).first()
        enrichment = Enrichment.objects.filter(business_id=business_id).order_by('id').first()

        if not business or not enrichment:
            logger.error('[DesignAgent] Missing data for #%s', business_id)
            return []

        site_info = self.extract_site_info((business.website_url or '').strip())

        logger.info('[DesignAgent] Generating %d designs for: %s', len(self.styles), business.name)

        design_ids = []
        for version, style in enumerate(self.styles, start=1):
            logger.info('[DesignAgent] Design #%d: %s', version, style['name'])

            page = self._generate_design(business, content, style, site_info)
            if not page:
                logger.warning('[DesignAgent] Skipped #%d', version)
                continue

            design = Design.objects.create(
                business=business,
                version=version,
                style_name=style['name'],
                html_code=page,
                css_framework='custom',
                status=Design.Status.DRAFT,
            )
            design_ids.append(design.id)

        return design_ids

    def _generate_design(self, b, content, style, site_info):
        page = self.ai.chat(self.build_prompt(b, content, style, site_info), SYSTEM_PROMPT, 16000)
        if not page or '<html' not in page.lower():
            return None
        return page

    def build_prompt(self, b: Business, c: dict, style: dict, site_info: dict) -> str:
        teaser = c.get('services_teaser') or c.get('menu_teaser') or []
        if isinstance(teaser, dict):
            teaser = [{'name': k, 'description': v} for k, v in teaser.items()]
        services = ''
        for item in teaser:
            if isinstance(item, dict):
                n, d = text(item.get('name')), text(item.get('description'))
            else:
                n, d = text(item), ''
            services += f'  • {n}' + (f': {d}' if d else '') + '\n'

        name = b.name
        biz_type = (b.business_type or '') + (f' — {b.category}' if b.category else '')
        phone = b.phone or 'Contact us'
        address = b.address or b.location
        email = b.email or ''
        headline = text(c.get('hero_headline', ''))
        sub = text(c.get('hero_subheadline', ''))
        about = text(c.get('about_text', ''))
        cta = text(c.get('cta_text', 'Get Started'))
        tagline = text(c.get('footer_tagline', ''))
        page_title = text(c.get('page_title', name))

        img_palette = style.get('img_palette') or '808080/FFFFFF'

        url = site_info.get('url', '')
        if url:
            mode_block = f'IMPROVEMENT MODE — client has existing site: {url}\n'
            if site_info['fetched']:
                mode_block += f"Existing title: {site_info['title']}\n"
                if site_info['theme_color']:
                    mode_block += f"Brand color: {site_info['theme_color']}\n"
                if site_info['text']:
                    mode_block += f"Site text: {site_info['text']}\n→ Use any real names/services/details found above.\n"
            mode_block += 'Redesign dramatically — 10× better than their current site.\n'
        else:
            mode_block = 'FRESH DESIGN — create stunning new website from scratch.'

        return f"""You are building a world-class single-page website. Follow every instruction exactly.

{mode_block}

═══ CONCEPT ═══
{style['concept']}

═══ REQUIRED CDN LINKS — paste ALL in <head> ═══
{self.cdn_links(style)}

═══ REQUIRED CSS FOUNDATION — paste VERBATIM as first content of your <style> block ═══
After pasting this foundation, write your own CSS below it for nav layout, hero layout,
grids, flexbox, section-specific styles, etc.
RULE: Use ONLY the CSS custom properties (var(--bg), var(--prim), etc.) for all colors.
Never hardcode a hex value in your own CSS — always use var(--*).
{style['css_foundation']}

═══ PAGE BLUEPRINT — build every section exactly as described ═══
{style['page_blueprint']}

═══ BUSINESS DATA — fill into every section ═══
Business: {name}
Type: {biz_type}
Location: {b.location}
Phone: {phone}
Address: {address}
Email: {email}
Page Title: {page_title}
Hero Headline: {headline}
Hero Subheadline: {sub}
About: {about}
CTA: {cta}
Tagline: {tagline}
Services:
{services}

═══ QUALITY STANDARD — YOU MUST HIT 10/10 ═══
Every website you generate is a portfolio showcase judged on these criteria:

HERO (must score high): h1 MUST be large (6rem+ desktop), bold, immediate impact in 3 seconds.
Hero MUST have visual layers: (a) decorative background element (gradient orb/grid/blob), (b) large
typographic column left, (c) visual column right with image + overlapping floating stat card.
Real business stats (3 numbers) displayed below CTAs. Nothing flat — no single-column text hero.

TYPOGRAPHY: Dramatic size contrast. h1 vs body = 5:1 minimum ratio. Numbers (.num-big / .num-vel /
.num-canvas / .num-obs / .num-ed) are the LARGEST non-heading text on the page.

VISUAL DEPTH: Sections alternate background colors (--bg, --surface, --card). Decorative background
elements (gradient orbs, grid patterns, diagonal lines, blob shapes) on hero and CTA sections.

SECTION VARIETY: Each section has a DISTINCT layout — not all the same card grid. Mix:
full-bleed columns, card grids, horizontal bands, alternating image+text, testimonial rows.

HOVER POLISH: Every card has hover with transform:translateY(-4px) + shadow + border-color change.
Every button transitions smoothly with box-shadow and translateY(-2px).

COLOR DISCIPLINE: 100% CSS variables. Zero hardcoded hex values in your own CSS rules.

CONTENT: Zero Lorem ipsum. Every word uses real business data. Manufacture believable specifics:
real-sounding stats, real-sounding testimonial quotes, real service descriptions.

TARGET QUALITY: Stripe.com, Linear.app, Vercel.com — not a WordPress template.

═══ ANIMATION HOOKS ═══
• Scroll reveal on any element: data-aos="fade-up" (or fade-left, fade-right, zoom-in)
• Stagger: data-aos-delay="100" (ms). All AOS elements auto-animate on scroll.
• Stat counters: class="counter" data-target="NUMBER" data-suffix="+"
• 3D card tilt: class="tilt-card" on any card

═══ REQUIRED SCRIPT BLOCK — paste VERBATIM before </body> ═══
{JS_BLOCK}

═══ FINAL RULES ═══
1. <style> block: start with the CSS foundation (verbatim), then your layout CSS
2. All colors via var(--*) variables only — no hardcoded hex in your own CSS
3. Follow the page blueprint — every section, every detail described
4. Fill all text with real business data — zero Lorem ipsum
5. Image placeholders: https://placehold.co/WIDTHxHEIGHT/{img_palette}?text=BusinessName (e.g. /480x560/{img_palette})
6. Mobile responsive: add @media(max-width:768px) rules for all grids and layouts
7. Paste the script block verbatim before </body>
8. Output ONLY raw HTML starting with <!DOCTYPE html>"""

    @staticmethod
    def cdn_links(style: dict) -> str:
        return (
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link href="{style["fonts_href"]}" rel="stylesheet">\n'
            '<link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">'
        )

    @staticmethod
    def extract_site_info(url: str) -> dict:
        """Fetch an existing website and pull out title, theme colour, palette and text."""
        info = {'url': url, 'fetched': False, 'title': '', 'description': '',
                'theme_color': '', 'colors': [], 'text': '', 'html_snippet': ''}

        parsed = urlparse(url)
        if not url or parsed.scheme not in ('http', 'https') or not parsed.netloc:
            return info

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html',
        }
        try:
            try:
                resp = requests.get(url, headers=headers, timeout=15)
            except requests.exceptions.SSLError:
                resp = requests.get(url, headers=headers, timeout=15, verify=False)
            raw = resp.text
        except requests.RequestException:
            raw = ''

        if not raw:
            logger.info('[DesignAgent] Could not fetch: %s', url)
            return info

        info['fetched'] = True

        m = re.search(r'<title[^>]*>(.*?)</title>', raw, re.I | re.S)
        if m:
            info['title'] = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()

        m = re.search(r'<meta[^>]+name=["\']theme-color["\'][^>]+content=["\']([^"\']+)', raw, re.I)
        if m:
            info['theme_color'] = m.group(1).strip()

        colors = list(dict.fromkeys(c.lower() for c in re.findall(r'#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', raw)))
        info['colors'] = [c for c in colors if 30 < _brightness(c) < 230][:6]

        stripped = re.sub(r'<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<!--.*?-->', '', raw, flags=re.I | re.S)
        stripped = html.unescape(re.sub(r'<[^>]+>', ' ', stripped))
        info['text'] = re.sub(r'\s+', ' ', stripped).strip()[:600]

        return info


def _brightness(hex_color: str) -> float:
    h = hex_color.lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r * 299 + g * 587 + b * 114) / 1000

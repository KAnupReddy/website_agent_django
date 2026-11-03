"""
UML diagram toolkit, the project's diagrams, and helpers that read facts
(models, routes, settings keys, design styles) straight from the code.
Used by build_project_doc.py.
"""

import math
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autobiz.settings')

import django  # noqa: E402

django.setup()

from reportlab.graphics.shapes import Circle, Drawing, Ellipse, Line, Polygon, PolyLine, Rect, String  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402

from dashboard.services.design_styles import STYLES  # noqa: E402

# Diagrams are drawn on this width and scaled to the page frame when placed.
FRAME_W = 487

# ─── Fonts & palette ───────────────────────────────────────────────────────

FONT_DIR = Path(os.environ.get('WINDIR', r'C:\Windows')) / 'Fonts'
pdfmetrics.registerFont(TTFont('UI', str(FONT_DIR / 'segoeui.ttf')))
pdfmetrics.registerFont(TTFont('UI-Bold', str(FONT_DIR / 'segoeuib.ttf')))
pdfmetrics.registerFont(TTFont('UI-Semi', str(FONT_DIR / 'seguisb.ttf')))
pdfmetrics.registerFont(TTFont('Mono', str(FONT_DIR / 'consola.ttf')))
pdfmetrics.registerFontFamily('UI', normal='UI', bold='UI-Bold', italic='UI', boldItalic='UI-Bold')

BRAND = colors.HexColor('#006BA7')
NAVY = colors.HexColor('#003756')
INK = colors.HexColor('#1E293B')
MUTED = colors.HexColor('#64748B')
RULE = colors.HexColor('#CBD5E1')
LIGHT = colors.HexColor('#F1F5F9')
TINT = colors.HexColor('#E6F1F8')
EDGE = colors.HexColor('#475569')
GOOD = colors.HexColor('#15803D')
WARN = colors.HexColor('#B45309')
BAD = colors.HexColor('#B91C1C')
WHITE = colors.white



# ─── Diagram toolkit (top-down coordinates) ────────────────────────────────

class Dia:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.d = Drawing(w, h)

    def Y(self, t):
        return self.h - t

    def text(self, x, t, s, size=7, font='UI', color=INK, anchor='start'):
        self.d.add(String(x, self.Y(t), s, fontName=font, fontSize=size, fillColor=color, textAnchor=anchor))

    def rect(self, x, t, w, h, fill=None, stroke=EDGE, sw=0.8, r=3, dash=None):
        self.d.add(Rect(x, self.Y(t + h), w, h, rx=r, ry=r, fillColor=fill, strokeColor=stroke,
                        strokeWidth=sw, strokeDashArray=dash))

    def line(self, pts, color=EDGE, sw=0.8, dash=None, head=None, tail=None, size=5):
        flat = []
        for x, t in pts:
            flat += [x, self.Y(t)]
        self.d.add(PolyLine(flat, strokeColor=color, strokeWidth=sw, strokeDashArray=dash))
        if head:
            self._end(pts[-2], pts[-1], head, color, size)
        if tail:
            self._end(pts[1], pts[0], tail, color, size)

    def _end(self, a, b, kind, color, size):
        (x1, t1), (x2, t2) = a, b
        y1, y2 = self.Y(t1), self.Y(t2)
        ang = math.atan2(y2 - y1, x2 - x1)
        if kind == 'diamond':
            s = size * 1.1
            p = [x2, y2,
                 x2 - s * math.cos(ang - 0.5), y2 - s * math.sin(ang - 0.5),
                 x2 - 2 * s * math.cos(ang), y2 - 2 * s * math.sin(ang),
                 x2 - s * math.cos(ang + 0.5), y2 - s * math.sin(ang + 0.5)]
            self.d.add(Polygon(p, fillColor=color, strokeColor=color, strokeWidth=0.6))
            return
        p1 = (x2 - size * math.cos(ang - 0.42), y2 - size * math.sin(ang - 0.42))
        p2 = (x2 - size * math.cos(ang + 0.42), y2 - size * math.sin(ang + 0.42))
        if kind == 'open':
            self.d.add(Line(x2, y2, *p1, strokeColor=color, strokeWidth=0.8))
            self.d.add(Line(x2, y2, *p2, strokeColor=color, strokeWidth=0.8))
        else:
            self.d.add(Polygon([x2, y2, *p1, *p2], fillColor=color, strokeColor=color, strokeWidth=0.5))

    def box(self, x, t, w, h, title, lines=(), fill=WHITE, stroke=EDGE, title_color=INK, size=7.4,
            line_size=6.4, sw=0.8, dash=None, stereo=None, r=4):
        """A rounded box with a centred bold title and optional centred body lines."""
        self.rect(x, t, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash, r=r)
        n = len(lines) + (1 if stereo else 0)
        block = size + n * (line_size + 2.4)
        y0 = t + (h - block) / 2 + size - 0.5
        cx = x + w / 2
        if stereo:
            self.text(cx, y0, f'«{stereo}»', line_size, 'UI', MUTED, 'middle')
            y0 += line_size + 2.4
        self.text(cx, y0, title, size, 'UI-Bold', title_color, 'middle')
        for i, ln in enumerate(lines):
            self.text(cx, y0 + (i + 1) * (line_size + 2.4), ln, line_size, 'UI', MUTED, 'middle')

    def uml_class(self, x, t, w, name, attrs, methods=(), stereo=None, header_fill=TINT):
        lh, fs = 8.7, 6.5
        hh = 16 + (8 if stereo else 0)
        ah = 5 + len(attrs) * lh
        mh = (5 + len(methods) * lh) if methods else 6
        total = hh + ah + mh
        self.rect(x, t, w, total, fill=WHITE, stroke=EDGE, r=2)
        self.rect(x, t, w, hh, fill=header_fill, stroke=EDGE, r=2)
        if stereo:
            self.text(x + w / 2, t + 9, f'«{stereo}»', 6, 'UI', MUTED, 'middle')
        self.text(x + w / 2, t + hh - 5, name, 8, 'UI-Bold', NAVY, 'middle')
        for i, a in enumerate(attrs):
            self.text(x + 5, t + hh + 3 + (i + 1) * lh - 1.5, a, fs, 'Mono', INK)
        self.d.add(Line(x, self.Y(t + hh + ah), x + w, self.Y(t + hh + ah), strokeColor=EDGE, strokeWidth=0.6))
        for i, m in enumerate(methods):
            self.text(x + 5, t + hh + ah + 3 + (i + 1) * lh - 1.5, m, fs, 'Mono', INK)
        return total

    def diamond(self, cx, ct, w, h, label, size=6.6):
        p = [cx, self.Y(ct - h / 2), cx + w / 2, self.Y(ct), cx, self.Y(ct + h / 2), cx - w / 2, self.Y(ct)]
        self.d.add(Polygon(p, fillColor=WHITE, strokeColor=EDGE, strokeWidth=0.8))
        self.text(cx, ct + size / 3, label, size, 'UI', INK, 'middle')

    def dot(self, cx, ct, r=5, final=False):
        if final:
            self.d.add(Circle(cx, self.Y(ct), r + 2.5, fillColor=WHITE, strokeColor=INK, strokeWidth=0.9))
        self.d.add(Circle(cx, self.Y(ct), r, fillColor=INK, strokeColor=INK))

    def ellipse(self, cx, ct, rx, ry, label, size=7):
        self.d.add(Ellipse(cx, self.Y(ct), rx, ry, fillColor=TINT, strokeColor=BRAND, strokeWidth=0.8))
        self.text(cx, ct + size / 3, label, size, 'UI', INK, 'middle')

    def actor(self, cx, t, name, size=7):
        y = self.Y
        self.d.add(Circle(cx, y(t + 6), 5.5, fillColor=WHITE, strokeColor=INK, strokeWidth=0.9))
        self.d.add(Line(cx, y(t + 11.5), cx, y(t + 30), strokeColor=INK, strokeWidth=0.9))
        self.d.add(Line(cx - 10, y(t + 18), cx + 10, y(t + 18), strokeColor=INK, strokeWidth=0.9))
        self.d.add(Line(cx, y(t + 30), cx - 8, y(t + 42), strokeColor=INK, strokeWidth=0.9))
        self.d.add(Line(cx, y(t + 30), cx + 8, y(t + 42), strokeColor=INK, strokeWidth=0.9))
        for i, part in enumerate(name.split('\n')):
            self.text(cx, t + 53 + i * 8.5, part, size, 'UI-Semi', INK, 'middle')

    def node(self, x, t, w, h, title, stereo=None, depth=7, fill=WHITE):
        """UML deployment node (3-D box)."""
        y = self.Y
        top = Polygon([x, y(t), x + depth, y(t - depth), x + w + depth, y(t - depth), x + w, y(t)],
                      fillColor=LIGHT, strokeColor=EDGE, strokeWidth=0.8)
        side = Polygon([x + w, y(t), x + w + depth, y(t - depth), x + w + depth, y(t + h - depth), x + w, y(t + h)],
                       fillColor=RULE, strokeColor=EDGE, strokeWidth=0.8)
        self.d.add(top)
        self.d.add(side)
        self.rect(x, t, w, h, fill=fill, stroke=EDGE, r=0)
        yy = t + 10
        if stereo:
            self.text(x + 6, yy, f'«{stereo}»', 6, 'UI', MUTED)
            yy += 9
        self.text(x + 6, yy, title, 7.4, 'UI-Bold', NAVY)

    def frame(self, x, t, w, h, tag, guard=''):
        self.rect(x, t, w, h, fill=None, stroke=MUTED, sw=0.7, r=0)
        tw = 6 + len(tag) * 4.6
        self.d.add(Polygon([x, self.Y(t), x + tw + 6, self.Y(t), x + tw + 6, self.Y(t + 7), x + tw, self.Y(t + 11),
                            x, self.Y(t + 11)], fillColor=LIGHT, strokeColor=MUTED, strokeWidth=0.7))
        self.text(x + 4, t + 8.5, tag, 6.6, 'UI-Bold', INK)
        if guard:
            self.text(x + tw + 12, t + 8.5, guard, 6.4, 'UI', MUTED)


# ─── Diagrams ──────────────────────────────────────────────────────────────

def pipeline_glance():
    g = Dia(FRAME_W, 78)
    steps = [('Enrichment', 'branding JSON'), ('Strategy', 'site copy JSON'), ('Design ×5', 'HTML per style'),
             ('Build', 'files on disk'), ('Hosting', 'FTP (off)'), ('Outreach', 'email (off)')]
    bw, gap = 70, (FRAME_W - 6 * 70) / 5
    for i, (name, sub) in enumerate(steps):
        x = i * (bw + gap)
        off = i >= 4
        g.box(x, 18, bw, 40, name, [sub], fill=LIGHT if off else TINT, stroke=MUTED if off else BRAND,
              title_color=MUTED if off else NAVY, dash=(3, 2) if off else None)
        if i < 5:
            g.line([(x + bw + 1, 38), (x + bw + gap - 1, 38)], head='filled', dash=(2, 2) if i >= 3 else None)
    g.text(0, 9, 'Orchestrator.process_business(id)', 7, 'UI-Semi', MUTED)
    g.text(FRAME_W, 72, 'dashed = implemented but disabled in the pipeline', 6.4, 'UI', MUTED, 'end')
    return g.d


def component_diagram():
    g = Dia(FRAME_W, 420)
    W = FRAME_W
    # actors / entry points
    g.box(20, 6, 150, 34, 'Operator web browser', ['dashboard pages, forms, ZIP download'], fill=LIGHT)
    g.box(200, 6, 175, 34, 'Command line', ['run.bat · run_pipeline.bat · manage.py'], fill=LIGHT)
    # Django container
    cx0, ct0, cw, ch = 8, 58, 375, 266
    g.rect(cx0, ct0, cw, ch, fill=None, stroke=BRAND, sw=1.1, r=6)
    g.text(cx0 + cw - 8, ct0 + 13, 'Django project — autobiz + dashboard app', 7.2, 'UI-Bold', BRAND, 'end')
    bw, bh = 108, 48
    xs = [cx0 + 12, cx0 + 12 + bw + 13.5, cx0 + 12 + 2 * (bw + 13.5)]
    r1, r2, r3 = ct0 + 24, ct0 + 96, ct0 + 192
    g.box(xs[0], r1, bw, bh, 'URL routing', ['autobiz/urls.py', 'dashboard/urls.py'])
    g.box(xs[1], r1, bw, bh, 'Views + forms', ['views.py · forms.py', 'ui.py (badges, labels)'])
    g.box(xs[2], r1, bw, bh, 'Templates', ['layouts/main.html', 'dashboard/*.html (Tailwind)'])
    g.box(xs[0], r2, bw, bh + 30, 'Management', ['agent_run', 'import_legacy', 'ensure_database'])
    g.box(xs[1], r2, bw * 2 + 13.5, bh + 30, 'Services — the agent pipeline',
          ['Orchestrator → Enrichment → Strategy → Design → Build',
           'Hosting (FTP) · Outreach (SMTP) — wired but disabled',
           'OpenAIClient · design_styles.STYLES (5 styles)'], fill=TINT, stroke=BRAND)
    g.box(xs[0], r3, bw, bh + 10, 'Admin', ['/admin — all 5 models'])
    g.box(xs[1], r3, bw, bh + 10, 'Models / ORM', ['Business · Enrichment', 'Design · Deployment · Email'])
    g.box(xs[2], r3, bw, bh + 10, 'Settings', ['autobiz/settings.py', '.env via python-dotenv', 'mysql_legacy backend'])
    # storage
    g.box(20, 350, 160, 44, 'MariaDB / MySQL', ['autobiz_ai_django (or SQLite)'], stereo='database', fill=LIGHT)
    g.box(200, 350, 175, 44, 'File system', ['writable/builds/<slug>/v<N>_<style>.html', 'writable/logs/autobiz.log'],
          fill=LIGHT)
    # externals
    ex = W - 92
    g.text(ex + 46, 52, 'External systems', 7.2, 'UI-Bold', MUTED, 'middle')
    ext = [('OpenAI API', 'chat completions'), ('Client website', 'HTTP fetch (redesign)'),
           ('SMTP server', 'outreach email'), ('FTP host', 'demo hosting'), ('CI4 database', 'autobiz_ai (legacy)')]
    for i, (n, s) in enumerate(ext):
        g.box(ex, 62 + i * 52, 92, 38, n, [s], fill=LIGHT, stereo='external' if i < 4 else 'database')
    # arrows: entry points
    g.line([(74, 40), (74, r1)], head='filled')
    g.text(78, 54, 'HTTP :8000', 6.2, 'UI', MUTED)
    lane = xs[0] + bw + 6.75  # the gap between the first and second column
    g.line([(215, 40), (215, 48), (lane, 48), (lane, r2 + 20), (xs[0] + bw, r2 + 20)], head='filled', dash=(3, 2))
    # inside the project
    g.line([(xs[0] + bw, r1 + 16), (xs[1], r1 + 16)], head='filled', size=4)
    g.line([(xs[1] + bw, r1 + 24), (xs[2], r1 + 24)], head='filled', size=4)
    g.line([(xs[1] + 54, r1 + bh), (xs[1] + 54, r2)], head='filled', size=4)
    g.line([(xs[0] + bw, r2 + 56), (xs[1], r2 + 56)], head='filled', size=4)
    g.line([(xs[1] + 54, r2 + bh + 30), (xs[1] + 54, r3)], head='filled', size=4)
    g.line([(xs[0] + bw, r3 + 29), (xs[1], r3 + 29)], head='filled', size=4)
    # to external systems
    sx, sy = xs[1] + 2 * bw + 13.5, r2 + 39
    for i, t in enumerate((81, 133, 185, 237)):
        g.line([(sx, sy), (ex, t)], head='filled', size=4, dash=(3, 2) if i >= 2 else None)
    # storage
    g.line([(xs[1] + 54, r3 + bh + 10), (xs[1] + 54, 338), (100, 338), (100, 350)], head='filled', size=4)
    g.line([(xs[2] - 7, r2 + bh + 30), (xs[2] - 7, 350)], head='filled', size=4)
    legacy_t = r2 + bh + 39  # just below the Services box
    g.line([(xs[0] + 30, r2 + bh + 30), (xs[0] + 30, legacy_t), (ex - 8, legacy_t),
            (ex - 8, 62 + 4 * 52 + 19), (ex, 62 + 4 * 52 + 19)], head='filled', dash=(1.5, 1.5), size=4)
    return g.d


def deployment_diagram():
    g = Dia(FRAME_W, 300)
    g.node(6, 14, 318, 272, 'Developer / office PC — Windows 11', stereo='device')
    g.node(20, 52, 180, 104, 'Python 3.13 virtualenv (.venv)', stereo='execution environment', fill=TINT)
    g.box(30, 86, 160, 60, 'Django 6.1 dev server', ['manage.py runserver 127.0.0.1:8000', 'AutoBiz AI app + agents'],
          stereo='artifact')
    g.node(20, 178, 180, 98, 'XAMPP MariaDB 10.4.32 :3306', stereo='execution environment', fill=TINT)
    g.box(30, 210, 78, 56, 'autobiz_ai_django', ['Django tables'], stereo='database', size=6.4, line_size=5.8)
    g.box(114, 210, 78, 56, 'autobiz_ai', ['CI4 legacy (read)'], stereo='database', size=6.4, line_size=5.8)
    g.box(222, 60, 90, 50, 'Web browser', ['Tailwind CDN', 'GSAP/AOS in designs'], stereo='device', size=6.8)
    g.box(222, 196, 90, 70, 'writable/', ['builds/<slug>/*.html', 'logs/autobiz.log', '.env (secrets)'],
          stereo='folder', size=6.8)
    ex = FRAME_W - 132
    g.text(ex + 66, 10, 'Internet', 7.4, 'UI-Bold', MUTED, 'middle')
    rows = [('api.openai.com', 'HTTPS 443 · Bearer key'), ('Client websites', 'HTTP/S GET (redesign mode)'),
            ('SMTP server', 'smtp.gmail.com:587 TLS'), ('FTP host', 'port 21 · demos.<domain>')]
    pc_right = 6 + 318 + 7  # PC node right edge incl. its 3-D side
    for i, (n, s) in enumerate(rows):
        t = 26 + i * 68
        g.node(ex, t, 120, 46, n, stereo='device' if i != 1 else 'devices', fill=LIGHT)
        g.text(ex + 6, t + 37, s, 6.2, 'UI', MUTED)
        g.line([(pc_right, t + 23), (ex, t + 23)], head='filled', size=4, dash=(3, 2) if i >= 2 else None)
    g.text((pc_right + ex) / 2, 26 + 23 - 4, 'Django', 6, 'UI', MUTED, 'middle')
    g.line([(222, 85), (190, 104)], head='filled', size=4)
    g.text(215, 104, 'HTTP', 6, 'UI', MUTED, 'middle')
    g.line([(110, 156), (110, 178)], head='filled', size=4)
    g.text(114, 170, 'TCP 3306 (PyMySQL)', 6, 'UI', MUTED)
    g.line([(190, 136), (211, 136), (211, 230), (222, 230)], head='filled', size=4)
    g.text(214, 160, 'files', 6, 'UI', MUTED)
    return g.d


def class_diagram_models():
    g = Dia(FRAME_W, 470)
    lx, rx, w = 0, 300, 187
    hb = g.uml_class(lx, 10, 172, 'Business', [
        '+id: BigAutoField «PK»', '+name: str(255)', '+business_type: str(100)?', '+location: str(255)',
        '+phone: str(50)?', '+email: Email(255)?', '+google_maps_id: str(100)? «unique»', '+address: text?',
        '+category: str(100)?', '+rating: Decimal(3,1)?', '+review_count: int = 0',
        '+website_status: WebsiteStatus', '+website_url: URL(500)?', '+scrape_source: str(50)?',
        '+status: Status = pending', '+created_at / updated_at'],
        ['+dashboard_stats(): dict «classmethod»'], stereo='table restaurants')
    he = g.uml_class(rx, 10, w, 'Enrichment', [
        '+id «PK»', '+business «FK restaurant_id»', '+business_summary: text?', '+target_audience: text?',
        '+branding_notes: text?', '+usp: text?', '+tone: str(50)?', '+color_palette: str(100)?',
        '+keywords: text? (comma list)', '+raw_gpt_response: text?', '+created_at / updated_at'],
        stereo='table enrichments')
    tm = 10 + he + 14
    hm = g.uml_class(rx, tm, w, 'Email', [
        '+id «PK»', '+business «FK restaurant_id»', '+to_email: str(255)', '+subject: str(255)?', '+body: text?',
        '+demo_links: text?', '+sent_status: pending|sent|failed', '+response_status: none|opened|…',
        '+sent_at: datetime?', '+error_msg: text?', '+created_at / updated_at'], stereo='table emails')
    td = tm + hm + 14
    hd = g.uml_class(rx, td, w, 'Design', [
        '+id «PK»', '+business «FK restaurant_id»', '+version: smallint = 1', '+style_name: str(100)?',
        '+html_code: text?', '+css_framework: str(50)', '+preview_path: str(255)?',
        '+status: draft|built|deployed|selected', '+created_at / updated_at'],
        ['+filename: str «property»'], stereo='table designs')
    tp = td + 10
    g.uml_class(lx, tp, 172, 'Deployment', [
        '+id «PK»', '+design «FK design_id»', '+url: str(255)?', '+subdomain: str(100)?', '+ftp_path: str(255)?',
        '+status: pending|uploading|live|failed', '+error_msg: text?', '+deployed_at: datetime?',
        '+created_at / updated_at'], stereo='table deployments')
    # associations (composition: deleting a business cascades)
    g.line([(172, 60), (rx, 60)], tail='diamond')
    g.text(178, 56, '1', 6.6, 'UI-Bold', INK); g.text(rx - 4, 56, '0..*', 6.6, 'UI-Bold', INK, 'end')
    g.text(236, 70, 'enrichments', 6.2, 'UI', MUTED, 'middle')
    te = tm + 12            # emails link: inside both the Business and the Email box
    g.line([(172, te), (rx, te)], tail='diamond')
    g.text(184, te - 4, '1', 6.6, 'UI-Bold', INK); g.text(rx - 4, te - 4, '0..*', 6.6, 'UI-Bold', INK, 'end')
    g.text(214, te + 10, 'emails', 6.2, 'UI', MUTED, 'middle')
    tb = 10 + hb - 7        # designs link leaves near the bottom of Business
    g.line([(172, tb), (250, tb), (250, td + 30), (rx, td + 30)], tail='diamond')
    g.text(184, tb - 4, '1', 6.6, 'UI-Bold', INK); g.text(rx - 4, td + 26, '0..*', 6.6, 'UI-Bold', INK, 'end')
    g.text(254, td + 18, 'designs', 6.2, 'UI', MUTED)
    g.line([(rx, td + 75), (172, td + 75)], tail='diamond')
    g.text(rx - 4, td + 71, '1', 6.6, 'UI-Bold', INK, 'end'); g.text(178, td + 71, '0..*', 6.6, 'UI-Bold', INK)
    g.text(236, td + 85, 'deployments', 6.2, 'UI', MUTED, 'middle')
    g.line([(16, 463), (2, 463)], head='diamond', size=4)
    g.text(20, 466, 'composition — on_delete=CASCADE: deleting a Business removes its enrichments, designs '
                    '(and their deployments) and emails.', 6.4, 'UI', MUTED)
    return g.d


def class_diagram_services():
    g = Dia(FRAME_W, 330)
    W = FRAME_W
    ho = g.uml_class(W / 2 - 95, 4, 190, 'Orchestrator', [
        '-enrichment, strategy, design', '-build, hosting, outreach'],
        ['+process_pending(): None', '+process_business(id): None', '-_set_status(id, status)'], stereo='service')
    agents = [
        ('EnrichmentAgent', ['+enrich(id): bool', '-_build_prompt(b)']),
        ('StrategyAgent', ['+strategize(id): dict?', '-_build_prompt(b, e)']),
        ('DesignAgent', ['+generate(id, c): [int]', '+build_prompt(...)', '+extract_site_info(url)']),
        ('BuildAgent', ['+build(id): [path]']),
        ('HostingAgent', ['+deploy(id): [url]', '-_upload_via_ftp()']),
        ('OutreachAgent', ['+send_outreach(id, urls)', '-_build_email_body()']),
    ]
    bw, gap = 76, (W - 6 * 76) / 5
    at = 130
    tops = []
    for i, (n, ms) in enumerate(agents):
        x = i * (bw + gap)
        g.uml_class(x, at, bw, n, [], ms, header_fill=TINT if i < 4 else LIGHT)
        tops.append(x + bw / 2)
        g.line([(W / 2, 4 + ho), (W / 2, at - 16), (x + bw / 2, at - 16), (x + bw / 2, at)], head='open' if False else None,
               tail=None)
    g.line([(W / 2, 4 + ho + 7), (W / 2, 4 + ho)], tail=None)
    g.d.add(Polygon([W / 2, g.Y(4 + ho), W / 2 - 4, g.Y(4 + ho + 6), W / 2, g.Y(4 + ho + 12), W / 2 + 4,
                     g.Y(4 + ho + 6)], fillColor=INK, strokeColor=INK))
    g.text(W / 2 + 8, at - 20, 'composition — one instance of each agent', 6.2, 'UI', MUTED)
    ct = 250
    g.uml_class(70, ct, 150, 'OpenAIClient', ['-api_key, model'],
                ['+chat(user, system, max_tokens): str', '-_stub_response(system)'], stereo='service')
    g.uml_class(250, ct, 120, 'design_styles', ['+STYLES: list[5 dict]'], stereo='module')
    g.uml_class(390, ct, 97, 'utils', ['+slugify(name)', '+parse_json_response()', '+build_dir_for()'],
                stereo='module', header_fill=LIGHT)
    for i in range(3):
        g.line([(tops[i], at + 42 + (12 if i == 2 else 0)), (tops[i], 232), (145, 232), (145, ct)],
               dash=(3, 2), head='open', size=5)
    g.line([(tops[2] + 10, at + 54), (tops[2] + 10, 240), (310, 240), (310, ct)], dash=(3, 2), head='open', size=5)
    g.text(150, 245, '«use»', 6.2, 'UI', MUTED)
    g.text(316, 247, '«use»', 6.2, 'UI', MUTED)
    return g.d


def use_case_diagram():
    g = Dia(FRAME_W, 452)
    cases = ['View dashboard KPIs', 'Browse & filter businesses', 'Add a business', 'Save & run pipeline',
             'Run pipeline (enrich → strategy → design → build)', 'Regenerate designs', 'View business detail',
             'Preview a generated design', 'Download designs as ZIP', 'Update status manually',
             'Delete business + files', 'Process all pending (CLI)']
    bx, bt, bw, bh = 92, 8, 300, 440
    g.rect(bx, bt, bw, bh, fill=None, stroke=BRAND, sw=1, r=4)
    g.text(bx + 8, bt + 13, 'AutoBiz AI (Django)', 7.6, 'UI-Bold', BRAND)
    cx, rx, ry, step = bx + bw / 2, 118, 12.5, 34.5
    centers = []
    for i, c in enumerate(cases):
        ct = bt + 38 + i * step
        g.ellipse(cx, ct, rx, ry, c, size=6.9)
        centers.append(ct)
    g.actor(32, 170, 'Operator')
    for i in range(11):
        g.line([(44, 196), (cx - rx * 0.97, centers[i])], color=EDGE, sw=0.6)
    g.actor(FRAME_W - 40, 140, 'OpenAI API')
    g.line([(FRAME_W - 52, 166), (cx + rx, centers[4])], sw=0.6)
    g.actor(FRAME_W - 40, 360, 'CLI /\nscheduler')
    g.line([(FRAME_W - 52, 386), (cx + rx, centers[11])], sw=0.6)
    for a, b in ((3, 4), (5, 4)):
        t1 = centers[a] + (ry if a < b else -ry)
        t2 = centers[b] + (-ry if a < b else ry)
        g.line([(cx + 70, t1), (cx + 70, t2)], dash=(2.5, 2), head='open', size=4)
        g.text(cx + 74, (t1 + t2) / 2 + 2.2, '«include»', 5.8, 'UI', MUTED)
    g.line([(cx + rx - 6, centers[11] - 7), (cx + rx + 14, centers[11] - 7), (cx + rx + 14, centers[4] + 7),
            (cx + rx - 4, centers[4] + 7)], dash=(2.5, 2), head='open', size=4)
    g.text(cx + rx + 10, (centers[8] + centers[9]) / 2 + 2, '«include»', 5.8, 'UI', MUTED, 'end')
    return g.d


def sequence_diagram():
    parts = ['Operator\n(browser)', 'run_pipeline\nview', 'Orchestrator', 'Enrichment\nAgent', 'Strategy\nAgent',
             'Design\nAgent', 'Build\nAgent', 'OpenAI\nAPI', 'Database\n/ files']
    n = len(parts)
    W = FRAME_W
    sp = W / n
    X = [sp * i + sp / 2 for i in range(n)]
    msgs = [
        (0, 1, 'POST /businesses/{id}/run'), (1, 2, 'process_business(id)'), (2, 8, 'load Business'),
        'opt', (2, 3, 'enrich(id)'), (3, 7, 'chat(prompt) — JSON'), (7, 3, 'branding JSON', 'r'),
        (3, 8, 'insert Enrichment · status = enriched'), 'end',
        (2, 4, 'strategize(id)'), (4, 7, 'chat(prompt) — JSON'), (7, 4, 'content strategy', 'r'),
        (4, 2, 'content dict', 'r'), (2, 5, 'generate(id, content)'),
        'loop', (5, 7, 'chat(prompt, 16k tokens)'), (7, 5, 'HTML page', 'r'), (5, 8, 'insert Design (draft)'), 'end',
        (5, 2, 'design ids', 'r'), (2, 6, 'build(id)'), (6, 8, 'write v<N>_<style>.html · status = built'),
        (6, 2, 'file paths', 'r'), (2, 8, 'status = designed'), (1, 0, '302 → detail page + flash message', 'r'),
    ]
    step = 16
    head_h = 26
    count = sum(1 for m in msgs if isinstance(m, tuple)) + sum(1 for m in msgs if m in ('opt', 'loop')) * 0.9
    H = head_h + 22 + count * step + 18
    g = Dia(W, H)
    for i, p in enumerate(parts):
        g.box(X[i] - sp / 2 + 3, 2, sp - 6, head_h, p.split('\n')[0], p.split('\n')[1:], fill=TINT, stroke=BRAND,
              size=6.4, line_size=6.0)
        g.line([(X[i], head_h + 2), (X[i], H - 4)], dash=(2, 2), color=MUTED, sw=0.6)
    t = head_h + 22
    open_frames = []
    for m in msgs:
        if m in ('opt', 'loop'):
            open_frames.append((m, t - 9))
            t += step * 0.9
            continue
        if m == 'end':
            kind, ft = open_frames.pop()
            if kind == 'opt':
                g.frame(X[2] - 22, ft, X[8] - X[2] + 36, t - ft - 8, 'opt', '[status == pending]')
            else:
                g.frame(X[5] - 22, ft, X[8] - X[5] + 36, t - ft - 8, 'loop', '[for each of the 5 styles]')
            continue
        a, b, label = m[:3]
        ret = len(m) > 3
        g.line([(X[a], t), (X[b], t)], dash=(3, 2) if ret else None, head='open' if ret else 'filled', size=4.5,
               sw=0.7)
        if b > a:
            g.text(X[a] + 4, t - 2.6, label, 6.1, 'UI', INK)
        else:
            g.text(X[a] - 4, t - 2.6, label, 6.1, 'UI', MUTED if ret else INK, 'end')
        t += step
    return g.d


def activity_diagram():
    g = Dia(FRAME_W, 640)
    cx, rcx = 170, 395
    aw, ah = 190, 24

    def action(t, label, sub=None, fill=TINT):
        g.box(cx - aw / 2, t, aw, ah, label, [sub] if sub else [], fill=fill, stroke=BRAND, size=7, line_size=6,
              r=9)

    def down(t1, t2):
        g.line([(cx, t1), (cx, t2)], head='filled', size=4.5)

    g.dot(cx, 14)
    down(19, 32)
    action(32, 'Load business by id')
    down(56, 66)
    g.diamond(cx, 80, 84, 28, 'found?')
    g.line([(cx + 42, 80), (rcx, 80), (rcx, 92)], head='filled', size=4.5)
    g.text(cx + 48, 76, 'no', 6.4, 'UI', MUTED)
    g.box(rcx - 70, 92, 140, 22, 'log error and stop', fill=LIGHT, r=9)
    g.dot(rcx, 128, final=True)
    g.line([(rcx, 114), (rcx, 120)], head='filled', size=4)
    down(94, 110)
    g.text(cx + 4, 104, 'yes', 6.4, 'UI', MUTED)
    g.diamond(cx, 124, 110, 28, 'status == pending?')
    down(138, 154)
    g.text(cx + 4, 148, 'yes', 6.4, 'UI', MUTED)
    action(154, 'EnrichmentAgent.enrich()', 'GPT → Enrichment row, status = enriched')
    down(178, 190)
    g.diamond(cx, 204, 84, 28, 'parsed OK?')
    g.line([(cx + 42, 204), (rcx, 204), (rcx, 222)], head='filled', size=4.5)
    g.text(cx + 48, 200, 'no', 6.4, 'UI', MUTED)
    g.box(rcx - 70, 222, 140, 22, 'status = skipped, stop', fill=colors.HexColor('#FEF2F2'),
          stroke=BAD, r=9)
    g.line([(rcx, 244), (rcx, 252)], head='filled', size=4)
    g.dot(rcx, 260, final=True)
    down(218, 262)
    g.text(cx + 4, 236, 'yes', 6.4, 'UI', MUTED)
    g.line([(cx - 55, 124), (cx - 120, 124), (cx - 120, 252), (cx, 252)], head='filled', size=4.5)
    g.text(cx - 62, 120, 'no (already enriched)', 6.2, 'UI', MUTED, 'end')
    action(262, 'StrategyAgent.strategize()', 'GPT → hero, about, services, CTA, tagline')
    down(286, 298)
    g.diamond(cx, 312, 84, 28, 'content?')
    g.line([(cx + 42, 312), (rcx + 30, 312), (rcx + 30, 244)], head='filled', size=4.5)
    g.text(cx + 48, 308, 'no', 6.4, 'UI', MUTED)
    down(326, 342)
    g.text(cx + 4, 336, 'yes', 6.4, 'UI', MUTED)
    action(342, 'DesignAgent.generate()', 'one GPT call per style ×5 → Design rows (draft)')
    down(366, 378)
    g.diamond(cx, 392, 100, 28, 'any designs?')
    g.line([(cx + 50, 392), (rcx, 392), (rcx, 404)], head='filled', size=4.5)
    g.text(cx + 56, 388, 'no', 6.4, 'UI', MUTED)
    g.box(rcx - 70, 404, 140, 22, 'log warning and stop', fill=LIGHT, r=9)
    g.line([(rcx, 426), (rcx, 432)], head='filled', size=4)
    g.dot(rcx, 440, final=True)
    down(406, 422)
    g.text(cx + 4, 416, 'yes', 6.4, 'UI', MUTED)
    action(422, 'BuildAgent.build()', 'write HTML files, Design.status = built')
    down(446, 458)
    g.diamond(cx, 472, 100, 28, 'files written?')
    down(486, 502)
    g.text(cx + 4, 496, 'yes', 6.4, 'UI', MUTED)
    action(502, 'Business.status = designed')
    g.line([(cx - 50, 472), (cx - 120, 472), (cx - 120, 540), (cx, 540)], head='filled', size=4.5)
    g.text(cx - 56, 468, 'no', 6.4, 'UI', MUTED, 'end')
    down(526, 540)
    g.box(cx - aw / 2, 548, aw, 30, 'Hosting.deploy() → Outreach.send_outreach()',
          ['present in code, commented out in the orchestrator'], fill=LIGHT, stroke=MUTED, dash=(3, 2), size=6.8,
          line_size=6, r=9)
    g.line([(cx, 540), (cx, 548)])
    down(578, 596)
    g.dot(cx, 606, final=True)
    g.text(cx + 14, 609, 'done — operator downloads the ZIP', 6.6, 'UI', MUTED)
    return g.d


def state_diagram():
    g = Dia(FRAME_W, 360)
    sw, sh = 84, 30

    def state(x, t, name, fill=TINT, stroke=BRAND):
        g.box(x, t, sw, sh, name, fill=fill, stroke=stroke, r=12, size=7.6)

    rowA, rowB, rowC = 70, 170, 280
    xa = [40, 210, 380]
    g.dot(10, rowA + sh / 2)
    g.line([(15, rowA + sh / 2), (xa[0], rowA + sh / 2)], head='filled', size=4.5)
    g.text(14, rowA + sh / 2 - 22, 'Add business', 6.4, 'UI', MUTED)
    g.text(14, rowA + sh / 2 - 14, '(web form)', 6.4, 'UI', MUTED)
    state(xa[0], rowA, 'pending')
    state(xa[1], rowA, 'enriched')
    state(xa[2], rowA, 'designed')
    state(125, rowB, 'skipped', fill=colors.HexColor('#FEF2F2'), stroke=BAD)
    state(xa[2], rowC, 'deployed', fill=LIGHT, stroke=MUTED)
    state(xa[1], rowC, 'contacted', fill=LIGHT, stroke=MUTED)
    state(xa[0], rowC, 'converted', fill=colors.HexColor('#F0FDF4'), stroke=GOOD)
    my = rowA + sh / 2
    g.line([(xa[0] + sw, my), (xa[1], my)], head='filled', size=4.5)
    g.text((xa[0] + sw + xa[1]) / 2, my - 4, 'enrichment OK', 6.3, 'UI', INK, 'middle')
    g.line([(xa[1] + sw, my), (xa[2], my)], head='filled', size=4.5)
    g.text((xa[1] + sw + xa[2]) / 2, my - 4, 'strategy + design', 6.3, 'UI', INK, 'middle')
    g.text((xa[1] + sw + xa[2]) / 2, my + 9, '+ build OK', 6.3, 'UI', INK, 'middle')
    g.line([(xa[2] + sw / 2, rowA), (xa[2] + sw / 2, rowA - 26), (xa[1] + sw / 2, rowA - 26), (xa[1] + sw / 2, rowA)],
           head='filled', size=4.5)
    g.text((xa[1] + xa[2] + sw) / 2, rowA - 30, 'Regenerate (designs deleted, pipeline re-run)', 6.3, 'UI', INK,
           'middle')
    g.line([(xa[0] + sw / 2, rowA + sh), (150, rowB)], head='filled', size=4.5)
    g.text(112, 140, 'enrichment failed', 6.3, 'UI', BAD, 'end')
    g.line([(xa[1] + sw / 2, rowA + sh), (190, rowB)], head='filled', size=4.5)
    g.text(226, 140, 'strategy failed', 6.3, 'UI', BAD)
    g.line([(xa[2] + sw / 2, rowA + sh), (xa[2] + sw / 2, rowC)], head='filled', size=4.5, dash=(3, 2))
    g.text(xa[2] + sw / 2 + 4, 200, 'HostingAgent', 6.3, 'UI', MUTED)
    g.text(xa[2] + sw / 2 + 4, 209, 'deploy (disabled)', 6.3, 'UI', MUTED)
    cy = rowC + sh / 2
    g.line([(xa[2], cy), (xa[1] + sw, cy)], head='filled', size=4.5, dash=(3, 2))
    g.text((xa[1] + sw + xa[2]) / 2, cy - 4, 'outreach sent', 6.3, 'UI', MUTED, 'middle')
    g.text((xa[1] + sw + xa[2]) / 2, cy + 10, '(disabled)', 6.3, 'UI', MUTED, 'middle')
    g.line([(xa[1], cy), (xa[0] + sw, cy)], head='filled', size=4.5)
    g.text((xa[0] + sw + xa[1]) / 2, cy - 4, 'client signs', 6.3, 'UI', INK, 'middle')
    g.text((xa[0] + sw + xa[1]) / 2, cy + 10, '(manual status)', 6.3, 'UI', INK, 'middle')
    g.rect(0, 330, FRAME_W, 24, fill=LIGHT, stroke=RULE, r=3)
    g.text(8, 345, 'Any state → any state: POST /businesses/<id>/status sets a status by hand (validated '
                   'against the 7 values).', 6.6, 'UI', INK)
    return g.d


# ─── Facts read from the code ──────────────────────────────────────────────

def field_rows(model):
    rows = [['Column', 'Type', 'Null', 'Default / choices']]
    for f in model._meta.concrete_fields:
        typ = f.get_internal_type().replace('Field', '')
        if getattr(f, 'max_length', None) and typ in ('Char', 'Email', 'URL'):
            typ += f'({f.max_length})'
        if typ == 'Decimal':
            typ += f'({f.max_digits},{f.decimal_places})'
        if f.is_relation:
            typ = f'FK → {f.related_model._meta.db_table}.id'
        extra = []
        if f.primary_key:
            extra.append('primary key')
        if f.unique and not f.primary_key:
            extra.append('unique')
        if f.choices:
            extra.append(' | '.join(str(c[0]) for c in f.choices))
        if f.has_default():
            extra.append(f'default {f.default}')
        if getattr(f, 'auto_now_add', False):
            extra.append('set on insert')
        elif getattr(f, 'auto_now', False):
            extra.append('set on every save')
        rows.append([f.column, typ, 'yes' if f.null else 'no', '; '.join(extra) or '—'])
    return rows


def route_rows():
    from dashboard import urls as dash_urls
    method = {'index': 'GET', 'businesses': 'GET', 'business_add': 'GET, POST', 'business_detail': 'GET',
              'business_run': 'POST', 'business_status': 'POST', 'business_download': 'GET',
              'business_delete': 'POST', 'business_regenerate': 'POST', 'preview': 'GET'}
    rows = [['Method', 'URL', 'View', 'What it does']]
    for p in dash_urls.urlpatterns:
        doc = (p.callback.__doc__ or '').strip().split('\n')[0]
        doc = re.sub(r'^(GET/POST|GET|POST) \S+ — ', '', doc)
        doc = doc[:1].upper() + doc[1:]
        url = '/' + str(p.pattern).replace('<int:pk>', '{id}').replace('<int:design_id>', '{design_id}')
        rows.append([method.get(p.name, 'GET'), url, f'views.{p.callback.__name__}', doc])
    rows.append(['GET, POST', '/admin/', 'django.contrib.admin', 'Admin for all 5 models (needs createsuperuser).'])
    return rows


def env_rows():
    notes = {
        'DJANGO_SECRET_KEY': 'Cryptographic signing key. Generated automatically into .env.',
        'DJANGO_DEBUG': 'true for development; set false in production.',
        'DJANGO_ALLOWED_HOSTS': 'Comma list of host names the server answers to.',
        'DJANGO_CSRF_TRUSTED_ORIGINS': 'Needed only behind HTTPS proxies / other origins.',
        'TIME_ZONE': 'Display time zone (data is stored in UTC).',
        'DB_ENGINE': 'sqlite | mysql | mysql_legacy (XAMPP MariaDB 10.4).',
        'DB_NAME': 'Database (or SQLite file) name. Default autobiz_ai_django.',
        'LEGACY_DB_NAME': 'The CodeIgniter database read by import_legacy.',
        'OPENAI_API_KEY': 'Empty = offline stub responses (no API cost).',
        'OPENAI_MODEL': 'Chat model, default gpt-4o.',
        'EMAIL_FROM': 'Sender and reply-to address of outreach emails.',
        'EMAIL_CRYPTO': 'tls | ssl.',
        'HOSTING_FTP_HOST': 'Empty = uploads are simulated and marked live.',
        'HOSTING_BASE_DOMAIN': 'Demo URLs become https://demos.<domain>/<slug>/…',
        'APIFY_API_TOKEN': 'Reserved for a future scraping agent; unused.',
    }
    rows = [['Variable', 'Default', 'Purpose']]
    for line in (ROOT / '.env.example').read_text(encoding='utf-8').splitlines():
        m = re.match(r'(\w+)=(.*)$', line)
        if m:
            k, v = m.groups()
            prefixes = [('LEGACY_DB_', 'Legacy (CI4) database connection.'), ('DB_', 'Database connection.'),
                        ('EMAIL_', 'SMTP settings for the Outreach agent.'),
                        ('HOSTING_', 'FTP settings for the Hosting agent.')]
            note = notes.get(k) or next((n for p, n in prefixes if k.startswith(p)), '')
            rows.append([k, v if v and 'change-me' not in v else ('(generated)' if k == 'DJANGO_SECRET_KEY' else '—'),
                         note])
    return rows


def style_rows():
    rows = [['#', 'Style', 'Fonts', 'Image palette', 'Concept']]
    for i, s in enumerate(STYLES, 1):
        fams = re.findall(r'family=([^:&]+)', s['fonts_href'])
        fonts = ', '.join(f.replace('+', ' ') for f in fams)
        concept = s['concept'].split('. ')[0] + '.'
        bg, fg = s['img_palette'].split('/')
        rows.append([str(i), s['name'], fonts, f'#{bg} / #{fg}', concept])
    return rows


# ─── Diagrams added for the project report ────────────────────────────────

def sdlc_diagram():
    g = Dia(FRAME_W, 190)
    stages = [
        ('A. Requirement gathering', ['read the CI4 code, routes,', 'migrations and .env']),
        ('B. Analysis', ['map PHP parts to Django;', 'pick DB, driver, libraries']),
        ('C. Designing', ['models, services, views,', 'templates, UML']),
        ('D. Development', ['port agents, views, CLI;', 'run.bat, import_legacy']),
        ('E. Integration & test', ['14 tests on MariaDB 10.4,', 'parity + smoke checks']),
        ('F. Installation & acceptance', ['run.bat on the target PC,', 'legacy data imported']),
    ]
    bw, bh, gap = 145, 58, (FRAME_W - 3 * 145) / 2
    for i, (name, lines) in enumerate(stages):
        row, col = divmod(i, 3)
        if row == 1:
            col = 2 - col  # second row runs right to left (snake)
        x, t = col * (bw + gap), 16 + row * (bh + 46)
        g.box(x, t, bw, bh, name, lines, fill=TINT, stroke=BRAND, size=7.4, line_size=6.4)
    y1 = 16 + bh / 2
    for col in range(2):
        g.line([((col + 1) * bw + col * gap, y1), ((col + 1) * (bw + gap), y1)], head='filled', size=4.5)
    g.line([(FRAME_W - bw / 2, 16 + bh), (FRAME_W - bw / 2, 16 + bh + 46)], head='filled', size=4.5)
    y2 = 16 + bh + 46 + bh / 2
    for col in (2, 1):
        g.line([(col * (bw + gap), y2), (col * (bw + gap) - gap, y2)], head='filled', size=4.5)
    g.line([(bw / 2, 16 + bh + 46), (bw / 2, 16 + bh)], dash=(3, 2), head='filled', size=4.5)
    g.text(bw / 2 + 5, 16 + bh + 26, 'feedback: defects found in testing', 6.2, 'UI', MUTED)
    g.text(bw / 2 + 5, 16 + bh + 34, 'return to analysis and design', 6.2, 'UI', MUTED)
    g.text(0, 8, 'Umbrella activities across all stages: documentation, version control, review', 6.4, 'UI', MUTED)
    return g.d


def collaboration_diagram():
    g = Dia(FRAME_W, 400)

    def obj(x, t, w, name, fill=WHITE):
        g.rect(x, t, w, 30, fill=fill, stroke=EDGE, r=2)
        g.text(x + w / 2, t + 18.5, name, 7.2, 'UI-Bold', NAVY, 'middle')
        tw = pdfmetrics.stringWidth(name, 'UI-Bold', 7.2)
        g.d.add(Line(x + w / 2 - tw / 2, g.Y(t + 20.5), x + w / 2 + tw / 2, g.Y(t + 20.5), strokeColor=NAVY,
                     strokeWidth=0.5))

    def msg(x, t, text, anchor='start', color=INK):
        g.text(x, t, text, 6.4, 'UI', color, anchor)

    g.actor(390, 4, ':Operator')
    obj(330, 88, 120, ':run_pipeline view')
    obj(330, 178, 120, ':Orchestrator', fill=TINT)
    obj(160, 108, 112, ':EnrichmentAgent')
    obj(160, 178, 112, ':StrategyAgent')
    obj(160, 248, 112, ':DesignAgent')
    obj(330, 268, 120, ':BuildAgent')
    obj(8, 178, 106, ':OpenAIClient')
    obj(160, 348, 290, ':Business / Enrichment / Design records')
    g.line([(390, 70), (390, 88)])
    msg(396, 82, '1: POST /businesses/{id}/run')
    g.line([(390, 118), (390, 178)])
    msg(396, 152, '2: process_business(id)')
    for t in (123, 193, 263):
        g.line([(330, 193), (272, t)])
    msg(276, 116, '3: enrich(id)')
    msg(276, 189, '4: strategize(id)')
    msg(276, 276, '5: generate()')
    for t in (123, 193, 263):
        g.line([(160, t), (114, 193)])
    msg(156, 117, '3.1: chat()', 'end', MUTED)
    msg(137, 189, '4.1: chat()', 'middle', MUTED)
    msg(156, 276, '5.1: chat() ×5', 'end', MUTED)
    g.line([(390, 208), (390, 268)])
    msg(386, 242, '6: build(id)', 'end')
    g.line([(390, 298), (390, 348)])
    msg(396, 318, '6.1: write files,')
    msg(396, 327, 'status = built')
    g.line([(216, 278), (216, 348)])
    msg(222, 318, '5.2: insert Design ×5')
    g.line([(450, 193), (466, 193), (466, 363), (450, 363)])
    msg(462, 236, '7: status = designed', 'end')
    return g.d


def dfd_diagram():
    g = Dia(FRAME_W, 340)

    def entity(x, t, w, name, sub=''):
        g.rect(x, t, w, 40, fill=LIGHT, stroke=INK, sw=1, r=0)
        g.text(x + w / 2, t + (18 if sub else 23), name, 7.2, 'UI-Bold', INK, 'middle')
        if sub:
            g.text(x + w / 2, t + 29, sub, 6, 'UI', MUTED, 'middle')

    def process(x, t, num, name):
        g.rect(x, t, 88, 42, fill=TINT, stroke=BRAND, r=9)
        g.d.add(Line(x, g.Y(t + 13), x + 88, g.Y(t + 13), strokeColor=BRAND, strokeWidth=0.6))
        g.text(x + 44, t + 9.5, num, 6.4, 'UI-Bold', BRAND, 'middle')
        g.text(x + 44, t + 30, name, 7, 'UI-Semi', INK, 'middle')

    def store(x, t, sid, name):
        y0, y1 = g.Y(t), g.Y(t + 24)
        g.d.add(Rect(x, y1, 88, 24, fillColor=WHITE, strokeColor=None))
        g.d.add(Line(x, y0, x + 88, y0, strokeColor=INK, strokeWidth=0.9))
        g.d.add(Line(x, y1, x + 88, y1, strokeColor=INK, strokeWidth=0.9))
        g.d.add(Line(x, y0, x, y1, strokeColor=INK, strokeWidth=0.9))
        g.d.add(Line(x + 22, y0, x + 22, y1, strokeColor=INK, strokeWidth=0.6))
        g.text(x + 11, t + 15, sid, 6.6, 'UI-Bold', INK, 'middle')
        g.text(x + 26, t + 15, name, 6.6, 'UI', INK)

    def flow(pts, label=None, at=None, anchor='start'):
        g.line(pts, head='filled', size=4)
        if label:
            g.text(at[0], at[1], label, 6.1, 'UI', MUTED, anchor)

    entity(0, 34, 62, 'Operator')
    entity(400, 110, 80, 'OpenAI API', 'chat completions')
    entity(400, 198, 80, 'Client website', 'existing pages')
    process(78, 30, '1.0', 'Onboard business')
    process(190, 30, '2.0', 'Enrich brand')
    process(302, 30, '3.0', 'Plan content')
    process(302, 198, '4.0', 'Generate designs')
    process(190, 198, '5.0', 'Build files')
    process(78, 198, '6.0', 'Deliver')
    store(78, 118, 'D1', 'restaurants')
    store(190, 118, 'D2', 'enrichments')
    store(302, 290, 'D3', 'designs')
    store(190, 290, 'D4', 'writable/builds')
    flow([(62, 51), (78, 51)], 'details', (36, 27))
    flow([(122, 72), (122, 118)], 'business row', (126, 98))
    flow([(166, 128), (222, 72)], 'business data', (196, 108))
    flow([(234, 72), (234, 118)], 'profile', (238, 98))
    flow([(234, 30), (234, 14), (440, 14), (440, 110)], 'prompts → JSON / HTML replies', (300, 11))
    flow([(278, 128), (334, 72)], 'brand profile', (308, 108))
    flow([(390, 62), (400, 116)])
    flow([(346, 72), (346, 198)], 'content strategy', (350, 150))
    flow([(400, 146), (382, 198)], 'HTML pages', (394, 184))
    flow([(400, 218), (390, 218)], 'site text', (404, 252))
    flow([(346, 240), (346, 290)], 'design rows', (350, 268))
    flow([(302, 300), (264, 240)], 'drafts', (288, 262))
    flow([(234, 240), (234, 290)], 'HTML files', (238, 268))
    flow([(190, 302), (122, 240)], 'files', (150, 286), 'end')
    flow([(78, 219), (31, 219), (31, 74)], 'preview / ZIP', (35, 150))
    g.text(0, 334, 'Level-1 DFD (Gane-Sarson): rounded boxes are processes, open boxes are data stores, '
                   'shaded boxes are external entities.', 6.3, 'UI', MUTED)
    return g.d

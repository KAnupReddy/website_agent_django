"""
Build docs/AutoBiz_AI_Django_Project_Document.pdf — the project report.

Layout follows the academic project-report format: Abstract, Index, List of
Figures, then chapters 1–11 (Introduction … References), each chapter on a new
page. The document is built twice so the Index and List of Figures carry real
page numbers. Facts that live in code (models, routes, styles, sample code) are
read from the project itself.

    .venv\\Scripts\\pip install reportlab
    .venv\\Scripts\\python docs\\build_project_doc.py
"""

import inspect
import io
import os
import sys
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))

import uml  # noqa: E402  (sets up Django, fonts and the diagram toolkit)
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.lib.utils import ImageReader  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import (  # noqa: E402
    BaseDocTemplate, CondPageBreak, Frame, Image, KeepTogether, NextPageTemplate, PageBreak, PageTemplate,
    Paragraph, Preformatted, Spacer, Table, TableStyle,
)

from dashboard.services.design_styles import STYLES  # noqa: E402
from dashboard.services.orchestrator import Orchestrator  # noqa: E402

ROOT = uml.ROOT
OUT = ROOT / 'docs' / 'AutoBiz_AI_Django_Project_Document.pdf'
SHOTS = ROOT / 'docs' / 'screenshots'
TESTS = 14

FONT_DIR = Path(os.environ.get('WINDIR', r'C:\Windows')) / 'Fonts'
for name, file in (('TNR', 'times.ttf'), ('TNR-B', 'timesbd.ttf'), ('TNR-I', 'timesi.ttf'), ('TNR-BI', 'timesbi.ttf')):
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / file)))
pdfmetrics.registerFontFamily('TNR', normal='TNR', bold='TNR-B', italic='TNR-I', boldItalic='TNR-BI')

PAGE_W, PAGE_H = A4
LM, RM, TM, BM = 25 * mm, 20 * mm, 22 * mm, 22 * mm
FRAME_W = PAGE_W - LM - RM
BLACK = colors.black
GREY = colors.HexColor('#E8E8E8')

S = {
    'body': ParagraphStyle('body', fontName='TNR', fontSize=11, leading=15.6, alignment=TA_JUSTIFY, spaceAfter=5),
    'chap_num': ParagraphStyle('chap_num', fontName='TNR-B', fontSize=16, leading=20, alignment=TA_CENTER),
    'chap_title': ParagraphStyle('chap_title', fontName='TNR-B', fontSize=16, leading=20, alignment=TA_CENTER,
                                 spaceAfter=14),
    'front_title': ParagraphStyle('front_title', fontName='TNR-B', fontSize=16, leading=20, alignment=TA_CENTER,
                                  spaceAfter=16),
    'h2': ParagraphStyle('h2', fontName='TNR-B', fontSize=13, leading=17, spaceBefore=8, spaceAfter=5),
    'h3': ParagraphStyle('h3', fontName='TNR-B', fontSize=11.5, leading=16, spaceBefore=4, spaceAfter=3),
    'bullet': ParagraphStyle('bullet', fontName='TNR', fontSize=11, leading=15.2, alignment=TA_JUSTIFY,
                             leftIndent=18, bulletIndent=4, spaceAfter=2),
    'cell': ParagraphStyle('cell', fontName='TNR', fontSize=10, leading=12.6),
    'cellb': ParagraphStyle('cellb', fontName='TNR-B', fontSize=10, leading=12.6),
    'cellm': ParagraphStyle('cellm', fontName='Mono', fontSize=8.4, leading=11),
    'caption': ParagraphStyle('caption', fontName='TNR-B', fontSize=10.5, leading=13, alignment=TA_CENTER,
                              spaceBefore=4, spaceAfter=12),
    'code': ParagraphStyle('code', fontName='Mono', fontSize=7.6, leading=9.7),
    'lit_title': ParagraphStyle('lit_title', fontName='TNR-B', fontSize=11.5, leading=16, spaceBefore=6),
    'lit_auth': ParagraphStyle('lit_auth', fontName='TNR-I', fontSize=11, leading=15, spaceAfter=2),
    'ref': ParagraphStyle('ref', fontName='TNR', fontSize=11, leading=15.5, leftIndent=24, firstLineIndent=-24,
                          spaceAfter=5, alignment=TA_JUSTIFY),
}


# ─── Chapter plan (drives both the headings and the Index) ─────────────────

CHAPTERS = [
    ('INTRODUCTION', ['1.1 Objective of the Project', '1.2 Scope of the Project']),
    ('LITERATURE SURVEY', []),
    ('SYSTEM STUDY ANALYSIS', ['3.1 Existing System', '3.2 Proposed System', '3.3 Modules',
                               '3.4 Feasibility Analysis']),
    ('REQUIREMENT ANALYSIS AND SPECIFICATION', ['4.1 Software Requirement Specification',
                                                '4.2 Hardware and Software Requirements']),
    ('SYSTEM DESIGN', ['5.1 UML Diagrams', '5.2 Database Design']),
    ('SYSTEM IMPLEMENTATION', ['6.1 Python and Django', '6.2 Algorithms', '6.3 Sample Code']),
    ('SYSTEM TESTING', ['7.1 Types of Testing', '7.2 Test Cases']),
    ('SCREENSHOTS', []),
    ('CONCLUSION', []),
    ('FUTURE ENHANCEMENTS', []),
    ('REFERENCES', []),
]


# ─── Small builders ────────────────────────────────────────────────────────

def P(text, style='body'):
    return Paragraph(text, S[style])


def bullets(items, numbered=False):
    return [Paragraph(t, S['bullet'], bulletText=f'{i}.' if numbered else '•') for i, t in enumerate(items, 1)]


def h2(text):
    return [CondPageBreak(70), Paragraph(text, S['h2'])]


def h3(text):
    return [CondPageBreak(50), Paragraph(text, S['h3'])]


def grid(rows, widths, mono_cols=(), bold_first=False, header=True):
    data = []
    for r, row in enumerate(rows):
        cells = []
        for c, v in enumerate(row):
            style = 'cellb' if (header and r == 0) or (bold_first and c == 0) else 'cellm' if c in mono_cols else 'cell'
            cells.append(Paragraph(escape(str(v)), S[style]))
        data.append(cells)
    t = Table(data, colWidths=[w * FRAME_W for w in widths], repeatRows=1 if header else 0)
    cmds = [('GRID', (0, 0), (-1, -1), 0.6, BLACK), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5)]
    if header:
        cmds.append(('BACKGROUND', (0, 0), (-1, 0), GREY))
    t.setStyle(TableStyle(cmds))
    return t


def code(text, title=None):
    body = Preformatted(text.strip('\n'), S['code'])
    rows = [[Paragraph(f'<b>{escape(title)}</b>', S['cellm'])], [body]] if title else [[body]]
    t = Table(rows, colWidths=[FRAME_W])
    t.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.6, BLACK), ('LINEBELOW', (0, 0), (-1, 0), 0.4, BLACK),
                           ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F7F7F7')),
                           ('LEFTPADDING', (0, 0), (-1, -1), 6), ('TOPPADDING', (0, 0), (-1, -1), 4),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
    return t


def caption(num, text):
    p = Paragraph(f'Fig {num} {escape(text)}', S['caption'])
    p._figure = (num, text)
    return p


def figure(drawing, num, text, max_h=None, keep=True):
    """A scaled diagram and its caption; keep=False returns the parts for an outer KeepTogether."""
    scale = FRAME_W / drawing.width
    if max_h and drawing.height * scale > max_h:
        scale = max_h / drawing.height
    drawing.scale(scale, scale)
    drawing.width *= scale
    drawing.height *= scale
    drawing.hAlign = 'CENTER'
    parts = [drawing, caption(num, text)]
    return KeepTogether(parts) if keep else parts


def shot(name, num, text, width=FRAME_W):
    path = SHOTS / name
    iw, ih = ImageReader(str(path)).getSize()
    img = Image(str(path), width=width, height=width * ih / iw)
    box = Table([[img]], colWidths=[width])
    box.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.6, BLACK), ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 0),
                             ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
    return KeepTogether([box, caption(num, text)])


def source(obj, start=None, stop=None):
    lines = inspect.getsource(obj).split('\n')
    return '\n'.join(lines[start:stop]).rstrip()


# ─── Document template (front matter unnumbered, chapters numbered from 1) ─

class ReportDoc(BaseDocTemplate):
    def __init__(self, target):
        super().__init__(target, pagesize=A4, leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
                         title='AutoBiz AI — Django Edition: Project Report', author='AutoBiz AI',
                         subject='AI-based business website generator (Python, Django, MySQL)')
        frame = Frame(LM, BM, FRAME_W, PAGE_H - TM - BM, leftPadding=0, rightPadding=0, topPadding=0,
                      bottomPadding=0)
        self.addPageTemplates([PageTemplate('title', [frame]),
                               PageTemplate('front', [frame]),
                               PageTemplate('body', [frame], onPageEnd=self._number)])
        self.body_start = None
        self.marks = {'chapters': {}, 'figures': []}

    def logical(self):
        return self.page - self.body_start + 1

    def afterFlowable(self, f):
        if getattr(f, '_chapter', None):
            if self.body_start is None:
                self.body_start = self.page
            n = f._chapter
            self.marks['chapters'][n] = self.logical()
            key = f'ch{n}'
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(f'Chapter {n} — {CHAPTERS[n - 1][0].title()}', key, level=0, closed=True)
        elif isinstance(f, Paragraph) and f.style.name == 'h2' and self.body_start:
            key = f'p{self.page}_{id(f)}'
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(f.getPlainText(), key, level=1)
        elif getattr(f, '_figure', None) and self.body_start:
            self.marks['figures'].append((*f._figure, self.logical()))
        elif getattr(f, '_front', None):
            key = f'front_{f._front}'
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(f._front.title(), key, level=0)

    @staticmethod
    def _number(canv, doc):
        if doc.body_start:
            canv.saveState()
            canv.setFont('TNR', 11)
            canv.drawRightString(PAGE_W - RM, 12 * mm, str(doc.logical()))
            canv.restoreState()


def chapter(n):
    title = CHAPTERS[n - 1][0]
    num = Paragraph(f'CHAPTER - {n}', S['chap_num'])
    num._chapter = n
    return [NextPageTemplate('body'), PageBreak(), num, Paragraph(title, S['chap_title'])]


def front_heading(text):
    p = Paragraph(text, S['front_title'])
    p._front = text
    return p


# ─── Front matter ──────────────────────────────────────────────────────────

def title_page():
    big = ParagraphStyle('t1', fontName='TNR-B', fontSize=24, leading=30, alignment=TA_CENTER)
    mid = ParagraphStyle('t2', fontName='TNR', fontSize=14, leading=20, alignment=TA_CENTER)
    small = ParagraphStyle('t3', fontName='TNR', fontSize=12, leading=17, alignment=TA_CENTER)
    return [
        Spacer(1, 110),
        Paragraph('AUTOBIZ AI', big),
        Spacer(1, 6),
        Paragraph('An AI-Based Multi-Agent Website Generator for Small Businesses', mid),
        Spacer(1, 40),
        Paragraph('PROJECT REPORT', ParagraphStyle('t4', parent=mid, fontName='TNR-B')),
        Spacer(1, 10),
        Paragraph('Django Edition — a port of the CodeIgniter 4 / PHP application to Python, Django and MySQL',
                  small),
        Spacer(1, 150),
        Paragraph('<b>Technology:</b> Python 3.13 · Django 6.1 · MariaDB / MySQL · OpenAI API · Tailwind CSS', small),
        Paragraph(f'<b>Project folder:</b> C:\\D Drive\\website_agent_django', small),
        Paragraph(f'<b>Date:</b> {date.today():%d %B %Y}', small),
        NextPageTemplate('front'),
    ]


def abstract():
    return [
        PageBreak(), front_heading('ABSTRACT'),
        P('Small businesses such as restaurants, clinics, salons and agencies often have no website, or an '
          'out-dated one, because a professional design costs time and money. This project presents '
          '<b>AutoBiz AI</b>, a web application that turns the basic details of a business — its name, type, '
          'city and contact information — into five complete, professionally styled single-page websites. '
          'A chain of cooperating software agents does the work: an Enrichment agent uses a large language model '
          '(OpenAI GPT-4o) to build a brand profile, a Strategy agent writes the website copy, a Design agent '
          'generates one full HTML page for each of five visual styles, and a Build agent saves the pages so the '
          'operator can preview them in the browser or download them as a ZIP file. Hosting (FTP) and Outreach '
          '(e-mail) agents are implemented for later use.'),
        P('The system was first built with PHP and CodeIgniter 4. This report documents its re-implementation '
          'in <b>Python with the Django framework and a MySQL/MariaDB database</b>. The port keeps the database '
          'schema, the agent prompts and the user interface unchanged, adds a one-click start script, a legacy '
          'data importer, an administration panel and an automated test suite, and fixes defects found during '
          f'the analysis. All {TESTS} automated tests pass against the target MariaDB 10.4 server, the five design '
          'styles were verified to be byte-for-byte identical to the original, and the existing business data '
          'was migrated successfully.'),
        Spacer(1, 6),
        P('<b>Keywords:</b> Website Generation, Large Language Models, Multi-Agent Systems, Prompt Engineering, '
          'Python, Django, MySQL, OpenAI API, Small Business Automation, Software Migration'),
    ]


def index_page(marks, total):
    rows = [['CHAPTER NO.', 'TOPIC', 'P.NO']]
    starts = marks['chapters'] if marks else {}
    for n, (title, sections) in enumerate(CHAPTERS, 1):
        topic = f'<b>{title}</b>' + ''.join(f'<br/>&nbsp;&nbsp;&nbsp;&nbsp;{escape(s)}' for s in sections)
        if n in starts:
            end = (starts[n + 1] - 1) if n + 1 in starts else total
            pno = str(starts[n]) if end <= starts[n] else f'{starts[n]}-{end}'
        else:
            pno = '—'
        rows.append([f'{n:02d}', topic, pno])
    data = [[Paragraph(r[0], S['cellb' if i == 0 else 'cell']),
             Paragraph(r[1], S['cellb' if i == 0 else 'cell']),
             Paragraph(r[2], S['cellb' if i == 0 else 'cell'])] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[0.16 * FRAME_W, 0.66 * FRAME_W, 0.18 * FRAME_W])
    t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.6, BLACK), ('BACKGROUND', (0, 0), (-1, 0), GREY),
                           ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('TOPPADDING', (0, 0), (-1, -1), 4),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
    return [PageBreak(), front_heading('INDEX'), t]


FIGURE_LIST = [
    ('3.4.1', 'SDLC Stages Followed in the Project'),
    ('5.1.1', 'Class Diagram'), ('5.1.2', 'Use Case Diagram'), ('5.1.3', 'Sequence Diagram'),
    ('5.1.4', 'Collaboration Diagram'), ('5.1.5', 'Component Diagram'), ('5.1.6', 'Deployment Diagram'),
    ('5.1.7', 'Activity Diagram'), ('5.1.8', 'Data Flow Diagram'),
    ('8.1', 'Dashboard'), ('8.2', 'All Businesses'), ('8.3', 'Add Business Form'),
    ('8.4', 'Form Validation Errors'), ('8.5', 'Business Detail'), ('8.6', 'Generated Design — Prestige Style'),
    ('8.7', 'Generated Design — Velocity Style'),
]


def figures_page(marks):
    pages = {num: pg for num, _, pg in marks['figures']} if marks else {}
    rows = [['FIGURE NO.', 'FIGURE NAME', 'P.NO']] + [[n, t, str(pages.get(n, '—'))] for n, t in FIGURE_LIST]
    return [PageBreak(), front_heading('LIST OF FIGURES'), grid(rows, [0.18, 0.64, 0.18])]


# ─── Chapters ──────────────────────────────────────────────────────────────

def ch1():
    return chapter(1) + [
        P('A website is now the first place customers look for a business: to read what it offers, to find its '
          'address and opening hours, and to decide whether to call or visit. Many small businesses still have '
          'none. A custom website from a design agency takes days of work — a brief, copywriting, visual design, '
          'HTML and CSS development and revisions — and its cost is out of reach for a neighbourhood restaurant '
          'or a single-doctor clinic. Template-based site builders are cheaper, but the owner still has to write '
          'the content and assemble the pages, and the results tend to look alike.'),
        P('Large language models (LLMs) changed what can be automated in this process. A model such as GPT-4o can '
          'analyse a business from a few facts, write persuasive marketing copy in a chosen tone, and produce '
          'complete HTML and CSS for a page when it is given precise instructions. AutoBiz AI uses this ability in a '
          'controlled way: instead of a single open-ended request, the work is split into small, well-defined '
          'steps, each handled by a dedicated agent with its own prompt and its own stored result. The output of '
          'one step becomes the input of the next, and every step can be inspected and repeated.'),
        P('An operator (for example a freelancer or a small agency) adds a business through a web dashboard. The '
          'pipeline then enriches the business with a brand profile, writes a content strategy, generates five '
          'complete website designs in five distinct visual styles, and writes them to disk. The operator previews '
          'the designs, downloads them as a ZIP file and presents them to the business owner. When the business '
          'already has a website, the Design agent fetches it first and produces redesigns that reuse its real '
          'content.'),
        P('The first version of AutoBiz AI was written in PHP with the CodeIgniter 4 framework. This project '
          're-implements the complete application in Python with the Django framework, keeping the behaviour and '
          'data of the original while improving its structure, testability and ease of setup.'),
    ] + h2('1.1 Objective of the Project') + [
        P('The objectives of the project are:'),
    ] + bullets([
        'To generate complete, responsive single-page websites for a business automatically from a small set of '
        'facts, using a pipeline of specialised LLM agents.',
        'To give the operator a dashboard to onboard businesses, run the pipeline, follow its progress, preview '
        'the generated designs and download them.',
        'To port the existing CodeIgniter 4 / PHP application to Python and Django without changing its database '
        'schema, prompts or user interface, so existing data can be migrated unchanged.',
        'To make the system easy to install and verify: a one-click start script, an offline mode that needs no '
        'API key, and an automated test suite.',
    ], numbered=True) + h2('1.2 Scope of the Project') + [
        P('The project covers the full web application: the five database tables, the seven services (OpenAI '
          'client, Enrichment, Strategy, Design, Build, Hosting and Outreach agents) and the Orchestrator that runs '
          'them, ten web routes with four screens, a command-line pipeline runner, a data importer for the original '
          'database and an administration panel. The Hosting and Outreach agents are implemented but switched off '
          'in the pipeline, as in the original, because generated designs are delivered as a ZIP download. '
          'Automatic discovery of businesses (web scraping) is outside the current scope.'),
    ]


LITERATURE = [
    ('"Language Models are Few-Shot Learners"', 'T. Brown et al., 2020.',
     'This paper introduced GPT-3, a 175-billion-parameter language model, and showed that a sufficiently large '
     'model can perform new tasks from a natural-language instruction and a few examples, without task-specific '
     'training. This "in-context learning" is the basis of AutoBiz AI: every agent describes its task, the expected '
     'output format and the business data in the prompt, and relies on the model to follow the instructions.'),
    ('"Evaluating Large Language Models Trained on Code"', 'M. Chen et al., 2021.',
     'The authors present Codex, a GPT model fine-tuned on public source code, and the HumanEval benchmark for '
     'measuring whether generated programs are functionally correct. The work showed that language models can '
     'write working code from a description, and that sampling and checking outputs improves reliability — the '
     'reason AutoBiz AI validates every generated page (it must contain an HTML document) before storing it.'),
    ('"pix2code: Generating Code from a Graphical User Interface Screenshot"', 'T. Beltramelli, 2017.',
     'pix2code trains a neural network to translate a screenshot of a user interface into code for web, Android '
     'and iOS targets. It was an early demonstration that front-end code can be produced automatically from a '
     'visual specification. AutoBiz AI approaches the same goal from text: the visual specification is a written '
     'page blueprint and a CSS foundation instead of an image.'),
    ('"Design2Code: How Far Are We From Automating Front-End Engineering?"', 'C. Si et al., 2024.',
     'Design2Code builds a benchmark of real web pages and measures how closely multimodal LLMs can reproduce '
     'them as HTML and CSS. The study reports that current models already produce usable pages and that detailed '
     'prompting improves layout fidelity. This supports the design choice in AutoBiz AI of giving the model a '
     'section-by-section blueprint and a fixed set of CSS variables instead of a short request.'),
    ('"ReAct: Synergizing Reasoning and Acting in Language Models"', 'S. Yao et al., 2023.',
     'ReAct interleaves model reasoning with actions such as tool calls, so that each step can use information '
     'gathered in the previous one. AutoBiz AI applies a simpler, deterministic form of this idea: the Orchestrator '
     'fixes the order of steps, and each agent acts on the stored results of the earlier ones.'),
    ('"ChatDev: Communicative Agents for Software Development"', 'C. Qian et al., 2023.',
     'ChatDev organises several LLM agents with roles such as designer, programmer and tester into a virtual '
     'software company that follows a waterfall-style process. The paper shows that dividing a large generation '
     'task among role-specific agents improves completeness. AutoBiz AI follows the same principle with roles '
     'for brand analysis, copywriting, design and build.'),
    ('"MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework"', 'S. Hong et al., 2023.',
     'MetaGPT encodes standard operating procedures into a multi-agent framework, with each agent producing a '
     'structured document for the next. Structured hand-offs reduce errors that build up across steps. In '
     'AutoBiz AI the hand-offs are JSON objects (brand profile, content strategy) stored in the database, which '
     'makes each step repeatable and easy to inspect.'),
]


def ch2():
    out = chapter(2) + [
        P('The project draws on research in large language models, automatic code generation and multi-agent LLM '
          'systems. The works below informed the design of the agent pipeline.'),
    ]
    for title, authors, text in LITERATURE:
        out.append(KeepTogether([P(title, 'lit_title'), P(authors, 'lit_auth'), P(text)]))
    out += [
        P('<b>Summary.</b> The literature shows that LLMs can write convincing copy and working front-end code, and '
          'that splitting a large task among specialised agents with structured hand-offs makes the result more '
          'complete and reliable. AutoBiz AI combines these findings into a practical tool for one domain — '
          'websites for small businesses — with fixed visual styles to keep the output consistent.'),
    ]
    return out


def ch3():
    modules = [
        ('Dashboard', 'Overview page with a count of businesses per pipeline stage, conversion, contact and deploy '
                      'rates, the agent pipeline and the eight most recent businesses.'),
        ('Business management', 'List with stage filter and pagination, onboarding form with validation, detail '
                                'page, manual status change and delete (rows and build files).'),
        ('Enrichment agent', 'Sends the business facts to GPT-4o and stores a brand profile: summary, target '
                             'audience, branding notes, unique selling proposition, tone, colour palette, keywords.'),
        ('Strategy agent', 'Writes the website copy as JSON: hero headline and sub-headline, about text, 3–4 '
                           'services, call to action, footer tagline and SEO page title.'),
        ('Design agent', 'For each of the five styles, builds a detailed prompt and asks the model for a complete '
                         'HTML page; fetches an existing website first to switch to redesign mode.'),
        ('Build agent', 'Writes every draft design to writable/builds/<business>/v<N>_<style>.html and marks it built.'),
        ('Preview and download', 'Serves a stored design as a web page and packs all built files into a ZIP file.'),
        ('Hosting agent', 'Uploads built pages by FTP and records demo URLs (implemented, disabled).'),
        ('Outreach agent', 'Sends an HTML e-mail with demo links to the owner by SMTP (implemented, disabled).'),
        ('Orchestrator and CLI', 'Runs the agents in order for one business or for all pending ones; available as '
                                 'manage.py agent_run and run_pipeline.bat.'),
        ('Data migration and admin', 'import_legacy copies all data from the original database; the Django admin '
                                     'gives direct access to all five tables.'),
    ]
    return chapter(3) + h2('3.1 Existing System') + [
        P('Without automation, a website for a small business is produced manually: an agency collects '
          'information from the owner, a copywriter drafts the text, a designer prepares mock-ups and a developer '
          'builds the pages. Each design option multiplies the effort, so owners usually see only one or two '
          'proposals.'),
        P('The first automated version of AutoBiz AI was written in PHP 8 on CodeIgniter 4.4, served by Apache '
          'from XAMPP with a MariaDB 10.4 database. It introduced the agent pipeline, but had several weaknesses '
          'that were found while analysing it for the port:'),
        P('<b>Disadvantages:</b>'),
    ] + bullets([
        'No automated tests; every change had to be checked by hand.',
        'Without an OpenAI key the stub replies returned HTML to the Strategy agent, so the offline pipeline always '
        'stopped at the second step.',
        'The manual status endpoint wrote any submitted value to the database.',
        'Setup required configuring Apache virtual hosts and running migrations by hand.',
        'Interface text promised ten designs although five styles exist; the outreach e-mail had a hard-coded reply '
        'address.',
    ], numbered=True) + h2('3.2 Proposed System') + [
        P('The proposed system is the Django edition of AutoBiz AI. It keeps the five tables with identical names, '
          'the seven services, the five design styles and prompts, and the four screens, and re-implements them in '
          'Python. The pipeline produces five complete designs for a business in a few minutes, so an owner can '
          'compare several finished options instead of mock-ups.'),
        P('<b>Advantages:</b>'),
    ] + bullets([
        'Five complete, responsive designs per business with no manual design work.',
        'One-click setup and start with run.bat; works with MySQL, MariaDB or SQLite.',
        f'{TESTS} automated tests and an offline mode that runs the whole pipeline without API cost.',
        'Existing data migrates unchanged through the import_legacy command.',
        'Input validation, CSRF protection and POST-only state changes from the Django framework.',
    ], numbered=True) + h2('3.3 Modules') + [
        grid([['Module', 'Description']] + [list(m) for m in modules], [0.26, 0.74], bold_first=True),
        Spacer(1, 8),
    ] + h2('3.4 Feasibility Analysis') + [
        P('<b>Technical feasibility.</b> The system uses mature, free technologies — Python, Django, PyMySQL and '
          'MariaDB — and a commercial API that is reachable over HTTPS. It runs on an ordinary Windows PC with '
          'XAMPP. The only non-standard requirement, Django 6 on MariaDB 10.4, was solved with a small database '
          'backend and verified by the test suite.'),
        P('<b>Economic feasibility.</b> All software used is open source. The running cost is the OpenAI usage: '
          'seven model calls per business (one enrichment, one strategy and five designs). This is small compared '
          'with the cost of designing five websites by hand, and the offline mode allows development and '
          'demonstrations at no cost.'),
        P('<b>Operational feasibility.</b> The operator works in a familiar web dashboard; starting the system is a '
          'double-click. The pipeline shows a progress overlay while it runs, and every result can be previewed, '
          'regenerated or deleted.'),
        P('<b>Software development life cycle.</b> The project followed the stages shown in Fig 3.4.1, adapted to '
          'a migration project: the requirements were derived from the existing code, and every stage was checked '
          'against the behaviour of the original.'),
        figure(uml.sdlc_diagram(), '3.4.1', 'SDLC Stages Followed in the Project', 165),
    ]


def ch4():
    frs = [
        ['FR-01', 'Add a business with name, type, category, location, address, phone, e-mail, website status, '
                  'website URL, rating and review count; validate the input.'],
        ['FR-02', 'Run the pipeline for one business from the dashboard ("Run", "Save & Run").'],
        ['FR-03', 'Generate a brand profile, a content strategy and one complete HTML design per style.'],
        ['FR-04', 'Redesign mode: fetch an existing website and use its title, theme colour and text.'],
        ['FR-05', 'Save built designs to disk; preview any design; download all designs as a ZIP file.'],
        ['FR-06', 'Regenerate designs: delete the old designs and files and run strategy, design and build again.'],
        ['FR-07', 'List businesses with stage filter and pagination; show a dashboard with stage counts and rates.'],
        ['FR-08', 'Change a business status by hand (only the seven valid values); delete a business and its data.'],
        ['FR-09', 'Run the pipeline from the command line for all pending businesses or for one id.'],
        ['FR-10', 'Import all data from the original CodeIgniter database.'],
        ['FR-11', 'Deploy designs by FTP and send outreach e-mail (available, disabled by default).'],
    ]
    return chapter(4) + h2('4.1 Software Requirement Specification') + [
        P('A Software Requirements Specification (SRS) is a complete description of the behaviour of the system to '
          'be developed. It lists the functional requirements — what the system must do — and the non-functional '
          'requirements that constrain how it does it.'),
    ] + h3('4.1.1 Overall Description') + [
        P('AutoBiz AI is a stand-alone web application used by one operator role. It runs on the operator\'s '
          'computer or on a server, stores its data in a MySQL-compatible database, and calls the OpenAI API to '
          'generate content. The operator needs only a web browser. The system must stay compatible with the '
          'database schema of the original application.'),
    ] + h3('4.1.2 Functional Requirements') + [
        grid([['ID', 'Requirement']] + frs, [0.11, 0.89], bold_first=True), Spacer(1, 6),
    ] + h3('4.1.3 Non-Functional Requirements') + bullets([
        '<b>Performance:</b> a full pipeline run (seven model calls) completes in about 1–3 minutes; dashboard '
        'pages render in well under a second.',
        '<b>Security:</b> CSRF protection on every form; state changes only through POST; validated input; '
        'secrets kept in a .env file outside version control; the server binds to the local machine by default.',
        '<b>Reliability:</b> a failed step marks the business "skipped" instead of failing the request; a style '
        'whose reply is not HTML is skipped while the others continue.',
        '<b>Maintainability:</b> one module per agent, settings in one place, automated tests for the pipeline and '
        'every route.',
        '<b>Portability:</b> runs on Windows, Linux or macOS with Python 3.12+; supports MySQL, MariaDB and SQLite.',
    ]) + h3('4.1.4 External Interfaces') + bullets([
        '<b>User interface:</b> web dashboard built with Django templates and Tailwind CSS.',
        '<b>Software interfaces:</b> OpenAI Chat Completions API over HTTPS; MySQL/MariaDB over TCP 3306; SMTP and '
        'FTP for the optional agents.',
        '<b>Operating environment:</b> Windows 10/11 with XAMPP (MariaDB) and Python, or any server with Python '
        'and MySQL.',
    ]) + h2('4.2 Hardware and Software Requirements') + [
        P('<b>A. Hardware Requirements:</b>'),
        grid([['Component', 'Minimum'], ['Processor', 'Intel Core i3 or equivalent'],
              ['RAM', '4 GB (8 GB recommended)'], ['Hard disk', '1 GB free for the application, database and builds'],
              ['Network', 'Internet connection for the OpenAI API']], [0.3, 0.7], bold_first=True),
        Spacer(1, 8),
        P('<b>B. Software Requirements:</b>'),
        grid([['Software', 'Version / purpose'], ['Operating system', 'Windows 10/11 (tested), Linux or macOS'],
              ['Programming language', 'Python 3.13 (3.12 or newer)'], ['Framework', 'Django 6.1.2'],
              ['Database', 'MariaDB 10.4+ (XAMPP) or MySQL 8; SQLite for demonstrations'],
              ['Libraries', 'PyMySQL 1.2.3, requests 2.34, python-dotenv 1.2'],
              ['AI service', 'OpenAI API key (model gpt-4o); optional — offline stub without it'],
              ['Browser', 'Any current browser (Chrome, Edge, Firefox)']], [0.3, 0.7], bold_first=True),
    ]


def ch5():
    out = chapter(5) + h2('5.1 UML Diagrams') + [
        P('The Unified Modelling Language (UML) is a standard language for specifying, visualising and documenting '
          'the structure and behaviour of a software system. The structural diagrams below (class, component and '
          'deployment) describe how AutoBiz AI is organised; the behavioural diagrams (use case, sequence, '
          'collaboration and activity) and the data flow diagram describe how it works when the pipeline runs.'),
    ]
    items = [
        ('a) Class Diagram', 'The class diagram shows the five persistent classes of the domain model, their '
         'attributes and their associations. A Business owns its enrichments, designs and outreach e-mails, and '
         'every design can have FTP deployments. All associations are compositions: deleting a business deletes '
         'everything that belongs to it.', uml.class_diagram_models(), '5.1.1', 'Class Diagram', 345),
        ('b) Use Case Diagram', 'The use case diagram shows how the actors interact with the system. The operator '
         'uses the dashboard for all tasks; a command-line user or scheduler processes all pending businesses; the '
         'OpenAI API is the external system used by every pipeline run.', uml.use_case_diagram(), '5.1.2',
         'Use Case Diagram', 360),
        ('c) Sequence Diagram', 'The sequence diagram shows the messages exchanged, in time order, when the operator '
         'presses "Run Pipeline": the view calls the Orchestrator, which calls each agent in turn; the agents call '
         'the OpenAI API and store their results.', uml.sequence_diagram(), '5.1.3', 'Sequence Diagram', 400),
        ('d) Collaboration Diagram', 'The collaboration (communication) diagram shows the same interaction as the '
         'sequence diagram, organised around the objects and their links. Message numbers give the order; numbers '
         'such as 3.1 are messages sent while handling message 3.', uml.collaboration_diagram(), '5.1.4',
         'Collaboration Diagram', 320),
        ('e) Component Diagram', 'The component diagram shows the parts of the system and their dependencies: the '
         'Django project with routing, views, templates, services, models and management commands, the storage it '
         'uses and the external systems it calls.', uml.component_diagram(), '5.1.5', 'Component Diagram', 285),
        ('f) Deployment Diagram', 'The deployment diagram shows the physical nodes: the Windows PC that runs the '
         'Django server and the XAMPP MariaDB server with the new and the legacy database, and the internet '
         'services the system connects to.', uml.deployment_diagram(), '5.1.6', 'Deployment Diagram', 222),
        ('g) Activity Diagram', 'The activity diagram shows the control flow of the Orchestrator for one business, '
         'including the decisions that skip enrichment for an enriched business and stop the run when a step '
         'fails.', uml.activity_diagram(), '5.1.7', 'Activity Diagram', 470),
        ('h) Data Flow Diagram', 'The level-1 data flow diagram shows how data moves between the external entities, '
         'the six main processes and the four data stores, from the business details entered by the operator to '
         'the finished files.', uml.dfd_diagram(), '5.1.8', 'Data Flow Diagram', 262),
    ]
    for title, text, drawing, num, name, max_h in items:
        out.append(KeepTogether([Paragraph(title, S['h3']), P(text), *figure(drawing, num, name, max_h, keep=False)]))
    out += [
        P('<b>Business status life cycle.</b> A new business starts as <i>pending</i>. A stored brand profile '
          'moves it to <i>enriched</i>, and built designs to <i>designed</i>; Regenerate moves it back to '
          '<i>enriched</i>. A failed enrichment or strategy step sets <i>skipped</i>. <i>Deployed</i> and '
          '<i>contacted</i> follow when the Hosting and Outreach agents are enabled, and <i>converted</i> is set '
          'by hand; the manual status form accepts only these seven values.'),
    ]
    out += h2('5.2 Database Design') + [
        P('The database has five tables. Table and column names are identical to the original CodeIgniter '
          'migrations, so data can be copied between the two systems without conversion. All foreign keys use '
          'ON DELETE CASCADE, and every table has created_at and updated_at timestamps. The status values '
          'are listed in the class diagram (Fig 5.1.1).'),
        grid([['Table', 'Primary key / foreign key', 'Main columns'],
              ['restaurants', 'id', 'name, business_type, category, location, address, phone, email, rating, '
                                    'review_count, website_status, website_url, scrape_source, status'],
              ['enrichments', 'id / restaurant_id', 'business_summary, target_audience, branding_notes, usp, tone, '
                                                   'color_palette, keywords, raw_gpt_response'],
              ['designs', 'id / restaurant_id', 'version, style_name, html_code, css_framework, preview_path, status'],
              ['deployments', 'id / design_id', 'url, subdomain, ftp_path, status, error_msg, deployed_at'],
              ['emails', 'id / restaurant_id', 'to_email, subject, body, demo_links, sent_status, response_status, '
                                              'sent_at, error_msg']],
             [0.17, 0.25, 0.58], mono_cols=(0,)),
    ]
    return out


def ch6():
    pipeline = source(Orchestrator.process_business)
    return chapter(6) + h2('6.1 Python and Django') + [
        P('Python is a high-level, general-purpose programming language known for readable syntax, a large '
          'standard library and a wide ecosystem of third-party packages. It is the most widely used language for '
          'working with AI services, and its "batteries included" approach keeps application code short. AutoBiz AI '
          'uses Python 3.13.'),
        P('Django is a Python web framework that follows the model–template–view pattern. It provides an '
          'object-relational mapper (ORM) and migrations for the database, URL routing, form validation, a template '
          'language, sessions and messages, protection against cross-site request forgery, an automatic '
          'administration interface and a test framework. These built-in parts replace most of the code that had '
          'to be written by hand in the PHP version.'),
        grid([['Library', 'Use in the project'],
              ['Django 6.1.2', 'Web framework: models, views, templates, forms, admin, tests'],
              ['PyMySQL 1.2.3', 'Pure-Python MySQL driver (no C compiler needed on Windows)'],
              ['requests 2.34', 'HTTP calls to the OpenAI API and to existing client websites'],
              ['python-dotenv 1.2', 'Loads settings and secrets from the .env file'],
              ['ftplib, zipfile (standard)', 'FTP upload in the Hosting agent; ZIP download'],
              ['Tailwind CSS (CDN)', 'Styling of the dashboard templates']], [0.32, 0.68], bold_first=True),
        Spacer(1, 6),
    ] + h2('6.2 Algorithms') + h3('A. Pipeline orchestration') + bullets([
        'Load the business; stop if it does not exist.',
        'If the status is pending, run the Enrichment agent; if its reply cannot be parsed, set the status to '
        'skipped and stop.',
        'Run the Strategy agent; if it returns no content, set the status to skipped and stop.',
        'For each of the five styles, build the design prompt and request an HTML page; keep only replies that '
        'contain an HTML document. Stop if no design was produced.',
        'Write every draft design to disk and mark it built; if any file was written, set the status to designed.',
    ], numbered=True) + h3('B. Design prompt construction') + [
        P('The prompt for one style concatenates: the mode (fresh design, or redesign with the fetched title, theme '
          'colour and text), the style concept, the font and animation-library links, the CSS foundation the model '
          'must paste verbatim, the section-by-section page blueprint, the business data and content strategy, a '
          'quality rubric, and a fixed JavaScript block for scroll animations, counters and card tilt. A system '
          'message requires raw HTML only and colours through CSS variables only.'),
    ] + h3('C. Existing-site analysis') + [
        P('The page is downloaded (TLS verified first, unverified only after a TLS error). The algorithm extracts the '
          '&lt;title&gt;, the theme-color meta tag and the first 600 characters of visible text after removing '
          'scripts, styles and comments. Hex colours found in the page are kept only if their perceived brightness '
          'B = (299·R + 587·G + 114·B) / 1000 lies between 30 and 230, which drops near-black and near-white values; '
          'at most six are kept.'),
    ] + h3('D. Reply parsing and offline mode') + [
        P('Model replies may be wrapped in Markdown code fences; the parser removes a leading ```json and a trailing '
          '``` and accepts the reply only if it decodes to a JSON object. Without an API key, the client returns '
          'stub content chosen by the system message: JSON when the agent asks for JSON, a sample HTML page '
          'otherwise.'),
    ] + h2('6.3 Sample Code') + [
        P('The listing below is the core of the system, taken directly from the project source: the '
          'Orchestrator method that runs the agent pipeline for one business.'),
        code(pipeline, 'dashboard/services/orchestrator.py — Orchestrator.process_business()'),
    ]


def ch7():
    cases = [
        ['01', 'Add business', 'Valid form saves and redirects', 'Submit name, type, city', 'Business saved as '
         'pending, redirect to detail', 'As expected', 'Pass', 'High'],
        ['02', 'Form validation', 'Invalid input is rejected', 'Name "A", empty city, bad e-mail', 'Form shown '
         'again with errors, nothing saved', 'As expected', 'Pass', 'High'],
        ['03', 'Run pipeline', 'Pipeline produces 5 designs', 'Run for a pending business', 'Status designed, 5 '
         'built designs and files', 'As expected', 'Pass', 'High'],
        ['04', 'Enrichment failure', 'Bad model reply handled', 'Model returns non-JSON', 'Status set to skipped',
         'As expected', 'Pass', 'High'],
        ['05', 'Batch run', 'Only pending, no-website businesses', 'Run agent_run without id', 'Business with a '
         'website untouched', 'As expected', 'Pass', 'Medium'],
        ['06', 'Download ZIP', 'Built designs are zipped', 'Open /businesses/{id}/download', 'ZIP with 5 HTML files',
         'As expected', 'Pass', 'High'],
        ['07', 'Preview', 'Stored design is served', 'Open /preview/{id}', 'HTML page displayed', 'As expected',
         'Pass', 'High'],
        ['08', 'Regenerate', 'Old designs replaced', 'Press Regenerate', 'Old designs deleted, 5 new designs',
         'As expected', 'Pass', 'Medium'],
        ['09', 'Delete', 'Rows and files removed', 'Press Delete', 'Business, designs and build folder removed',
         'As expected', 'Pass', 'High'],
        ['10', 'Manual status', 'Only valid statuses', 'Post "hacked", then "converted"', 'First rejected, second '
         'saved', 'As expected', 'Pass', 'Medium'],
        ['11', 'POST only', 'State changes need POST', 'GET the delete URL', 'HTTP 405', 'As expected', 'Pass',
         'Medium'],
        ['12', 'Not found', 'Unknown ids', 'Open business 999, preview 999', 'HTTP 404', 'As expected', 'Pass',
         'Low'],
        ['13', 'Legacy import', 'Data copied from CI4 database', 'Run import_legacy', '1 business, 1 enrichment, 5 '
         'designs, files rebuilt', 'As expected', 'Pass', 'High'],
        ['14', 'Style parity', 'Styles equal the PHP source', 'Compare via PHP reflection', '5 of 5 identical',
         'As expected', 'Pass', 'High'],
    ]
    return chapter(7) + [
        P('Implementation is the stage in which the design becomes a working system, and testing confirms that it '
          'does what the requirements say. Because this project is a port, testing had two goals: that every '
          'function works, and that the behaviour matches the original PHP application.'),
    ] + h2('7.1 Types of Testing') + bullets([
        '<b>Unit testing</b> checks single functions in isolation — for example the slug rule for build folders and '
        'the parsing of model replies.',
        '<b>Integration testing</b> checks that the agents, the database and the file system work together: the '
        'whole pipeline is run with the offline stub and its rows and files are inspected.',
        '<b>Functional (system) testing</b> exercises every route through Django\'s test client: forms, run, '
        'download, preview, regenerate, status change, delete, error pages.',
        '<b>Regression and parity testing</b> compares the port with the original: the five styles, the JavaScript '
        'block and the CDN links were compared with the PHP source, and the legacy data was imported.',
        '<b>Acceptance testing</b> runs the system as the operator would: run.bat on the target PC, every page '
        'opened in a browser, previews and the ZIP download checked.',
        '<b>White-box and black-box testing:</b> unit and integration tests are written with knowledge of the code '
        '(white box); functional and acceptance tests use only inputs and outputs (black box).',
    ]) + h2('7.2 Test Cases') + [
        grid([['Test Case Id', 'Test Case Name', 'Test Case Desc.', 'Step', 'Expected', 'Actual', 'Status',
               'Priority']] + cases, [0.08, 0.13, 0.15, 0.17, 0.19, 0.1, 0.08, 0.1]),
        Spacer(1, 8),
        P(f'<b>Result:</b> all {TESTS} automated tests pass on the XAMPP MariaDB 10.4.32 server '
          '(<font name="Mono" size="10">manage.py test dashboard</font>). Cases 13 and 14 were run as scripted '
          'checks during the port. Not yet verified: a live run against the OpenAI API, and real SMTP and FTP '
          'transfers, which are disabled in the pipeline.'),
    ]


def ch8():
    runlog = '''[1/5] Virtual environment found.
[2/5] Installing requirements...
[3/5] Ensuring database exists...
  MySQL database `autobiz_ai_django` is ready.
[4/5] Applying migrations...
  No migrations to apply.
[5/5] Starting server at http://127.0.0.1:8000  (Ctrl+C to stop)'''
    w = FRAME_W * 0.74
    return chapter(8) + [
        P('To run the project, install Python 3.13 and XAMPP, and start MySQL in the XAMPP control panel. Then '
          'double-click <b>run.bat</b> in the project folder. On the first run it creates a virtual environment and '
          'installs the packages from requirements.txt; every run creates the database if needed, applies the '
          'migrations and starts the web server, then opens the browser at http://127.0.0.1:8000.'),
        code(runlog, 'run.bat — console output'),
        Spacer(1, 10),
        shot('shot_dashboard.png', '8.1', 'Dashboard', w),
        P('In above screen the dashboard shows how many businesses are in each pipeline stage, the conversion, '
          'contact and deploy rates, the six agents and the most recent businesses. Click "All Businesses" in the '
          'menu to get below page.'),
        shot('shot_list.png', '8.2', 'All Businesses', w),
        P('In above screen all businesses are listed with their location, type, rating and stage. The tabs filter '
          'by stage, and hovering a row shows the View, Run and Delete buttons. Click "Add Business" to get below '
          'page.'),
        shot('shot_add.png', '8.3', 'Add Business Form', w),
        P('In above screen the operator enters the business details in four sections. "Save Business" stores it; '
          '"Save &amp; Run Pipeline" stores it and generates the designs immediately. If the input is invalid the '
          'form is shown again with messages, as in below screen.'),
        shot('shot_add_errors.png', '8.4', 'Form Validation Errors', w),
        P('In above screen the name is too short, the type and city are missing and the e-mail address is invalid; '
          'each field is highlighted with its own message and nothing is saved.'),
        shot('shot_detail.png', '8.5', 'Business Detail', w),
        P('In above screen the business detail page shows the contact and source information, the pipeline '
          'progress and the five generated designs. The buttons run the pipeline, regenerate the designs, '
          'download the ZIP file or delete the business. Clicking "Preview" on a design opens it, as in below '
          'screens.'),
        shot('shot_design_prestige.png', '8.6', 'Generated Design — Prestige Style', w),
        P('In above screen the Prestige design for the business uses a dark navy background with champagne-gold '
          'accents, a serif headline built from the generated copy and an animated statistics card.'),
        shot('shot_design_velocity.png', '8.7', 'Generated Design — Velocity Style', w),
        P('In above screen the Velocity design for the same business uses a light layout with an indigo-to-purple '
          'gradient. Similarly, the Canvas, Obsidian and Editorial designs can be previewed, and all five can be '
          'downloaded together as a ZIP file.'),
    ]


def ch9():
    return chapter(9) + [
        P('This project shows that a pipeline of specialised language-model agents can turn a handful of facts about '
          'a business into several complete, professional website designs in a few minutes. Splitting the work into '
          'enrichment, strategy, design and build steps, each with a precise prompt and a stored result, keeps the '
          'output consistent and makes every step repeatable; five fixed visual styles with verbatim CSS foundations '
          'give the owner real choice while keeping quality predictable.'),
        P('The re-implementation in Python and Django achieved its goals. The database schema, prompts, design styles '
          'and user interface are unchanged, and the original data was migrated with one command. At the same time '
          'the system became easier to install (one double-click), safer (validated input, CSRF protection, POST-only '
          f'changes) and verifiable ({TESTS} automated tests that pass on the target MariaDB 10.4 server). Several '
          'defects of the original were fixed on the way, including the offline mode that stopped at the strategy '
          'step.'),
        P('AutoBiz AI is therefore ready for local use by an operator, and its modular agent design leaves a clear '
          'path for the enhancements described in the next chapter.'),
    ]


def ch10():
    return chapter(10) + [
        P('The current system provides a solid base for real-world use. The following enhancements are planned, '
          'with rough effort estimates:'),
    ] + bullets([
        '<b>Background processing (1–2 days).</b> Run the pipeline in a task queue (Django-Q2, Celery or RQ) with '
        'live progress, so the browser no longer waits 1–3 minutes for a request.',
        '<b>Authentication (½ day).</b> Require a login for the dashboard so that only authorised users can start '
        'paid API calls.',
        '<b>Production deployment (1 day).</b> Serve with waitress or gunicorn behind IIS or nginx, with '
        'DEBUG off and a supported database (MariaDB 10.11+ or MySQL 8.4).',
        '<b>Live hosting and outreach (1 day).</b> Re-enable the Hosting and Outreach agents and test FTP upload and '
        'e-mail delivery end to end.',
        '<b>Lead discovery (2–3 days).</b> A scraping agent (the project already has an Apify token configured) that '
        'finds businesses without websites and adds them automatically.',
        '<b>Static front-end build (½ day).</b> Compile Tailwind CSS into static files instead of loading it from a '
        'CDN.',
        '<b>Design editing and selection.</b> Let the owner pick a design, edit texts and images in place and '
        'publish the selected site.',
        '<b>More styles and languages.</b> Additional visual styles per industry and generation of the website copy '
        'in regional languages.',
    ], numbered=True)


def ch11():
    refs = [
        'T. Brown et al., "Language Models are Few-Shot Learners", Advances in Neural Information Processing '
        'Systems (NeurIPS), vol. 33, 2020.',
        'M. Chen et al., "Evaluating Large Language Models Trained on Code", arXiv:2107.03374, 2021.',
        'T. Beltramelli, "pix2code: Generating Code from a Graphical User Interface Screenshot", Proc. ACM SIGCHI '
        'Symposium on Engineering Interactive Computing Systems, 2018 (arXiv:1705.07962, 2017).',
        'C. Si, Y. Zhang, Z. Yang, R. Liu and D. Yang, "Design2Code: How Far Are We From Automating Front-End '
        'Engineering?", arXiv:2403.03163, 2024.',
        'S. Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models", International Conference on '
        'Learning Representations (ICLR), 2023.',
        'C. Qian et al., "ChatDev: Communicative Agents for Software Development", arXiv:2307.07924, 2023.',
        'S. Hong et al., "MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework", arXiv:2308.00352, '
        '2023.',
        'OpenAI, "GPT-4 Technical Report", arXiv:2303.08774, 2023.',
        'Django Software Foundation, Django documentation, https://docs.djangoproject.com/',
        'OpenAI, API reference — Chat Completions, https://platform.openai.com/docs/api-reference/chat',
        'CodeIgniter Foundation, CodeIgniter 4 User Guide, https://codeigniter.com/user_guide/',
        'MariaDB Foundation, MariaDB Server documentation, https://mariadb.com/kb/en/documentation/',
        'PyMySQL contributors, PyMySQL documentation, https://pymysql.readthedocs.io/',
        'Object Management Group, OMG Unified Modeling Language (UML) Specification, version 2.5.1, 2017.',
        'C. Gane and T. Sarson, Structured Systems Analysis: Tools and Techniques, Prentice Hall, 1979.',
        'ReportLab, ReportLab PDF library user guide, https://docs.reportlab.com/',
    ]
    return chapter(11) + [Paragraph(f'[{i}] {escape(r)}', S['ref']) for i, r in enumerate(refs, 1)]


# ─── Build (two passes for real page numbers) ──────────────────────────────

def story(marks, total):
    s = title_page() + abstract() + index_page(marks, total) + figures_page(marks)
    for ch in (ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11):
        s += ch()
    return s


def build():
    marks, total = None, None
    for _ in range(4):
        doc = ReportDoc(io.BytesIO())
        doc.build(story(marks, total))
        new_total = doc.logical()
        if doc.marks == marks and new_total == total:
            break
        marks, total = doc.marks, new_total
    doc = ReportDoc(str(OUT))
    doc.build(story(marks, total))
    print(f'wrote {OUT}: {doc.page} pages ({doc.page - doc.logical()} front matter + {doc.logical()} numbered)')


if __name__ == '__main__':
    build()

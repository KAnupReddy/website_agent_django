"""
The five visual styles the DesignAgent generates, one website per style.

Each style has a concept, a Google Fonts link, a verbatim CSS foundation the
model must paste into its <style> block, and a section-by-section page blueprint.
"""

STYLES = [
    {
        'name': 'prestige',
        'img_palette': '0E1826/C5973A',
        'concept': 'Established market leader. Dark navy authority with champagne gold accents. The visitor feels they have landed on the premium, undisputed choice in the market. Every detail signals trust, experience, and worth the premium price.',
        'fonts_href': 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,600;1,700&family=DM+Sans:wght@300;400;500;600;700&display=swap',
        'css_foundation': """\
:root{--bg:#08111F;--surface:#0E1826;--card:#142030;--border:rgba(197,151,58,0.16);--prim:#C5973A;--prim-l:#E8C97A;--txt:#E8EDF5;--muted:#7A93B8;--head:#FFFFFF;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;}
body{background:var(--bg);color:var(--txt);font-family:'DM Sans',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;}
h1,h2,h3,h4{font-family:'Cormorant Garamond',serif;color:var(--head);line-height:1.06;}
h1{font-size:clamp(3.2rem,6vw,6.5rem);font-weight:700;letter-spacing:-0.01em;}
h2{font-size:clamp(1.9rem,3.5vw,3.2rem);font-weight:700;}
h3{font-size:1.35rem;font-weight:600;}
p{line-height:1.85;color:var(--muted);}
a{text-decoration:none;color:inherit;}
img{max-width:100%;display:block;}
.eyebrow{font-size:0.68rem;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:var(--prim);display:flex;align-items:center;gap:12px;margin-bottom:22px;}
.eyebrow::before{content:'';width:28px;height:1px;background:var(--prim);flex-shrink:0;}
.gold-bar{width:48px;height:2px;background:var(--prim);margin:26px 0;}
.btn-gold{display:inline-flex;align-items:center;gap:8px;background:var(--prim);color:#06090F;padding:15px 38px;font-weight:700;font-family:'DM Sans',sans-serif;letter-spacing:0.1em;font-size:0.78rem;text-transform:uppercase;border:none;cursor:pointer;transition:all 0.3s;text-decoration:none;}
.btn-gold:hover{background:var(--prim-l);box-shadow:0 8px 32px rgba(197,151,58,0.35);transform:translateY(-2px);}
.btn-outline-gold{display:inline-flex;align-items:center;background:transparent;border:1px solid rgba(197,151,58,0.35);color:var(--prim);padding:14px 37px;font-weight:600;font-size:0.78rem;letter-spacing:0.1em;text-transform:uppercase;cursor:pointer;transition:all 0.3s;text-decoration:none;font-family:'DM Sans',sans-serif;}
.btn-outline-gold:hover{border-color:var(--prim);background:rgba(197,151,58,0.07);}
.p-card{background:var(--card);border:1px solid var(--border);padding:36px;transition:all 0.4s;}
.p-card:hover{border-color:rgba(197,151,58,0.4);transform:translateY(-5px);box-shadow:0 20px 60px rgba(0,0,0,0.4);}
.num-big{font-family:'Cormorant Garamond',serif;font-size:clamp(3.5rem,5.5vw,5rem);font-weight:700;color:var(--prim);line-height:1;}
.section-wrap{max-width:1200px;margin:0 auto;padding:100px 60px;}
.full-band{padding:80px 60px;}
.text-prim{color:var(--prim);}
@keyframes floatY{0%,100%{transform:translateY(0);}50%{transform:translateY(-10px);}}
.float{animation:floatY 6s ease-in-out infinite;}
.icon-box{width:48px;height:48px;display:flex;align-items:center;justify-content:center;background:rgba(197,151,58,0.08);border:1px solid rgba(197,151,58,0.2);font-size:1.2rem;flex-shrink:0;}
.marq-wrap{overflow:hidden;border-top:1px solid var(--border);border-bottom:1px solid var(--border);padding:18px 0;background:var(--surface);}
.marq-inner{display:flex;gap:60px;white-space:nowrap;animation:marq 28s linear infinite;}
@keyframes marq{0%{transform:translateX(0);}100%{transform:translateX(-50%);}}
.marq-item{font-size:0.72rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);flex-shrink:0;}
.stat-row{display:flex;gap:40px;padding-top:28px;border-top:1px solid var(--border);margin-top:28px;flex-wrap:wrap;}
.stat-row .s-num{font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:700;color:var(--prim);display:block;line-height:1;}
.stat-row .s-lbl{font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--muted);margin-top:2px;display:block;}
.glass{background:rgba(255,255,255,0.03);backdrop-filter:blur(20px);border:1px solid var(--border);}
@media(max-width:768px){h1{font-size:2.4rem;}h2{font-size:1.7rem;}.section-wrap{padding:60px 20px!important;}.full-band{padding:50px 20px!important;}.p-card{padding:24px;}.hide-mob{display:none!important;}.stat-row{gap:24px;}}""",
        'page_blueprint': """\
DESIGN DIRECTIVES:
• Image placeholders: placehold.co/WxH/0E1826/C5973A?text=BusinessName (adapt dimensions per use)
• Hero MUST have: radial gradient orb (position:absolute, ~600px, rgba(197,151,58,0.06)) + image with .p-card stat badge overlapping bottom-left + small 72×72px gold square top-right of image + .stat-row with real numbers using .s-num/.s-lbl below the CTA buttons
• Use .glass for frosted-glass overlay cards on dark sections
• Use .marq-wrap/.marq-inner/.marq-item for a trust ticker/marquee strip between hero and about
• Use .float class on hero image or decorative elements for subtle floating animation
• Use .icon-box for feature/service icon containers

Build these sections in exact order:

NAV: Fixed, height 72px. bg:transparent on load, becomes rgba(8,17,31,0.94) with backdrop-filter:blur(16px) on scroll (add JS snippet: window.addEventListener('scroll',()=>document.getElementById('site-nav').classList.toggle('scrolled',scrollY>60)); CSS: #site-nav.scrolled{background:rgba(8,17,31,0.94);backdrop-filter:blur(16px);}). border-bottom:1px solid var(--border). inner: max-width 1200px margin auto, flex, space-between, align-center, padding 0 60px. Left: business name Cormorant Garamond 600 italic 1.35rem color:var(--prim). Center: 4 links (About Services Results Contact) DM Sans 0.78rem letter-spacing:0.08em uppercase color:var(--muted) hover:var(--head). Right: .btn-gold with padding 10px 22px font-size 0.72rem.

HERO: min-height:100vh, position:relative, display:flex, align-items:center. Decorative: position:absolute top:0 right:0 width:600px height:600px bg:radial-gradient(circle, rgba(197,151,58,0.06), transparent) pointer-events:none. Content: .section-wrap. Two columns — left 55% flex-col gap:24px: .eyebrow "[BusinessType] · [Location]", h1 with the exact hero headline (2-3 last words in color:var(--prim)), .gold-bar, p hero subheadline DM Sans 1rem max-width:480px, flex gap:12px flex-wrap: .btn-gold "[CTA]" + .btn-outline-gold "Learn More". Below buttons: flex gap:40px margin-top:16px — 3 trust signals "200+ Projects" / "98% Satisfaction" / "15+ Years" each in DM Sans 700 0.78rem uppercase letter-spacing:0.06em color:var(--muted). Right 40%: position:relative. Main rect 340×440px bg:var(--card) border:2px solid var(--border) overflow:hidden: placehold.co/340x440 img full size opacity:0.85. Overlapping stat card (position:absolute bottom:-16px left:-28px) .p-card width:170px: .num-big (2-digit number) class="counter" data-target="N" data-suffix="+" + DM Sans 0.7rem muted label below.

TRUST STRIP: bg:var(--surface), border-top/bottom:1px solid var(--border), padding:24px 60px. max-width:1200px margin:auto. flex, justify-center, align-center, gap:0, flex-wrap:wrap — 4 items each: padding:16px 48px border-right:1px solid var(--border) (last: no border). DM Sans 700 1rem color:var(--prim) + label 0.7rem uppercase letter-spacing:0.1em color:var(--muted) below. Text: "200+ Completed Projects" / "98% Client Retention" / "15+ Years Experience" / "40+ Industries Served".

ABOUT: .section-wrap. Two columns (47%/47%, gap:80px, align:center). Left: placehold.co/480x560 in div with border:2px solid var(--border) position:relative. After pseudo or sibling element: 60×60px square position:absolute bottom:-12px right:-12px bg:var(--prim). Right: .eyebrow, h2, .gold-bar, 2 body paragraphs from about data. Then 3 feature points (flex col gap:12px margin:24px 0): each flex gap:12px align-start — "◆" DM Sans 0.7rem color:var(--prim) mt:4px + div: strong DM Sans 700 0.9rem color:var(--head) + p.m-0 DM Sans 0.85rem color:var(--muted). .btn-outline-gold at bottom. data-aos="fade-left" on right column.

SERVICES: .section-wrap pt:60px. Centered header: .eyebrow + h2 + .gold-bar centered. 3-column grid gap:1px bg:var(--border) margin-top:56px border:1px solid var(--border) — each .p-card (no gap between cards, they share the 1px grid gap as border): large emoji in 44px square bg:rgba(197,151,58,0.08) border:1px solid var(--border) flex:center mb:20px, h3 DM Sans 700 color:var(--head), p.mt-2 DM Sans 0.88rem. data-aos="fade-up" data-aos-delay="0/100/200".

RESULTS: .full-band bg:var(--surface) border-top/bottom:1px solid var(--border). max-width:1000px margin:auto. Centered .eyebrow + h2. 4-col grid gap:48px margin-top:48px — each text-center: .num-big class="counter" data-target="N" data-suffix="+", DM Sans 0.7rem uppercase letter-spacing:0.12em color:var(--muted) mt:8px. data-aos="zoom-in" data-aos-delay staggered 0/100/200/300.

TESTIMONIALS: .section-wrap. .eyebrow + h2. 3-col grid gap:28px mt:48px — each .p-card.tilt-card: Cormorant Garamond 3.5rem color:var(--prim) line-height:0.8 mb:16px (the " character), italic Cormorant 1.05rem color:var(--txt) p, .gold-bar, flex gap:12px align-center: 40px circle bg:var(--card) border:1px solid var(--prim) flex:center DM Sans 700 0.7rem color:var(--prim) (initials) + div: strong 0.88rem color:var(--head) + small 0.78rem color:var(--muted). data-aos="fade-up" staggered.

CTA BAND: .full-band bg:linear-gradient(135deg,var(--surface),var(--bg)) border-top:1px solid var(--border). max-width:1200px margin:auto flex justify-between align-center gap:60px flex-wrap. Left: h2 + p max-width:480px. Right: flex gap:16px align-center flex-wrap — .btn-gold + .btn-outline-gold "Schedule a Call".

FOOTER: bg:#040A12 padding:60px. max-width:1200px margin:auto. 4-col grid gap:40px. Col1: Cormorant italic 1.5rem color:var(--prim) (name) + p 0.82rem color:var(--muted) mt:12px (tagline) + flex gap:12px mt:24px: 3 SVG social icon circles 36px border:1px solid var(--border) hover:border-color:var(--prim). Cols 2-3: DM Sans 700 0.72rem uppercase letter-spacing:0.1em color:var(--muted) mb:16px heading + links list 0.85rem color:var(--muted) hover:color:var(--head) gap:10px flex-col. Col4: contact details with SVG icons. Bottom: 1px var(--border) mt:48px pt:24px flex justify-between — copyright DM Sans 0.75rem var(--muted).""",
    },
    {
        'name': 'velocity',
        'img_palette': 'EEF0FF/4F46E5',
        'concept': 'High-growth momentum. Clean white surfaces with vivid indigo-purple gradient accents. The visitor feels they have discovered a forward-thinking industry leader. Confident, modern, and unmistakably professional.',
        'fonts_href': 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap',
        'css_foundation': """\
:root{--bg:#F8F9FF;--surface:#EEF0FF;--card:#FFFFFF;--border:rgba(79,70,229,0.1);--border-h:#E2E4F0;--prim:#4F46E5;--sec:#7C3AED;--grad:linear-gradient(135deg,#4F46E5 0%,#7C3AED 100%);--txt:#111827;--muted:#6B7280;--head:#0F172A;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;}
body{background:var(--bg);color:var(--txt);font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;}
h1,h2,h3,h4{font-family:'Plus Jakarta Sans',sans-serif;color:var(--head);line-height:1.1;font-weight:800;}
h1{font-size:clamp(3rem,6vw,6rem);letter-spacing:-0.03em;}
h2{font-size:clamp(1.8rem,3.5vw,3rem);letter-spacing:-0.02em;}
h3{font-size:1.2rem;font-weight:700;letter-spacing:-0.01em;}
p{line-height:1.75;color:var(--muted);}
a{text-decoration:none;color:inherit;}
img{max-width:100%;display:block;}
.chip{display:inline-flex;align-items:center;gap:8px;background:var(--surface);border:1px solid var(--border);color:var(--prim);font-size:0.7rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:6px 14px;border-radius:100px;margin-bottom:24px;}
.chip::before{content:'';width:6px;height:6px;border-radius:50%;background:var(--grad);}
.grad-text{background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.btn-vel{display:inline-flex;align-items:center;gap:8px;background:var(--grad);color:#fff;padding:14px 32px;border-radius:10px;font-weight:700;font-family:'Plus Jakarta Sans',sans-serif;font-size:0.9rem;border:none;cursor:pointer;transition:all 0.3s;text-decoration:none;box-shadow:0 4px 16px rgba(79,70,229,0.25);}
.btn-vel:hover{box-shadow:0 8px 32px rgba(79,70,229,0.4);transform:translateY(-2px);}
.btn-vel-ghost{display:inline-flex;align-items:center;gap:8px;background:var(--card);border:1.5px solid var(--border-h);color:var(--head);padding:13px 31px;border-radius:10px;font-weight:600;font-size:0.9rem;cursor:pointer;transition:all 0.3s;text-decoration:none;font-family:'Plus Jakarta Sans',sans-serif;}
.btn-vel-ghost:hover{border-color:var(--prim);color:var(--prim);}
.v-card{background:var(--card);border:1px solid var(--border-h);border-radius:16px;padding:32px;transition:all 0.35s;box-shadow:0 1px 4px rgba(0,0,0,0.04);}
.v-card:hover{border-color:var(--border);box-shadow:0 12px 40px rgba(79,70,229,0.1);transform:translateY(-4px);}
.num-vel{font-family:'Plus Jakarta Sans',sans-serif;font-size:clamp(3rem,5vw,4.5rem);font-weight:800;background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1;}
.section-wrap{max-width:1200px;margin:0 auto;padding:100px 60px;}
.full-band{padding:80px 60px;}
.text-prim{color:var(--prim);}
.feature-icon{width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,rgba(79,70,229,0.12),rgba(124,58,237,0.08));display:flex;align-items:center;justify-content:center;font-size:1.3rem;margin-bottom:20px;border:1px solid var(--border);}
.badge-pill{display:inline-flex;align-items:center;gap:8px;padding:6px 16px 6px 6px;background:var(--card);border:1px solid var(--border-h);border-radius:100px;font-size:0.72rem;font-weight:600;color:var(--head);margin-bottom:28px;}
.badge-pill .bp-dot{width:24px;height:24px;border-radius:50%;background:var(--grad);display:flex;align-items:center;justify-content:center;color:#fff;font-size:0.65rem;}
.check-item{display:flex;align-items:flex-start;gap:12px;margin-bottom:14px;}
.check-icon{width:22px;height:22px;border-radius:50%;background:var(--grad);display:flex;align-items:center;justify-content:center;color:#fff;font-size:0.65rem;flex-shrink:0;margin-top:2px;}
.stat-card{background:var(--card);border:1px solid var(--border-h);border-radius:14px;padding:20px 24px;box-shadow:0 4px 20px rgba(79,70,229,0.06);}
@media(max-width:768px){h1{font-size:2.4rem;}h2{font-size:1.6rem;}.section-wrap{padding:60px 20px!important;}.full-band{padding:50px 20px!important;}.v-card{padding:24px;}.hide-mob{display:none!important;}}""",
        'page_blueprint': """\
DESIGN DIRECTIVES:
• Image placeholders: placehold.co/WxH/EEF0FF/4F46E5?text=BusinessName (adapt dimensions per use)
• Hero MUST have: radial gradient orb (position:absolute top-right, ~700px, rgba(79,70,229,0.07)) + layered card stack (main card + 2 floating mini cards at different z-levels) + trust stats row below CTAs (3 real metrics, Plus Jakarta 800) + key h1 words in span.grad-text
• Use .badge-pill for hero eyebrow element (replace .chip in hero)
• Use .feature-icon for service/feature icon containers
• Use .check-item/.check-icon for feature bullet points
• Use .stat-card for floating stat mini-cards in hero

Build these sections in exact order:

NAV: Fixed, height 68px. bg:var(--card) border-bottom:1px solid var(--border-h) box-shadow:0 1px 8px rgba(0,0,0,0.05). inner: max-width 1200px margin:auto flex space-between align-center padding:0 60px. Left: business name Plus Jakarta Sans 700 1.05rem color:var(--head). Center: 4 links Inter 0.85rem color:var(--muted) hover:color:var(--prim) transition. Right: .btn-vel-ghost "Log in" (padding 8px 18px 0.82rem) + .btn-vel (padding 10px 22px 0.82rem).

HERO: .section-wrap min-height:92vh display:flex align-items:center position:relative. Decorative: position:absolute top:-100px right:-100px width:700px height:700px bg:radial-gradient(circle at center, rgba(79,70,229,0.07) 0%, transparent 65%) pointer-events:none border-radius:50%. Two columns (52%/44%, gap:80px, align:center). Left: .chip "[BusinessType] · [Location]", h1 with 2 key words wrapped in span.grad-text, p Inter 1rem max-width:500px mt:20px, flex gap:12px mt:32px: .btn-vel "[CTA]" + .btn-vel-ghost "See Work". Trust row flex gap:32px mt:36px — 3 items each: Plus Jakarta Sans 800 1.1rem color:var(--head) + Inter 0.75rem color:var(--muted). Right: position:relative. Stack of .v-card divs: main card 320×380px — top gradient strip (height:4px bg:var(--grad) border-radius:16px 16px 0 0), placehold.co/320x240 img full-width, content: name bold + location muted. Second card (position:absolute top:20px right:-20px width:180px opacity:0.7 scale:0.95): mini stat card. Third small (position:absolute bottom:-16px left:-16px width:160px): rating badge "★ 4.9 / 5.0". data-aos="fade-left" on right col.

LOGOS STRIP: bg:var(--card) border-top/bottom:1px solid var(--border-h) padding:28px 60px. max-width:1200px margin:auto. Inter 0.72rem uppercase letter-spacing:0.1em color:var(--muted) text-center mb:20px "Trusted by growing businesses". flex gap:40px justify-center align-center flex-wrap: 5 placeholder "logos" (div width:90px height:28px bg:var(--surface) border-radius:4px).

ABOUT: .section-wrap. Two columns (47%/48%, gap:80px, align:center). Left column: A mockup frame div — bg:var(--head) border-radius:16px overflow:hidden box-shadow:0 20px 60px rgba(0,0,0,0.12). Top bar 40px bg:#1a1f2e flex align-center gap:8px pl:16px (3 circles 10px: #FF5F57, #FFBD2E, #28CA41). placehold.co/480x340 img full-width opacity:0.9. Right col: .chip, h2, 3 short paragraphs from about data Inter 0.95rem. Feature 2x2 grid gap:20px mt:28px — each .v-card p:20px: 32px gradient icon block border-radius:8px flex:center emoji mb:12px, h3 0.95rem, p.text-xs Inter 0.82rem. .btn-vel-ghost mt:32px.

SERVICES: .section-wrap. Centered: .chip + h2 + p Inter 1rem color:var(--muted) max-width:520px mt:12px. 3-col grid gap:24px mt:56px — each .v-card.tilt-card: 48px square border-radius:12px bg:var(--surface) flex:center emoji font-size:1.5rem mb:20px, h3 Plus Jakarta 700, p Inter 0.9rem mt:10px, span "Learn more →" Plus Jakarta 700 0.82rem color:var(--prim) mt:20px display:block. data-aos="fade-up" delay:0/100/200.

STATS: .full-band bg:var(--surface) border-top/bottom:1px solid var(--border). max-width:1200px margin:auto. Centered .chip + h2. 4-col grid gap:8px mt:48px — each bg:var(--card) border-radius:16px padding:36px 24px text-center border:1px solid var(--border-h): .num-vel class="counter" data-target="N" data-suffix="+", Inter 0.72rem uppercase letter-spacing:0.08em color:var(--muted) mt:8px. data-aos="zoom-in" delay staggered.

TESTIMONIALS: .section-wrap. Centered .chip + h2. 3-col grid gap:24px mt:48px — each .v-card.tilt-card: flex align-center gap:4px mb:16px (5× span "★" color:#FBBF24 0.85rem + "5.0" Plus Jakarta 700 0.85rem color:var(--head)). italic Inter 0.95rem color:var(--txt) p. border-top:1px solid var(--border-h) mt:20px pt:20px flex align-center gap:12px: 40px circle bg:var(--surface) border-radius:50% flex:center Plus Jakarta 700 0.78rem color:var(--prim) + div: strong 0.88rem color:var(--head) + small 0.8rem color:var(--muted). data-aos="fade-up" staggered.

CTA BAND: .full-band bg:var(--grad) position:relative overflow:hidden. Decorative circles: 2 position:absolute rgba(255,255,255,0.05) border-radius:50% circles. Centered content: .chip (bg:rgba(255,255,255,0.15) border:1px solid rgba(255,255,255,0.25) color:#fff), h2 color:#fff, p Inter rgba(255,255,255,0.75) max-width:480px mx:auto mt:16px, flex gap:12px justify-center mt:32px: bg-white color:var(--prim) btn (Plus Jakarta 700 padding 14px 32px border-radius:10px border:none cursor:pointer) + bg:transparent border:1.5px solid rgba(255,255,255,0.35) text:white btn.

FOOTER: bg:var(--head) padding:60px. max-width:1200px margin:auto. 4-col grid gap:40px. Col1: Plus Jakarta 700 1.05rem color:#fff + Inter 0.82rem rgba(255,255,255,0.45) mt:10px + flex gap:10px mt:24px social icons SVG 20px rgba(255,255,255,0.35) hover:#fff. Cols 2-3: Inter 700 0.72rem uppercase letter-spacing rgba(255,255,255,0.4) mb:14px + links list Inter 0.85rem rgba(255,255,255,0.45) hover:#fff gap:8px. Col4: contact. Bottom: 1px rgba(255,255,255,0.08) mt:48px pt:24px flex space-between — copyright Inter 0.75rem rgba(255,255,255,0.3).""",
    },
    {
        'name': 'canvas',
        'img_palette': 'F7F5F1/0D6E6E',
        'concept': 'Quiet luxury through restraint. Warm white with deep teal as the single accent. Generous whitespace, italic serif headings, and minimal color signal that the quality of work speaks for itself. Premium boutique feel.',
        'fonts_href': 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,600;1,700&family=DM+Sans:wght@300;400;500;600;700&display=swap',
        'css_foundation': """\
:root{--bg:#FFFFFF;--surface:#F7F5F1;--card:#FAFAF7;--border:#E8E4DC;--prim:#0D6E6E;--prim-l:#14A0A0;--txt:#2D2926;--muted:#877F74;--head:#1A1614;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;}
body{background:var(--bg);color:var(--txt);font-family:'DM Sans',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;}
h1,h2,h3,h4{font-family:'Cormorant Garamond',serif;color:var(--head);line-height:1.06;}
h1{font-size:clamp(3.2rem,6vw,6.5rem);font-weight:600;font-style:italic;letter-spacing:-0.01em;}
h2{font-size:clamp(2rem,3.8vw,3.2rem);font-weight:700;}
h3{font-size:1.2rem;font-weight:700;font-family:'DM Sans',sans-serif;}
p{line-height:1.9;color:var(--muted);}
a{text-decoration:none;color:inherit;}
img{max-width:100%;display:block;}
.sec-num{font-family:'Cormorant Garamond',serif;font-size:5rem;font-weight:700;color:var(--border);line-height:1;display:block;margin-bottom:-12px;}
.teal-line{width:40px;height:2px;background:var(--prim);margin:24px 0;}
.label-sm{font-size:0.68rem;font-weight:600;letter-spacing:0.18em;text-transform:uppercase;color:var(--prim);margin-bottom:16px;display:block;}
.btn-teal{display:inline-flex;align-items:center;gap:8px;background:var(--prim);color:#fff;padding:15px 36px;font-weight:600;font-family:'DM Sans',sans-serif;font-size:0.88rem;border:none;cursor:pointer;transition:all 0.3s;text-decoration:none;border-radius:4px;}
.btn-teal:hover{background:var(--prim-l);transform:translateY(-2px);box-shadow:0 8px 24px rgba(13,110,110,0.25);}
.btn-outline-t{display:inline-flex;align-items:center;background:transparent;border:1.5px solid var(--border);color:var(--txt);padding:14px 35px;font-weight:600;font-size:0.88rem;cursor:pointer;transition:all 0.3s;text-decoration:none;font-family:'DM Sans',sans-serif;border-radius:4px;}
.btn-outline-t:hover{border-color:var(--prim);color:var(--prim);}
.c-card{background:var(--card);border:1px solid var(--border);padding:36px;transition:all 0.4s;}
.c-card:hover{border-color:var(--prim);box-shadow:0 12px 40px rgba(13,110,110,0.08);transform:translateY(-4px);}
.num-canvas{font-family:'Cormorant Garamond',serif;font-size:clamp(3rem,5vw,4.5rem);font-weight:700;color:var(--prim);line-height:1;}
.divider{width:100%;height:1px;background:var(--border);}
.section-wrap{max-width:1200px;margin:0 auto;padding:100px 60px;}
.full-band{padding:80px 60px;}
.text-teal{color:var(--prim);}
@keyframes morphit{0%{border-radius:60% 40% 30% 70%/60% 30% 70% 40%;}50%{border-radius:30% 60% 70% 40%/50% 60% 30% 60%;}100%{border-radius:40% 60% 50% 50%/30% 50% 70% 50%;}}
.blob-bg{background:linear-gradient(135deg,rgba(13,110,110,0.12),rgba(13,110,110,0.04));animation:morphit 10s ease-in-out infinite alternate;border-radius:60% 40% 30% 70%/60% 30% 70% 40%;}
.pull-quote{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1.2rem;color:var(--prim);border-left:3px solid var(--prim);padding-left:20px;line-height:1.7;margin:24px 0;}
.check-row{display:flex;align-items:flex-start;gap:10px;margin-bottom:12px;}
.teal-dot-sm{width:7px;height:7px;border-radius:50%;background:var(--prim);flex-shrink:0;margin-top:6px;}
@media(max-width:768px){h1{font-size:2.4rem;}h2{font-size:1.7rem;}.section-wrap{padding:60px 20px!important;}.full-band{padding:50px 20px!important;}.c-card{padding:24px;}.hide-mob{display:none!important;}}""",
        'page_blueprint': """\
DESIGN DIRECTIVES:
• Image placeholders: placehold.co/WxH/F7F5F1/0D6E6E?text=BusinessName (adapt dimensions per use)
• Hero MUST have: .blob-bg div (400×460px, already animated with morphit keyframes) on right column + image positioned absolute center of blob + floating .c-card stat badge bottom-left of blob outside its bounds
• Use .pull-quote for blockquote/highlight text elements (replaces plain blockquote)
• Use .check-row/.teal-dot-sm for feature bullet points
• Use .text-teal for teal-coloured accent text spans

Build these sections in exact order:

NAV: Fixed, height 68px. bg:var(--bg) border-bottom:1px solid var(--border). On scroll add shadow: nav.scrolled{box-shadow:0 2px 24px rgba(0,0,0,0.06);} via JS. inner: max-width 1200px margin:auto flex space-between align-center padding:0 60px. Left: business name Cormorant Garamond 600 italic 1.3rem color:var(--head). Center: 4 links DM Sans 0.82rem color:var(--muted) hover:color:var(--prim). Right: .btn-teal padding:10px 22px 0.82rem.

HERO: .section-wrap min-height:92vh display:flex align-items:center. Two columns (54%/42%, gap:80px, align:center). Left: .label-sm "[BusinessType]", h1 (italic Cormorant — hero headline, key word in color:var(--prim)), .teal-line, p Inter 1rem max-width:480px color:var(--muted), flex gap:12px mt:32px: .btn-teal "[CTA]" + .btn-outline-t "Our Work". Trust strip flex gap:36px mt:32px — 3 items DM Sans 700 0.78rem uppercase letter-spacing:0.06em color:var(--muted). Right: position:relative. Morphing blob shape — div width:400px height:460px bg:linear-gradient(135deg, rgba(13,110,110,0.1), rgba(13,110,110,0.04)) border-radius:60% 40% 30% 70%/60% 30% 70% 40% animation: morphit 10s ease-in-out infinite alternate. CSS: @keyframes morphit{0%{border-radius:60% 40% 30% 70%/60% 30% 70% 40%;}50%{border-radius:30% 60% 70% 40%/50% 60% 30% 60%;}100%{border-radius:40% 60% 50% 50%/30% 50% 70% 50%;}}. Over the blob (position:absolute top:50% left:50% transform:translate(-50%,-50%)): placehold.co/320x380 img border-radius:8px. Float badge (position:absolute bottom:-16px left:-16px) .c-card width:160px padding:18px: DM Sans 700 1.4rem color:var(--prim) + DM Sans 0.72rem color:var(--muted).

DIVIDER: full-width .divider margin:0.

ABOUT: .section-wrap. .sec-num "01". Two columns (46%/46%, gap:80px). Right text col: .label-sm, h2, .teal-line, 2 paragraphs about data. 3 feature bullets mt:24px flex-col gap:10px: each flex gap:10px align-start — 8px circle bg:var(--prim) border-radius:50% mt:6px flex-shrink:0 + p DM Sans 0.88rem color:var(--txt). .btn-outline-t mt:28px. Left image col: placehold.co/480x560 in div border-radius:8px overflow:hidden border:1px solid var(--border) box-shadow:0 8px 32px rgba(0,0,0,0.06). data-aos="fade-right" on image.

DIVIDER.

SERVICES: .section-wrap. .sec-num "02". Centered: .label-sm + h2 + p DM Sans max-width:500px mx:auto mt:8px. 3-col grid gap:28px mt:56px — each .c-card.tilt-card: .label-sm (01/02/03), h3, .teal-line 28px, p DM Sans 0.88rem. data-aos="fade-up" delay:0/120/240.

DIVIDER.

STATS: .full-band bg:var(--surface) border-top/bottom:1px solid var(--border). max-width:1200px margin:auto. .sec-num "03". h2 + p mx:auto max-width:500px. 4-col grid gap:40px mt:48px — each text-center: .num-canvas class="counter" data-target="N" data-suffix="+", .teal-line width:28px mx:auto, DM Sans 0.72rem uppercase letter-spacing:0.12em color:var(--muted). data-aos="zoom-in" delay staggered.

DIVIDER.

TESTIMONIALS: .section-wrap. .sec-num "04". .label-sm + h2. 3-col grid gap:28px mt:48px — each .c-card.tilt-card: Cormorant 3.5rem color:var(--border) line-height:0.8 mb:16px ("), italic Cormorant 1.1rem color:var(--txt) p, .teal-line 28px, DM Sans 700 0.88rem color:var(--head) + DM Sans 0.78rem color:var(--muted). data-aos="fade-up" staggered.

CTA BAND: .full-band bg:var(--prim) position:relative. Centered: h2 Cormorant 700 color:#fff clamp(2.4rem,4vw,3.5rem), p DM Sans rgba(255,255,255,0.8) max-width:480px mx:auto mt:16px, flex gap:12px justify-center mt:32px: btn bg:#fff color:var(--prim) DM Sans 700 padding:14px 36px border-radius:4px + btn bg:transparent border:1.5px solid rgba(255,255,255,0.35) color:#fff same padding.

DIVIDER.

FOOTER: bg:var(--head) padding:60px. max-width:1200px margin:auto. 4-col grid gap:40px. Col1: Cormorant italic 1.4rem color:var(--surface) + DM Sans 0.82rem rgba(255,255,255,0.4) mt:10px + links mt:20px gap:8px. Cols 2-3: link lists DM Sans 0.84rem rgba(255,255,255,0.4) hover:#fff gap:8px. Col4: contact. Bottom: 1px rgba(255,255,255,0.08) mt:40px pt:20px copyright DM Sans 0.75rem rgba(255,255,255,0.3).""",
    },
    {
        'name': 'obsidian',
        'img_palette': '191919/FF6B35',
        'concept': 'Sophisticated dark premium. Pure black canvas with warm orange fire accents. High-contrast, dramatic, and exclusive. The visitor feels they have found something reserved for serious clients who expect the best.',
        'fonts_href': 'https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=DM+Sans:wght@300;400;500;600&display=swap',
        'css_foundation': """\
:root{--bg:#070707;--surface:#111111;--card:#191919;--border:rgba(255,255,255,0.06);--border-h:rgba(255,255,255,0.1);--prim:#FF6B35;--prim-l:#FF9162;--txt:#E8E8E8;--muted:#5A5A5A;--head:#FFFFFF;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;}
body{background:var(--bg);color:var(--txt);font-family:'DM Sans',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;}
h1,h2,h3,h4{font-family:'Outfit',sans-serif;color:var(--head);line-height:1.05;}
h1{font-size:clamp(3rem,6vw,6.5rem);font-weight:900;letter-spacing:-0.03em;}
h2{font-size:clamp(1.8rem,3.5vw,3.2rem);font-weight:800;letter-spacing:-0.02em;}
h3{font-size:1.15rem;font-weight:700;}
p{line-height:1.85;color:var(--muted);}
a{text-decoration:none;color:inherit;}
img{max-width:100%;display:block;}
.tag{display:inline-flex;align-items:center;gap:8px;background:rgba(255,107,53,0.08);border:1px solid rgba(255,107,53,0.2);color:var(--prim);font-size:0.68rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;padding:6px 14px;border-radius:4px;margin-bottom:22px;}
.orange-line{width:40px;height:3px;background:var(--prim);margin:24px 0;}
.btn-obs{display:inline-flex;align-items:center;gap:8px;background:var(--prim);color:#070707;padding:14px 36px;font-weight:700;font-family:'Outfit',sans-serif;font-size:0.9rem;border:none;cursor:pointer;transition:all 0.3s;text-decoration:none;}
.btn-obs:hover{background:var(--prim-l);box-shadow:0 0 40px rgba(255,107,53,0.35);transform:translateY(-2px);}
.btn-obs-ghost{display:inline-flex;align-items:center;background:transparent;border:1px solid var(--border-h);color:var(--txt);padding:13px 35px;font-weight:600;font-size:0.9rem;cursor:pointer;transition:all 0.3s;text-decoration:none;font-family:'Outfit',sans-serif;}
.btn-obs-ghost:hover{border-color:var(--prim);color:var(--prim);}
.o-card{background:var(--card);border:1px solid var(--border);padding:32px;transition:all 0.35s;position:relative;overflow:hidden;}
.o-card::after{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--prim);transform:scaleX(0);transform-origin:left;transition:transform 0.4s;}
.o-card:hover::after{transform:scaleX(1);}
.o-card:hover{border-color:rgba(255,107,53,0.2);transform:translateY(-4px);box-shadow:0 16px 48px rgba(0,0,0,0.5);}
.num-obs{font-family:'Outfit',sans-serif;font-size:clamp(3.5rem,5vw,5rem);font-weight:900;color:var(--prim);line-height:1;letter-spacing:-0.03em;}
.section-wrap{max-width:1200px;margin:0 auto;padding:100px 60px;}
.full-band{padding:80px 60px;}
.text-prim{color:var(--prim);}
@keyframes gridMove{from{background-position:0 0;}to{background-position:40px 40px;}}
.grid-bg{background-image:linear-gradient(rgba(255,107,53,0.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,107,53,0.025) 1px,transparent 1px);background-size:40px 40px;animation:gridMove 4s linear infinite;}
.glow{box-shadow:0 0 40px rgba(255,107,53,0.15);}
.feat-icon{width:44px;height:44px;background:rgba(255,107,53,0.08);border:1px solid rgba(255,107,53,0.2);display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0;}
.code-label{font-family:monospace;font-size:0.68rem;letter-spacing:0.16em;text-transform:uppercase;color:rgba(255,107,53,0.5);display:block;margin-bottom:16px;}
.anim-in{opacity:0;transform:translateY(30px);transition:opacity 0.7s ease,transform 0.7s ease;}
.anim-in.visible{opacity:1;transform:none;}
@media(max-width:768px){h1{font-size:2.4rem;}h2{font-size:1.7rem;}.section-wrap{padding:60px 20px!important;}.full-band{padding:50px 20px!important;}.o-card{padding:22px;}.hide-mob{display:none!important;}}""",
        'page_blueprint': """\
DESIGN DIRECTIVES:
• Image placeholders: placehold.co/WxH/191919/FF6B35?text=BusinessName (adapt dimensions per use)
• Hero MUST have: add class .grid-bg to the hero section for the animated grid background + radial glow orb top-right (rgba(255,107,53,0.05)) + main image card with image + 3 mini stats inside it at bottom + apply .glow to the main card
• Use .feat-icon for feature/service icon containers
• Use .code-label for service codes and section category labels
• Use .anim-in on key hero elements (h1, p, buttons) — IntersectionObserver in JS adds .visible class
• Use .text-prim for orange accent text spans in h1/h2

Build these sections in exact order:

NAV: Fixed, height 68px. bg:rgba(7,7,7,0.9) backdrop-filter:blur(16px) border-bottom:1px solid var(--border). inner: max-width 1200px margin:auto flex space-between align-center padding:0 60px. Left: Outfit 700 1.05rem color:var(--head). Center: 4 links DM Sans 0.82rem color:var(--muted) hover:color:var(--txt). Right: .btn-obs padding:10px 22px 0.82rem.

HERO: .section-wrap min-height:100vh display:flex align-items:center position:relative. Decorative: position:absolute right:0 top:0 width:500px height:500px bg:radial-gradient(circle, rgba(255,107,53,0.05), transparent) pointer-events:none. Two columns (54%/42%, gap:60px, align:center). Left: .tag, h1 (key word in color:var(--prim)), .orange-line, p DM Sans max-width:480px mt:4px, flex gap:12px mt:28px: .btn-obs "[CTA]" + .btn-obs-ghost "Learn More". Right: position:relative. Main block div 360×440px bg:var(--card) border:1px solid var(--border) padding:24px. Inside: placehold.co/360x380 img full-width opacity:0.85. Below image inside card — border-top:1px solid var(--border) pt:16px flex justify-between: 3 mini stats Outfit 700 1rem color:var(--prim) + DM Sans 0.7rem color:var(--muted) mt:2px.

ABOUT: .section-wrap. .tag + h2 + .orange-line. Two columns (45%/50%, gap:80px, align:flex-start). Left: placehold.co/460x520 div border:1px solid var(--border) overflow:hidden. Right: 2 body paragraphs about data. 4 features mt:28px flex-col gap:16px — each flex gap:12px align-start: 36px square bg:rgba(255,107,53,0.08) border:1px solid rgba(255,107,53,0.15) flex:center border-radius:6px emoji + div h3 Outfit 700 0.95rem color:var(--head) + p DM Sans 0.82rem color:var(--muted) mt:4px. .btn-obs mt:32px. data-aos="fade-left" on right col.

SERVICES: .section-wrap. Centered .tag + h2 + .orange-line centered. 3-col grid gap:1px bg:var(--border) mt:48px border:1px solid var(--border) — each .o-card.tilt-card: Outfit 700 0.68rem letter-spacing:0.16em uppercase color:rgba(255,107,53,0.5) mb:16px (3-letter code), h3 Outfit 700, .orange-line 24px, p DM Sans 0.88rem. data-aos="fade-up" delay:0/100/200.

STATS: .full-band bg:var(--surface) border-top/bottom:1px solid var(--border). max-width:1200px margin:auto. .tag centered + h2 centered + p centered. 4-col grid gap:0 mt:48px border:1px solid var(--border) — each .o-card padding:40px text-center border:none border-right:1px solid var(--border) (last: no border): .num-obs class="counter" data-target="N" data-suffix="+", DM Sans 0.7rem uppercase letter-spacing:0.1em color:var(--muted) mt:10px. data-aos="zoom-in" staggered.

TESTIMONIALS: .section-wrap. .tag + h2. 3-col grid gap:24px mt:48px — each .o-card.tilt-card: flex gap:2px mb:16px (5× "★" DM Sans 0.85rem color:var(--prim)). italic DM Sans 0.95rem color:var(--txt) p. border-top:1px solid var(--border) mt:20px pt:20px flex gap:12px align-center: 38px circle bg:var(--card) border:1px solid var(--border) flex:center Outfit 700 0.78rem color:var(--prim) (initials) + Outfit 700 0.88rem color:var(--head) + DM Sans 0.78rem color:var(--muted). data-aos="fade-up" staggered.

CTA BAND: .full-band bg:var(--surface) border-top/bottom:1px solid var(--border). max-width:1200px margin:auto flex justify-between align-center gap:60px flex-wrap. Left: h2 + p max-width:480px. Right flex col gap:16px: .btn-obs + flex gap:10px align-center (SVG phone 18px color:var(--prim) + DM Sans 0.9rem color:var(--txt) phone number).

FOOTER: bg:#030303 padding:60px. max-width:1200px margin:auto. 4-col grid gap:40px. Col1: Outfit 800 1.1rem color:var(--head) + DM Sans 0.82rem color:var(--muted) mt:10px + flex gap:10px mt:20px social SVG circles 36px border:1px solid var(--border) hover:border-color:var(--prim). Cols 2-3: DM Sans 700 0.72rem uppercase letter-spacing color:var(--muted) mb:14px + links DM Sans 0.84rem color:var(--muted) hover:color:var(--txt) flex-col gap:8px. Col4 contact. Bottom: 1px var(--border) mt:40px pt:20px flex space-between copyright DM Sans 0.75rem color:var(--muted).""",
    },
    {
        'name': 'editorial',
        'img_palette': '1A1A1A/F5F3EE',
        'concept': 'Authoritative magazine editorial. Warm cream, bold Bebas Neue headlines, and crimson red used as the single powerful accent. The visitor feels they are reading the definitive industry publication. Credentialed, prestigious, impossible to ignore.',
        'fonts_href': 'https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=DM+Mono:wght@400&display=swap',
        'css_foundation': """\
:root{--bg:#F5F3EE;--surface:#FFFFFF;--card:#FAFAF7;--border:#DDD9D0;--ink:#1A1A1A;--red:#C41E3A;--txt:#2D2926;--muted:#7A7268;--head:#1A1A1A;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;}
body{background:var(--bg);color:var(--txt);font-family:'Libre Baskerville',serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;}
h1,h2,h3,h4{font-family:'Bebas Neue',sans-serif;color:var(--head);line-height:0.95;letter-spacing:0.02em;}
h1{font-size:clamp(5rem,10vw,10rem);}
h2{font-size:clamp(2.5rem,5vw,5rem);}
h3{font-size:clamp(1.6rem,2.5vw,2.2rem);}
p{line-height:1.9;font-family:'Libre Baskerville',serif;color:var(--txt);font-size:0.95rem;}
blockquote{font-family:'Libre Baskerville',serif;font-style:italic;font-size:1.15rem;color:var(--red);border-left:3px solid var(--red);padding-left:24px;margin:24px 0;line-height:1.7;}
a{text-decoration:none;color:inherit;}
img{max-width:100%;display:block;}
.mono{font-family:'DM Mono',monospace;font-size:0.68rem;letter-spacing:0.14em;text-transform:uppercase;color:var(--muted);}
.red-rule{height:4px;background:var(--red);width:100%;}
.red-sm{width:48px;height:3px;background:var(--red);margin:22px 0;}
.ed-label{font-family:'DM Mono',monospace;font-size:0.68rem;letter-spacing:0.16em;text-transform:uppercase;color:var(--muted);display:flex;align-items:center;gap:12px;margin-bottom:20px;}
.ed-label::after{content:'';flex:1;height:1px;background:var(--border);}
.btn-ink{display:inline-flex;align-items:center;gap:8px;background:var(--ink);color:var(--bg);padding:16px 40px;font-family:'Bebas Neue',sans-serif;font-size:1.05rem;letter-spacing:0.1em;border:none;cursor:pointer;transition:all 0.3s;text-decoration:none;}
.btn-ink:hover{background:var(--red);}
.btn-red{display:inline-flex;align-items:center;background:var(--red);color:#fff;padding:15px 39px;font-family:'Bebas Neue',sans-serif;font-size:1.05rem;letter-spacing:0.1em;border:none;cursor:pointer;transition:all 0.3s;text-decoration:none;}
.btn-red:hover{background:var(--ink);}
.e-card{background:var(--surface);border-top:3px solid var(--border);padding:32px;transition:all 0.3s;}
.e-card:hover{border-top-color:var(--red);transform:translateY(-3px);box-shadow:0 12px 32px rgba(0,0,0,0.06);}
.num-ed{font-family:'Bebas Neue',sans-serif;font-size:clamp(4rem,7vw,6.5rem);color:var(--ink);line-height:1;}
.section-wrap{max-width:1200px;margin:0 auto;padding:100px 60px;}
.full-band{padding:80px 60px;}
.text-red{color:var(--red);}
.masthead-name{font-family:'Bebas Neue',sans-serif;font-size:2.6rem;color:var(--ink);line-height:1;transition:font-size 0.3s;}
.drop-cap::first-letter{font-family:'Bebas Neue',sans-serif;font-size:4.5rem;float:left;line-height:0.85;margin:4px 12px 0 0;color:var(--red);font-weight:normal;}
.col-2{column-count:2;column-gap:48px;}
.ruled{border-bottom:1px solid var(--border);padding-bottom:28px;margin-bottom:28px;}
.ed-tag{display:inline-flex;align-items:center;gap:8px;background:var(--red);color:#fff;font-family:'DM Mono',monospace;font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;padding:4px 12px;}
@media(max-width:768px){h1{font-size:3.5rem;}h2{font-size:2.2rem;}.section-wrap{padding:60px 20px!important;}.full-band{padding:50px 20px!important;}.e-card{padding:20px;}.hide-mob{display:none!important;}.col-2{column-count:1;}}""",
        'page_blueprint': """\
DESIGN DIRECTIVES:
• Image placeholders: placehold.co/WxH/1A1A1A/F5F3EE?text=BusinessName (adapt dimensions per use)
• Hero MUST have: enormous full-width h1 (Bebas Neue, 5–10rem), large editorial image in right column with .mono caption, use .masthead-name class on nav brand for compact-scroll effect
• Use .drop-cap on the first paragraph in the about/hero section
• Use .ed-tag for section category tags (instead of plain labels)
• Use .ruled for dividers with content above them
• Use .col-2 for editorial two-column body text in about section
• Use .text-red for crimson accent spans inside headlines

Build these sections in exact order:

MASTHEAD (fixed): Top red strip: .red-rule height:6px. Below: bg:var(--bg) border-bottom:2px solid var(--ink). inner: max-width 1200px margin:auto flex space-between align-center padding:14px 60px. Left: business name Bebas Neue 2.6rem color:var(--ink) line-height:1 (add CSS .masthead-name transition font-size 0.3s). Center: 4 links .mono hover:color:var(--red). Right: .mono "Vol. I · 2025" + .btn-ink padding:10px 24px. On scroll JS: document.getElementById('masthead').classList.toggle('compact',scrollY>60); CSS: #masthead.compact .masthead-name{font-size:1.6rem;} #masthead.compact{padding-top:8px;padding-bottom:8px;}

HERO: .section-wrap padding-top:160px min-height:95vh. Top row: .mono "Special Issue · [BusinessType]" mb:24px. Full-width h1 Bebas Neue — hero headline, key 1-2 words wrapped in span style="color:var(--red)". .red-sm. Two columns below h1 (55%/40%, gap:80px, mt:32px): Left: Libre Baskerville 1.05rem p (subheadline), blockquote (key business quote 1-2 lines). flex gap:12px mt:28px: .btn-ink "[CTA]" + .btn-red "Our Work". Right: placehold.co/440x500 img border:2px solid var(--border) w-full. Small .mono caption below image.

RED RULE: full-width .red-rule margin:48px 0 0.

ABOUT: .section-wrap. .ed-label "About the Brand". Two columns (48%/46%, gap:80px). Left: h2 (italic — add font-style:italic on this h2 only via inline style or class) + .red-sm + 3 Libre Baskerville paragraphs from about data + blockquote. Right: flex-col gap:0 — 3 stacked .e-card: .mono mb:8px, h3 1.8rem, Libre Baskerville 0.85rem p mt:8px. data-aos="fade-left" on right. data-aos="fade-right" on left.

SERVICES: .section-wrap. .ed-label "What We Do". h2 + .red-sm. flex-col gap:0 — each .e-card flex align-start gap:32px: Bebas Neue 3.5rem color:var(--border) line-height:1 (01/02/03...) flex-shrink:0 + div: h3 Bebas Neue 1.8rem + Libre Baskerville 0.88rem p mt:8px. data-aos="fade-up" staggered delay.

STATS: .full-band bg:var(--ink). .ed-label (color:rgba(245,243,238,0.45)) "By The Numbers". 4-col grid mt:40px — each text-center padding:40px 20px: .num-ed class="counter" data-target="N" data-suffix="+" style="color:#FFFFFF", .mono mt:10px style="color:rgba(245,243,238,0.4)" label. data-aos="zoom-in" staggered.

TESTIMONIALS: .section-wrap. .ed-label "Reader Testimonials". 3-col grid gap:28px mt:40px — each .e-card: .mono mb:12px ("Letter No.01" etc), blockquote (italic quote starting "Dear [BusinessName],"), .red-sm 28px, Bebas Neue 1.2rem color:var(--ink) (client name) + .mono mt:4px (title/company). data-aos="fade-up" staggered.

CTA BAND: .full-band bg:var(--red) position:relative overflow:hidden. Centered: h2 Bebas Neue color:#fff clamp(3rem,6vw,5.5rem), Libre Baskerville rgba(255,255,255,0.8) p max-width:480px mx:auto mt:16px font-size:0.95rem, flex gap:12px justify-center mt:32px: btn bg:#fff color:var(--red) (Bebas Neue 1.05rem letter-spacing padding 15px 40px) + btn bg:transparent border:1.5px solid rgba(255,255,255,0.4) color:#fff (same font+padding).

FOOTER: bg:var(--ink) padding:60px. max-width:1200px margin:auto. 4-col grid gap:40px. Col1: Bebas Neue 2.2rem color:var(--bg) (brand name) + Libre Baskerville 0.82rem color:rgba(245,243,238,0.4) mt:10px (tagline) + .mono links mt:20px gap:8px flex-col color:rgba(245,243,238,0.35) hover:rgba(245,243,238,0.7). Cols 2-3 link lists .mono style. Col4 contact. Bottom: 1px rgba(245,243,238,0.1) mt:40px pt:20px flex space-between .mono color:rgba(245,243,238,0.25) copyright.""",
    },
]

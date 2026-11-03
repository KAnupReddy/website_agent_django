"""Display configuration shared by the dashboard views (badges, icons, labels)."""

STAGE_ORDER = ['pending', 'enriched', 'designed', 'deployed', 'contacted', 'converted']

# Pill badge per status (dashboard + list tables)
STAGE_PILLS = {
    'pending':   {'dot': 'bg-slate-400',  'text': 'text-slate-600',  'ring': 'ring-slate-200',  'label': 'Added'},
    'enriched':  {'dot': 'bg-blue-500',   'text': 'text-blue-700',   'ring': 'ring-blue-100',   'label': 'Enriched'},
    'designed':  {'dot': 'bg-purple-500', 'text': 'text-purple-700', 'ring': 'ring-purple-100', 'label': 'Designed'},
    'deployed':  {'dot': 'bg-indigo-500', 'text': 'text-indigo-700', 'ring': 'ring-indigo-100', 'label': 'Deployed'},
    'contacted': {'dot': 'bg-orange-500', 'text': 'text-orange-700', 'ring': 'ring-orange-100', 'label': 'Contacted'},
    'converted': {'dot': 'bg-green-500',  'text': 'text-green-700',  'ring': 'ring-green-100',  'label': 'Converted'},
    'skipped':   {'dot': 'bg-slate-300',  'text': 'text-slate-400',  'ring': 'ring-slate-100',  'label': 'Skipped'},
}

# KPI cards on the overview page
STAGE_CARDS = [
    {'key': 'pending', 'label': 'Added', 'color': 'bg-slate-100 text-slate-500', 'bar': 'bg-slate-400',
     'icon': 'M12 4v16m8-8H4'},
    {'key': 'enriched', 'label': 'Enriched', 'color': 'bg-blue-50 text-blue-600', 'bar': 'bg-blue-500',
     'icon': 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z'},
    {'key': 'designed', 'label': 'Designed', 'color': 'bg-purple-50 text-purple-600', 'bar': 'bg-purple-500',
     'icon': 'M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01'},
    {'key': 'deployed', 'label': 'Deployed', 'color': 'bg-indigo-50 text-indigo-600', 'bar': 'bg-indigo-500',
     'icon': 'M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z'},
    {'key': 'contacted', 'label': 'Contacted', 'color': 'bg-orange-50 text-orange-600', 'bar': 'bg-orange-500',
     'icon': 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z'},
    {'key': 'converted', 'label': 'Converted', 'color': 'bg-green-50 text-green-600', 'bar': 'bg-green-500',
     'icon': 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'},
]

AGENTS = [
    {'icon': '📊', 'name': 'Enrichment', 'desc': 'GPT business analysis'},
    {'icon': '🧠', 'name': 'Strategy', 'desc': 'Content planning'},
    {'icon': '🎨', 'name': 'Design', 'desc': '5 HTML variations'},
    {'icon': '💻', 'name': 'Build', 'desc': 'Write to disk'},
    {'icon': '🌐', 'name': 'Hosting', 'desc': 'FTP deploy'},
    {'icon': '📧', 'name': 'Outreach', 'desc': 'Email outreach'},
]

# Detail page
STAGE_STEPS = {
    'pending':   {'label': 'Added',     'icon': '📋', 'agent': 'Manual Entry'},
    'enriched':  {'label': 'Enriched',  'icon': '📊', 'agent': 'Enrichment Agent'},
    'designed':  {'label': 'Designed',  'icon': '🎨', 'agent': 'Design Agent'},
    'deployed':  {'label': 'Deployed',  'icon': '🌐', 'agent': 'Hosting Agent'},
    'contacted': {'label': 'Contacted', 'icon': '📧', 'agent': 'Outreach Agent'},
    'converted': {'label': 'Converted', 'icon': '✅', 'agent': 'Client'},
}

STATUS_BADGES = {
    'pending':   'bg-slate-100 text-slate-600',
    'enriched':  'bg-blue-100 text-blue-700',
    'designed':  'bg-purple-100 text-purple-700',
    'deployed':  'bg-indigo-100 text-indigo-700',
    'contacted': 'bg-orange-100 text-orange-700',
    'converted': 'bg-green-100 text-green-700',
    'skipped':   'bg-red-50 text-red-600',
}

WEBSITE_STATUS_BADGES = {
    'no_website':  ('No Website', 'text-red-600 bg-red-50 border-red-100'),
    'has_website': ('Has Website', 'text-green-600 bg-green-50 border-green-100'),
    'unknown':     ('Unknown', 'text-slate-500 bg-slate-50 border-slate-100'),
}

STYLE_BADGES = {
    'prestige':  'bg-slate-800 text-amber-300',
    'velocity':  'bg-indigo-50 text-indigo-700',
    'canvas':    'bg-teal-50 text-teal-700',
    'obsidian':  'bg-neutral-900 text-orange-400',
    'editorial': 'bg-red-50 text-red-700',
}

DESIGN_STATUS_COLORS = {
    'draft': 'text-slate-400',
    'built': 'text-blue-500',
    'deployed': 'text-green-600',
    'selected': 'text-purple-600',
}

RESPONSE_COLORS = {
    'none': 'text-slate-400',
    'opened': 'text-blue-500',
    'replied': 'text-purple-500',
    'interested': 'text-green-600',
    'not_interested': 'text-red-500',
}

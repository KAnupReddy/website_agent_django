import io
import os
import zipfile

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from . import ui
from .forms import BUSINESS_TYPES, BusinessForm
from .models import Business, Design
from .services import Orchestrator
from .services.design_styles import STYLES
from .services.utils import remove_build_dir, slugify


def _crumbs(*items):
    """[('Dashboard', url), ('Businesses', url), ('Name', None)] → breadcrumb dicts."""
    return [{'label': label, 'url': url} for label, url in items]


def _with_pills(businesses):
    for b in businesses:
        b.pill = ui.STAGE_PILLS.get(b.status, ui.STAGE_PILLS['skipped'])
    return businesses


@require_GET
def index(request):
    """GET / — overview dashboard."""
    stats = Business.dashboard_stats()
    total = max(1, stats['total'])

    cards = [{**c, 'count': stats[c['key']], 'pct': round(stats[c['key']] / total * 100)} for c in ui.STAGE_CARDS]
    metrics = [
        {'label': label, 'pct': round(stats[key] / total * 100, 1), 'color': color}
        for label, key, color in (
            ('Conversion rate', 'converted', 'bg-green-400'),
            ('Contact rate', 'contacted', 'bg-orange-400'),
            ('Deploy rate', 'deployed', 'bg-indigo-400'),
        )
    ]

    return render(request, 'dashboard/index.html', {
        'stats': stats,
        'cards': cards,
        'metrics': metrics,
        'agents': ui.AGENTS,
        'recent': _with_pills(list(Business.objects.order_by('-created_at')[:8])),
        'page_title': 'AutoBiz AI — Dashboard',
        'breadcrumbs': _crumbs(('Dashboard', None)),
    })


@require_GET
def businesses(request):
    """GET /businesses — paginated list with optional status filter."""
    status = request.GET.get('status', '')
    qs = Business.objects.order_by('-created_at')
    if status:
        qs = qs.filter(status=status)

    page = Paginator(qs, 20).get_page(request.GET.get('page'))
    total = Business.objects.count()

    filters = [('', f'All ({total})')] + [(k, ui.STAGE_PILLS[k]['label']) for k in ui.STAGE_ORDER]

    return render(request, 'dashboard/businesses.html', {
        'page': page,
        'businesses': _with_pills(list(page.object_list)),
        'total': total,
        'filters': filters,
        'active_filter': status,
        'page_title': 'AutoBiz AI — Businesses',
        'breadcrumbs': _crumbs(('Dashboard', reverse('index')), ('Businesses', None)),
    })


def create(request):
    """GET/POST /businesses/add — onboarding form; optionally run the pipeline on save."""
    form = BusinessForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        business = form.save(commit=False)
        business.scrape_source = 'manual'
        business.status = Business.Status.PENDING
        business.save()

        if request.POST.get('action') == 'save_and_run':
            Orchestrator().process_business(business.id)
            messages.success(request, 'Business saved and pipeline completed.')
        else:
            messages.success(request, 'Business added successfully.')
        return redirect('business_detail', pk=business.id)

    return render(request, 'dashboard/add_business.html', {
        'form': form,
        'business_types': BUSINESS_TYPES,
        'errors': [e for errs in form.errors.values() for e in errs] if form.is_bound else [],
        'page_title': 'AutoBiz AI — Add Business',
        'breadcrumbs': _crumbs(('Dashboard', reverse('index')), ('Businesses', reverse('businesses')), ('Add Business', None)),
    })


@require_GET
def show(request, pk):
    """GET /businesses/<id> — business detail."""
    business = get_object_or_404(Business, pk=pk)
    designs = list(business.designs.order_by('version'))
    emails = list(business.emails.all())

    order = ui.STAGE_ORDER
    current = order.index(business.status) if business.status in order else -1
    steps = [
        {**ui.STAGE_STEPS[key], 'done': i < current, 'active': i == current}
        for i, key in enumerate(order)
    ]

    for d in designs:
        d.badge = ui.STYLE_BADGES.get(d.style_name, 'bg-slate-100 text-slate-600')
        d.status_color = ui.DESIGN_STATUS_COLORS.get(d.status, 'text-slate-400')
    for e in emails:
        e.response_color = ui.RESPONSE_COLORS.get(e.response_status, 'text-slate-400')
        e.is_sent = e.sent_status == 'sent'

    ws_label, ws_cls = ui.WEBSITE_STATUS_BADGES.get(business.website_status, ui.WEBSITE_STATUS_BADGES['unknown'])

    return render(request, 'dashboard/business.html', {
        'business': business,
        'designs': designs,
        'emails': emails,
        'has_built': any(d.preview_path for d in designs),
        'live_count': sum(d.status == Design.Status.DEPLOYED for d in designs),
        'style_count': len(STYLES),
        'steps': steps,
        'step_number': max(0, current + 1),
        'step_total': len(order),
        'progress_pct': current / (len(order) - 1) * 100 if current >= 0 else None,
        'badge': ui.STATUS_BADGES.get(business.status, 'bg-slate-100 text-slate-600'),
        'stars': [i <= round(business.rating) for i in range(1, 6)] if business.rating else [],
        'ws_label': ws_label,
        'ws_cls': ws_cls,
        'page_title': f'AutoBiz AI — {business.name}',
        'breadcrumbs': _crumbs(('Dashboard', reverse('index')), ('Businesses', reverse('businesses')), (business.name, None)),
    })


@require_POST
def run_pipeline(request, pk):
    """POST /businesses/<id>/run — trigger the pipeline (runs synchronously)."""
    get_object_or_404(Business, pk=pk)
    Orchestrator().process_business(pk)
    messages.success(request, 'Pipeline completed.')
    return redirect('business_detail', pk=pk)


@require_POST
def update_status(request, pk):
    """POST /businesses/<id>/status — set the business status manually."""
    business = get_object_or_404(Business, pk=pk)
    status = request.POST.get('status')
    if status not in Business.Status.values:
        messages.error(request, 'Invalid status.')
    else:
        business.status = status
        business.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Status updated.')
    return redirect(request.META.get('HTTP_REFERER') or reverse('business_detail', args=[pk]))


@require_POST
def delete_business(request, pk):
    """POST /businesses/<id>/delete — delete a business, its rows (cascade) and build files."""
    business = Business.objects.filter(pk=pk).first()
    if not business:
        messages.error(request, 'Business not found.')
        return redirect('businesses')

    name = business.name
    remove_build_dir(name)
    business.delete()  # enrichments, designs (+ deployments) and emails cascade

    messages.success(request, f'"{name}" has been deleted.')
    return redirect('businesses')


@require_POST
def regenerate(request, pk):
    """POST /businesses/<id>/regenerate — drop old designs and re-run strategy → design → build."""
    business = get_object_or_404(Business, pk=pk)

    business.designs.all().delete()
    remove_build_dir(business.name)

    # Reset to 'enriched' — the pipeline skips enrichment but re-runs strategy + design + build
    business.status = Business.Status.ENRICHED
    business.save(update_fields=['status', 'updated_at'])

    Orchestrator().process_business(pk)

    messages.success(request, 'Website designs regenerated successfully.')
    return redirect('business_detail', pk=pk)


@require_GET
def download(request, pk):
    """GET /businesses/<id>/download — ZIP of all built HTML files."""
    business = get_object_or_404(Business, pk=pk)
    designs = business.designs.exclude(preview_path__isnull=True).exclude(preview_path='')

    files = [d for d in designs if os.path.exists(d.preview_path)]
    if not files:
        messages.error(request, 'No built files available. Run the pipeline first.')
        return redirect('business_detail', pk=pk)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for d in files:
            zf.write(d.preview_path, d.filename)

    response = HttpResponse(buf.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{slugify(business.name)}_websites.zip"'
    response['Cache-Control'] = 'no-store'
    return response


@require_GET
def preview(request, design_id):
    """GET /preview/<id> — serve a design's raw generated HTML."""
    design = Design.objects.filter(pk=design_id).first()
    if not design or not design.html_code:
        raise Http404('Design not found')
    return HttpResponse(design.html_code, content_type='text/html; charset=utf-8')

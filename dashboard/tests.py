import io
import shutil
import tempfile
import zipfile
from pathlib import Path
from unittest import mock

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Business, Design, Enrichment
from .services import Orchestrator
from .services.design import DesignAgent
from .services.design_styles import STYLES
from .services.utils import parse_json_response, slugify

TMP_BUILD = Path(tempfile.mkdtemp(prefix='autobiz_test_builds_'))


def make_business(**kw):
    data = dict(name='Sunrise Café & Bar', business_type='Restaurant / Cafe', location='Hyderabad',
                website_status='no_website', scrape_source='manual')
    data.update(kw)
    return Business.objects.create(**data)


class UtilsTests(TestCase):
    def test_slugify_matches_php_rule(self):
        self.assertEqual(slugify('  The Brand Chimp!! '), 'the-brand-chimp')
        self.assertEqual(slugify('Rovix AI'), 'rovix-ai')

    def test_parse_json_strips_fences(self):
        self.assertEqual(parse_json_response('```json\n{"a": 1}\n```'), {'a': 1})
        self.assertIsNone(parse_json_response('not json'))
        self.assertIsNone(parse_json_response('[1, 2]'))


@override_settings(OPENAI_API_KEY='', BUILD_DIR=TMP_BUILD)
class PipelineTests(TestCase):
    """Runs the full pipeline against the offline stub responses."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_BUILD, ignore_errors=True)

    def test_full_pipeline_creates_one_built_design_per_style(self):
        b = make_business()
        Orchestrator().process_business(b.id)

        b.refresh_from_db()
        self.assertEqual(b.status, 'designed')
        self.assertEqual(Enrichment.objects.filter(business=b).count(), 1)

        designs = list(b.designs.order_by('version'))
        self.assertEqual([d.style_name for d in designs], [s['name'] for s in STYLES])
        for d in designs:
            self.assertEqual(d.status, 'built')
            self.assertTrue(Path(d.preview_path).exists())

    def test_failed_enrichment_marks_business_skipped(self):
        b = make_business()
        with mock.patch('dashboard.services.openai_client.OpenAIClient.chat', return_value='garbage'):
            Orchestrator().process_business(b.id)
        b.refresh_from_db()
        self.assertEqual(b.status, 'skipped')

    def test_process_pending_only_picks_no_website_businesses(self):
        a = make_business(name='Alpha')
        c = make_business(name='Charlie', website_status='has_website')
        Orchestrator().process_pending()
        a.refresh_from_db(); c.refresh_from_db()
        self.assertEqual(a.status, 'designed')
        self.assertEqual(c.status, 'pending')

    def test_agent_run_command(self):
        b = make_business()
        call_command('agent_run', id=b.id, stdout=io.StringIO())
        b.refresh_from_db()
        self.assertEqual(b.status, 'designed')

    def test_design_prompt_contains_style_and_business_data(self):
        b = make_business(phone='+91 12345')
        prompt = DesignAgent().build_prompt(
            b, {'hero_headline': 'Hello', 'services_teaser': [{'name': 'Coffee', 'description': 'Hot'}]},
            STYLES[0], {'url': ''},
        )
        self.assertIn(STYLES[0]['css_foundation'], prompt)
        self.assertIn('  • Coffee: Hot', prompt)
        self.assertIn('Phone: +91 12345', prompt)
        self.assertIn('FRESH DESIGN', prompt)


@override_settings(OPENAI_API_KEY='', BUILD_DIR=TMP_BUILD)
class ViewTests(TestCase):
    def test_dashboard_and_list_render(self):
        make_business()
        self.assertContains(self.client.get(reverse('index')), 'Recent Businesses')
        resp = self.client.get(reverse('businesses') + '?status=pending')
        self.assertContains(resp, 'Sunrise Café &amp; Bar')

    def test_add_business_validation(self):
        resp = self.client.post(reverse('business_add'), {'name': 'A', 'location': '', 'email': 'bad'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Please fix the following errors')
        self.assertEqual(Business.objects.count(), 0)

    def test_add_business_saves_and_redirects(self):
        resp = self.client.post(reverse('business_add'), {
            'name': 'Glow Spa', 'business_type': 'Salon / Spa & Beauty', 'location': 'Pune',
            'website_status': 'no_website', 'review_count': '', 'action': 'save',
        })
        b = Business.objects.get()
        self.assertRedirects(resp, reverse('business_detail', args=[b.id]))
        self.assertEqual((b.status, b.scrape_source, b.review_count, b.email), ('pending', 'manual', 0, None))

    def test_run_download_preview_regenerate_delete(self):
        b = make_business()
        self.client.post(reverse('business_run', args=[b.id]))
        self.assertContains(self.client.get(reverse('business_detail', args=[b.id])), 'Download ZIP')

        resp = self.client.get(reverse('business_download', args=[b.id]))
        self.assertEqual(resp['Content-Type'], 'application/zip')
        names = zipfile.ZipFile(io.BytesIO(resp.content)).namelist()
        self.assertEqual(len(names), len(STYLES))

        design = b.designs.first()
        self.assertContains(self.client.get(reverse('preview', args=[design.id])), '<!DOCTYPE html>')

        self.client.post(reverse('business_regenerate', args=[b.id]))
        self.assertEqual(b.designs.count(), len(STYLES))
        self.assertFalse(Design.objects.filter(id=design.id).exists())

        build_dir = Path(b.designs.first().preview_path).parent
        self.client.post(reverse('business_delete', args=[b.id]))
        self.assertFalse(Business.objects.filter(id=b.id).exists())
        self.assertFalse(build_dir.exists())

    def test_update_status_rejects_unknown_value(self):
        b = make_business()
        self.client.post(reverse('business_status', args=[b.id]), {'status': 'hacked'})
        b.refresh_from_db()
        self.assertEqual(b.status, 'pending')
        self.client.post(reverse('business_status', args=[b.id]), {'status': 'converted'})
        b.refresh_from_db()
        self.assertEqual(b.status, 'converted')

    def test_post_only_endpoints_reject_get(self):
        b = make_business()
        self.assertEqual(self.client.get(reverse('business_delete', args=[b.id])).status_code, 405)

    def test_missing_pages_404(self):
        self.assertEqual(self.client.get(reverse('business_detail', args=[999])).status_code, 404)
        self.assertEqual(self.client.get(reverse('preview', args=[999])).status_code, 404)

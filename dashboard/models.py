"""
Database models — one per table from the original CodeIgniter migrations.

Table and column names are kept identical to the CI4 schema (`restaurants`,
`restaurant_id`, …) so data can be moved between the two apps unchanged.
"""

from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class Business(TimestampedModel):
    """A business being onboarded (table kept as `restaurants` for compatibility)."""

    class WebsiteStatus(models.TextChoices):
        NO_WEBSITE = 'no_website', 'No Website'
        HAS_WEBSITE = 'has_website', 'Has Website'
        UNKNOWN = 'unknown', 'Unknown'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Added'
        ENRICHED = 'enriched', 'Enriched'
        DESIGNED = 'designed', 'Designed'
        DEPLOYED = 'deployed', 'Deployed'
        CONTACTED = 'contacted', 'Contacted'
        CONVERTED = 'converted', 'Converted'
        SKIPPED = 'skipped', 'Skipped'

    name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    google_maps_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    address = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    review_count = models.PositiveIntegerField(default=0)
    website_status = models.CharField(max_length=20, choices=WebsiteStatus.choices, default=WebsiteStatus.UNKNOWN)
    website_url = models.URLField(max_length=500, null=True, blank=True)
    scrape_source = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        db_table = 'restaurants'
        ordering = ['-created_at']
        verbose_name_plural = 'businesses'

    def __str__(self):
        return self.name

    @classmethod
    def dashboard_stats(cls):
        counts = dict(cls.objects.values_list('status').annotate(n=models.Count('id')).order_by())
        stats = {s: counts.get(s, 0) for s in ('pending', 'enriched', 'designed', 'deployed', 'contacted', 'converted')}
        stats['total'] = sum(counts.values())
        return stats


class Enrichment(TimestampedModel):
    """GPT-generated branding / audience analysis for a business."""

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='enrichments', db_column='restaurant_id')
    business_summary = models.TextField(null=True, blank=True)
    target_audience = models.TextField(null=True, blank=True)
    branding_notes = models.TextField(null=True, blank=True)
    usp = models.TextField(null=True, blank=True)
    tone = models.CharField(max_length=50, null=True, blank=True)
    color_palette = models.CharField(max_length=100, null=True, blank=True)
    keywords = models.TextField(null=True, blank=True)
    raw_gpt_response = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'enrichments'

    def __str__(self):
        return f'Enrichment for {self.business}'


class Design(TimestampedModel):
    """One generated single-page website (one per style)."""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        BUILT = 'built', 'Built'
        DEPLOYED = 'deployed', 'Deployed'
        SELECTED = 'selected', 'Selected'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='designs', db_column='restaurant_id')
    version = models.PositiveSmallIntegerField(default=1)
    style_name = models.CharField(max_length=100, null=True, blank=True)
    html_code = models.TextField(null=True, blank=True)
    css_framework = models.CharField(max_length=50, default='tailwind')
    preview_path = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        db_table = 'designs'
        ordering = ['version']

    def __str__(self):
        return f'{self.business} v{self.version} ({self.style_name})'

    @property
    def filename(self):
        return f'v{self.version}_{self.style_name}.html'


class Deployment(TimestampedModel):
    """An FTP upload of a built design to the demo host."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        UPLOADING = 'uploading', 'Uploading'
        LIVE = 'live', 'Live'
        FAILED = 'failed', 'Failed'

    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name='deployments')
    url = models.CharField(max_length=255, null=True, blank=True)
    subdomain = models.CharField(max_length=100, null=True, blank=True)
    ftp_path = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error_msg = models.TextField(null=True, blank=True)
    deployed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'deployments'

    def __str__(self):
        return self.url or f'Deployment #{self.pk}'


class Email(TimestampedModel):
    """An outreach email sent (or attempted) to a business owner."""

    class SentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        FAILED = 'failed', 'Failed'

    class ResponseStatus(models.TextChoices):
        NONE = 'none', 'None'
        OPENED = 'opened', 'Opened'
        REPLIED = 'replied', 'Replied'
        INTERESTED = 'interested', 'Interested'
        NOT_INTERESTED = 'not_interested', 'Not interested'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='emails', db_column='restaurant_id')
    to_email = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    demo_links = models.TextField(null=True, blank=True)
    sent_status = models.CharField(max_length=20, choices=SentStatus.choices, default=SentStatus.PENDING)
    response_status = models.CharField(max_length=20, choices=ResponseStatus.choices, default=ResponseStatus.NONE)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_msg = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'emails'

    def __str__(self):
        return f'{self.to_email} ({self.sent_status})'

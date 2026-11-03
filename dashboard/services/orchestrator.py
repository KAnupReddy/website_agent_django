import logging

from django.utils import timezone

from ..models import Business
from .build import BuildAgent
from .design import DesignAgent
from .enrichment import EnrichmentAgent
from .hosting import HostingAgent
from .outreach import OutreachAgent
from .strategy import StrategyAgent

logger = logging.getLogger('autobiz')


class Orchestrator:
    """
    Master orchestrator — coordinates all agents in sequence for each business.

    Workflow (manual entry):
        Enrichment → Strategy → Design (×5) → Build → Hosting → Outreach
    """

    def __init__(self):
        self.enrichment = EnrichmentAgent()
        self.strategy = StrategyAgent()
        self.design = DesignAgent()
        self.build = BuildAgent()
        self.hosting = HostingAgent()
        self.outreach = OutreachAgent()

    def process_pending(self) -> None:
        """Process every business with no website that is still pending/enriched."""
        pending = list(Business.objects.filter(
            website_status=Business.WebsiteStatus.NO_WEBSITE,
            status__in=[Business.Status.PENDING, Business.Status.ENRICHED],
        ).values_list('id', flat=True))

        logger.info('[Orchestrator] Processing %d pending businesses.', len(pending))
        for business_id in pending:
            self.process_business(business_id)

    def process_business(self, business_id: int) -> None:
        """Run the full pipeline for a single business."""
        business = Business.objects.filter(pk=business_id).first()
        if not business:
            logger.error('[Orchestrator] Business #%s not found.', business_id)
            return

        logger.info('[Orchestrator] ===== Processing: %s (#%s) =====', business.name, business_id)

        # Step 1: Enrichment
        if business.status == Business.Status.PENDING:
            if not self.enrichment.enrich(business_id):
                logger.warning('[Orchestrator] Enrichment failed for #%s — skipping.', business_id)
                self._set_status(business_id, Business.Status.SKIPPED)
                return

        # Step 2: Content strategy
        content = self.strategy.strategize(business_id)
        if not content:
            logger.warning('[Orchestrator] Strategy failed for #%s — skipping.', business_id)
            self._set_status(business_id, Business.Status.SKIPPED)
            return

        # Step 3: Generate one design per style
        design_ids = self.design.generate(business_id, content)
        if not design_ids:
            logger.warning('[Orchestrator] Design generation failed for #%s.', business_id)
            return
        logger.info('[Orchestrator] Generated %d designs.', len(design_ids))

        # Step 4: Build (write HTML to disk)
        local_paths = self.build.build(business_id)
        logger.info('[Orchestrator] Built %d files.', len(local_paths))

        if local_paths:
            self._set_status(business_id, Business.Status.DESIGNED)

        # Step 5: Host (FTP upload) — disabled; use ZIP download instead
        # demo_urls = self.hosting.deploy(business_id)
        # logger.info('[Orchestrator] Deployed %d pages.', len(demo_urls))

        # Step 6: Outreach email — disabled; notify user via ZIP download
        # if demo_urls:
        #     self.outreach.send_outreach(business_id, demo_urls)

        logger.info('[Orchestrator] ===== Done: %s =====', business.name)

    @staticmethod
    def _set_status(business_id: int, status: str) -> None:
        Business.objects.filter(pk=business_id).update(status=status, updated_at=timezone.now())

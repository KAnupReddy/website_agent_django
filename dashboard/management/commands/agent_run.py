from django.core.management.base import BaseCommand

from dashboard.services import Orchestrator


class Command(BaseCommand):
    """
    Run the AutoBiz AI pipeline from the command line.

    Usage:
        python manage.py agent_run           # Process all pending businesses
        python manage.py agent_run --id 5    # Process a single business by ID
    """

    help = 'Run the AutoBiz AI pipeline for manually added businesses.'

    def add_arguments(self, parser):
        parser.add_argument('--id', type=int, help='Process a single business by its database ID')

    def handle(self, *args, **options):
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('  AutoBiz AI — Business Website Generator'))
        self.stdout.write(self.style.HTTP_INFO('  ========================================'))
        self.stdout.write('')

        orchestrator = Orchestrator()
        business_id = options.get('id')

        if business_id is not None:
            self.stdout.write(self.style.WARNING(f'  Processing business #{business_id}...'))
            orchestrator.process_business(business_id)
            self.stdout.write(self.style.SUCCESS('  Done!'))
            return

        self.stdout.write(self.style.WARNING('  Processing all pending businesses...'))
        orchestrator.process_pending()
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('  Pipeline complete!'))

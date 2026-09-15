from django.core.management.base import BaseCommand

from reconciler.services.comparator import reconcile_records


class Command(BaseCommand):
    help = "Run cross-system reconciliation"

    def handle(self, *args, **options):
        self.stdout.write("Starting reconciliation...")

        discrepancies = reconcile_records()

        self.stdout.write(
            self.style.SUCCESS(
                f"Reconciliation completed. "
                f"Discrepancies found: {len(discrepancies)}"
            )
        )
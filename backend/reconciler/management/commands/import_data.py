import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from reconciler.models import (
    Location,
    SystemARecord,
    SystemBRecord,
)


def normalize_reference(value):
    """
    Normalize System B references for comparison.

    Examples:
    REC-1034   -> rec1034
    rec1034    -> rec1034
    REC - 1070 -> rec1070
    """
    if not value:
        return ""

    return "".join(
        character.lower()
        for character in value.strip()
        if character.isalnum()
    )


class Command(BaseCommand):
    help = "Import System A, System B, and location CSV data"

    def handle(self, *args, **options):
        # Project root:
        # C:\Users\gandl\reconciliation-engine
        project_root = Path(__file__).resolve().parents[4]

        # CSV folder:
        # C:\Users\gandl\reconciliation-engine\data
        data_dir = project_root / "data"

        locations_file = data_dir / "locations.csv"
        system_a_file = data_dir / "system_a.csv"
        system_b_file = data_dir / "system_b.csv"

        self.stdout.write("Starting CSV import...")

        # Import locations first because locations determine tenant/org.
        self.import_locations(locations_file)

        # Import System A.
        self.import_system_a(system_a_file)

        # Import System B.
        self.import_system_b(system_b_file)

        self.stdout.write(
            self.style.SUCCESS(
                "CSV import completed successfully."
            )
        )

    def import_locations(self, file_path):
        self.stdout.write("Importing locations...")

        with open(
            file_path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                location_id = row.get("location_id", "").strip()
                org_id = row.get("org_id", "").strip()

                Location.objects.update_or_create(
                    location_id=location_id,
                    defaults={
                        "org_id": org_id,
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Locations imported: {Location.objects.count()}"
            )
        )

    def import_system_a(self, file_path):
        self.stdout.write("Importing System A...")

        with open(
            file_path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                record_id = row.get("record_id", "").strip()

                SystemARecord.objects.update_or_create(
                    record_id=record_id,
                    defaults={
                        "location_id": row.get(
                            "location_id", ""
                        ).strip(),

                        "event_date": row.get(
                            "event_date", ""
                        ).strip(),

                        "category_code": row.get(
                            "category_code", ""
                        ).strip(),

                        "actor_id": row.get(
                            "actor_id", ""
                        ).strip(),

                        "base_value": row.get(
                            "base_value", ""
                        ).strip(),

                        "adjustment": row.get(
                            "adjustment", ""
                        ).strip(),

                        "total_value": row.get(
                            "total_value", ""
                        ).strip(),

                        "state": row.get(
                            "state", ""
                        ).strip(),
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"System A records imported: "
                f"{SystemARecord.objects.count()}"
            )
        )

    def import_system_b(self, file_path):
        self.stdout.write("Importing System B...")

        with open(
            file_path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                raw_reference = row.get(
                    "record_ref", ""
                ).strip()

                normalized_reference = normalize_reference(
                    raw_reference
                )

                # IMPORTANT:
                # Use create(), not update_or_create().
                #
                # System B intentionally contains duplicate
                # references. We must preserve every row so
                # the reconciliation logic can detect duplicates.
                SystemBRecord.objects.create(
                    record_ref=raw_reference,

                    normalized_ref=normalized_reference,

                    location_id=row.get(
                        "location_id", ""
                    ).strip(),

                    event_date=row.get(
                        "event_date", ""
                    ).strip(),

                    value=row.get(
                        "value", ""
                    ).strip(),

                    state=row.get(
                        "state", ""
                    ).strip(),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"System B records imported: "
                f"{SystemBRecord.objects.count()}"
            )
        )
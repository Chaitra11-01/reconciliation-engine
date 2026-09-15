from decimal import Decimal

from django.test import TestCase

from reconciler.models import (
    Discrepancy,
    Location,
    SystemARecord,
    SystemBRecord,
)
from reconciler.services.comparator import (
    normalize_reference,
    safe_parse_decimal,
    values_are_different,
    reconcile_records,
)


class ComparatorTests(TestCase):

    def test_detects_record_missing_in_system_b(self):
        Location.objects.create(
            location_id="LOC-101",
            org_id="ORG-A",
        )

        SystemARecord.objects.create(
            record_id="REC-1001",
            location_id="LOC-101",
            total_value="1000",
        )

        reconcile_records()

        self.assertTrue(
            Discrepancy.objects.filter(
                record_ref="REC-1001",
                reason="MISSING_IN_B",
            ).exists()
        )

    def test_detects_orphan_record_in_system_b(self):
        Location.objects.create(
            location_id="LOC-101",
            org_id="ORG-A",
        )

        SystemBRecord.objects.create(
            record_ref="REC-9999",
            normalized_ref="rec9999",
            location_id="LOC-101",
            value="500",
        )

        reconcile_records()

        self.assertTrue(
            Discrepancy.objects.filter(
                record_ref="REC-9999",
                reason="ORPHAN_IN_B",
            ).exists()
        )

    def test_detects_duplicate_entries_in_system_b(self):
        Location.objects.create(
            location_id="LOC-101",
            org_id="ORG-A",
        )

        SystemARecord.objects.create(
            record_id="REC-1001",
            location_id="LOC-101",
            total_value="1000",
        )

        SystemBRecord.objects.create(
            record_ref="REC-1001",
            normalized_ref="rec1001",
            location_id="LOC-101",
            value="1000",
        )

        SystemBRecord.objects.create(
            record_ref="rec1001",
            normalized_ref="rec1001",
            location_id="LOC-101",
            value="1000",
        )

        reconcile_records()

        self.assertTrue(
            Discrepancy.objects.filter(
                record_ref="REC-1001",
                reason="DUPLICATE_IN_B",
            ).exists()
        )

    def test_detects_value_mismatch(self):
        Location.objects.create(
            location_id="LOC-101",
            org_id="ORG-A",
        )

        SystemARecord.objects.create(
            record_id="REC-1001",
            location_id="LOC-101",
            total_value="1000.00",
        )

        SystemBRecord.objects.create(
            record_ref="REC-1001",
            normalized_ref="rec1001",
            location_id="LOC-101",
            value="1200.00",
        )

        reconcile_records()

        self.assertTrue(
            Discrepancy.objects.filter(
                record_ref="REC-1001",
                reason="VALUE_MISMATCH",
            ).exists()
        )

    def test_tenant_boundary_isolation(self):
        Location.objects.create(
            location_id="LOC-A",
            org_id="ORG-A",
        )

        Location.objects.create(
            location_id="LOC-B",
            org_id="ORG-B",
        )

        SystemARecord.objects.create(
            record_id="REC-A",
            location_id="LOC-A",
            total_value="1000",
        )

        SystemARecord.objects.create(
            record_id="REC-B",
            location_id="LOC-B",
            total_value="2000",
        )

        reconcile_records()

        org_a_results = Discrepancy.objects.filter(
            org_id="ORG-A"
        )

        org_b_results = Discrepancy.objects.filter(
            org_id="ORG-B"
        )

        self.assertTrue(
            org_a_results.exists()
        )

        self.assertTrue(
            org_b_results.exists()
        )

        for item in org_a_results:
            self.assertEqual(item.org_id, "ORG-A")

        for item in org_b_results:
            self.assertEqual(item.org_id, "ORG-B")


class NormalizationTests(TestCase):

    def test_normalize_reference(self):
        self.assertEqual(
            normalize_reference("REC-1034"),
            "rec1034",
        )

        self.assertEqual(
            normalize_reference("rec1034"),
            "rec1034",
        )

        self.assertEqual(
            normalize_reference("REC - 1034"),
            "rec1034",
        )

    def test_safe_parse_decimal(self):
        self.assertEqual(
            safe_parse_decimal("1,234.50"),
            Decimal("1234.50"),
        )

        self.assertEqual(
            safe_parse_decimal("$1,234.50"),
            Decimal("1234.50"),
        )

        self.assertIsNone(
            safe_parse_decimal(""),
        )

        self.assertIsNone(
            safe_parse_decimal("N/A"),
        )

    def test_values_are_different(self):
        self.assertFalse(
            values_are_different(
                "1,000.00",
                "1000.00",
            )
        )

        self.assertTrue(
            values_are_different(
                "1000.00",
                "1200.00",
            )
        )
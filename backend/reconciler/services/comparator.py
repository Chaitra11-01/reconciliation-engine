from collections import defaultdict
from decimal import Decimal, InvalidOperation
import re

from reconciler.models import (
    Discrepancy,
    Location,
    SystemARecord,
    SystemBRecord,
)


def normalize_reference(value):
    """
    Normalize a record reference so different formats
    can still be compared.

    Examples:
    REC-1034    -> rec1034
    rec1034     -> rec1034
    REC - 1070  -> rec1070
    """

    if not value:
        return ""

    return "".join(
        character.lower()
        for character in value.strip()
        if character.isalnum()
    )


def safe_parse_decimal(value):
    """
    Safely convert a messy numeric value to Decimal.

    Blank or non-parseable values return None instead
    of crashing the reconciliation process.
    """

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    if value.upper() in {"N/A", "NULL", "NONE", "-"}:
        return None

    # Keep digits, decimal point and minus sign.
    cleaned = re.sub(r"[^0-9.\-]", "", value)

    if not cleaned:
        return None

    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


def values_are_different(value_a, value_b):
    """
    Compare numeric values safely.

    If both values can be parsed, compare their numeric
    values. Otherwise compare their original text.
    """

    parsed_a = safe_parse_decimal(value_a)
    parsed_b = safe_parse_decimal(value_b)

    if parsed_a is not None and parsed_b is not None:
        return parsed_a != parsed_b

    return str(value_a).strip() != str(value_b).strip()


def get_location_org(location_id):
    """
    Find the tenant/org associated with a location.
    """

    location = Location.objects.filter(
        location_id=location_id
    ).first()

    if location:
        return location.org_id

    return ""


def reconcile_records():
    """
    Compare System A and System B and create discrepancy records.

    Discrepancy types:

    1. Missing in System B
    2. Orphan in System B
    3. Duplicate in System B
    4. Value mismatch
    """

    # Remove previous reconciliation results so that
    # running reconciliation again does not create
    # duplicate discrepancy records.
    Discrepancy.objects.all().delete()

    system_a_records = list(
        SystemARecord.objects.all()
    )

    system_b_records = list(
        SystemBRecord.objects.all()
    )

    # Group System B records by normalized reference.
    b_by_reference = defaultdict(list)

    for record in system_b_records:
        normalized = normalize_reference(
            record.record_ref
        )

        b_by_reference[normalized].append(record)

    # Keep track of references that actually exist in System A.
    system_a_references = set()

    discrepancies = []

    # ---------------------------------------------------------
    # Compare System A records against System B
    # ---------------------------------------------------------

    for record_a in system_a_records:

        normalized_a = normalize_reference(
            record_a.record_id
        )

        system_a_references.add(normalized_a)

        matching_b_records = b_by_reference.get(
            normalized_a,
            []
        )

        # Case 1:
        # System A record has no System B entry.
        if not matching_b_records:

            discrepancies.append(
                Discrepancy(
                    record_ref=record_a.record_id,
                    reason="MISSING_IN_B",
                    location_id=record_a.location_id,
                    org_id=get_location_org(
                        record_a.location_id
                    ),
                    system_a_value=record_a.total_value,
                    system_b_value="",
                )
            )

            continue

        # Case 2:
        # Multiple System B entries point to the
        # same System A record.
        if len(matching_b_records) > 1:

            discrepancies.append(
                Discrepancy(
                    record_ref=record_a.record_id,
                    reason="DUPLICATE_IN_B",
                    location_id=record_a.location_id,
                    org_id=get_location_org(
                        record_a.location_id
                    ),
                    system_a_value=record_a.total_value,
                    system_b_value=", ".join(
                        record.value
                        for record in matching_b_records
                    ),
                )
            )

            # We do not perform a normal one-to-one
            # value comparison when duplicates exist.
            continue

        # Case 3:
        # Exactly one System B record exists.
        record_b = matching_b_records[0]

        if values_are_different(
            record_a.total_value,
            record_b.value,
        ):

            discrepancies.append(
                Discrepancy(
                    record_ref=record_a.record_id,
                    reason="VALUE_MISMATCH",
                    location_id=record_a.location_id,
                    org_id=get_location_org(
                        record_a.location_id
                    ),
                    system_a_value=record_a.total_value,
                    system_b_value=record_b.value,
                )
            )

    # ---------------------------------------------------------
    # Find orphan System B records
    # ---------------------------------------------------------

    for record_b in system_b_records:

        normalized_b = normalize_reference(
            record_b.record_ref
        )

        if normalized_b not in system_a_references:

            discrepancies.append(
                Discrepancy(
                    record_ref=record_b.record_ref,
                    reason="ORPHAN_IN_B",
                    location_id=record_b.location_id,
                    org_id=get_location_org(
                        record_b.location_id
                    ),
                    system_a_value="",
                    system_b_value=record_b.value,
                )
            )

    # Save all discrepancies.
    Discrepancy.objects.bulk_create(
        discrepancies
    )

    return discrepancies
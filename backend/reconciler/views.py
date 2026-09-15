from django.http import JsonResponse

from .models import Discrepancy, Location


def discrepancies(request):
    """
    Return discrepancies for one tenant.

    Tenant isolation is enforced at the database-query level
    before the results are serialized.
    """

    org_id = request.GET.get("org_id")

    # Tenant is mandatory.
    if not org_id:
        return JsonResponse(
            {
                "error": "org_id is required"
            },
            status=400,
        )

    # Start with discrepancies belonging to the requested tenant.
    queryset = Discrepancy.objects.filter(
        org_id=org_id
    )

    # Optional reason filter.
    reason = request.GET.get("reason")

    if reason:
        queryset = queryset.filter(
            reason=reason
        )

    # Optional sorting.
    sort = request.GET.get("sort", "record_ref")

    allowed_sort_fields = {
        "record_ref": "record_ref",
        "reason": "reason",
        "system_a_value": "system_a_value",
        "system_b_value": "system_b_value",
        "location_id": "location_id",
    }

    sort_field = allowed_sort_fields.get(
        sort,
        "record_ref"
    )

    order = request.GET.get("order", "asc")

    if order == "desc":
        sort_field = f"-{sort_field}"

    queryset = queryset.order_by(sort_field)

    results = []

    for item in queryset:

        results.append(
            {
                "id": item.id,
                "record_ref": item.record_ref,
                "reason": item.reason,
                "location_id": item.location_id,
                "org_id": item.org_id,
                "system_a_value": item.system_a_value,
                "system_b_value": item.system_b_value,
            }
        )

    return JsonResponse(
        {
            "count": len(results),
            "results": results,
        }
    )


def tenants(request):
    """
    Return available tenants.

    This is used by the frontend tenant selector.
    """

    locations = Location.objects.all().order_by(
        "org_id"
    )

    tenant_ids = sorted(
        set(
            location.org_id
            for location in locations
            if location.org_id
        )
    )

    return JsonResponse(
        {
            "tenants": tenant_ids
        }
    )
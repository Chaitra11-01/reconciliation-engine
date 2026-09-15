from django.db import models


class Location(models.Model):
    location_id = models.CharField(max_length=100, unique=True)
    org_id = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.location_id} - {self.org_id}"


class SystemARecord(models.Model):
    record_id = models.CharField(max_length=100, unique=True)
    location_id = models.CharField(max_length=100)
    event_date = models.CharField(max_length=100, blank=True)
    category_code = models.CharField(max_length=100, blank=True)
    actor_id = models.CharField(max_length=100, blank=True)
    base_value = models.CharField(max_length=100, blank=True)
    adjustment = models.CharField(max_length=100, blank=True)
    total_value = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.record_id


class SystemBRecord(models.Model):
    record_ref = models.CharField(max_length=100, blank=True)
    normalized_ref = models.CharField(max_length=100, blank=True, db_index=True)
    location_id = models.CharField(max_length=100, blank=True)
    event_date = models.CharField(max_length=100, blank=True)
    value = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.record_ref


class Discrepancy(models.Model):
    REASON_CHOICES = [
        ("MISSING_IN_B", "Missing in System B"),
        ("ORPHAN_IN_B", "Orphan in System B"),
        ("DUPLICATE_IN_B", "Duplicate in System B"),
        ("VALUE_MISMATCH", "Value mismatch"),
    ]

    record_ref = models.CharField(max_length=100)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    location_id = models.CharField(max_length=100, blank=True)
    org_id = models.CharField(max_length=100, blank=True)
    system_a_value = models.CharField(max_length=100, blank=True)
    system_b_value = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.record_ref} - {self.reason}"
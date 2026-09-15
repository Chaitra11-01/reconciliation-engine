# Design Decisions

## 1. Store raw values as strings during ingestion

**Decision:**  
Store imported CSV values such as dates and monetary values as strings in the database instead of immediately converting every field to a strict type.

**Rejected alternative:**  
Convert all CSV values to numbers and dates during import.

**Reasoning:**  
The assignment contains intentionally dirty data, including blanks and malformed values. Keeping the original values prevents data from being silently dropped or changed during ingestion.

---

## 2. Normalize System B references before comparison

**Decision:**  
Normalize System B references by trimming whitespace, removing non-alphanumeric characters, and converting to lowercase before matching records.

**Rejected alternative:**  
Require exact string equality between System A and System B references.

**Reasoning:**  
The source data contains multiple reference formats such as `REC-1034`, `rec1034`, and `REC - 1070`. Normalization allows equivalent references to match while preserving the original reference for display.

---

## 3. Preserve duplicate System B rows

**Decision:**  
Use a normal `create()` operation when importing System B records so every source row is retained, including duplicate references.

**Rejected alternative:**  
Use `update_or_create()` based on the reference.

**Reasoning:**  
Duplicates are one of the required discrepancy types. Updating an existing row would silently remove the evidence needed to detect duplicates.

---

## 4. Derive tenant ownership from locations

**Decision:**  
Use `locations.csv` as the source of truth for mapping a location to its organization/tenant.

**Rejected alternative:**  
Store an independently supplied tenant value on each System A or System B import row.

**Reasoning:**  
The assignment states that every location belongs to exactly one organization and that this is the only tenant mapping available.

---

## 5. Enforce tenant isolation in the API query

**Decision:**  
Require `org_id` in the discrepancy API request and filter the database queryset by that organization before serializing results.

**Rejected alternative:**  
Load all discrepancies and filter them in the React frontend.

**Reasoning:**  
Filtering at the database-query layer prevents records from another tenant from being returned to the client in the first place.

---

## 6. Keep reconciliation logic in a dedicated service

**Decision:**  
Place comparison logic in `reconciler/services/comparator.py`.

**Rejected alternative:**  
Put the reconciliation rules directly inside Django views or management commands.

**Reasoning:**  
A dedicated service keeps business logic independent from HTTP and command-line code and makes the comparison rules easier to test.

---

## 7. Use a management command for reconciliation

**Decision:**  
Run reconciliation through the Django management command:

`python manage.py reconcile`

**Rejected alternative:**  
Run reconciliation automatically every time the API endpoint is requested.

**Reasoning:**  
Separating ingestion/reconciliation from the read API keeps the API simple and makes the reconciliation process explicit and repeatable.

---

## 8. Keep the frontend intentionally simple

**Decision:**  
Use a small React interface with tenant selection, reason filtering, sorting, and a discrepancy table.

**Rejected alternative:**  
Spend significant time on advanced visual design, dashboards, charts, and authentication.

**Reasoning:**  
The assignment prioritizes correctness, dirty-data handling, tenant isolation, and tests over visual polish and features outside the required scope.
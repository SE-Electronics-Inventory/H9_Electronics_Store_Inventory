# NFR-02 Inventory Scalability

**Acceptance target:** Inventory operations continue to work with at least 1,000 component records (TC-PERF-02).

## Load a local development database

Run from `src`:

```powershell
python manage.py seed_components --count 1000
```

The command retains the original realistic demo seed and adds deterministic scalability IDs `SCALE-000001` through `SCALE-001000`. It is safe to run again: existing IDs are left unchanged and missing IDs are added. Use `--prefix TEST-SCALE` to keep a separate generated set. The command never deletes or overwrites records.

## Validation

```powershell
python manage.py test inventory.test_scalability -v 2
```

The test suite checks command idempotence, renders the inventory list with 1,000 rows, searches for a known row, then adds, edits, and deactivates a component through the application views. Test data is rolled back when the run ends.

## Result

Validation passed locally on 2026-11-06: the seed command ensured 1,000 records, and list, search, add, edit, and deactivate requests all succeeded against the 1,000-record test dataset.

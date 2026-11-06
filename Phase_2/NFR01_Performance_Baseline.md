# NFR-01 Inventory Response Performance

**Acceptance target:** At least 90% of normal-load inventory list, search, add, edit, and delete requests complete in under 2 seconds (TC-PERF-01).

## Measurement

Run from `src`:

```powershell
python manage.py test nfr_tools.test_inventory_performance -v 2
```

The test uses Django's test client and a fresh in-memory SQLite test database. It measures ten requests for each operation (50 requests total), including Django view, ORM, and template processing. It prints a JSON summary prefixed with `NFR01_PERFORMANCE=`. The test database is rolled back when the run ends.

## Baseline run

| Date | Runtime | Requests under 2 s | Overall p90 | List p90 | Search p90 | Add p90 | Edit p90 | Delete p90 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-11-06 | Python 3.13.7, Django 6.1.2, SQLite in-memory | 50/50 (100%) | 15.65 ms | 11.68 ms | 12.96 ms | 16.53 ms | 15.64 ms | 9.48 ms |

This is a repeatable application-level baseline, not a production network-latency measurement. Results depend on the machine running the test.

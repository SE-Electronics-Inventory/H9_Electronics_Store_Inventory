# NFR-04 application availability measurement

This tool measures endpoint reachability; implementing and smoke-testing the tool does not demonstrate that the application met the 99% scheduled availability target. Run it for the agreed full measurement window and retain its JSONL observations and JSON report as evidence.

## Run a controlled measurement

1. Agree on a start/end time and polling interval with the team. Keep the application available at the URL during that full period.
2. Create an output directory outside the repository, for example `D:\ESIMS-evidence\availability-2026-11-05`.
3. If there is planned maintenance, create a CSV outside the repository with `start,end` columns. Use ISO-8601 timestamps with a timezone offset, for example `2026-11-05T13:00:00+05:30,2026-11-05T13:10:00+05:30`.
4. From `src`, run (replace the URL and duration with the agreed test window):

   ```powershell
   python -m nfr_tools.availability --url http://127.0.0.1:8000/ --duration-seconds 604800 --interval-seconds 60 --output-dir D:\ESIMS-evidence\availability-2026-11-05 --planned-maintenance D:\ESIMS-evidence\planned-maintenance.csv
   ```

   Omit `--planned-maintenance` when there is no planned maintenance. Keep the terminal/process alive for the full duration. Use an externally reachable URL if the test must cover network access beyond the local machine.

The output directory contains `availability_checks.jsonl` (timestamped success/failure samples) and `availability_report.json` (test start/end, eligible duration, excluded planned maintenance, downtime, uptime and percentage). The log is append-only across runs; use a fresh output directory for each controlled run.

## Interpretation and limitations

Availability is `(eligible duration - measured downtime) / eligible duration × 100`. Planned maintenance is removed from eligible duration. To avoid overstating availability, the measured outage window begins at the last successful sample (or test start when there is no prior success) and ends at the next successful sample (or test end if service does not recover). This conservative window may count some time before or after the true outage; the report records that method. Confirm outages against server logs. A short test run validates operation of the monitor only. Do not report 99% achievement until a full controlled test has completed and its evidence has been reviewed.

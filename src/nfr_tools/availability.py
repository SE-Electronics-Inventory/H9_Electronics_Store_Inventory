"""Sample an HTTP endpoint and calculate availability from recorded observations."""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Check:
    timestamp: datetime
    success: bool
    status_code: int | None = None
    error: str = ""


@dataclass(frozen=True)
class Interval:
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.start.tzinfo is None or self.start.utcoffset() is None or self.end.tzinfo is None or self.end.utcoffset() is None:
            raise ValueError("Interval timestamps must include a timezone.")
        if self.end < self.start:
            raise ValueError("Interval end must not be before its start.")


def parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"Timestamp must include a timezone offset: {value}")
    return parsed.astimezone(timezone.utc)


def load_maintenance(path: Path | None) -> list[Interval]:
    if path is None:
        return []
    intervals = []
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            intervals.append(Interval(parse_timestamp(row["start"]), parse_timestamp(row["end"])))
    return intervals


def check_url(url: str, timeout: float = 5.0) -> Check:
    timestamp = datetime.now(timezone.utc)
    request = urllib.request.Request(url, headers={"User-Agent": "ESIMS-Availability-Monitor/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            code = response.status
            return Check(timestamp, 200 <= code < 400, code, "" if 200 <= code < 400 else f"HTTP {code}")
    except urllib.error.HTTPError as exc:
        return Check(timestamp, False, exc.code, f"HTTP {exc.code}")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return Check(timestamp, False, None, str(exc.reason if isinstance(exc, urllib.error.URLError) else exc))


def _overlap_seconds(start: datetime, end: datetime, excluded: Iterable[Interval]) -> float:
    clipped = sorted(
        (max(start, item.start), min(end, item.end))
        for item in excluded
        if min(end, item.end) > max(start, item.start)
    )
    merged = []
    for item_start, item_end in clipped:
        if merged and item_start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], item_end))
        else:
            merged.append((item_start, item_end))
    return sum((item_end - item_start).total_seconds() for item_start, item_end in merged)


def calculate_report(
    checks: list[Check],
    test_start: datetime,
    test_end: datetime,
    planned_maintenance: list[Interval] | None = None,
) -> dict:
    """Calculate sampled downtime spans; outage boundaries are bounded by poll times."""
    if (
        test_start.tzinfo is None
        or test_start.utcoffset() is None
        or test_end.tzinfo is None
        or test_end.utcoffset() is None
        or test_end < test_start
    ):
        raise ValueError("Test start/end must be timezone-aware and ordered.")
    if any(check.timestamp.tzinfo is None or check.timestamp.utcoffset() is None for check in checks):
        raise ValueError("Check timestamps must include a timezone.")
    maintenance = planned_maintenance or []
    total = (test_end - test_start).total_seconds()
    maintenance_seconds = _overlap_seconds(test_start, test_end, maintenance)
    eligible = max(0.0, total - maintenance_seconds)
    ordered = sorted(checks, key=lambda item: item.timestamp)
    outages: list[Interval] = []
    outage_start = None
    last_success = None
    for check in ordered:
        point = min(max(check.timestamp, test_start), test_end)
        if not check.success and outage_start is None:
            # A failed poll only proves that the outage began after the last
            # successful poll. Use that whole interval as downtime so sampling
            # cannot inflate availability by assuming a later failure onset.
            outage_start = last_success or test_start
        elif check.success:
            if outage_start is not None:
                outages.append(Interval(outage_start, point))
                outage_start = None
            last_success = point
    if outage_start is not None:
        outages.append(Interval(outage_start, test_end))
    observed_downtime = sum((item.end - item.start).total_seconds() for item in outages)
    downtime = max(0.0, observed_downtime - sum(_overlap_seconds(item.start, item.end, maintenance) for item in outages))
    uptime = max(0.0, eligible - downtime) if ordered else None
    availability = 100.0 * uptime / eligible if eligible and uptime is not None else None
    return {
        "test_start": test_start.isoformat(),
        "test_end": test_end.isoformat(),
        "eligible_duration_seconds": eligible,
        "planned_maintenance_seconds_excluded": maintenance_seconds,
        "downtime_seconds": downtime if ordered else None,
        "uptime_seconds": uptime,
        "availability_percent": availability,
        "sample_count": len(ordered),
        "measurement_status": "samples recorded" if ordered else "no samples; availability is undetermined",
        "outages": [{"start": item.start.isoformat(), "end": item.end.isoformat()} for item in outages],
        "method_note": "Downtime is conservatively bounded from the last successful poll (or test start) through the next successful poll (or test end), so polling uncertainty cannot inflate availability.",
    }


def run_monitor(url: str, duration: float, interval: float, output: Path, maintenance: list[Interval]) -> dict:
    if duration <= 0 or interval <= 0:
        raise ValueError("Duration and polling interval must be positive.")
    output.mkdir(parents=True, exist_ok=True)
    log_path = output / "availability_checks.jsonl"
    report_path = output / "availability_report.json"
    start = datetime.now(timezone.utc)
    end_target = time.monotonic() + duration
    checks = []
    with log_path.open("a", encoding="utf-8") as stream:
        while True:
            check = check_url(url)
            checks.append(check)
            stream.write(json.dumps({"url": url, **asdict(check), "timestamp": check.timestamp.isoformat()}) + "\n")
            stream.flush()
            remaining = end_target - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(interval, remaining))
    end = datetime.now(timezone.utc)
    report = calculate_report(checks, start, end, maintenance)
    report.update({"url": url, "check_log": str(log_path), "planned_maintenance_intervals": len(maintenance)})
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Application URL to check")
    parser.add_argument("--duration-seconds", type=float, required=True)
    parser.add_argument("--interval-seconds", type=float, default=60)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--planned-maintenance", type=Path, help="CSV with timezone-aware start,end columns")
    args = parser.parse_args(argv)
    try:
        report = run_monitor(args.url, args.duration_seconds, args.interval_seconds, args.output_dir, load_maintenance(args.planned_maintenance))
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

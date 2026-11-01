from datetime import datetime, timedelta, timezone
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from nfr_tools.availability import Check, Interval, calculate_report, parse_timestamp, run_monitor


class AvailabilityCalculationTests(SimpleTestCase):
    def setUp(self):
        self.start = datetime(2026, 11, 5, 10, tzinfo=timezone.utc)

    def test_successful_checks_report_full_availability(self):
        report = calculate_report(
            [Check(self.start, True), Check(self.start + timedelta(minutes=10), True)],
            self.start,
            self.start + timedelta(minutes=10),
        )
        self.assertEqual(report["availability_percent"], 100)
        self.assertEqual(report["downtime_seconds"], 0)

    def test_failure_to_recovery_uses_conservative_previous_success_bound(self):
        report = calculate_report(
            [Check(self.start, True), Check(self.start + timedelta(minutes=2), False), Check(self.start + timedelta(minutes=5), True)],
            self.start,
            self.start + timedelta(minutes=10),
        )
        self.assertEqual(report["downtime_seconds"], 300)
        self.assertEqual(report["uptime_seconds"], 300)
        self.assertEqual(report["availability_percent"], 50)

    def test_first_failed_poll_counts_from_test_start(self):
        report = calculate_report(
            [Check(self.start + timedelta(minutes=2), False), Check(self.start + timedelta(minutes=4), True)],
            self.start,
            self.start + timedelta(minutes=10),
        )
        self.assertEqual(report["downtime_seconds"], 240)
        self.assertEqual(report["availability_percent"], 60)

    def test_last_failed_poll_counts_to_test_end(self):
        report = calculate_report(
            [Check(self.start, True), Check(self.start + timedelta(minutes=5), True), Check(self.start + timedelta(minutes=8), False)],
            self.start,
            self.start + timedelta(minutes=10),
        )
        self.assertEqual(report["downtime_seconds"], 300)
        self.assertEqual(report["availability_percent"], 50)

    def test_planned_maintenance_is_excluded_from_duration_and_downtime(self):
        maintenance = Interval(self.start + timedelta(minutes=2), self.start + timedelta(minutes=4))
        report = calculate_report(
            [Check(self.start, True), Check(self.start + timedelta(minutes=1), False), Check(self.start + timedelta(minutes=5), True)],
            self.start,
            self.start + timedelta(minutes=10),
            [maintenance],
        )
        self.assertEqual(report["eligible_duration_seconds"], 480)
        self.assertEqual(report["downtime_seconds"], 180)
        self.assertEqual(report["availability_percent"], 62.5)

    def test_timezone_is_required_for_maintenance_dates(self):
        with self.assertRaises(ValueError):
            parse_timestamp("2026-11-05T10:00:00")
        with self.assertRaises(ValueError):
            calculate_report([Check(datetime(2026, 11, 5, 10), True)], self.start, self.start + timedelta(minutes=1))

    def test_empty_sample_set_does_not_claim_full_availability(self):
        report = calculate_report([], self.start, self.start + timedelta(minutes=5))
        self.assertIsNone(report["availability_percent"])
        self.assertIsNone(report["uptime_seconds"])
        self.assertEqual(report["measurement_status"], "no samples; availability is undetermined")

    def test_monitor_writes_timestamped_checks_and_a_report(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as temporary:
            output = Path(temporary) / "evidence"
            sample = Check(datetime.now(timezone.utc), True, 200)
            with patch("nfr_tools.availability.check_url", return_value=sample), patch(
                "nfr_tools.availability.time.monotonic", side_effect=[0, 0, 2]
            ), patch("nfr_tools.availability.time.sleep"):
                report = run_monitor("https://inventory.example.test/", 1, 1, output, [])

            rows = [json.loads(line) for line in (output / "availability_checks.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(rows), 2)
            self.assertTrue(rows[0]["success"])
            self.assertEqual(rows[0]["timestamp"], sample.timestamp.isoformat())
            self.assertEqual(report["sample_count"], 2)
            self.assertTrue((output / "availability_report.json").is_file())

# Unit Test Report

Report revision: 1.1, prepared 11 November 2026. Team H9.
Recorded execution: 9 November 2026, Swara Potdar.
Tested application commit: `b1e3590fd85014ed06d8f0443a03fd04f20a5695`.
Environment: Windows, Python 3.11.9, Django 5.2.18, Coverage.py 7.17.2.
Document status: final submission, 11 November 2026.
Results and limitations below describe the available execution evidence.

The current application source at c8b3812 matches the recorded application source
(no differences under src/); this does not change the historical execution date.

## 1. Objective and classification

Verify individual calculation and timestamp-validation functions against explicit
expected outputs. This report identifies **7 existing pure-helper unit-test methods**
in `nfr_tools.test_availability.AvailabilityCalculationTests`. They call calculation
functions with synthetic inputs and do not require a live application server.

These seven tests passed as members of the recorded 158-test combined run.
A separate unit-only execution log has not yet been retained. The earlier assertion
of 52 isolated unit tests is withdrawn: no verified classification/log supports it.
This selection is not a claim that no other unit/component tests exist.

## 2. Test design and execution

The selected code tests successful/failed observation intervals, beginning/end
boundaries, planned-maintenance subtraction, missing samples and invalid timezones.
Inputs and assertions are executable in
[the source test file](../src/nfr_tools/test_availability.py).

| ID | Actual test method | Expected result verified by assertions | Result |
|---|---|---|---|
| U01 | `test_successful_checks_report_full_availability` | 100% for a fully successful synthetic window. | Passed within combined run |
| U02 | `test_failure_to_recovery_uses_conservative_previous_success_bound` | Conservative outage bounds produce 300 s downtime and 50% availability. | Passed within combined run |
| U03 | `test_first_failed_poll_counts_from_test_start` | Initial failure is counted from test start: 240 s downtime and 60% availability. | Passed within combined run |
| U04 | `test_last_failed_poll_counts_to_test_end` | Unrecovered final failure is counted to test end: 300 s downtime. | Passed within combined run |
| U05 | `test_planned_maintenance_is_excluded_from_duration_and_downtime` | Maintenance is excluded: 480 s eligible, 180 s downtime, 62.5% availability. | Passed within combined run |
| U06 | `test_timezone_is_required_for_maintenance_dates` | Naive timestamps raise ValueError. | Passed within combined run |
| U07 | `test_empty_sample_set_does_not_claim_full_availability` | No samples return undetermined availability, not 100%. | Passed within combined run |

## 3. Other component tests and exclusions

`inventory.tests.ComponentModelTests` checks stock-status calculation and string
representation. `inventory.test_constraints.ComponentDatabaseConstraintTests`
checks non-negative database constraints. `accounts.test_sr03_password_storage`
checks Django password-storage integration. These involve model/framework or database
facilities and should be described as component/database checks where applicable.

The monitor-writing test mocks networking but writes temporary files. View/client,
CRUD, report and audit-integration tests belong in the integration/system report;
they must not be relabelled as isolated units merely because they use TestCase.

## 4. Reproduce a dedicated unit run

From src with the project's environment active, run each selected label (one command):

```bat
python manage.py test nfr_tools.test_availability.AvailabilityCalculationTests.test_successful_checks_report_full_availability nfr_tools.test_availability.AvailabilityCalculationTests.test_failure_to_recovery_uses_conservative_previous_success_bound nfr_tools.test_availability.AvailabilityCalculationTests.test_first_failed_poll_counts_from_test_start nfr_tools.test_availability.AvailabilityCalculationTests.test_last_failed_poll_counts_to_test_end nfr_tools.test_availability.AvailabilityCalculationTests.test_planned_maintenance_is_excluded_from_duration_and_downtime nfr_tools.test_availability.AvailabilityCalculationTests.test_timezone_is_required_for_maintenance_dates nfr_tools.test_availability.AvailabilityCalculationTests.test_empty_sample_set_does_not_claim_full_availability --verbosity 2
```

Record the actual date, commit, runtime and output if executing now. Do not change
this report's historical results to a new date without retaining the new output.

## 5. Results, limitations and defects

The seven mapped assertions passed in the combined run. This is not proof of live
99% uptime: synthetic calculation correctness and measured service availability
are different claims. No new defect-discovery history is asserted in this report.
Use real issue/commit references for any future defect entries.

## 6. Evidence and conclusion

- [158-test execution evidence](evidence/tests_passed.png)
- [Recorded environment and commit](evidence/environment.txt)
- [Full requirement matrix](../Phase_3/Team_Test_Execution_Matrix.md)

Unit calculation evidence is available within the combined run. A dedicated log is
recommended for direct evaluator review. Final approval/marks are not claimed.

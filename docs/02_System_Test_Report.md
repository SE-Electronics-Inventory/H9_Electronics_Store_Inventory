# System Test and Validation Report

Report revision: 1.1, prepared 11 November 2026. Team H9.
Recorded execution: 9 November 2026, Swara Potdar.
Tested application commit: `b1e3590fd85014ed06d8f0443a03fd04f20a5695`.
Environment: Windows, Python 3.11.9, Django 5.2.18, Coverage.py 7.17.2.
Review status: corrected evidence report for team review; faculty approval is not claimed.

The current application source at c8b3812 matches the recorded application source
(no differences under src/); this does not change the historical execution date.

## 1. Scope and objective

Assess the implemented inventory workflows across authentication, roles, CRUD,
search, stock status, reporting, persistence and audit, with security and NFR checks.
Distinguish Django client integration tests from actual browser/system observations.
The 158-test run is a combined automated suite, not 158 manual end-to-end scenarios.

## 2. Environment, setup and execution

Django created an isolated test database and destroyed it after the run. Individual
tests construct their users, role groups and component data. Expected results and
assertions are defined in the mapped source files. Python paths in the tables are
relative to src/; Phase_2 paths are relative to the repository root.

```bat
cd src
python manage.py test inventory accounts reports audit nfr_tools --verbosity 2
```

Recorded combined outcome: **158 passed, no failures/errors reported**. A successful
suite does not automatically satisfy unexecuted manual acceptance steps.

## 3. Requirement-level results

The following matrix preserves the reviewed requirement IDs and qualifications.
Automated passed means the named assertions passed at the recorded baseline.

## Functional Requirements



| Requirement | Original test case | Automated test file / class | Recorded result and scope |
|---|---|---|---|
| FR-01 Authentication | TC-AUTH-01 | accounts/tests.py: LoginTests | Automated passed: valid login, invalid credentials and empty fields. |
| FR-02 Logout | TC-AUTH-02 | accounts/tests.py: LogoutSessionTests | Automated passed: session termination, protected-page access after logout and cache controls. |
| FR-03 Add component | TC-INV-01 | inventory/tests.py: ComponentAddAuthorizationTests | Automated passed: authorized creation, invalid input and access restrictions. |
| FR-04 View inventory | TC-INV-02 | inventory/tests.py: InventoryListViewTests | Automated passed: list contents, template and empty state. |
| FR-05 Search and filter | TC-SEARCH-01 | inventory/tests.py: SearchAndFilterTests | Automated passed: ID/name search, category filters, combined filters and no-match results. |
| FR-06 Edit component | TC-INV-03 | inventory/tests.py: ComponentEditViewTests | Automated passed: updates, duplicate-ID rejection and access restrictions. |
| FR-07 Delete/deactivate | TC-INV-04 | inventory/tests.py: ComponentDeleteAndDeactivateTests | Automated passed: confirmation, soft deactivation, cancellation and access restrictions. |
| FR-08 Availability display | TC-AVAIL-01 | inventory/test_availability_display.py; inventory/tests.py: ComponentModelTests | Automated passed: zero, below, equal to and above minimum-stock boundaries. |
| FR-09 Low-stock list | TC-LOW-01 | inventory/test_low_stock_list.py | Automated passed: threshold boundaries, empty state and updates after quantity changes. |
| FR-10 Dashboard | TC-DASH-01 | reports/tests.py: InventoryDashboardTests | Automated passed for implemented active-inventory metrics and role restrictions. Requirement/design wording reconciliation remains open. |
| FR-11 Reports | TC-REP-01 | reports/tests.py: InventoryReportTests | Automated passed: totals, filters, CSV headers/data and permissions. Implementation PR #109. |
| FR-12 Input validation | TC-VAL-01 | inventory/tests.py: InventoryPersistenceAndValidationTests; inventory/test_error_handling.py | Automated passed: required fields, duplicate IDs, negative/invalid values and preservation of existing data. |
| FR-13 Persistent storage | TC-DATA-01 | inventory/tests.py: InventoryPersistenceAndValidationTests | Automated passed: records saved and retrieved from the test database. Server-restart durability is not established by these assertions alone. |
| FR-14 Role authorization | TC-SEC-01; TC-SEC-02 | accounts/tests.py: RoleAuthorizationTests; accounts/test_sr02_role_escalation.py | Automated passed for tested role restrictions and unauthorized requests. |
| FR-15 Error handling | TC-ERR-01 | inventory/test_error_handling.py | Automated passed: selected friendly error pages, invalid operations and simulated database failures. |
| FR-16 Change tracking | TC-AUD-01 | audit/tests.py | Automated passed: change records, audit listing/filtering and permissions. Implementation PR #110. |



## Non-Functional Requirements



| Requirement | Original test case | Evidence / implementation | Recorded result and outstanding work |
|---|---|---|---|
| NFR-01 Performance | TC-PERF-01 | nfr_tools/test_inventory_performance.py; Phase_2/NFR01_Performance_Baseline.md | Automated passed. Swara's uninstrumented run: 50/50 requests below two seconds, overall p90 8.49 ms. Application-level timing only; excludes browser/network latency and concurrent load. |
| NFR-02 Scalability | TC-PERF-02 | inventory/test_scalability.py; Phase_2/NFR02_Scalability_Validation.md | Automated passed: operations with 1,000 records and seed-command idempotence. |
| NFR-03 Reliability | TC-REL-01 | inventory/test_transaction_reliability.py; PR #111 | Automated passed: successful transactions and rollback after simulated failures. |
| NFR-04 Availability | TC-REL-02 | nfr_tools/test_availability.py; PR #108 | Monitor tests passed. Actual agreed-duration availability measurement remains pending; 99% achievement is not established. Owner: Ahana. |
| NFR-05 Usability | TC-UX-01 | inventory/test_usability.py; PR #107 | Automated UI-response checks passed. Unassisted new-user session and participant feedback remain pending. Owner: Ahana. |
| NFR-06 Modularity | Code review | Phase_2/NFR06_Django_Modularity_Review.md | Repository contains a documented modularity review. This is review evidence, not a measured automated-test result. |
| NFR-07 Browser compatibility | TC-COMP-01 | inventory/test_browser_compatibility.py; Phase_2/NFR07_Browser_Compatibility_Report.md; PR #112 | Partial. User-Agent-based server checks passed. Shriya reports Chrome/Edge manual checks; exact versions and supporting records need confirmation. Actual Firefox testing remains pending. Owner: Shriya. |
| NFR-08 Recovery | TC-REC-01 | nfr_tools/test_database_recovery.py; PR #106 | Automated tests passed. PR documents successful isolated backup/restore, integrity checks and all 11 tables matching. Separate execution JSON has not been supplied for this review. |



## Security Requirements



| Requirement | Original test case | Automated test file | Recorded result and scope |
|---|---|---|---|
| SR-01 Protected pages | TC-SEC-01 | accounts/test_sr01_protected_pages.py | Automated passed: selected protected pages require authentication. |
| SR-02 Unauthorized operations | TC-SEC-02 | accounts/test_sr02_role_escalation.py | Automated passed: selected restricted requests are blocked without unauthorized data changes. |
| SR-03 Password storage | TC-SEC-03 | accounts/test_sr03_password_storage.py | Automated passed: password hashing and verification checks. |
| SR-04 CSRF protection | TC-SEC-04 | accounts/test_sr04_csrf.py | Automated passed: selected missing-token rejection and valid-token control requests. |
| SR-05 Input security | TC-SEC-05 | accounts/test_sr05_input_security.py | Automated passed for selected malicious inputs and invalid values. Not an exhaustive attack assessment. |
| SR-06 Secrets in logs | TC-SEC-06 | accounts/test_sr06_log_secrets.py | Automated passed: captured logs contained none of the tested secrets. This does not prove every authentication event is logged. |




## 4. Observed working-product scenarios

The supplied Sprint 2 recording (about 1:58) was visually reviewed through frames
sampled across the full recording. It demonstrates selected workflows, not all test
plan cases and not cross-browser acceptance.

| Approximate video time | Observed scenario | Observed outcome / limit |
|---|---|---|
| 00:00-00:17 | Manager login, dashboard, search, low-stock page | Pages load with relevant results. |
| 00:18-00:28 | Report filtering and CSV download | Filtered report and download visible; downloaded contents not opened. |
| 00:30-00:55 | Administrator login and add with invalid quantity | Error shown; corrected submission saved. |
| 01:00-01:09 | Edit component and audit history | Updated quantity and add/edit audit entries visible. |
| 01:13-01:18 | Confirm deactivation | Success message and active total reduced from 12 to 11. |
| 01:19-01:39 | Staff login and direct dashboard URL | Restricted navigation and access-denied response visible. |
| 01:47-01:49 | Nonexistent route | Friendly missing-page response visible. |

- [Sprint 1 video](../Phase_2/Sprint_1_Demo.mp4)
- [Sprint 2 video](../Phase_2/Sprint_2_Demo.mp4)

## 5. Outstanding acceptance work

| Item | Owner | Required closure evidence |
|---|---|---|
| Actual Firefox workflows; Chrome/Edge version and execution details | Shriya | Browser-specific results, exact versions and supporting captures/logs. |
| Agreed-duration availability | Ahana | Timestamped observations and availability report for full agreed window. |
| Unassisted usability | Ahana | Actual participant task outcomes and feedback. |
| Isolated recovery execution | Ahana | PR #106 documents success; retain JSON output if available. |
| Restart persistence and any remaining original manual steps | Team | Actual execution results or explicit reviewed deferral. |
| Planned security scan / testing-tool changes | Team | Execution evidence or reviewed change to STP approach. |
| Requirement/design deviations | Team / owner | Explicit decisions with reviewer/date/PR; no assumed approval. |

## 6. Defects and acceptance decision

Automated failures in the recorded run: zero. This does not establish that the issue
tracker contains zero open defects. No invented bug IDs, repairs or faculty sign-off
are included. Review real issues before freeze.

**Decision: automated regression passed; system acceptance remains partial/pending.**
The report exists for submission, but the outstanding checks must not be called passed.

## 7. Evidence

- [Execution screenshot](evidence/tests_passed.png)
- [Runtime and tested commit](evidence/environment.txt)
- [Coverage report](03_Code_and_Branch_Coverage_Report.md)
- [Validation update](../Phase_3/Validation_Spec_Update.md)
- [Recovery execution summary, PR #106](https://github.com/SE-Electronics-Inventory/H9_Electronics_Store_Inventory/pull/106)

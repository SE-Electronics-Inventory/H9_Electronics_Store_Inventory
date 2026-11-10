# Phase 3 - Team Test Execution Matrix



Prepared by: Swara Potdar

Evidence consolidation date: 10 November 2026

Status: Draft for team review



## Baseline and Interpretation



Automated execution date: 9 November 2026.

Tested commit: b1e3590fd85014ed06d8f0443a03fd04f20a5695

Environment: Windows, Python 3.11.9, Django 5.2.18.

Combined automated suite: 158 tests passed.



This matrix links original requirement and test-case IDs to implemented

checks and available evidence. It supplements the original test cases;

it does not claim that every original manual procedure was executed.



"Automated passed" means the mapped assertions passed within the

recorded suite. It does not establish unrestricted requirement acceptance.



Test paths below are relative to src/.

The mapped test code contains executable setup, inputs and assertions.

Full original procedures remain in the Phase 1 test-case document.



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



## Evidence References



- [Original test cases](../Phase_1/03_COMPLETE_TEST_CASES_15.pdf)

- [Test execution screenshot](Test_Evidence/tests_passed.png)

- [Environment and tested commit](Test_Evidence/environment.txt)

- [Test approach and coverage evidence](Test_Evidence/README.md)

- [Validation specification update](Validation_Spec_Update.md)

- [Swara's detailed security RTM](Swara_Security_RTM.md)

- [Implementation and design deviations](Swara_Implementation_Notes.md)

- [Recovery PR #106](https://github.com/SE-Electronics-Inventory/H9_Electronics_Store_Inventory/pull/106)

- [Usability PR #107](https://github.com/SE-Electronics-Inventory/H9_Electronics_Store_Inventory/pull/107)

- [Availability PR #108](https://github.com/SE-Electronics-Inventory/H9_Electronics_Store_Inventory/pull/108)

- [Reports PR #109](https://github.com/SE-Electronics-Inventory/H9_Electronics_Store_Inventory/pull/109)

- [Audit PR #110](https://github.com/SE-Electronics-Inventory/H9_Electronics_Store_Inventory/pull/110)

- [Reliability PR #111](https://github.com/SE-Electronics-Inventory/H9_Electronics_Store_Inventory/pull/111)

- [Compatibility PR #112](https://github.com/SE-Electronics-Inventory/H9_Electronics_Store_Inventory/pull/112)



Evidence dates differ between historical PR execution summaries and

Swara's combined regression run. They are separate executions.



## Remaining Acceptance and Review Actions



- Ahana: provide actual availability observations and the measurement report.

- Ahana: conduct and document the unassisted new-user usability session.

- Shriya: complete Firefox testing and clarify Chrome/Edge evidence.

- Shriya: correct the browser report so pending checks are not labelled passed.

- Team: reconcile dashboard metrics, role access and other documented design differences.

- Team: provide the planned security-scan evidence or review and document a change to the test approach.

- Team: reconcile other promised tools/procedures with actual execution.

- Team: map any remaining original manual steps to evidence or explicit pending status.

- Team: review open defects; no claim of zero outstanding defects is made here.

- Team: review this matrix and identify the final implementation baseline.



These rows map all 30 requirements; they do not mean all 30 are fully

accepted. Final review and outstanding validation remain pending.

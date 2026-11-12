# Phase 3 - Validation Specification Update



Project: Electronics Store Inventory Management System

Team: H9

Prepared by: Swara Potdar (PES1UG24CS487)

Date: 10 November 2026

Status: Draft for team review



## 1. Purpose and References



This document updates the validation approach and execution status

following implementation. It supplements the original submitted

documents without replacing their historical versions.



References:

- ../Phase_1/02_COMPLETE_IEEE_TEST_PLAN.pdf

- ../Phase_1/03_COMPLETE_TEST_CASES_15.pdf

- Test_Evidence/README.md

- Swara_Security_RTM.md

- Swara_Implementation_Notes.md



This is a Phase 3 update, not the final Phase 4 system-validation report.



## 2. Tested Version and Environment



Recorded local execution date: 9 November 2026.

Tested application commit:

b1e3590fd85014ed06d8f0443a03fd04f20a5695



Environment:

- Windows

- Python 3.11.9

- Django 5.2.18

- Coverage.py 7.17.2

- Separate database created and destroyed by the Django test runner



Evidence and documentation were subsequently merged into main.

The recorded local results apply to the tested commit above.



## 3. Validation Methodology



Unit tests exercise individual rules and helpers, including stock

availability, validation and supporting utility functions.



Integration tests exercise Django views, authentication, role checks,

forms, database operations, reports and audit behaviour.



Negative and boundary tests cover selected invalid values,

unauthorized requests and transaction-failure scenarios.



Regression testing runs the combined automated suite.

GitHub Actions now includes inventory, accounts, reports, audit

and nfr_tools on Python 3.12 and 3.13, following PR #116.



Real-browser, usability and controlled uptime validation require

separate execution evidence. Automated test-client responses alone

do not establish those results.



## 4. Automated Execution Results



Command run from src with the virtual environment active:



    python -m coverage run --branch --source=accounts,inventory,reports,audit,nfr_tools,esims manage.py test inventory accounts reports audit nfr_tools



Observed result:

- Tests executed: 158.

- Tests failed or errored: 0.

- Final test-runner status: OK.

- Django system checks: no issues reported.



Evidence:

- [Execution screenshot](Test_Evidence/tests_passed.png)

- [Environment and commit](Test_Evidence/environment.txt)



Passing the suite establishes the outcomes of its implemented

assertions. It does not automatically mark every planned manual

test or every requirement as fully validated.



## 5. Coverage



Coverage command:



    python -m coverage report -m --omit="*/tests.py,*/test_*.py,*/migrations/*"



Measured results:

- Statement coverage: 89%.

- Branch coverage: 78%.

- Combined coverage: 88%.



Scope includes accounts, inventory, reports, audit, nfr_tools and

esims. Test files and migrations are excluded from the report.



These are combined unit and integration coverage results.

They are not a separate unit-only coverage measurement.

No faculty-mandated minimum coverage percentage has been established

from the supplied deliverable instructions.



Uncovered areas include selected validation and exception paths,

role setup, seed commands, monitoring/recovery utilities and the

ASGI/WSGI entry points.



Evidence:

- [Coverage summary and missing lines](Test_Evidence/coverage_summary.txt)

- [Coverage screenshot](Test_Evidence/coverage_totals.png)



## 6. Security Validation Update



The following automated checks passed within the combined suite:



- SR-01: protected-page redirects and prevention of unauthenticated

  inventory access.

- SR-02: selected role restrictions and direct unauthorized

  add/edit/delete requests, with checks for unchanged data.

- SR-03: password hashing and verification.

- SR-04: CSRF tokens, selected missing-token rejection cases and

  a valid-token control request.

- SR-05: selected malicious inputs and invalid field values.

- SR-06: captured logs checked for the tested passwords and

  application secret key.



Detailed mappings:

[Swara's authentication and security RTM](Swara_Security_RTM.md)



These checks are not a comprehensive penetration test.

The planned security scan requires separate evidence or a documented

change to the original validation approach.



## 7. Requirement and Test-Case Traceability



The original requirement and test-case IDs remain authoritative.



Swara's RTM maps FR-01, FR-14 and SR-01 to SR-06 to implementation

files, stories, tests and original PRs.



The [Team Test Execution Matrix](Team_Test_Execution_Matrix.md)
maps all 30 requirements to automated checks, available evidence
and outstanding validation actions.

This establishes a consolidated mapping, not full acceptance of
every requirement. Team review and the listed pending checks
remain outstanding.



For each planned test case, record:

- Requirement ID and test-case ID.

- Preconditions, input and execution steps.

- Expected and actual result.

- Execution date, environment and tested commit.

- Evidence reference and any defect reference.

- Passed, Failed, Blocked or Not executed status.



Do not replace a pending status with Passed solely because its

GitHub issue was closed.



## 8. Non-Functional Validation Status



### Performance and scalability

Evidence:
- [Performance baseline](../Phase_2/NFR01_Performance_Baseline.md)
- [Scalability validation](../Phase_2/NFR02_Scalability_Validation.md)
- [Performance tests](../src/nfr_tools/test_inventory_performance.py)
- [Scalability tests](../src/inventory/test_scalability.py)

NFR-01 / TC-PERF-01:
Swara's recorded run without coverage on 9 November 2026 measured
50 requests across inventory list, search, add, edit and deactivate
operations. All 50 completed within two seconds; overall p90 was
8.49 ms. The performance test passed.

This measures Django test-client request processing, including views,
ORM and templates. It excludes browser rendering and network latency.
It does not establish concurrent-user load performance.

NFR-02 / TC-PERF-02:
The scalability tests exercise listing and searching with 1,000
component records, followed by adding, editing and deactivating a
component. Additional tests verify seed-command behaviour and
idempotence. These tests passed within the recorded 158-test suite.

The tested commit and local environment are recorded in Section 2.
Simret's separately documented baseline has its own date, runtime
and timings; it must not be combined with Swara's measurement.

Status: automated application-level performance and 1,000-record
scalability checks passed within the stated scope.


### Availability



The monitoring tool and its automated tests exist.

The previously reviewed availability document requires a completed

controlled measurement and retained observations.



Team action: provide the actual measurement window and report.

Until reviewed, the 99% availability target is not established here.



### Usability

Swara reports P01, a first-time non-developer user, completed sign-in, search, restocking interpretation and sign-out without task-specific help on 11 November 2026. Feedback: "very easy to understand and use". Scoped four-task session; [execution record](../docs/evidence/usability/README.md).

The facilitator supplied project-purpose context only. P01 identified stock of 5
and correctly concluded restocking was needed against the existing minimum of 10.
This record supports the listed tasks for this participant, not general population
or completion-time claims.

### Browser compatibility

The browser report and automated checks are linked to PR #112:
https://github.com/SE-Electronics-Inventory/H9_Electronics_Store_Inventory/pull/112

Shriya reports manual Chrome and Edge testing on Windows 11 on
8 November 2026. Exact installed browser versions and supporting
browser-specific execution records remain to be confirmed.

The Sprint 2 recording demonstrates working application workflows.
It does not independently establish compatibility across all three
required browsers.

The automated tests use Django's test client with Chrome, Edge and
Firefox User-Agent strings. They check selected server responses,
HTML content and CSV headers; they do not launch browser engines
or verify visual rendering.

Firefox 147.0.3 on Ubuntu/Linux in VMware: Swara completed login, empty inventory, add, matching/nonmatching search, low-stock display, CSV export and logout/protected-access checks on 11 November 2026.
[Completed Firefox checks](../docs/evidence/firefox/README.md).

Status: partially validated. NFR-07 / TC-COMP-01 must not yet be
recorded as fully passed.

Follow-up owner: Shriya.
Supply exact Chrome/Edge versions and browser-specific records. Firefox results
are recorded for the workflows listed in the linked execution evidence.


### Backup and recovery
Recovery tooling and automated tests exist.

PR #106 documents a successful backup and isolated restore verification
using a disposable migrated Django database. Backup and restored-database
integrity checks passed, all 11 tables matched, and seeded inventory
values were unchanged. The active application database was not used.

Evidence source:
https://github.com/SE-Electronics-Inventory/H9_Electronics_Store_Inventory/pull/106

Status: isolated recovery execution documented in the PR.
The automated recovery tests also passed within the recorded 158-test suite.

The PR execution summary is available; a separate JSON execution report
has not been supplied for this review.



### Modularity and transaction reliability



The repository contains a modularity review and automated transaction

reliability tests. The reliability tests passed in the combined run.

Link these to their requirement/test-case rows in the consolidated RTM.



## 9. Design Changes Affecting Validation



See [Implementation notes](Swara_Implementation_Notes.md).



The team must reconcile:

- Actual login/logout routes and login redirect.

- Dashboard role-access policy.

- Authentication-event logging expectations.

- Active-only dashboard totals versus ambiguous requirement wording.



Any accepted requirement/design change must be reflected in the

corresponding expected results and traceability.



## 10. Completion Criteria



Before declaring Phase 3 validation documentation complete:

- Complete the team requirement-to-test mappings.

- Record actual results and evidence for executed planned tests.

- Identify remaining unexecuted or blocked checks explicitly.

- Review relevant design deviations and update expected behaviour.

- Review defects and unresolved validation risks.

- Link sprint videos and identify the final implementation version.



If a planned check is deferred to Phase 4, record its owner,

reason and intended execution point. Deferral is not a Passed result.



# Phase 3 - Swara: Authentication and Security RTM

Owner: Swara Potdar (PES1UG24CS487)

Validation date: 9 November 2026

Tested commit: b1e3590fd85014ed06d8f0443a03fd04f20a5695

## Scope

This matrix covers Swara's requirements: FR-01, FR-14 and SR-01 to SR-06.

It is a partial project RTM; other team members' requirements need separate mapping.

All file paths below are relative to the repository root.

PR numbers identify the implementation/test PRs recorded in the project history.

## Requirements Traceability

| Requirement | Requirement issue | User stories | Implementation / control | Automated tests | Test case | Original PR |
|---|---|---|---|---|---|---|
| FR-01 / ESIM-F-001: User authentication | #1 | #34, #35, #36 | src/accounts/urls.py; src/templates/accounts/login.html; src/esims/settings.py | src/accounts/tests.py | TC-AUTH-01 | #93 |
| FR-14 / ESIM-F-014: Role-based authorization | #16 | #37, #38, #39 | src/accounts/roles.py; role checks in inventory, reports and audit views; src/templates/403.html | src/accounts/tests.py; src/accounts/test_sr02_role_escalation.py | TC-SEC-01; TC-SEC-02 | #94 |
| SR-01 / ESIM-SR-001: Protected-page authentication | #27 | #40 | LoginRequiredMiddleware in src/esims/settings.py | src/accounts/test_sr01_protected_pages.py | TC-SEC-01 | #95 |
| SR-02 / ESIM-SR-002: Prevent unauthorized operations | #28 | #41, #42 | src/accounts/roles.py; server-side role checks on restricted views | src/accounts/test_sr02_role_escalation.py | TC-SEC-02 | #96 |
| SR-03 / ESIM-SR-003: Secure password storage | #29 | #43 | Django password hashing; create_user/set_password usage | src/accounts/test_sr03_password_storage.py | TC-SEC-03 | #97 |
| SR-04 / ESIM-SR-004: CSRF protection | #30 | #44 | CsrfViewMiddleware; CSRF tokens in forms | src/accounts/test_sr04_csrf.py | TC-SEC-04 | #98 |
| SR-05 / ESIM-SR-005: Server-side input security | #31 | #45, #46 | src/inventory/forms.py; Django ORM; template escaping | src/accounts/test_sr05_input_security.py | TC-SEC-05 | #99 |
| SR-06 / ESIM-SR-006: No secrets in application logs | #32 | #47 | Logging behaviour during authentication and denied-access requests | src/accounts/test_sr06_log_secrets.py | TC-SEC-06 | #100 |

## Observed Results

All automated tests in the files mapped above passed as part of the

158-test combined suite executed locally on the tested commit.

Checks covered:

- Valid and invalid login, session creation and protected-page access.

- Role restrictions and direct unauthorized POST requests.

- Password hashing and password verification.

- CSRF rejection and a valid-token control request.

- Selected malicious inputs and invalid field values.

- Captured logs containing no tested passwords or application secret key.

"Passed" describes the automated scenarios executed. It does not mean

every possible attack, input or deployment configuration was tested.

## Evidence

- [Test execution screenshot](Test_Evidence/tests_passed.png)

- [Coverage summary](Test_Evidence/coverage_summary.txt)

- [Coverage screenshot](Test_Evidence/coverage_totals.png)

- [Environment and tested commit](Test_Evidence/environment.txt)

- [Test approach and limitations](Test_Evidence/README.md)

Evidence submission PR: #115.

Expanded CI test-command PR: #116.

The reported 88% combined coverage applies to the selected project

packages, not only to Swara's code.

## Limitations and Follow-up

- This document does not replace the full project RTM.

- Automated security checks are not a complete penetration test.

- Real-browser checks, usability testing and controlled uptime

  measurement require their own evidence.

- Revalidate affected requirements after relevant code changes.


# Software Test Plan Revision 1.1

Team H9. Prepared 11 November 2026. Status: revised execution approach for team review.
Read with the [complete STP](../Phase_1/02_Software_Test_Plan_STP.pdf), retaining its
introduction, sections 3/4/5, security section 5.1, environment, schedule, roles,
risks, suspension/resumption and approvals. The older short extract is historical.
This revision does not backdate execution or sign-off.

## 1. Scope and test items

Retain all 30 original requirements and original test IDs. Test accounts, inventory,
reports, audit, project-level handlers and nfr_tools. Out-of-scope purchasing,
payments and accounting remain excluded.

## 2. Test levels and method changes

| Level/type | Actual evidence | Original-plan difference / remaining action |
|---|---|---|
| Unit | Seven explicitly identified pure calculation/helper tests in unit report. | Dedicated log can be produced; unsupported 52-unit count removed. |
| Component/integration | Django TestCase/client suite with test database. | Do not call all 158 cases isolated unit or browser-system tests. |
| Browser/system | Selected sprint workflows visible; manual browser claims qualified. | Original Selenium/manual approach needs actual browser results or reviewed method change. |
| Performance | Django-client 50-request measurements. | Does not replace concurrent-load Locust/JMeter evidence automatically; review intended load and method. |
| Security | Six SR test files, strict CSRF client and negative requests. | Original OWASP ZAP scan remains pending unless performed or formally revised. |
| Availability | Calculation/monitor tests only. | Agreed full measurement window still required. |
| Usability | Automated feedback checks only. | Unassisted participant session still required. |
| Recovery | Automated tests and PR #106 isolated execution summary. | Retain raw JSON if available. |

## 3. Updated cases and expected outcomes

[Team matrix](../Phase_3/Team_Test_Execution_Matrix.md) maps all requirements to source
and results. Preserve the original PDFs as baseline, but use current route names,
active-only metrics, soft-deactivation and implemented role behaviour when recording
actual results. Where original expectations disagree, mark the decision pending;
do not silently redefine the expected outcome to make a failing requirement pass.
Each additional execution needs input/steps, expected/actual result, date, environment,
commit, tester, evidence reference and defect reference when relevant.

## 4. Security validation (supplements STP 5.1)

Authentication redirect/data leakage; unauthorized GET/direct POST with unchanged
DB; salted password storage; missing CSRF rejection plus valid-token control;
selected SQL/XSS-style inputs and invalid values; absence of tested secrets in
captured logs. These are targeted checks, not comprehensive penetration testing.
An active security scan must use the authorized isolated project test environment.

## 5. Results and reporting

The 9 November run at b1e3590 passed 158 combined tests. Record its environment from
[evidence/environment.txt](evidence/environment.txt). Coverage: 89% statement,
78% branch, 88% combined; no supplied faculty minimum threshold is asserted.
Reports are physically in docs/:

- [Unit Test Report](01_Unit_Test_Report.md)
- [System Test Report](02_System_Test_Report.md)
- [Code and Branch Coverage Report](03_Code_and_Branch_Coverage_Report.md)

## 6. Entry, exit, defects and approval

Retain original entry/exit criteria. Full acceptance is not achieved merely by a
passing regression run: planned cases need results, high-priority failures need
resolution and requirement deviations need review. Deferred cases remain pending,
with owner/reason/target. Review actual issue records before claiming zero defects.

Team review: pending. Faculty approval: not recorded. Development freeze must identify
an agreed implementation commit/date; do not declare a freeze on behalf of the team.

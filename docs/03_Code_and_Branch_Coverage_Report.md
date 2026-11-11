# Code and Branch Coverage Report

Report revision: 1.1, prepared 11 November 2026. Team H9.
Recorded execution: 9 November 2026, Swara Potdar.
Tested application commit: `b1e3590fd85014ed06d8f0443a03fd04f20a5695`.
Environment: Windows, Python 3.11.9, Django 5.2.18, Coverage.py 7.17.2.
Review status: corrected evidence report for team review; faculty approval is not claimed.

The current application source at c8b3812 matches the recorded application source
(no differences under src/); this does not change the historical execution date.

## 1. Measurement and result

| Measure | Recorded result | Interpretation |
|---|---|---|
| Statement coverage | 89% | 590 of 661 executable statements covered; 71 missed. |
| Branch coverage | 78% | Percentage shown in the recorded HTML totals screenshot. |
| Combined coverage | 88% | Coverage.py combines statement and branch opportunities; not a simple average. |
| Branch opportunities | 124 | Reported Branch total. |
| Partial branches | 19 | Reported BrPart total; not the total number of missing branch destinations. |
| Tests | 158 passed | Combined unit/component/integration suite. |

No 80%/70%/75% faculty threshold was established in the supplied instructions.
The prior claims of exceeding those thresholds and earning full marks are withdrawn.
No faculty review or sign-off is asserted.

## 2. Reproduction and scope

From src, with the project environment and coverage installed:

```bat
python -m coverage run --branch --source=accounts,inventory,reports,audit,nfr_tools,esims manage.py test inventory accounts reports audit nfr_tools
python -m coverage report -m --omit="*/tests.py,*/test_*.py,*/migrations/*"
python -m coverage html --omit="*/tests.py,*/test_*.py,*/migrations/*" -d ../docs/evidence/htmlcov
```

The report includes the six selected packages, configuration, management commands
and monitoring/recovery utilities. Tests and migration files are omitted from
reporting. Migrations can contain meaningful logic; omission is a declared scope
choice, not proof that they do not need validation. Templates, browser rendering,
network load and production deployment correctness are not measured by these totals.

## 3. Exact recorded file-level results

```text
Name                                                Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------------------------------
accounts\__init__.py                                    0      0      0      0   100%
accounts\admin.py                                       1      0      0      0   100%
accounts\apps.py                                        9      0      0      0   100%
accounts\context_processors.py                          4      0      0      0   100%
accounts\management\__init__.py                         0      0      0      0   100%
accounts\management\commands\__init__.py                0      0      0      0   100%
accounts\management\commands\create_demo_users.py      18      0      2      0   100%
accounts\models.py                                      1      0      0      0   100%
accounts\roles.py                                      39      0     12      1    98%   56->51
accounts\urls.py                                        5      0      0      0   100%
accounts\views.py                                       7      0      0      0   100%
audit\__init__.py                                       0      0      0      0   100%
audit\admin.py                                         12      2      0      0    83%   16, 19
audit\apps.py                                           3      0      0      0   100%
audit\models.py                                        22      0      0      0   100%
audit\urls.py                                           4      0      0      0   100%
audit\views.py                                         18      0      4      0   100%
esims\__init__.py                                       0      0      0      0   100%
esims\asgi.py                                           4      4      0      0     0%   10-16
esims\settings.py                                      27      0      0      0   100%
esims\urls.py                                           6      0      0      0   100%
esims\views.py                                          5      0      0      0   100%
esims\wsgi.py                                           4      4      0      0     0%   10-16
inventory\__init__.py                                   0      0      0      0   100%
inventory\admin.py                                      8      0      0      0   100%
inventory\apps.py                                       3      0      0      0   100%
inventory\forms.py                                     17      2      4      2    81%   30, 36
inventory\management\__init__.py                        0      0      0      0   100%
inventory\management\commands\__init__.py               0      0      0      0   100%
inventory\management\commands\seed_components.py       36      3     14      3    88%   143, 148, 150
inventory\models.py                                    32      0      4      0   100%
inventory\urls.py                                       4      0      0      0   100%
inventory\views.py                                     80      3     16      0    97%   36-38
nfr_tools\__init__.py                                   0      0      0      0   100%
nfr_tools\availability.py                             127     37     34      8    70%   32, 34, 41, 45-51, 55-64, 76, 96, 114->107, 142, 167-179, 183
nfr_tools\database_recovery.py                        104     16     22      5    80%   19, 27, 43, 45-48, 81-82, 121-124, 141-142, 148
reports\__init__.py                                     0      0      0      0   100%
reports\admin.py                                        1      0      0      0   100%
reports\apps.py                                         3      0      0      0   100%
reports\models.py                                       1      0      0      0   100%
reports\urls.py                                         4      0      0      0   100%
reports\views.py                                       52      0     12      0   100%
-----------------------------------------------------------------------------------------------
TOTAL                                                 661     71    124     19    88%
```

## 4. Analysis and priorities

| Area | Evidence-based interpretation | Follow-up |
|---|---|---|
| accounts/roles.py: 98%, branch 56->51 | The false path of the permission-found condition is not fully exercised. | Consider meaningful missing-permission handling tests if required. |
| inventory/forms.py: 81%, lines 30 and 36 | Explicit empty-ID and empty-name ValidationError statements were not reached. | Review whether field validation rejects those values before custom cleaners. |
| inventory/views.py: 97% | Three statements were missed in the recorded report. | Inspect the baseline lines before assigning a cause; do not invent a defect history. |
| audit/admin.py: 83% | Two admin display/helper statements missed. | Exercise relevant admin behaviour if in acceptance scope. |
| availability utility: 70%; recovery utility: 80% | Multiple input/error/CLI paths remain uncovered. | Prioritize error and data-safety paths based on risk. |
| ASGI and WSGI entry points: 0% | Recorded tests did not execute these entry modules. | Separate deployment smoke testing is needed for a deployed server. |

Not every core source file is 97-100% covered: forms and audit admin are clear
counterexamples. Uncovered lines are not automatically defects, but they are not
automatically harmless either.

## 5. Stock-rule branch example

The actual property is `Component.availability`: quantity <= 0 gives Out of Stock;
otherwise quantity <= minimum_stock gives Low Stock; otherwise In Stock.
`inventory.tests.ComponentModelTests.test_availability_calculation_rules` exercises
boundary values. This is a concrete example of why alternative decision paths matter.

## 6. Conclusion and artifacts

The recorded run achieved 89% statement, 78% branch and 88% combined coverage.
These are combined-suite metrics, not separate unit-only coverage and not a guarantee
that all requirements or attacks have been tested.

- [Exact summary](evidence/coverage_summary.txt)
- [Coverage totals screenshot](evidence/coverage_totals.png)
- [HTML report](evidence/htmlcov/index.html) - download and open locally.
- [Execution screenshot](evidence/tests_passed.png)
- [Environment](evidence/environment.txt)

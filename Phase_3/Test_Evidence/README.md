# Phase 3 - Automated Test and Coverage Evidence



Executed by: Swara Potdar (PES1UG24CS487)

Date: 9 November 2026

Commit tested: b1e3590fd85014ed06d8f0443a03fd04f20a5695



## Environment

- Windows

- Python 3.11.9

- Django 5.2.18

- Coverage.py 7.17.2



## Results

- 158 automated tests passed.

- Statement coverage: 89%.

- Branch coverage: 78%.

- Combined coverage: 88%.



The suite includes unit and integration tests. These percentages

describe the combined suite, not unit tests alone.



## Reproduce

Run from src with the project's virtual environment active:



python -m coverage run --branch --source=accounts,inventory,reports,audit,nfr_tools,esims manage.py test inventory accounts reports audit nfr_tools



python -m coverage report -m --omit="*/tests.py,*/test_*.py,*/migrations/*"



Test files and migrations are excluded from the reported coverage.



## Evidence

- tests_passed.png: successful test execution.

- coverage_summary.txt: coverage totals and missing lines.

- coverage_totals.png: coverage summary screenshot.

- [Restored HTML coverage report](../../docs/evidence/htmlcov/index.html): historical interactive coverage report.

- environment.txt: runtime versions and tested commit.



## Remaining gaps

Some paths in form validation, error handling, role setup,

seed commands, availability monitoring and database recovery

were not exercised. ASGI and WSGI entry points were not exercised.



Passing tests and coverage do not establish completion of

real-browser, new-user usability or controlled uptime validation.

Those require separate execution evidence.

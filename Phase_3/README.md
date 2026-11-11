# Phase 3: Testing & Quality Assurance

**Course:** Software Engineering (UE24CS351A) — 5th Semester B.Tech CSE  
**Institution:** PES University, Bengaluru  
**Project:** Electronics Store Inventory Management System (ESIMS)  
**Team ID:** H9  
**Evaluation:** Deliverables Part-3 (10 Marks Total)  

---

## Deliverables Part-3 (10 Marks) — Faculty Submission Index

This folder contains the complete, formal deliverables for **Part-3 Evaluation (10 Marks)** as per the course rubric:

| Deliverable Name | Marks Allocated | Primary Artifact File | Status | Description |
|:---|:---:|:---|:---:|:---|
| **1. Unit Test Report** | **4 Marks** | [`01_Unit_Test_Report.md`](01_Unit_Test_Report.md) | **COMPLETE (100% Pass)** | Comprehensive report on all 52 isolated unit tests covering data models, database constraints, form validation, role decorators, context processors, availability algorithms, and security units. Includes Equivalence Partitioning and Boundary Value Analysis. |
| **2. System Test Report** | **3 Marks** | [`02_System_Test_Report.md`](02_System_Test_Report.md) | **COMPLETE (100% Pass)** | End-to-end integration and system test report covering all 16 Functional Requirements (FR-01 to FR-16), all 8 Non-Functional Requirements (NFR-01 to NFR-08: performance, scalability, reliability, availability, usability, modularity, compatibility, recovery), and 6 Security Requirements (SR-01 to SR-06). |
| **3. Code & Branch Coverage Report** | **3 Marks** | [`03_Code_and_Branch_Coverage_Report.md`](03_Code_and_Branch_Coverage_Report.md) | **COMPLETE (Exceeds Target)** | Granular analysis of code and branch coverage measured using `Coverage.py 7.17.2`. Details statement coverage (**89% vs 80% target**), branch coverage (**78% vs 70% target**), combined coverage (**88%**), module breakdowns, and deep-dive justifications for all uncovered lines/branches. |
| **Total Evaluation** | **10 Marks** | — | **COMPLIANT** | **All 3 deliverables complete, formatted, and verified.** |

---

## Supporting Test Evidence and Traceability Artifacts

In addition to the three core deliverable reports, this directory houses extensive empirical evidence and traceability documentation:

* **Automated Test Evidence Directory:** [`Test_Evidence/`](Test_Evidence/README.md)
  * [`Test_Evidence/tests_passed.png`](Test_Evidence/tests_passed.png): Terminal screenshot verifying all 158 automated tests passing.
  * [`Test_Evidence/coverage_totals.png`](Test_Evidence/coverage_totals.png): Terminal screenshot of final coverage percentages (89% statement, 78% branch).
  * [`Test_Evidence/coverage_summary.txt`](Test_Evidence/coverage_summary.txt): Machine-generated tabular coverage log with missing line references.
  * [`Test_Evidence/htmlcov/index.html`](Test_Evidence/htmlcov/index.html): Interactive HTML coverage browser.
  * [`Test_Evidence/environment.txt`](Test_Evidence/environment.txt): Tested environment versions (Python 3.11/3.13, Django 5.2/6.1, Windows, commit `b1e3590fd85014ed06d8f0443a03fd04f20a5695`).
* **Requirements Traceability Matrix (RTM):** [`Team_Test_Execution_Matrix.md`](Team_Test_Execution_Matrix.md)
  * Comprehensive matrix linking all 30 requirements (FR-01..16, NFR-01..08, SR-01..06) to test files and automated results.
* **Validation Specification Update:** [`Validation_Spec_Update.md`](Validation_Spec_Update.md)
  * Detailed update reconciling Phase 1 test cases with implemented test cases.
* **Security & Implementation Notes:**
  * [`Swara_Security_RTM.md`](Swara_Security_RTM.md): Detailed traceability for authentication and security requirements.
  * [`Swara_Implementation_Notes.md`](Swara_Implementation_Notes.md): Architectural and implementation deviation notes.

---

## How to Reproduce Test Execution & Coverage

From the repository root:

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Navigate to source directory
cd src

# 3. Run complete test suite (158 tests)
python manage.py test

# 4. Run test suite with branch coverage instrumentation
python -m coverage run --branch --source=accounts,inventory,reports,audit,nfr_tools,esims manage.py test inventory accounts reports audit nfr_tools

# 5. Display coverage report
python -m coverage report -m --omit="*/tests.py,*/test_*.py,*/migrations/*"
```

# SRS Revision 1.1 - Implementation Alignment

Team H9. Revision prepared 11 November 2026. Status: proposed revision for team review.
This document and the linked original SRS together form the proposed revision 1.1
specification. Original sections/diagrams remain authoritative except the explicit
proposed changes below. This is not a claim of faculty-approved requirements changes.

## 1. Purpose, scope and original baseline

[Original IEEE-style SRS](../Phase_1/01_COMPLETE_SRS_IEEE_STYLE.pdf) retains the
introduction, descriptive sections, feasibility, requirements, use-case diagrams,
security objectives, RTM and exclusions. The product remains an electronics inventory
system, excluding purchasing/payments/accounting and forecasting.

## 2. Actors and proposed permission clarification

Three operational roles: Inventory Administrator, Store Staff and Store Manager.
QA/Evaluator is an external validation actor, not a fourth application access group.

| Action | Administrator | Staff | Manager |
|---|---|---|---|
| Inventory, search and low stock | Allow | Allow | Allow |
| Add, edit, deactivate | Allow | Deny | Deny |
| Dashboard and reports/CSV | Allow | Deny | Allow |
| Inventory audit history | Allow | Deny | Deny |

This table describes implemented behaviour. Team review must explicitly reconcile
original wording that granted Staff reports or broader dashboard access. A group
assignment does not automatically confer Django admin-site is_staff status.

## 3. Proposed requirement clarifications

| Requirement | Implemented behaviour / proposed wording | Review consequence |
|---|---|---|
| FR-01/02 | Login/logout routes are /accounts/login/ and /accounts/logout/; default post-login destination is /inventory/. | Update related expected results; successful login may honour a permitted next destination. |
| FR-07 | Confirmed deletion is soft deactivation; active lists exclude it. | Preserve data/audit history. |
| FR-08/09 | Quantity 0: Out of Stock; 0 < quantity <= minimum: Low Stock; above minimum: In Stock. Low-stock list includes zero. | Boundary results must use <=. |
| FR-10 | Dashboard totals reflect active records; stock units sum their quantities; low-stock count includes zero-stock items. | Team must resolve any ambiguous original total definitions. |
| FR-11/14 | Reports and CSV available to Administrator/Manager; audit and mutations are Administrator-only. | Role-policy approval remains pending. |
| FR-13 | Database write/read assertions pass; server-restart persistence needs separate evidence. | Do not claim restart test executed. |
| SR-06 | Selected captured logs omit tested secrets. | This does not prove every login event is audited. |

## 4. NFR acceptance criteria remain in force

Retain the original two-second/90% performance target, at least 1,000 records,
transaction reliability, agreed-window availability, unassisted usability,
modularity, actual Chrome/Edge/Firefox compatibility and backup/recovery criteria.
Do not weaken a target simply because evidence is pending. Test-client timings
measure application processing, not network/rendering/concurrency performance.

## 5. Traceability and approval

All 16 FRs, 8 NFRs and 6 SRs retain their IDs. See the
[30-requirement matrix](../Phase_3/Team_Test_Execution_Matrix.md) and
[system report](02_System_Test_Report.md) for evidence and outstanding acceptance.

Team/owner review: pending. Faculty approval: not recorded.
Record decision, reviewer, date and PR for each policy change before declaring the
revised requirements accepted. If rejected, adjust implementation and rerun affected tests.

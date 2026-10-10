# Phase 2 – Subtasks by Epic and Story

Each story in the Jira backlog (project SEGP) is broken into small subtasks. The last subtask of each story is a test step linked to its Phase 1 test case (TC-xx).

**Total:** 6 epics · 30 stories · 84 subtasks

---

## EPIC 1 — User Authentication and Access Control

| Story | Subtask | What to do |
|-------|---------|------------|
| SEGP-1: User login | SEGP-37 | Make the login page |
| | SEGP-38 | Write the login logic using Django's built-in login |
| | SEGP-39 | Block inventory pages for users who are not logged in |
| | SEGP-40 | Test correct and wrong logins (TC-AUTH-01) |
| SEGP-2: Logout and session | SEGP-41 | Add a Logout button and logout logic |
| | SEGP-42 | End the session fully so old pages can't be reopened |
| | SEGP-43 | Test logout and the browser Back button (TC-AUTH-02) |
| SEGP-14: Role-based access | SEGP-81 | Create user roles: Admin, Staff, Manager |
| | SEGP-82 | Check the user's role before add, edit, delete and user management |
| | SEGP-83 | Show an "access denied" message when blocked |
| | SEGP-84 | Test that each role can only do what it is allowed to (TC-SEC-01) |
| SEGP-25: Protected-page access (SR-01) | SEGP-109 | Try opening protected pages without logging in |
| | SEGP-110 | Write down the results (TC-SEC-01) |
| SEGP-26: Privilege escalation (SR-02) | SEGP-111 | Try restricted actions using Staff and Manager accounts |
| | SEGP-112 | Try sending restricted requests directly (TC-SEC-02) |
| SEGP-27: Password storage (SR-03) | SEGP-113 | Check that passwords are not saved as plain text |
| | SEGP-114 | Check Django's password hashing settings (TC-SEC-03) |
| SEGP-28: CSRF protection (SR-04) | SEGP-115 | Check every form has a CSRF token |
| | SEGP-116 | Test that a fake request without a token is rejected (TC-SEC-04) |
| SEGP-29: Server-side input security (SR-05) | SEGP-117 | Try harmful inputs, like SQL-injection text |
| | SEGP-118 | Check the server rejects bad input before saving (TC-SEC-05) |
| SEGP-30: Logs have no secrets (SR-06) | SEGP-119 | Review the logging settings |
| | SEGP-120 | Check logs after login, logout and failed login (TC-SEC-06) |

## EPIC 2 — Component Inventory Management

| Story | Subtask | What to do |
|-------|---------|------------|
| SEGP-3: Add component | SEGP-44 | Create the Component table (ID, name, category, description, price, quantity, minimum stock) |
| | SEGP-45 | Make the Add Component form and page |
| | SEGP-46 | Allow only permitted users to add components |
| | SEGP-47 | Test adding a component (TC-INV-01) |
| SEGP-4: View inventory | SEGP-48 | Make the inventory list page |
| | SEGP-49 | Show each component's details and availability |
| | SEGP-50 | Test that the list matches the database (TC-INV-02) |
| SEGP-6: Update component | SEGP-55 | Make the Edit Component form and page |
| | SEGP-56 | Stop duplicate component IDs when editing |
| | SEGP-57 | Test that edits are saved correctly (TC-INV-03) |
| SEGP-7: Delete / deactivate | SEGP-58 | Ask for confirmation before deleting |
| | SEGP-59 | Add delete and deactivate options |
| | SEGP-60 | Allow only permitted users to delete |
| | SEGP-61 | Test delete and deactivate (TC-INV-04) |
| SEGP-12: Input validation | SEGP-76 | Add checks: required fields, unique ID, no negative quantity, valid price |
| | SEGP-77 | Show a clear error next to the wrong field |
| | SEGP-78 | Test that wrong input is rejected (TC-VAL-01) |
| SEGP-13: Save data permanently | SEGP-79 | Set up the database (SQLite) and migrations |
| | SEGP-80 | Test that data stays after logout and server restart (TC-DATA-01) |

## EPIC 3 — Inventory Search and Stock Monitoring

| Story | Subtask | What to do |
|-------|---------|------------|
| SEGP-5: Search and filter | SEGP-51 | Add search by component ID and name |
| | SEGP-52 | Add a category filter |
| | SEGP-53 | Show "No components found" when nothing matches |
| | SEGP-54 | Test search and filter results (TC-SEARCH-01) |
| SEGP-8: Availability status | SEGP-62 | Work out availability from quantity and minimum stock |
| | SEGP-63 | Show the availability status in the list |
| | SEGP-64 | Test quantities below, equal to and above the minimum (TC-AVAIL-01) |
| SEGP-9: Low-stock items | SEGP-65 | Find components at or below minimum stock |
| | SEGP-66 | Make a low-stock items page |
| | SEGP-67 | Test that all low-stock items are found (TC-LOW-01) |

## EPIC 4 — Inventory Dashboard and Reporting

| Story | Subtask | What to do |
|-------|---------|------------|
| SEGP-10: Dashboard | SEGP-68 | Count total components, available stock and low-stock items |
| | SEGP-69 | Make the dashboard page |
| | SEGP-70 | Highlight low-stock items on the dashboard |
| | SEGP-71 | Test that dashboard numbers match the database (TC-DASH-01) |
| SEGP-11: Reports | SEGP-72 | Make the report page |
| | SEGP-73 | Add report filters (category, availability) |
| | SEGP-74 | Let users download the report as CSV |
| | SEGP-75 | Test that report values match the database (TC-REP-01) |

## EPIC 5 — Error Handling and Audit Trail

| Story | Subtask | What to do |
|-------|---------|------------|
| SEGP-15: Error messages | SEGP-85 | Make friendly error pages (404 and 500) |
| | SEGP-86 | Show simple success and error messages to users |
| | SEGP-87 | Test that errors don't damage saved data (TC-ERR-01) |
| SEGP-16: Change tracking | SEGP-88 | Create a ChangeLog table (item, action, time) |
| | SEGP-89 | Save a record for every add, edit and delete |
| | SEGP-90 | Make a change history page for the admin |
| | SEGP-91 | Test that change records are saved (TC-AUD-01) |

## EPIC 6 — System Quality and Reliability

| Story | Subtask | What to do |
|-------|---------|------------|
| SEGP-17: Speed (NFR-01) | SEGP-92 | Write a speed test for list, search, add, edit and delete |
| | SEGP-93 | Run the test and record response times (TC-PERF-01) |
| | SEGP-94 | Speed up slow parts if needed |
| SEGP-18: Large data (NFR-02) | SEGP-95 | Fill the test database with 1,000+ components |
| | SEGP-96 | Check everything still works at this size (TC-PERF-02) |
| SEGP-19: Safe updates (NFR-03) | SEGP-97 | Save each update fully or not at all (database transactions) |
| | SEGP-98 | Test that a failed update leaves data unchanged (TC-REL-01) |
| SEGP-20: Availability (NFR-04) | SEGP-99 | Plan a test run schedule |
| | SEGP-100 | Track uptime and note any downtime (TC-REL-02) |
| SEGP-21: Ease of use (NFR-05) | SEGP-101 | Let a new user try the system |
| | SEGP-102 | Collect feedback and fix problems (TC-UX-01) |
| SEGP-22: Clean code structure (NFR-06) | SEGP-103 | Split the Django project into separate modules |
| | SEGP-104 | Review the code to confirm the split |
| SEGP-23: Browser support (NFR-07) | SEGP-105 | Test main features on Chrome, Edge and Firefox (TC-COMP-01) |
| | SEGP-106 | Fix any browser-specific problems |
| SEGP-24: Backup and restore (NFR-08) | SEGP-107 | Write a database backup script |
| | SEGP-108 | Test restoring the backup (TC-REC-01) |

# Phase 3 - Authentication and Security Implementation



Owner: Swara Potdar (PES1UG24CS487)



## Scope



This note covers FR-01, FR-14 and SR-01 to SR-06.

It describes the implementation tested at commit:

b1e3590fd85014ed06d8f0443a03fd04f20a5695



## Implementation



### Authentication - FR-01



Django's LoginView handles authentication at /accounts/login/.

The login template displays an error for invalid credentials.

Successful login redirects to /inventory/.



LoginRequiredMiddleware protects application pages unless explicitly

marked public. Django manages authenticated sessions.



Session settings configure a 30-minute inactivity timeout and

session expiry when the browser closes.



Key files:

- src/accounts/urls.py

- src/templates/accounts/login.html

- src/esims/settings.py



### Authorization - FR-14



Three Django groups represent the operational roles:

- Inventory Administrator

- Store Staff

- Store Manager



Server-side role checks restrict component creation, editing,

deactivation and audit-history access to Inventory Administrators.

Dashboard and report views allow Inventory Administrators and

Store Managers.



Unauthorized role access returns a 403 Access Denied response.

Hiding navigation buttons is supplementary; server checks enforce access.



Key files:

- src/accounts/roles.py

- src/inventory/views.py

- src/reports/views.py

- src/audit/views.py

- src/templates/403.html



### Security Validation - SR-01 to SR-06



Automated tests check:

- Protected pages require authentication.

- Unauthorized roles cannot perform restricted operations.

- Passwords are hashed and can be verified correctly.

- Selected requests without valid CSRF tokens are rejected.

- Selected malicious inputs are handled safely and invalid values rejected.

- Captured authentication/access-denial logs contain no tested secrets.



Tests are in src/accounts/test_sr01_protected_pages.py through

src/accounts/test_sr06_log_secrets.py.



## Design Differences and Implementation Decisions



| Area | Submitted SAD | Implemented behaviour | Impact / explanation |
|---|---|---|---|
| Login URL | /login/ | /accounts/login/ | URLs are grouped by Django app; documentation must use the actual route. |
| Logout URL | /logout/ | /accounts/logout/ | Same app-based URL organization. |
| Successful login | Redirect to /dashboard/ | Redirect to /inventory/ | Inventory is the common landing page; dashboard access is role-restricted. |
| Authentication modules | Named AuthModule and SessionManager | Django authentication views, middleware and sessions | Design responsibilities use framework facilities rather than separate custom classes. |
| Authorization module | Named AuthorizationModule | Group checks and decorators in accounts/roles.py | Implements the responsibility using shared helpers. |
| Dashboard access | UX table lists all users, mainly Manager | Inventory Administrator and Store Manager only | Team must reconcile the SAD role table with the implemented access policy. |
| Authentication logging | Describes login and failed-login event logging | Tests inspect emitted logs for secrets | Secret-free log tests do not prove that every authentication event is logged; this needs separate verification. |



These differences are documented for team review.

This note does not claim that all deviations have been approved.



## Validation Evidence



The combined automated suite passed all 158 tests on 9 November 2026.

Environment: Python 3.11.9, Django 5.2.18, Windows.



Project-wide measured coverage:

- Statements: 89%.

- Branches: 78%.

- Combined: 88%.



See Test_Evidence/README.md for scope, commands and limitations.

See Swara_Security_RTM.md, submitted in PR #117, for detailed mappings.



## Remaining Team Actions



- Review and reconcile the role and URL differences above.

- Incorporate accepted changes into the SAD and validation documents.

- Complete traceability for the other team members' requirements.

- Record separate browser, usability and uptime evidence.

- Confirm accessible sprint videos and the final frozen version.



This note documents Swara's area only and does not declare the

complete project validated or ready for final submission.


# Architecture and Design Revision 1.1

Team H9. Prepared 11 November 2026. Status: implementation-alignment revision for review.
Read with the [original SAD](../Phase_1/04_Architecture_and_Design_Specification_SAD.pdf),
which retains the component diagram, descriptions, architectural rationale, security
architecture, class model and at least two UML sequence diagrams.
The documents together form this proposed revision; approval is not assumed.

## 1. Architecture and component realization

Django MVT modular monolith. accounts handles auth integration/roles, inventory handles
components/stock/CRUD, reports handles dashboard/CSV, audit records inventory changes.
nfr_tools is a Python utility package, not an installed Django app with its own models/views.
SQLite is the demonstrated database; production database alternatives are not a deployment claim.

| Design responsibility | Actual realization |
|---|---|
| AuthModule / SessionManager | Django LoginView/LogoutView, authentication/session middleware and settings. |
| AuthorizationModule | accounts/roles.py group checks and decorators. |
| Presentation | Django templates, views, URL dispatch and shared CSS. |
| Inventory/domain rules | Component model properties, forms and inventory views. |
| Persistence | Django ORM, migrations and database constraints. |
| Inventory change tracking | audit models and inventory/audit integration. |
| Error handling | Validation feedback, PermissionDenied/403 and registered 404/500 handlers. |

## 2. Actual URL interfaces

| Route | Behaviour | Permission |
|---|---|---|
| /accounts/login/ | GET form, POST authentication | Public login entry |
| /accounts/logout/ | POST logout | Authenticated |
| /inventory/ | GET list/search/category filter | Logged in |
| /inventory/add/ | GET form, POST create | Administrator |
| /inventory/<pk>/edit/ | GET form, POST update | Administrator |
| /inventory/<pk>/delete/ | GET confirmation, POST deactivate | Administrator |
| /inventory/low-stock/ | GET low-stock records | Logged in |
| /reports/dashboard/ | GET active-inventory metrics | Administrator/Manager |
| /reports/ | GET filtered report | Administrator/Manager |
| /reports/export/ | GET CSV | Administrator/Manager |
| /audit/ | GET audit list/search/filter | Administrator |

These are server-rendered HTTP interfaces, not a claimed standalone REST API.
No project-specific native binary ABI is defined.

## 3. Sequence and error clarifications

Login: request -> LoginView -> credential verification -> session -> inventory redirect
(or permitted next destination). Restricted mutation: middleware identifies user ->
role decorator -> form validation -> transaction/ORM and audit -> redirect/feedback.
Anonymous requests redirect to login; authenticated forbidden requests return 403.
Invalid forms can return HTTP 200 with errors and unchanged data; missing resources
return 404; unexpected failures use generic 500 handling. GET must not perform mutations.

Original sequence diagrams should be interpreted with these actual module/route names.
Keep the original UML figures as design history rather than claiming new diagrams were approved.

## 4. Data and security details

Component stores unique component_id, name, category choice, description, decimal
price, quantity, minimum_stock (default 10), active flag and timestamps. Category is
a choice field in this implementation, not a separate Category table. Availability
is calculated; deactivation retains the record. Role groups are named Inventory
Administrator, Store Staff and Store Manager; no Viewer role or staff_required
decorator is claimed. Server checks are authoritative even when links are hidden.
Password storage uses Django hashers; forms use CSRF tokens; unsafe raw SQL/escaping
bypasses must not be introduced. Selected secret-free logging tests are not proof
of complete authentication-event auditing or log redaction infrastructure.

## 5. Open design decisions

See [SRS revision](04_SRS_Revision_1_1.md) for role/metric decisions and
[implementation notes](../Phase_3/Swara_Implementation_Notes.md) for history.
Review authentication-event logging, original pagination/indexing intentions and
production deployment assumptions before claiming conformance. Record accepted
changes or implement missing requirements; no approval is manufactured here.

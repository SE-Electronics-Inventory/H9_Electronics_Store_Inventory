# NFR-06 Django Application Modularity Review

**Review date:** 2026-11-07
**Requirement:** NFR-06 — Review Django application modularity
**Scope:** `src/esims/settings.py`, `src/esims/urls.py`, and the runtime modules, tests, and templates for `accounts`, `inventory`, `reports`, and `audit`.

## Application responsibilities

| Django app | Responsibility | Main ownership |
|---|---|---|
| `accounts` | Authentication support and role checks | Role constants/decorators, role context processor, role setup; user records use Django's built-in auth models |
| `inventory` | Component inventory and stock operations | `Component` model, form validation, list/search, add/edit/deactivate, stock status |
| `reports` | Inventory summaries and exports | Dashboard metrics, filtered report view, CSV export |
| `audit` | Inventory change history | `ChangeLog` model, change-record helper, administrator-only history view |

The project registers each app in `INSTALLED_APPS` and mounts its URL configuration from `esims/urls.py`. Domain templates are grouped under `src/templates/<app>/`, and tests are kept with their corresponding apps.

## Dependency review

Observed runtime dependencies are one-directional:

```text
inventory ──> accounts (role checks)
inventory ──> audit (record inventory changes)
reports   ──> accounts (role checks)
reports   ──> inventory (read component data)
audit     ──> accounts (protect audit history)
```

No circular runtime imports were found among these applications. Applications use models and focused helpers across boundaries; none imports another application's views or URL configuration. The audit helper accepts a component-like object and stores the changed ID/name in its own model, which avoids making the audit schema depend on the inventory model.

## Review result

The four applications have clear responsibilities and the project-level `esims` package handles shared configuration and URL routing. The reviewed split satisfies the intent of NFR-06. The direct dependencies listed above are appropriate for current features; keeping them one-directional will help preserve the boundaries as the project grows. No code changes were required for this review.

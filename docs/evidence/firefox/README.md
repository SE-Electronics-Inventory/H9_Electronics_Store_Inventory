# Completed Firefox Browser Checks

Executed by: Swara Potdar. Date: 11 November 2026.
Browser: Firefox 147.0.3. Client: Ubuntu/Linux x86_64 in a VMware VM.
Server: Django on Windows, accessed over the VMware network at
http://192.168.179.1:8000. Repository baseline reported before testing: 122b1ac.

## Test setup

The server temporarily allowed host 192.168.179.1 for this session. Existing
migrations were applied to initialize the local application database, and the
project's create_demo_users command created the role accounts. These setup steps
resolved the initial host rejection and missing auth_user table before successful
workflow execution. No application-source change was needed for these setup steps.

## Completed checks and evidence

| Check | Observed result | Evidence |
|---|---|---|
| Invalid login | Invalid-credentials feedback appeared. | [Screenshot](firefox_invalid_login.png) |
| Administrator login | admin1 reached inventory with the administrator role. | [Screenshot](firefox_inventory.png) |
| Empty inventory | Empty-state message displayed. | [Screenshot](firefox_inventory.png) |
| Add component | FF-TEST-001 saved; price 100.00, quantity 5, minimum 10, Low Stock. | [Screenshot](firefox_add_component.png) |
| Matching search | Search for FF-TEST-001 returned one match. | [Screenshot](firefox_search.png) |
| Nonmatching search | NO-SUCH-COMPONENT returned zero matches and the empty state. | [Screenshot](firefox_search_no_match.png) |
| Low-stock page | FF-TEST-001 appeared with quantity 5 and minimum 10. | [Screenshot](firefox_low_stock.png) |
| CSV export | Supplied downloaded CSV contains the expected headers and component values. | [CSV](inventory_report.csv) |
| Logout and protected-page access | Following logout, opening /inventory/ redirected to /accounts/login/?next=/inventory/. | [Screenshot](firefox_logout_redirect.png) |

[Browser version and environment](firefox_environment.png).

## Result

The listed Firefox workflows passed in the documented environment. This is a
scoped execution record for these workflows and this browser/OS combination.

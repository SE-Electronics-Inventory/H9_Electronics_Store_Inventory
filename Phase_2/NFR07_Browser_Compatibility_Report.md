# NFR-07 Browser Compatibility Report

Requirement: ESIM-NF-007. Test case: TC-COMP-01. Owner: Shriya S R.
Revision 1.1, 11 November 2026. Status: PARTIALLY VALIDATED; acceptance pending.

## Evidence and method

| Browser / check | Evidence available | Status |
|---|---|---|
| Chrome | Shriya reports a Windows 11 manual session on 8 November; exact version and browser-specific capture not supplied for this review. | Reported manual completion; supporting details pending. |
| Edge | Shriya reports a Windows 11 manual session on 8 November; exact version and browser-specific capture not supplied for this review. | Reported manual completion; supporting details pending. |
| Firefox | User-Agent-based Django client checks exist; actual browser trial scheduled. | Real-browser execution pending. |
| Django test-client checks | Four methods in test_browser_compatibility.py passed in the combined 158-test run. | Passed for their server-response assertions only. |

The client tests check selected HTML markers, page status/content type, search/filter
results and CSV response headers/data using three User-Agent strings. They do not
launch Chrome, Edge or Firefox; they are not multi-engine or headless-browser tests.
They do not prove layout, actual download behaviour or comprehensive CSRF handling.

The Sprint 2 video demonstrates selected working workflows. It does not independently
establish all three browsers or exact installed versions.

## Required real-browser record

For each browser record exact version, OS, date, commit, tester, expected/actual
result and screenshot/log reference for login/logout, inventory/search, permitted
add/edit/deactivation, low-stock display, dashboard/reports, CSV download, audit,
role-denied access and the viewports actually tested. Do not fill PASS before execution.

## Conclusion

The requirement is not yet fully accepted. Standards-based HTML/CSS is useful design
practice but does not guarantee identical behaviour across browsers.

- [Automated source](../src/inventory/test_browser_compatibility.py)
- [Sprint 2 recording](Sprint_2_Demo.mp4)
- [PR #112](https://github.com/SE-Electronics-Inventory/H9_Electronics_Store_Inventory/pull/112)
- [System validation status](../docs/02_System_Test_Report.md)

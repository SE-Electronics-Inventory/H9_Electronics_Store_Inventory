# NFR-07 Browser Compatibility Report

Requirement: ESIM-NF-007. Test case: TC-COMP-01. Owner: Shriya S R.
Revision 1.2, 11 November 2026. Firefox completed-workflow evidence added.

## Evidence and method

| Browser / check | Evidence available | Status |
|---|---|---|
| Chrome | Shriya reports a Windows 11 manual session on 8 November; exact version and browser-specific capture not supplied for this review. | Reported manual completion; supporting details pending. |
| Edge | Shriya reports a Windows 11 manual session on 8 November; exact version and browser-specific capture not supplied for this review. | Reported manual completion; supporting details pending. |
| Firefox 147.0.3 | Swara executed the linked workflows on Ubuntu/Linux in VMware, 11 November 2026. | Listed workflows passed; screenshots and exported CSV retained. |
| Django test-client checks | Four methods in test_browser_compatibility.py passed in the combined 158-test run. | Passed for their server-response assertions only. |

The client tests check selected HTML markers, page status/content type, search/filter
results and CSV response headers/data using three User-Agent strings. They do not
launch Chrome, Edge or Firefox; they are not multi-engine or headless-browser tests.
They do not prove layout, actual download behaviour or comprehensive CSRF handling.

The Sprint 2 video demonstrates selected working workflows. It does not independently
establish all three browsers or exact installed versions.

## Real-browser evidence scope

For each browser record exact version, OS, date, commit, tester, expected/actual
result and screenshot/log reference for login/logout, inventory/search, permitted
add/edit/deactivation, low-stock display, dashboard/reports, CSV download, audit,
role-denied access and the viewports actually tested. Do not fill PASS before execution.

## Conclusion

The documented Firefox workflows passed in the recorded environment. Results apply
to those workflows and that browser/OS combination; Chrome/Edge reported sessions
remain distinct evidence sources.

- [Automated source](../src/inventory/test_browser_compatibility.py)
- [Sprint 2 recording](Sprint_2_Demo.mp4)
- [PR #112](https://github.com/SE-Electronics-Inventory/H9_Electronics_Store_Inventory/pull/112)
- [System validation status](../docs/02_System_Test_Report.md)

## Completed Firefox checks

Firefox 147.0.3 on Ubuntu/Linux in VMware: Swara completed login, empty inventory, add, matching/nonmatching search, low-stock display, CSV export and logout/protected-access checks on 11 November 2026.

[Execution summary, screenshots and CSV](../docs/evidence/firefox/README.md).

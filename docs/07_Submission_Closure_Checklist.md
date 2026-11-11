# Submission Closure Checklist

Audit baseline: c8b3812290e99203122e0316b0ae2f247707fcc3, reviewed 11 November 2026.

## Repository corrections prepared in this change

- Three formal reports physically in docs/, using actual tests and recorded evidence.
- Historical evidence copied unchanged into docs/evidence; removed HTML report restored from 316eed4.
- Video links corrected to Phase_2; outdated report copies replaced with canonical links.
- Unsupported 52-unit count, fictional methods/defects, invented coverage targets,
  full-mark verdicts and faculty-approval statements removed from canonical reports.
- Browser compatibility report corrected to distinguish client tests and actual browsers.
- SRS, SAD and complete STP revision supplements identify actual behaviour and review decisions.

## Part 1 - Review before declaring complete

- Confirm original SRS IEEE/template sections, measurable requirements, UML use cases
  and at least two security objectives/requirements in the submitted PDF.
- Complete STP exists; verify it is the linked authoritative plan (not the short extract).
- Original SAD retains component diagram, architecture/security/traceability, sequence
  diagrams, APIs and errors. Review 1.1 supplements with those original diagrams.
- Existing original test catalogue covers FR/NFR cases; current matrix supplements
  results but does not invent execution of every original manual step.
- Team/owner must decide role permissions, active-only metrics and authentication
  event logging deviations. Record reviewer/date/PR. Do not fill approvals without review.

## Part 2 - Project records and freeze

- Verify GitHub Project link, assigned stories, points and both sprint plans.
- Verify assigned authors and actual owner review records for feature PRs.
- Videos exist: Sprint 1 about 1:04, Sprint 2 about 1:58. If one minute is a strict cap,
  trim idle time in Sprint 1 without removing the working outcome.
- Record the actual final implementation commit and team-agreed freeze date.

## Part 3 - Execution still outstanding

- Unit: completed dedicated verbose execution of seven helper tests at bcb4ccd;
  all passed in 0.002 seconds. Log and runtime metadata are linked from the unit report.
- Ahana: availability observations/report over the agreed full window.
- Ahana: unassisted new-user task results and feedback.
- Shriya: actual Firefox execution and exact Chrome/Edge versions/evidence.
- Team: planned security scan or formally reviewed approach change; likewise explain
  client performance tests versus planned load tools and browser tests versus Selenium.
- Team: restart persistence and any remaining original manual steps, if not already evidenced.
- Review actual defects; no invented zero-open-defect or acceptance claim.

## Final evaluation and broader rubric

- Prepare working demo, explanation of deviations and each member's code/PR viva.
- The original broad phase rubric also lists a maintenance plan and final presentation;
  those are not created by this correction packet. Prepare them if in today's submission scope.
- Final acceptance must reflect actual pending results. Reports can be submitted with
  clearly declared limitations; documentation cannot substitute for unexecuted tests.

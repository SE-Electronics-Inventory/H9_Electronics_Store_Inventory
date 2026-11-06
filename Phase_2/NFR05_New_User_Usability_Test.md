# NFR-05 new-user usability test

**Status: real-user evidence pending.** A developer must not coach the participant, answer task questions, or complete tasks for them. Do not fill in participant observations, task outcomes, success rates, or feedback before the session.

## Setup

- Recruit one person who has not used ESIMS and is not a developer of this project.
- Prepare a test account with the role and permissions needed for the common inventory task. Use a disposable/test database with sample inventory; do not use production data.
- Seed `USABILITY-SENSOR-01` as an active low-stock component (quantity 2, minimum stock 5). Keep other sample records available so the participant can search and compare.
- If the participant is assigned the administrator role for Task 4, give them these add-form values: ID `USABILITY-NEW-01`, name `Usability test component`, category `Other`, description `Participant test record`, price `1.00`, quantity `3`, minimum stock `1`.
- Provide the participant only this sheet and the account credentials. Start from the login page and observe without hints.
- Record the app version/commit, browser, date, facilitator, and whether test data was reset.

## Tasks (read verbatim)

1. Sign in with the account provided.
2. Open the inventory list and find component `USABILITY-SENSOR-01` using search.
3. Open the low-stock view and determine whether that component needs restocking.
4. If the account permits component creation, add a test component using the supplied values. If it does not, describe where you would expect to find the action and stop without trying to bypass permissions.
5. Sign out.

Do not explain where controls are or what the expected results are. Record any participant request for help. Stop if the participant encounters a security or data-safety concern.

## Blank observation sheet

| Task | Completed without help? | Time / attempts | Observed difficulty, error or hesitation (quote only with consent) |
|---|---|---|---|
| 1. Sign in |  |  |  |
| 2. Search inventory |  |  |  |
| 3. Check low stock |  |  |  |
| 4. Permitted common operation |  |  |  |
| 5. Sign out |  |  |  |

**Participant's own feedback (verbatim, with consent):**

____________________________________________________________________

**Issues observed:**

____________________________________________________________________

**Fixes made after the session (commit/version and issue):**

____________________________________________________________________

**Retest date and result:**

____________________________________________________________________

Report actual counts and outcomes only after a real session. Keep participant identity private unless they explicitly agree to attribution.

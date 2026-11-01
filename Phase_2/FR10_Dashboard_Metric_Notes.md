# FR-10 dashboard metric interpretation

The dashboard currently follows the application's active-inventory convention:

- `Component.is_active` is the soft-deactivation flag. Deactivated rows remain stored for history, but the normal inventory list and FR-09 low-stock view filter to `is_active=True`.
- Total components counts active records only.
- Available stock is the sum of the stored `quantity` values for active records.
- Low-stock count and list include active components with `quantity <= minimum_stock`, matching the model rule and FR-09 view.

The FR-10 parent issue's phrase “total component records” could also mean all persisted rows, including deactivated records. Confirm with the requirement owner whether the total should include those historical, inactive rows. The implementation and tests make the active-only interpretation explicit; this note does not claim the issue wording resolves that ambiguity.

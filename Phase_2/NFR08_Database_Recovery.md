# NFR-08 database backup and restore

The development settings use SQLite at `src/db.sqlite3`. The recovery tool reads the selected database in read-only mode, makes a SQLite online backup, checks integrity, restores to a new destination, and compares every user table and row. It refuses to overwrite a backup or restore destination. Use paths outside the repository so database contents and credentials never enter Git.

## Create a backup

From the repository's `src` directory, replace the example date/path with a protected evidence location:

```powershell
python -m nfr_tools.database_recovery backup --database .\db.sqlite3 --output D:\ESIMS-evidence\inventory-2026-11-07.sqlite3
```

The command prints a JSON result with the backup path, nonzero file size and SQLite integrity result. Protect the backup as sensitive inventory data. The `--database` argument is explicit; review it before running. Never point the output at the source database.

## Restore verification in isolation

Use a new restore target in a disposable directory. This command does not replace the active database:

```powershell
python -m nfr_tools.database_recovery restore-test --backup D:\ESIMS-evidence\inventory-2026-11-07.sqlite3 --original .\db.sqlite3 --restore-to D:\ESIMS-evidence\restore-test\restored.sqlite3
```

The report confirms integrity, tables, row counts, and whether records match. Do not use an active or production path for `--restore-to`. Preserve the resulting JSON in the evidence folder. If restore comparison fails, keep the backup and report the table/row mismatch; do not treat recovery as successful.

"""Create SQLite backups and verify restores in an isolated destination database."""

from __future__ import annotations

import argparse
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


def _distinct_paths(source: Path, destination: Path) -> tuple[Path, Path]:
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()
    if source == destination:
        raise ValueError("Source and destination database paths must be different.")
    if not source.is_file():
        raise FileNotFoundError(f"Source database does not exist: {source}")
    return source, destination


def _check_database(path: Path) -> None:
    with closing(sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)) as connection:
        result = connection.execute("PRAGMA integrity_check").fetchone()
    if not result or result[0] != "ok":
        raise sqlite3.DatabaseError(f"SQLite integrity check failed for {path}: {result}")


def create_backup(source: Path, destination: Path) -> dict:
    source, destination = _distinct_paths(source, destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open("xb"):
            pass
    except FileExistsError:
        raise FileExistsError(f"Refusing to overwrite existing backup: {destination}")
    try:
        with closing(sqlite3.connect(f"file:{source.as_posix()}?mode=ro", uri=True)) as source_db:
            with closing(sqlite3.connect(destination)) as backup_db:
                source_db.backup(backup_db)
        if destination.stat().st_size == 0:
            raise sqlite3.DatabaseError("Backup file is empty.")
        _check_database(destination)
    except Exception:
        if destination.exists():
            destination.unlink()
        raise
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "backup": str(destination),
        "bytes": destination.stat().st_size,
        "integrity": "ok",
    }


def _table_names(connection: sqlite3.Connection) -> list[str]:
    return [row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )]


def _quoted(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def compare_databases(original: Path, restored: Path) -> dict:
    original, restored = _distinct_paths(original, restored)
    _check_database(original)
    _check_database(restored)
    with closing(sqlite3.connect(f"file:{original.as_posix()}?mode=ro", uri=True)) as left, closing(sqlite3.connect(
        f"file:{restored.as_posix()}?mode=ro", uri=True
    )) as right:
        left_tables, right_tables = _table_names(left), _table_names(right)
        tables = sorted(set(left_tables) | set(right_tables))
        differences = []
        row_counts = {}
        for table in tables:
            if table not in left_tables or table not in right_tables:
                differences.append({"table": table, "reason": "table missing"})
                continue
            left_rows = left.execute(f"SELECT * FROM {_quoted(table)} ORDER BY rowid").fetchall()
            right_rows = right.execute(f"SELECT * FROM {_quoted(table)} ORDER BY rowid").fetchall()
            row_counts[table] = len(left_rows)
            if left_rows != right_rows:
                differences.append({
                    "table": table,
                    "reason": "record mismatch",
                    "source_rows": len(left_rows),
                    "restored_rows": len(right_rows),
                })
    return {
        "source": str(original),
        "restored": str(restored),
        "integrity": "ok",
        "tables_compared": tables,
        "row_counts": row_counts,
        "differences": differences,
        "matches": not differences,
    }


def restore_test(backup: Path, destination: Path, original: Path) -> dict:
    backup, destination = _distinct_paths(backup, destination)
    original = Path(original).expanduser().resolve()
    if destination == original:
        raise ValueError("Restore destination must be different from the original database.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open("xb"):
            pass
    except FileExistsError:
        raise FileExistsError(f"Refusing to overwrite restore target: {destination}")
    try:
        with closing(sqlite3.connect(f"file:{backup.as_posix()}?mode=ro", uri=True)) as backup_db:
            with closing(sqlite3.connect(destination)) as restored_db:
                backup_db.backup(restored_db)
        _check_database(destination)
        comparison = compare_databases(original, destination)
    except Exception:
        if destination.exists():
            destination.unlink()
        raise
    return {"restored_at": datetime.now(timezone.utc).isoformat(), "backup": str(backup), **comparison}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    backup_parser = subparsers.add_parser("backup")
    backup_parser.add_argument("--database", type=Path, required=True, help="SQLite database file to read")
    backup_parser.add_argument("--output", type=Path, required=True, help="New backup file; existing paths are refused")
    restore_parser = subparsers.add_parser("restore-test")
    restore_parser.add_argument("--backup", type=Path, required=True)
    restore_parser.add_argument("--original", type=Path, required=True)
    restore_parser.add_argument("--restore-to", type=Path, required=True, help="New isolated database path")
    args = parser.parse_args(argv)
    try:
        result = create_backup(args.database, args.output) if args.action == "backup" else restore_test(args.backup, args.restore_to, args.original)
    except (OSError, ValueError, sqlite3.Error) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return int(args.action == "restore-test" and not result["matches"])


if __name__ == "__main__":
    raise SystemExit(main())

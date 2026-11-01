import io
import sqlite3
import tempfile
from contextlib import closing
from contextlib import redirect_stdout
from pathlib import Path

from django.test import SimpleTestCase

from nfr_tools.database_recovery import compare_databases, create_backup, main, restore_test


class DatabaseRecoveryTests(SimpleTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.root = Path(self.temp.name)
        self.source = self.root / "source.sqlite3"
        with closing(sqlite3.connect(self.source)) as connection:
            with connection:
                connection.execute("CREATE TABLE inventory_component (component_id TEXT PRIMARY KEY, name TEXT, quantity INTEGER)")
                connection.executemany(
                    "INSERT INTO inventory_component VALUES (?, ?, ?)",
                    [("REC-001", "Resistor", 12), ("REC-002", "Sensor", 4)],
                )

    def tearDown(self):
        self.temp.cleanup()

    def test_backup_is_nonempty_and_restores_matching_inventory_rows(self):
        backup = self.root / "backups" / "inventory-backup.sqlite3"
        restored = self.root / "isolated" / "restored.sqlite3"

        result = create_backup(self.source, backup)
        self.assertGreater(result["bytes"], 0)
        restore_result = restore_test(backup, restored, self.source)

        self.assertTrue(restore_result["matches"])
        self.assertEqual(restore_result["row_counts"]["inventory_component"], 2)
        self.assertEqual(compare_databases(self.source, restored)["differences"], [])

    def test_backup_refuses_to_overwrite_existing_file(self):
        destination = self.root / "existing.sqlite3"
        destination.write_bytes(b"preserve me")
        with self.assertRaises(FileExistsError):
            create_backup(self.source, destination)
        self.assertEqual(destination.read_bytes(), b"preserve me")

    def test_backup_refuses_source_as_destination(self):
        with self.assertRaises(ValueError):
            create_backup(self.source, self.source)

    def test_restore_refuses_source_and_preexisting_destinations(self):
        backup = self.root / "backup.sqlite3"
        create_backup(self.source, backup)
        with self.assertRaises(ValueError):
            restore_test(backup, self.source, self.source)

        existing = self.root / "existing-restore.sqlite3"
        existing.write_bytes(b"preserve restore target")
        with self.assertRaises(FileExistsError):
            restore_test(backup, existing, self.source)
        self.assertEqual(existing.read_bytes(), b"preserve restore target")

    def test_mismatched_restore_is_reported(self):
        backup = self.root / "backup.sqlite3"
        restored = self.root / "restored.sqlite3"
        create_backup(self.source, backup)
        with closing(sqlite3.connect(backup)) as connection:
            with connection:
                connection.execute("UPDATE inventory_component SET quantity=0 WHERE component_id='REC-001'")
        result = restore_test(backup, restored, self.source)
        self.assertFalse(result["matches"])
        self.assertEqual(result["differences"][0]["table"], "inventory_component")
        with redirect_stdout(io.StringIO()):
            exit_code = main([
                "restore-test",
                "--backup", str(backup),
                "--original", str(self.source),
                "--restore-to", str(self.root / "cli-restored.sqlite3"),
            ])
        self.assertEqual(exit_code, 1)

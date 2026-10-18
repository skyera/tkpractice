"""Regression checks for JSON and SQLite persistence without opening windows."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from persistence_demo import DEFAULT_SETTINGS, TaskStore, load_settings, save_settings


class PersistenceTests(unittest.TestCase):
    """Use isolated data folders so tests never modify user preferences."""

    def setUp(self) -> None:
        self.temporary_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_dir.cleanup)
        self.directory = Path(self.temporary_dir.name)

    def test_settings_round_trip_and_missing_defaults(self) -> None:
        path = self.directory / "nested" / "settings.json"
        self.assertEqual(load_settings(path), DEFAULT_SETTINGS)
        settings = {"name": "Zoë", "show_completed": False}
        save_settings(path, settings)
        self.assertEqual(load_settings(path), settings)

    def test_invalid_settings_are_reported_and_preserved(self) -> None:
        path = self.directory / "settings.json"
        for content in ("{broken", "[]", '{"name": 1}', '{"show_completed": "yes"}'):
            with self.subTest(content=content):
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_settings(path)
                self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_failed_settings_replace_preserves_previous_file(self) -> None:
        path = self.directory / "settings.json"
        save_settings(path, DEFAULT_SETTINGS)
        with patch.object(Path, "replace", side_effect=PermissionError("Read-only")):
            with self.assertRaises(PermissionError):
                save_settings(path, {"name": "New", "show_completed": False})
        self.assertEqual(load_settings(path), DEFAULT_SETTINGS)
        self.assertEqual(list(self.directory.iterdir()), [path])

    def test_sqlite_crud_survives_reopening_and_handles_sql_text(self) -> None:
        path = self.directory / "tasks.sqlite3"
        store = TaskStore(path)
        title = "Learn 'SQL'; DROP TABLE tasks; --"
        task_id = store.save_task(title, False)
        other_id = store.save_task("Second", False)
        reopened = TaskStore(path)
        self.assertEqual(reopened.list_tasks()[0], (task_id, title, 0))
        reopened.save_task("Finished", True, task_id)
        self.assertEqual(reopened.list_tasks(False), [(other_id, "Second", 0)])
        reopened.delete_task(task_id)
        self.assertEqual(TaskStore(path).list_tasks(), [(other_id, "Second", 0)])

    def test_invalid_task_does_not_modify_database(self) -> None:
        store = TaskStore(self.directory / "tasks.sqlite3")
        with self.assertRaises(ValueError):
            store.save_task("   ", False)
        with self.assertRaises(ValueError):
            store.save_task("Missing", False, 999)
        self.assertEqual(store.list_tasks(), [])


if __name__ == "__main__":
    unittest.main()

"""Practice JSON settings and SQLite CRUD with a persistent task list.

Run ``python persistence_demo.py`` or select this file in run_practice.py.
Data is stored in ~/.tkpractice/persistence and survives application restarts.
Only the Python standard library is required.
"""

import json
import sqlite3
import tempfile
import tkinter as tk
from contextlib import closing
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Optional

DATA_DIR = Path.home() / ".tkpractice" / "persistence"
DEFAULT_SETTINGS = {"name": "Learner", "show_completed": True}


def load_settings(path: Path) -> dict:
    """Read validated preferences; use defaults only when no file exists."""
    try:
        with path.open(encoding="utf-8") as source:
            settings = json.load(source)
    except FileNotFoundError:
        return DEFAULT_SETTINGS.copy()
    if not isinstance(settings, dict):
        raise ValueError("Settings must be a JSON object.")
    name = settings.get("name", DEFAULT_SETTINGS["name"])
    show_completed = settings.get("show_completed", True)
    if not isinstance(name, str) or not name.strip():
        raise ValueError("The display name must be a nonempty string.")
    if not isinstance(show_completed, bool):
        raise ValueError("show_completed must be true or false.")
    return {"name": name.strip(), "show_completed": show_completed}


def save_settings(path: Path, settings: dict) -> None:
    """Replace settings atomically so a failed write preserves the old file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as target:
            temporary_path = Path(target.name)
            json.dump(settings, target, indent=2, ensure_ascii=False)
            target.write("\n")
        temporary_path.replace(path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


class TaskStore:
    """Persist tasks with parameterized SQL and short-lived connections."""

    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(path)) as connection, connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS tasks ("
                "id INTEGER PRIMARY KEY, "
                "title TEXT NOT NULL CHECK(length(trim(title)) > 0), "
                "done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0, 1)))"
            )

    def list_tasks(self, show_completed: bool = True) -> list:
        """Read tasks in creation order, optionally hiding completed tasks."""
        with closing(sqlite3.connect(self.path)) as connection:
            return connection.execute(
                "SELECT id, title, done FROM tasks "
                "WHERE (? OR done = 0) ORDER BY id",
                (show_completed,),
            ).fetchall()

    def save_task(
        self, title: str, done: bool, task_id: Optional[int] = None
    ) -> int:
        """Create a task, or update an existing task by its stable ID."""
        title = title.strip()
        if not title:
            raise ValueError("Enter a task title.")
        with closing(sqlite3.connect(self.path)) as connection, connection:
            if task_id is None:
                cursor = connection.execute(
                    "INSERT INTO tasks (title, done) VALUES (?, ?)", (title, done)
                )
                return cursor.lastrowid
            cursor = connection.execute(
                "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
                (title, done, task_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("This task no longer exists. Refresh the list.")
            return task_id

    def delete_task(self, task_id: int) -> None:
        """Delete one task without interpolating values into SQL."""
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))


class PersistenceDemo(tk.Tk):
    """A settings form and task editor demonstrating persistent state."""

    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        super().__init__()
        self.title("Persistence: JSON Settings and SQLite Tasks")
        self.geometry("760x540")
        self.minsize(620, 460)
        self.settings_path = data_dir / "settings.json"
        self.store = None
        self.selected_id = None
        self.name_var = tk.StringVar(value=DEFAULT_SETTINGS["name"])
        self.show_completed_var = tk.BooleanVar(value=True)
        self.task_title_var = tk.StringVar()
        self.done_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Ready")
        self._build_ui()
        try:
            self.store = TaskStore(data_dir / "tasks.sqlite3")
        except (OSError, sqlite3.Error) as error:
            self._show_error("Cannot open task database", error)
        self._load_preferences()

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=12, pady=12)
        settings_tab = ttk.Frame(notebook, padding=16)
        tasks_tab = ttk.Frame(notebook, padding=16)
        notebook.add(settings_tab, text="JSON Settings")
        notebook.add(tasks_tab, text="SQLite Tasks")

        ttk.Label(
            settings_tab,
            text="Save preferences, close the window, then reopen to restore them.",
            wraplength=550,
        ).pack(anchor="w", pady=(0, 16))
        ttk.Label(settings_tab, text="Display name:").pack(anchor="w")
        ttk.Entry(settings_tab, textvariable=self.name_var).pack(fill="x", pady=6)
        ttk.Checkbutton(
            settings_tab,
            text="Show completed tasks",
            variable=self.show_completed_var,
            command=self._refresh_tasks,
        ).pack(anchor="w", pady=8)
        buttons = ttk.Frame(settings_tab)
        buttons.pack(anchor="w", pady=8)
        ttk.Button(buttons, text="Save Settings", command=self._save_preferences).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(
            buttons, text="Reload Settings", command=self._load_preferences
        ).pack(side="left")
        ttk.Label(
            settings_tab,
            text=f"Data folder: {self.settings_path.parent}",
            wraplength=550,
        ).pack(anchor="w", pady=16)

        ttk.Label(
            tasks_tab,
            text="Add a task or select a row to edit it. Changes save immediately.",
            wraplength=550,
        ).pack(anchor="w", pady=(0, 12))
        list_frame = ttk.Frame(tasks_tab)
        list_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(
            list_frame, columns=("title", "done"), show="headings", selectmode="browse"
        )
        self.tree.heading("title", text="Task")
        self.tree.heading("done", text="Completed")
        self.tree.column("title", width=420)
        self.tree.column("done", width=90, stretch=False, anchor="center")
        scrollbar = ttk.Scrollbar(list_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._select_task)

        editor = ttk.Frame(tasks_tab)
        editor.pack(fill="x", pady=12)
        editor.columnconfigure(1, weight=1)
        ttk.Label(editor, text="Title:").grid(row=0, column=0, padx=(0, 8))
        self.title_entry = ttk.Entry(editor, textvariable=self.task_title_var)
        self.title_entry.grid(row=0, column=1, sticky="ew")
        ttk.Checkbutton(editor, text="Completed", variable=self.done_var).grid(
            row=0, column=2, padx=8
        )
        controls = ttk.Frame(tasks_tab)
        controls.pack(fill="x")
        for label, callback in (
            ("New / Clear", self._clear_editor),
            ("Save Task", self._save_task),
            ("Delete Selected", self._delete_task),
            ("Refresh", self._refresh_tasks),
        ):
            ttk.Button(controls, text=label, command=callback).pack(
                side="left", padx=(0, 8)
            )
        ttk.Label(self, textvariable=self.status_var, padding=8).pack(fill="x")

    def _show_error(self, title: str, error: Exception) -> None:
        self.status_var.set(title)
        messagebox.showerror(title, str(error), parent=self)

    def _load_preferences(self) -> None:
        try:
            settings = load_settings(self.settings_path)
        except (OSError, ValueError) as error:
            self._show_error("Cannot load settings; current preferences kept", error)
        else:
            self.name_var.set(settings["name"])
            self.show_completed_var.set(settings["show_completed"])
            self.status_var.set(f"Welcome, {settings['name']}!")
        self._refresh_tasks()

    def _save_preferences(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning(
                "Display name required", "Enter a name.", parent=self
            )
            return
        try:
            save_settings(
                self.settings_path,
                {"name": name, "show_completed": self.show_completed_var.get()},
            )
        except (OSError, ValueError) as error:
            self._show_error("Cannot save settings", error)
        else:
            self.status_var.set(f"Settings saved for {name}.")

    def _refresh_tasks(self) -> None:
        if self.store is None:
            return
        try:
            rows = self.store.list_tasks(self.show_completed_var.get())
        except sqlite3.Error as error:
            self._show_error("Cannot read tasks", error)
            return
        self.tree.delete(*self.tree.get_children())
        for task_id, title, done in rows:
            self.tree.insert(
                "", "end", iid=str(task_id), values=(title, "Yes" if done else "No")
            )
        self._clear_editor()

    def _clear_editor(self) -> None:
        self.selected_id = None
        self.tree.selection_remove(*self.tree.selection())
        self.task_title_var.set("")
        self.done_var.set(False)

    def _select_task(self, event: Optional[tk.Event] = None) -> None:
        selection = self.tree.selection()
        if selection:
            self.selected_id = int(selection[0])
            title, done = self.tree.item(selection[0], "values")
            self.task_title_var.set(title)
            self.done_var.set(done == "Yes")

    def _save_task(self) -> None:
        if self.store is None:
            messagebox.showerror(
                "Database unavailable", "Reopen the demo to retry.", parent=self
            )
            return
        try:
            self.store.save_task(
                self.task_title_var.get(), self.done_var.get(), self.selected_id
            )
        except (sqlite3.Error, ValueError) as error:
            self._show_error("Cannot save task", error)
        else:
            self._refresh_tasks()
            self.status_var.set("Task saved to SQLite.")

    def _delete_task(self) -> None:
        if self.store is None or self.selected_id is None:
            messagebox.showinfo("Select a task", "Select a row to delete.", parent=self)
            return
        if not messagebox.askyesno(
            "Delete task?", "Delete the selected task?", parent=self
        ):
            return
        try:
            self.store.delete_task(self.selected_id)
        except sqlite3.Error as error:
            self._show_error("Cannot delete task", error)
        else:
            self._refresh_tasks()
            self.status_var.set("Task deleted from SQLite.")


def main() -> None:
    """Run the standalone persistence demo."""
    PersistenceDemo().mainloop()


if __name__ == "__main__":
    main()

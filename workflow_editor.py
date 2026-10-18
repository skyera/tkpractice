"""Build branching text workflows on a light, zoomable canvas.

Run ``python workflow_editor.py`` or use run_practice.py. Drag output ports to
input ports, edit parameters, preview results, and run UTF-8 file workflows.
JSON workflows from the original editor remain compatible. Standard library only.
"""

import json
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from workflow_support import (
    COLORS,
    FIELDS,
    KINDS,
    NODE_HEIGHT,
    NODE_WIDTH,
    History,
    Workflow,
    parameter_error,
    resolve_path,
    run_workflow,
    save_workflow,
    write_json,
)

STATE_COLORS = {
    "running": "#2563eb",
    "success": "#16834a",
    "failed": "#c53030",
    "cancelled": "#a16207",
    "skipped": "#64748b",
}
HINTS = {
    "Read Text": "Read a UTF-8 file. Its output can feed multiple branches.",
    "Replace Text": "Literal, case-sensitive replacement. Empty replacement deletes text.",
    "Uppercase": "Convert every character to uppercase.",
    "Lowercase": "Convert every character to lowercase.",
    "Trim Whitespace": "Strip leading and trailing whitespace from each line.",
    "Filter Lines": "Keep lines containing the exact, case-sensitive search text.",
    "Preview Text": "Inspect text without saving it. May end a branch or pass text onward.",
    "Save File": "Create a new UTF-8 file. Existing files are never overwritten.",
}


class WorkflowEditor(tk.Tk):
    """A visual graph editor with history, previews, and background execution."""

    def __init__(self, preferences_path: Optional[Path] = None) -> None:
        super().__init__()
        self.geometry("1220x820")
        self.minsize(940, 650)
        self.preferences_path = preferences_path or (
            Path.home() / ".tkpractice" / "workflow_editor" / "recent.json"
        )
        self.graph = Workflow()
        self.workflow_path = None
        self.base_dir = Path(__file__).resolve().parent
        self.selected = set()
        self.selected_edge = None
        self.connecting = None
        self.pointer = (0, 0)
        self.drag_origin = None
        self.drag_positions = {}
        self.drag_before = None
        self.selection_box = None
        self.pan_origin = None
        self.zoom = 1.0
        self.offset = [20.0, 30.0]
        self.history = History()
        self.saved_graph = {}
        self.edit_before = None
        self.edit_id = None
        self.running = False
        self.closing = False
        self.messages = queue.Queue()
        self.stop = threading.Event()
        self.worker = None
        self.poll_id = None
        self.states = {}
        self.previews = {}
        self.variables = {}
        self.text_fields = {}
        self.recent_paths = self._read_recent()
        self.status = tk.StringVar(value="Ready")
        self.document_label = tk.StringVar()
        self.zoom_label = tk.StringVar(value="100%")
        self.validation = tk.StringVar()
        self.path_hint = tk.StringVar()
        self.preview_label = tk.StringVar(value="Select a node to see its output.")
        self.snap = tk.BooleanVar(value=True)
        self.inspector_visible = True
        self.initial_fit_pending = True
        self._build_ui()
        self._new_graph()
        if self.preference_warning:
            self._append_log(self.preference_warning)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.poll_id = self.after(50, self._poll_messages)

    @property
    def dirty(self) -> bool:
        """Compare document contents, so undo can return to a saved state."""
        return self.graph.to_dict() != self.saved_graph

    def _build_ui(self) -> None:
        self._build_menu()
        toolbar = ttk.Frame(self, padding=(10, 8))
        toolbar.pack(fill="x")
        for label, action in (
            ("New", self._new),
            ("Open…", self._open),
            ("Save", self._save),
            ("Save As…", self._save_as),
        ):
            ttk.Button(toolbar, text=label, command=action).pack(side="left", padx=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=8)
        self.kind_var = tk.StringVar(value="Replace Text")
        ttk.Combobox(
            toolbar,
            values=KINDS,
            textvariable=self.kind_var,
            state="readonly",
            width=18,
        ).pack(side="left", padx=3)
        ttk.Button(
            toolbar, text="+ Add Node", command=lambda: self._add(self.kind_var.get())
        ).pack(side="left", padx=3)
        self.run_button = ttk.Button(toolbar, text="Run Workflow", command=self._run)
        self.run_button.pack(side="right", padx=3)
        self.cancel_button = ttk.Button(
            toolbar, text="Cancel", command=self.stop.set, state="disabled"
        )
        self.cancel_button.pack(side="right", padx=3)
        viewbar = ttk.Frame(self, padding=(12, 0, 12, 8))
        viewbar.pack(fill="x")
        ttk.Label(viewbar, textvariable=self.document_label, width=25).pack(side="left")
        for label, action in (
            ("Undo", self._undo),
            ("Redo", self._redo),
            ("Arrange", self._arrange),
            ("Fit All", self._fit_all),
            ("Reset View", self._reset_view),
            ("Properties", self._toggle_inspector),
        ):
            ttk.Button(viewbar, text=label, command=action).pack(side="right", padx=2)
        ttk.Checkbutton(viewbar, text="Snap", variable=self.snap).pack(
            side="right", padx=4
        )
        ttk.Label(viewbar, textvariable=self.zoom_label, width=6).pack(side="right")
        ttk.Label(
            self,
            text="Drag ports to connect • Wheel: zoom • Middle drag: pan • "
            "Shift-click or drag empty space: select • Select wire + Delete: remove",
            padding=(12, 0, 12, 8),
        ).pack(anchor="w")
        self.vertical_pane = ttk.Panedwindow(self, orient="vertical")
        self.vertical_pane.pack(fill="both", expand=True, padx=12)
        self.main_pane = ttk.Panedwindow(self.vertical_pane, orient="horizontal")
        self.vertical_pane.add(self.main_pane, weight=5)
        self.canvas = tk.Canvas(
            self.main_pane, bg="#f3f6fa", highlightthickness=0, takefocus=True
        )
        self.main_pane.add(self.canvas, weight=4)
        self.inspector = ttk.Frame(self.main_pane, width=305)
        self.main_pane.add(self.inspector, weight=1)
        self.inspector_tabs = ttk.Notebook(self.inspector)
        self.inspector_tabs.pack(fill="both", expand=True)
        self.properties = ttk.Frame(self.inspector_tabs, padding=12)
        preview_tab = ttk.Frame(self.inspector_tabs, padding=12)
        self.inspector_tabs.add(self.properties, text="Properties")
        self.inspector_tabs.add(preview_tab, text="Output Preview")
        ttk.Label(preview_tab, textvariable=self.preview_label, wraplength=260).pack(
            fill="x", pady=(0, 8)
        )
        self.preview_button = ttk.Button(
            preview_tab, text="Refresh Preview (no file writes)", command=self._preview
        )
        self.preview_button.pack(fill="x", pady=(0, 8))
        self.preview_text = self._scrolling_text(preview_tab, height=12)
        self.log = self._scrolling_text(self.vertical_pane, height=7, pane=True)
        ttk.Label(self, textvariable=self.status, padding=10).pack(fill="x")
        bindings = {
            "<Button-1>": self._press,
            "<B1-Motion>": self._drag,
            "<ButtonRelease-1>": self._release,
            "<Motion>": self._motion,
            "<Button-2>": self._pan_start,
            "<B2-Motion>": self._pan,
            "<ButtonRelease-2>": self._pan_end,
            "<MouseWheel>": self._wheel,
            "<Button-4>": self._wheel,
            "<Button-5>": self._wheel,
            "<Button-3>": self._context_menu,
            "<Configure>": self._resize,
            "<Escape>": lambda event: self._cancel_connection(),
            "<Delete>": lambda event: self._delete(),
            "<BackSpace>": lambda event: self._delete(),
            "<Control-a>": self._select_all,
            "<Control-c>": lambda event: self._copy(),
            "<Control-v>": lambda event: self._paste(),
            "<Control-d>": lambda event: self._duplicate(),
        }
        for sequence, callback in bindings.items():
            self.canvas.bind(sequence, callback)
        for sequence, action in (
            ("<Control-s>", self._save),
            ("<Control-Shift-S>", self._save_as),
            ("<Control-o>", self._open),
            ("<Control-n>", self._new),
            ("<Control-z>", self._undo),
            ("<Control-y>", self._redo),
        ):
            self.bind(sequence, lambda event, action=action: self._shortcut(action))

    def _scrolling_text(self, parent, height: int, pane: bool = False) -> tk.Text:
        frame = ttk.Frame(parent)
        if pane:
            parent.add(frame, weight=1)
        else:
            frame.pack(fill="both", expand=True)
        text = tk.Text(
            frame,
            height=height,
            width=28,
            state="disabled",
            wrap="word",
            bg="white",
            fg="#253447",
            relief="flat",
            padx=8,
            pady=8,
        )
        scroll = ttk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        text.pack(side="left", fill="both", expand=True)
        return text

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        files = tk.Menu(menubar, tearoff=False)
        for label, command in (
            ("New    Ctrl+N", self._new),
            ("Open…    Ctrl+O", self._open),
            ("Save    Ctrl+S", self._save),
            ("Save As…    Ctrl+Shift+S", self._save_as),
        ):
            files.add_command(label=label, command=command)
        self.recent_menu = tk.Menu(files, tearoff=False)
        files.add_cascade(label="Recent Files", menu=self.recent_menu)
        files.add_separator()
        files.add_command(label="Close", command=self._close)
        menubar.add_cascade(label="File", menu=files)
        edits = tk.Menu(menubar, tearoff=False)
        for label, action in (
            ("Undo    Ctrl+Z", self._undo),
            ("Redo    Ctrl+Y", self._redo),
            ("Copy Nodes    Ctrl+C", self._copy),
            ("Paste Nodes    Ctrl+V", self._paste),
            ("Duplicate    Ctrl+D", self._duplicate),
            ("Delete Selection", self._delete),
        ):
            edits.add_command(label=label, command=action)
        menubar.add_cascade(label="Edit", menu=edits)
        self.configure(menu=menubar)
        self._refresh_recent_menu()

    def _shortcut(self, action) -> str:
        action()
        return "break"

    def _read_recent(self) -> list:
        self.preference_warning = ""
        try:
            data = json.loads(self.preferences_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("paths"), list):
                self.preference_warning = (
                    "Recent-file history is invalid; starting empty."
                )
                return []
            return [p for p in data["paths"] if isinstance(p, str)][:8]
        except FileNotFoundError:
            return []
        except (OSError, ValueError) as error:
            self.preference_warning = f"Could not read recent-file history: {error}"
            return []

    def _refresh_recent_menu(self) -> None:
        self.recent_menu.delete(0, "end")
        for path in self.recent_paths:
            self.recent_menu.add_command(
                label=path, command=lambda path=path: self._open(Path(path))
            )
        if not self.recent_paths:
            self.recent_menu.add_command(label="No recent workflows", state="disabled")

    def _remember(self, path: Path) -> None:
        value = str(path.resolve())
        self.recent_paths = [value] + [p for p in self.recent_paths if p != value][:7]
        self._refresh_recent_menu()
        try:
            self.preferences_path.parent.mkdir(parents=True, exist_ok=True)
            write_json(self.preferences_path, {"paths": self.recent_paths})
        except OSError as error:
            self._append_log(f"Could not save recent files: {error}")

    def _editable(self) -> bool:
        if self.running:
            self.status.set(
                "Wait for execution to finish, or cancel it before editing."
            )
            return False
        return True

    def _new_graph(self) -> None:
        self._flush_edit()
        self.graph = Workflow()
        read = self.graph.add_node("Read Text", 50, 100)
        replace = self.graph.add_node("Replace Text", 330, 180)
        save = self.graph.add_node("Save File", 610, 100)
        self.graph.connect(read.id, replace.id)
        self.graph.connect(replace.id, save.id)
        self.workflow_path = None
        self.base_dir = Path(__file__).resolve().parent
        self._reset_document()
        self.status.set("Choose file paths and replacement text, or add more nodes.")

    def _reset_document(self) -> None:
        self.selected.clear()
        self.selected_edge = None
        self.connecting = None
        self.history = History()
        self.saved_graph = self.graph.to_dict()
        self.states.clear()
        self.previews.clear()
        self._reset_view()
        self._inspect()
        self._update_title()

    def _update_title(self) -> None:
        name = self.workflow_path.name if self.workflow_path else "Untitled workflow"
        marker = " *" if self.dirty else ""
        self.document_label.set(name + marker)
        self.title(f"{name}{marker} — Text Flow")

    def _record(self, before: dict) -> None:
        if self.history.record(before, self.graph.to_dict()):
            self.states.clear()
            self.previews.clear()
            self._show_preview()
        self._update_title()
        self._draw()

    def _flush_edit(self) -> None:
        if self.edit_id is not None:
            self.after_cancel(self.edit_id)
            self.edit_id = None
        if self.edit_before is not None:
            before, self.edit_before = self.edit_before, None
            self._record(before)

    def _undo(self) -> None:
        if not self._editable():
            return
        self._flush_edit()
        previous = self.history.undo(self.graph.to_dict())
        if previous is not None:
            self._restore(previous)

    def _redo(self) -> None:
        if not self._editable():
            return
        self._flush_edit()
        following = self.history.redo(self.graph.to_dict())
        if following is not None:
            self._restore(following)

    def _restore(self, document: dict) -> None:
        self.graph = Workflow.from_dict(document)
        self.selected.intersection_update(self.graph.nodes)
        self.selected_edge = None
        self.connecting = None
        self.states.clear()
        self.previews.clear()
        self._draw()
        self._inspect()
        self._update_title()

    def _screen(self, x: float, y: float) -> tuple:
        return x * self.zoom + self.offset[0], y * self.zoom + self.offset[1]

    def _resize(self, event: tk.Event) -> None:
        if (
            self.initial_fit_pending
            and self.graph.nodes
            and event.width > 300
            and event.height > 150
        ):
            self.initial_fit_pending = False
            self._fit_all()
        else:
            self._draw()

    def _world(self, x: float, y: float) -> tuple:
        return (x - self.offset[0]) / self.zoom, (y - self.offset[1]) / self.zoom

    def _draw(self) -> None:
        self.canvas.delete("all")
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        spacing = 20 * self.zoom
        if spacing < 12:
            spacing *= 2
        for x in range(int(self.offset[0] % spacing), width, max(1, int(spacing))):
            self.canvas.create_line(x, 0, x, height, fill="#e5ebf2", tags="grid")
        for y in range(int(self.offset[1] % spacing), height, max(1, int(spacing))):
            self.canvas.create_line(0, y, width, y, fill="#e5ebf2", tags="grid")
        for source, target in self.graph.edges:
            self._wire(source, target)
        for node in self.graph.nodes.values():
            self._draw_node(node)
        if self.connecting is not None and self.connecting in self.graph.nodes:
            node = self.graph.nodes[self.connecting]
            x, y = self._screen(node.x + NODE_WIDTH, node.y + NODE_HEIGHT / 2)
            self._curve(x, y, *self.pointer, fill="#2563eb", dash=(5, 3), tags="ghost")
        if self.selection_box is not None:
            self.canvas.create_rectangle(
                *self.selection_box, outline="#2563eb", dash=(4, 3), tags="marquee"
            )
        self.zoom_label.set(f"{self.zoom:.0%}")

    def _curve(self, x1, y1, x2, y2, **options) -> None:
        bend = max(45, abs(x2 - x1) / 2)
        self.canvas.create_line(
            x1,
            y1,
            x1 + bend,
            y1,
            x2 - bend,
            y2,
            x2,
            y2,
            smooth=True,
            splinesteps=24,
            width=3,
            arrow="last",
            **options,
        )

    def _wire(self, source: int, target: int) -> None:
        a, b = self.graph.nodes[source], self.graph.nodes[target]
        start = self._screen(a.x + NODE_WIDTH, a.y + NODE_HEIGHT / 2)
        end = self._screen(b.x, b.y + NODE_HEIGHT / 2)
        selected = self.selected_edge == (source, target)
        self._curve(
            *start,
            *end,
            fill="#c27a00" if selected else "#71849a",
            tags=(f"edge:{source}:{target}",),
        )

    def _draw_node(self, node) -> None:
        x, y = self._screen(node.x, node.y)
        w, h = NODE_WIDTH * self.zoom, NODE_HEIGHT * self.zoom
        tag = f"node:{node.id}"
        state = self.states.get(node.id, "")
        outline = STATE_COLORS.get(state, "#a3b1c2")
        if node.id in self.selected:
            outline = "#b77900"
        self.canvas.create_rectangle(
            x + 3,
            y + 4,
            x + w + 3,
            y + h + 4,
            fill="#dce3eb",
            outline="",
            tags=(tag,),
        )
        self.canvas.create_rectangle(
            x,
            y,
            x + w,
            y + h,
            fill="white",
            outline=outline,
            width=3 if node.id in self.selected or state else 1,
            tags=(tag,),
        )
        self.canvas.create_rectangle(
            x + 2,
            y + 2,
            x + w - 2,
            y + 30 * self.zoom,
            fill=COLORS[node.kind],
            outline="",
            tags=(tag,),
        )
        font_size = max(7, round(10 * self.zoom))
        self.canvas.create_text(
            x + 10 * self.zoom,
            y + 16 * self.zoom,
            text=f"{node.id}  {node.kind}",
            fill="white",
            anchor="w",
            font=("Segoe UI", font_size, "bold"),
            tags=(tag,),
        )
        summary = next(iter(node.settings.values()), "Pass text onward")
        if not summary:
            summary = "Choose a file" if "path" in node.settings else "Set parameters"
        self.canvas.create_text(
            x + 10 * self.zoom,
            y + 52 * self.zoom,
            text=summary.replace("\n", " ")[:25],
            fill="#334155",
            anchor="w",
            font=("Segoe UI", max(7, round(9 * self.zoom))),
            tags=(tag,),
        )
        label = (
            state.title()
            if state
            else ("Needs settings" if parameter_error(node) else "Ready")
        )
        self.canvas.create_text(
            x + 10 * self.zoom,
            y + 80 * self.zoom,
            text=label,
            fill=STATE_COLORS.get(state, "#64748b"),
            anchor="w",
            font=("Segoe UI", max(7, round(8 * self.zoom))),
            tags=(tag,),
        )
        for direction, px in (("in", x), ("out", x + w)):
            if (direction == "in" and node.kind == "Read Text") or (
                direction == "out" and node.kind == "Save File"
            ):
                continue
            color = "#168573"
            if direction == "in" and self.connecting is not None:
                try:
                    self.graph.check_connection(self.connecting, node.id)
                except ValueError:
                    color = "#b7c0cc"
                else:
                    color = "#22a35a"
            if direction == "out" and self.connecting == node.id:
                color = "#2563eb"
            radius = max(6, 7 * self.zoom)
            py = y + h / 2
            self.canvas.create_oval(
                px - radius,
                py - radius,
                px + radius,
                py + radius,
                fill=color,
                outline="white",
                width=2,
                tags=(tag, f"{direction}:{node.id}"),
            )

    def _hit(self, x: float, y: float) -> tuple:
        items = self.canvas.find_overlapping(x - 4, y - 4, x + 4, y + 4)
        tags = [tag for item in reversed(items) for tag in self.canvas.gettags(item)]
        for prefix in ("in:", "out:", "node:", "edge:"):
            for tag in tags:
                if tag.startswith(prefix):
                    return prefix[:-1], tuple(int(n) for n in tag.split(":")[1:])
        return "", ()

    def _press(self, event: tk.Event) -> None:
        self._flush_edit()
        self.canvas.focus_set()
        self.drag_origin = None
        kind, ids = self._hit(event.x, event.y)
        self.pointer = (event.x, event.y)
        if kind == "out" and self._editable():
            self.connecting = ids[0]
            self._draw()
            return
        if kind == "in" and self.connecting is not None:
            self._finish_connection(ids[0])
            return
        self.connecting = None
        if kind == "edge":
            self.selected_edge = ids
            self.selected.clear()
            self.status.set("Wire selected. Press Delete, or right-click to remove it.")
        elif kind in ("node", "in", "out"):
            node_id = ids[0]
            if event.state & 1:
                self.selected.symmetric_difference_update({node_id})
            elif node_id not in self.selected:
                self.selected = {node_id}
            self.selected_edge = None
            if not self.running:
                self.drag_origin = self._world(event.x, event.y)
                self.drag_positions = {
                    n: (self.graph.nodes[n].x, self.graph.nodes[n].y)
                    for n in self.selected
                }
                self.drag_before = self.graph.to_dict()
        else:
            if not event.state & 1:
                self.selected.clear()
            self.selected_edge = None
            self.selection_box = (event.x, event.y, event.x, event.y)
        self._draw()
        self._inspect()

    def _motion(self, event: tk.Event) -> None:
        if self.connecting is not None:
            self.pointer = (event.x, event.y)
            self._draw()

    def _drag(self, event: tk.Event) -> None:
        if self.connecting is not None:
            self._motion(event)
        elif self.drag_origin is not None:
            x, y = self._world(event.x, event.y)
            dx, dy = x - self.drag_origin[0], y - self.drag_origin[1]
            if self.drag_positions:
                dx = max(dx, 20 - min(p[0] for p in self.drag_positions.values()))
                dy = max(dy, 20 - min(p[1] for p in self.drag_positions.values()))
                dx = min(dx, 10000 - max(p[0] for p in self.drag_positions.values()))
                dy = min(dy, 10000 - max(p[1] for p in self.drag_positions.values()))
            for node_id, (start_x, start_y) in self.drag_positions.items():
                self.graph.nodes[node_id].x = start_x + dx
                self.graph.nodes[node_id].y = start_y + dy
            self._draw()
        elif self.selection_box is not None:
            self.selection_box = (*self.selection_box[:2], event.x, event.y)
            self._draw()

    def _release(self, event: tk.Event) -> None:
        if self.connecting is not None:
            kind, ids = self._hit(event.x, event.y)
            if kind == "in":
                self._finish_connection(ids[0])
            elif kind != "out":
                self._cancel_connection()
            return
        if self.drag_origin is not None:
            if self.drag_before != self.graph.to_dict() and self.snap.get():
                for node_id in self.selected:
                    node = self.graph.nodes[node_id]
                    node.x = max(20, min(10000, round(node.x / 20) * 20))
                    node.y = max(20, min(10000, round(node.y / 20) * 20))
            self._record(self.drag_before)
        elif self.selection_box is not None:
            x1, y1, x2, y2 = self.selection_box
            left, right = sorted((x1, x2))
            top, bottom = sorted((y1, y2))
            for node in self.graph.nodes.values():
                x, y = self._screen(node.x, node.y)
                if (
                    left <= x <= right
                    and top <= y <= bottom
                    and x + NODE_WIDTH * self.zoom <= right
                    and y + NODE_HEIGHT * self.zoom <= bottom
                ):
                    self.selected.add(node.id)
        self.drag_origin = None
        self.drag_before = None
        self.selection_box = None
        self._draw()
        self._inspect()

    def _finish_connection(self, target: int) -> None:
        if not self._editable():
            return
        before = self.graph.to_dict()
        try:
            self.graph.connect(self.connecting, target)
        except ValueError as error:
            self.status.set(str(error))
        else:
            self._record(before)
            self.status.set("Connected. Drag this output again to add another branch.")
        self.connecting = None
        self._draw()

    def _cancel_connection(self) -> None:
        self.connecting = None
        self.selection_box = None
        self._draw()
        self.status.set("Connection cancelled.")

    def _pan_start(self, event: tk.Event) -> None:
        self.pan_origin = (event.x, event.y, *self.offset)

    def _pan(self, event: tk.Event) -> None:
        if self.pan_origin is not None:
            x, y, ox, oy = self.pan_origin
            self.offset = [ox + event.x - x, oy + event.y - y]
            self._draw()

    def _pan_end(self, event: tk.Event) -> None:
        self.pan_origin = None

    def _wheel(self, event: tk.Event) -> str:
        direction = 1 if getattr(event, "num", None) == 4 or event.delta > 0 else -1
        self._zoom_at(event.x, event.y, 1.12 if direction > 0 else 1 / 1.12)
        return "break"

    def _zoom_at(self, x: float, y: float, factor: float) -> None:
        wx, wy = self._world(x, y)
        self.zoom = max(0.25, min(2.5, self.zoom * factor))
        self.offset = [x - wx * self.zoom, y - wy * self.zoom]
        self._draw()

    def _reset_view(self) -> None:
        self.zoom = 1.0
        self.offset = [20.0, 30.0]
        self._draw()

    def _fit_all(self) -> None:
        if not self.graph.nodes:
            self._reset_view()
            return
        nodes = list(self.graph.nodes.values())
        left, top = min(n.x for n in nodes), min(n.y for n in nodes)
        right = max(n.x for n in nodes) + NODE_WIDTH
        bottom = max(n.y for n in nodes) + NODE_HEIGHT
        width = max(200, self.canvas.winfo_width() - 70)
        height = max(150, self.canvas.winfo_height() - 70)
        self.zoom = max(0.25, min(1.5, width / (right - left), height / (bottom - top)))
        self.offset = [35 - left * self.zoom, 35 - top * self.zoom]
        self._draw()

    def _toggle_inspector(self) -> None:
        if self.inspector_visible:
            self.main_pane.forget(self.inspector)
        else:
            self.main_pane.add(self.inspector, weight=1)
        self.inspector_visible = not self.inspector_visible

    def _context_menu(self, event: tk.Event) -> None:
        kind, ids = self._hit(event.x, event.y)
        menu = tk.Menu(self, tearoff=False)
        if kind == "edge":
            self.selected_edge = ids
            menu.add_command(label="Remove Wire", command=self._delete)
        else:
            self.selected_edge = None
            if kind in ("node", "in", "out") and ids[0] not in self.selected:
                self.selected = {ids[0]}
                self._inspect()
            menu.add_command(label="Duplicate Selection", command=self._duplicate)
            menu.add_command(label="Delete Selection", command=self._delete)
            menu.add_command(label="Fit All", command=self._fit_all)
        self._draw()
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _inspect(self) -> None:
        self._flush_edit()
        for widget in self.properties.winfo_children():
            widget.destroy()
        self.variables = {}
        self.text_fields = {}
        if len(self.selected) != 1:
            ttk.Label(
                self.properties,
                text=f"{len(self.selected)} nodes selected."
                if self.selected
                else "Select a block to edit its properties.",
                wraplength=260,
            ).pack(anchor="w")
            self._show_preview()
            return
        node = self.graph.nodes[next(iter(self.selected))]
        ttk.Label(
            self.properties,
            text=f"#{node.id} {node.kind}",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 8))
        ttk.Label(self.properties, text=HINTS[node.kind], wraplength=260).pack(
            anchor="w", pady=(0, 8)
        )
        for key in FIELDS[node.kind]:
            ttk.Label(self.properties, text=key.title()).pack(anchor="w", pady=(8, 3))
            if key in ("find", "replace", "contains"):
                text = tk.Text(
                    self.properties, height=3, width=28, wrap="word", undo=True
                )
                text.insert("1.0", node.settings[key])
                text.edit_modified(False)
                text.pack(fill="x")
                text.bind(
                    "<<Modified>>",
                    lambda event, key=key, node_id=node.id: self._text_changed(
                        node_id, key, event.widget
                    ),
                )
                text.bind("<Control-z>", lambda event: self._shortcut(self._undo))
                text.bind("<Control-y>", lambda event: self._shortcut(self._redo))
                self.text_fields[key] = text
                if self.running:
                    text.configure(state="disabled")
            else:
                variable = tk.StringVar(value=node.settings[key])
                self.variables[key] = variable
                ttk.Entry(
                    self.properties,
                    textvariable=variable,
                    width=28,
                    state="disabled" if self.running else "normal",
                ).pack(fill="x")
                variable.trace_add(
                    "write",
                    lambda *args, key=key, var=variable, node_id=node.id: self._edit(
                        node_id, key, var.get()
                    ),
                )
        if "path" in node.settings:
            ttk.Button(
                self.properties,
                text="Browse…",
                command=self._browse,
                state="disabled" if self.running else "normal",
            ).pack(anchor="w", pady=6)
            ttk.Label(
                self.properties,
                textvariable=self.path_hint,
                wraplength=260,
                foreground="#596b80",
            ).pack(anchor="w", pady=4)
        ttk.Label(
            self.properties,
            textvariable=self.validation,
            foreground="#b42318",
            wraplength=260,
        ).pack(anchor="w", pady=8)
        controls = ttk.Frame(self.properties)
        controls.pack(fill="x", pady=6)
        for label, action in (
            ("Disconnect", self._disconnect),
            ("Delete", self._delete),
        ):
            ttk.Button(controls, text=label, command=action).pack(side="left", padx=3)
        ttk.Button(
            self.properties,
            text="Preview This Node",
            command=self._preview,
            state="disabled" if self.running else "normal",
        ).pack(fill="x", pady=6)
        self._update_validation(node)
        self._show_preview()

    def _text_changed(self, node_id: int, key: str, text: tk.Text) -> None:
        if text.edit_modified():
            text.edit_modified(False)
            self._edit(node_id, key, text.get("1.0", "end-1c"))

    def _edit(self, node_id: int, key: str, value: str) -> None:
        if self.running or node_id not in self.graph.nodes:
            return
        node = self.graph.nodes[node_id]
        if node.settings[key] == value:
            return
        if self.edit_before is None:
            self.edit_before = self.graph.to_dict()
        node.settings[key] = value
        if self.edit_id is not None:
            self.after_cancel(self.edit_id)
        self.edit_id = self.after(450, self._flush_edit)
        self.previews.clear()
        self.states.clear()
        self._update_validation(node)
        self._update_title()
        self._show_preview()
        self._draw()

    def _update_validation(self, node) -> None:
        error = parameter_error(node)
        self.validation.set(f"Required: {error}." if error else "")
        self.path_hint.set(
            f"Relative paths use: {self.base_dir}" if "path" in node.settings else ""
        )

    def _show_preview(self) -> None:
        payload = None
        if len(self.selected) == 1:
            node_id = next(iter(self.selected))
            payload = self.previews.get(node_id)
        if payload:
            length = payload["characters"]
            truncated = " (first 8,000 shown)" if length > len(payload["text"]) else ""
            self.preview_label.set(f"{length:,} characters{truncated}")
            content = payload["text"]
        else:
            self.preview_label.set(
                "No cached output. Refresh Preview to evaluate upstream."
            )
            content = ""
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", content)
        self.preview_text.configure(state="disabled")

    def _browse(self) -> None:
        if not self._editable() or len(self.selected) != 1:
            return
        node = self.graph.nodes[next(iter(self.selected))]
        options = {"parent": self, "initialdir": str(self.base_dir)}
        path = (
            filedialog.askopenfilename(**options)
            if node.kind == "Read Text"
            else filedialog.asksaveasfilename(defaultextension=".txt", **options)
        )
        if path:
            self.variables["path"].set(path)

    def _add(self, kind: str) -> None:
        if not self._editable():
            return
        self._flush_edit()
        before = self.graph.to_dict()
        x, y = self._world(150, 100)
        node = self.graph.add_node(kind, max(20, min(10000, x)), max(20, min(10000, y)))
        self.selected = {node.id}
        self.selected_edge = None
        self._record(before)
        self._inspect()

    def _disconnect(self) -> None:
        if not self._editable():
            return
        self._flush_edit()
        before = self.graph.to_dict()
        for node_id in self.selected:
            self.graph.disconnect(node_id)
        self.connecting = None
        self._record(before)

    def _delete(self) -> str:
        if not self._editable():
            return "break"
        self._flush_edit()
        before = self.graph.to_dict()
        if self.selected_edge is not None:
            if self.selected_edge in self.graph.edges:
                self.graph.edges.remove(self.selected_edge)
        else:
            for node_id in self.selected:
                self.graph.disconnect(node_id)
                del self.graph.nodes[node_id]
            self.selected.clear()
        self.selected_edge = None
        self.connecting = None
        self._record(before)
        self._inspect()
        return "break"

    def _select_all(self, event=None) -> str:
        self.selected = set(self.graph.nodes)
        self.selected_edge = None
        self._draw()
        self._inspect()
        return "break"

    def _copy_document(self) -> dict:
        return {
            "version": 1,
            "nodes": [
                n for n in self.graph.to_dict()["nodes"] if n["id"] in self.selected
            ],
            "edges": [
                [a, b]
                for a, b in self.graph.edges
                if a in self.selected and b in self.selected
            ],
        }

    def _copy(self) -> str:
        self._flush_edit()
        if self.selected:
            self.clipboard_clear()
            self.clipboard_append(json.dumps(self._copy_document()))
            self.status.set(f"Copied {len(self.selected)} node(s).")
        return "break"

    def _paste(self) -> str:
        if not self._editable():
            return "break"
        try:
            data = Workflow.from_dict(json.loads(self.clipboard_get()))
        except (tk.TclError, ValueError) as error:
            self.status.set(f"Clipboard does not contain workflow nodes: {error}")
            return "break"
        self._insert_copy(data)
        return "break"

    def _duplicate(self) -> str:
        if self.selected and self._editable():
            self._insert_copy(Workflow.from_dict(self._copy_document()))
        return "break"

    def _insert_copy(self, source: Workflow) -> None:
        self._flush_edit()
        before = self.graph.to_dict()
        mapping = {}
        for original in source.nodes.values():
            node = self.graph.add_node(
                original.kind, min(10000, original.x + 40), min(10000, original.y + 40)
            )
            node.settings = original.settings.copy()
            mapping[original.id] = node.id
        for a, b in source.edges:
            self.graph.connect(mapping[a], mapping[b])
        self.selected = set(mapping.values())
        self.selected_edge = None
        self._record(before)
        self._inspect()

    def _arrange(self) -> None:
        if not self._editable():
            return
        self._flush_edit()
        before = self.graph.to_dict()
        parents = {b: a for a, b in self.graph.edges}
        levels = {}
        for node_id in self.graph.nodes:
            current, depth = node_id, 0
            while current in parents:
                current = parents[current]
                depth += 1
            levels[node_id] = depth
        rows = {}
        for node_id, depth in sorted(
            levels.items(), key=lambda item: (item[1], item[0])
        ):
            row = rows.get(depth, 0)
            node = self.graph.nodes[node_id]
            node.x, node.y = min(10000, 50 + 280 * depth), min(10000, 60 + row * 150)
            rows[depth] = row + 1
        self._record(before)
        self._fit_all()

    def _can_discard(self) -> bool:
        self._flush_edit()
        if not self.dirty:
            return True
        choice = messagebox.askyesnocancel(
            "Unsaved workflow", "Save changes before continuing?", parent=self
        )
        if choice is None:
            return False
        return self._save() if choice else True

    def _new(self) -> None:
        if self._editable() and self._can_discard():
            self._new_graph()

    def _open(self, path: Optional[Path] = None) -> None:
        if not self._editable() or not self._can_discard():
            return
        if path is None:
            filename = filedialog.askopenfilename(
                parent=self, filetypes=[("Workflow JSON", "*.json")]
            )
            if not filename:
                return
            path = Path(filename)
        try:
            path = path.resolve()
            graph = Workflow.from_dict(json.loads(path.read_text(encoding="utf-8")))
            # Absolute references preserve semantics across Save As and undo.
            for node in graph.nodes.values():
                if node.settings.get("path"):
                    node.settings["path"] = str(
                        resolve_path(node.settings["path"], path.parent)
                    )
        except (OSError, ValueError, RuntimeError) as error:
            messagebox.showerror("Cannot open workflow", str(error), parent=self)
            return
        self._flush_edit()
        self.graph = graph
        self.workflow_path = path
        self.base_dir = path.parent
        self._reset_document()
        self._remember(path)
        self._fit_all()
        self.status.set(f"Opened {path.name}.")

    def _save(self) -> bool:
        if self.workflow_path is None:
            return self._save_as()
        return self._save_to(self.workflow_path)

    def _save_as(self) -> bool:
        if self.closing:
            return False
        filename = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".json",
            initialdir=str(
                self.workflow_path.parent if self.workflow_path else self.base_dir
            ),
            initialfile=self.workflow_path.name
            if self.workflow_path
            else "workflow.json",
            filetypes=[("Workflow JSON", "*.json")],
        )
        return self._save_to(Path(filename)) if filename else False

    def _save_to(self, path: Path) -> bool:
        self._flush_edit()
        try:
            path = path.resolve()
            snapshot = Workflow.from_dict(self.graph.to_dict())
            for node in snapshot.nodes.values():
                if node.settings.get("path"):
                    node.settings["path"] = str(
                        resolve_path(node.settings["path"], self.base_dir)
                    )
            save_workflow(path, snapshot)
        except (OSError, ValueError, RuntimeError) as error:
            messagebox.showerror("Cannot save workflow", str(error), parent=self)
            return False
        self.workflow_path = path
        self.saved_graph = self.graph.to_dict()
        self._update_title()
        self._remember(path)
        self.status.set(f"Saved {path.name}.")
        return True

    def _append_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        if int(self.log.index("end-1c").split(".")[0]) > 1000:
            self.log.delete("1.0", "100.0")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _preview(self) -> None:
        if len(self.selected) != 1:
            self.status.set("Select one node to preview.")
            return
        self.inspector_tabs.select(1)
        self._start_run(next(iter(self.selected)))

    def _run(self) -> None:
        self._start_run()

    def _start_run(self, target: Optional[int] = None) -> None:
        if self.running:
            return
        self._flush_edit()
        try:
            snapshot = Workflow.from_dict(self.graph.to_dict())
            nodes = snapshot.ordered_nodes(target)
        except ValueError as error:
            messagebox.showerror("Incomplete workflow", str(error), parent=self)
            return
        self.stop.clear()
        self.running = True
        self.states = {n.id: "queued" for n in nodes}
        self.previews.clear()
        self.run_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.preview_button.configure(state="disabled")
        self._inspect()
        self._draw()
        self.status.set("Previewing upstream (no writes)…" if target else "Running…")
        self._append_log("--- Preview started ---" if target else "--- Run started ---")
        base = self.base_dir

        def worker() -> None:
            outcome = "Preview complete." if target else "Workflow complete."
            try:
                run_workflow(
                    snapshot,
                    base,
                    self.stop,
                    lambda text: self.messages.put(("log", text)),
                    lambda kind, payload: self.messages.put((kind, payload)),
                    target,
                )
                if self.stop.is_set():
                    outcome = "Cancelled between operations. Completed writes are kept."
            except (OSError, ValueError, RuntimeError) as error:
                outcome = f"Failed: {error}"
                self.messages.put(("log", outcome))
            finally:
                self.messages.put(("finished", outcome))

        self.worker = threading.Thread(target=worker, daemon=False)
        self.worker.start()

    def _poll_messages(self) -> None:
        self.poll_id = None
        changed = False
        for _ in range(150):
            try:
                kind, payload = self.messages.get_nowait()
            except queue.Empty:
                break
            changed = True
            if kind == "log":
                self._append_log(payload)
            elif kind == "state":
                self.states[payload["id"]] = payload["state"]
            elif kind == "preview":
                self.previews[payload["id"]] = payload
            elif kind == "finished":
                self.running = False
                for node_id, state in self.states.items():
                    if state == "queued":
                        self.states[node_id] = (
                            "cancelled" if self.stop.is_set() else "skipped"
                        )
                self.run_button.configure(state="normal")
                self.cancel_button.configure(state="disabled")
                self.preview_button.configure(state="normal")
                self.status.set(payload)
                self._inspect()
        if changed:
            self._show_preview()
            self._draw()
        self.poll_id = self.after(50, self._poll_messages)

    def _close(self) -> None:
        if not self._can_discard():
            return
        self.closing = True
        self.stop.set()
        if self.edit_id is not None:
            self.after_cancel(self.edit_id)
            self.edit_id = None
        if self.poll_id is not None:
            self.after_cancel(self.poll_id)
            self.poll_id = None
        # The worker never calls Tk; it finishes the current I/O operation safely.
        self.destroy()


def main() -> None:
    """Launch the standalone editor."""
    WorkflowEditor().mainloop()


if __name__ == "__main__":
    main()

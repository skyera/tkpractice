"""Build and run a visual text workflow with draggable nodes and connecting wires.

Run ``python workflow_editor.py`` or launch it through run_practice.py.
Connect one Read Text node through Replace Text nodes to one Save File node.
Workflows save as JSON. Relative file paths resolve beside that JSON file (or
the script for a new workflow). Only the standard library is required.
"""

import json
import math
import queue
import tempfile
import threading
import tkinter as tk
from dataclasses import asdict, dataclass, field
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable

NODE_WIDTH = 190
NODE_HEIGHT = 90
KINDS = ("Read Text", "Replace Text", "Save File")
COLORS = {"Read Text": "#256d85", "Replace Text": "#8056a5", "Save File": "#387657"}
FIELDS = {
    "Read Text": ("path",),
    "Replace Text": ("find", "replace"),
    "Save File": ("path",),
}


@dataclass
class Node:
    """A block's stable identity, canvas position, and editable parameters."""

    id: int
    kind: str
    x: float
    y: float
    settings: dict = field(default_factory=dict)


class Workflow:
    """Manage a graph with at most one incoming and outgoing wire per node."""

    def __init__(self) -> None:
        self.nodes = {}
        self.edges = []

    def add_node(self, kind: str, x: float, y: float) -> Node:
        """Add a supported node with empty parameters."""
        if kind not in KINDS:
            raise ValueError("Unknown node type.")
        node_id = max(self.nodes, default=0) + 1
        node = Node(node_id, kind, x, y, dict.fromkeys(FIELDS[kind], ""))
        self.nodes[node_id] = node
        return node

    def connect(self, source: int, target: int) -> None:
        """Connect compatible free ports, rejecting cycles and branching."""
        if source not in self.nodes or target not in self.nodes:
            raise ValueError("Both nodes must exist.")
        if source == target:
            raise ValueError("A node cannot connect to itself.")
        if self.nodes[source].kind == "Save File":
            raise ValueError("Save File has no output.")
        if self.nodes[target].kind == "Read Text":
            raise ValueError("Read Text has no input.")
        if any(a == source or b == target for a, b in self.edges):
            raise ValueError("That port is occupied. Disconnect its node first.")
        following = dict(self.edges)
        current = target
        while current in following:
            current = following[current]
            if current == source:
                raise ValueError("Connections cannot form a cycle.")
        self.edges.append((source, target))

    def disconnect(self, node_id: int) -> None:
        """Remove all wires touching a node."""
        self.edges = [(a, b) for a, b in self.edges if node_id not in (a, b)]

    def ordered_nodes(self) -> list:
        """Validate one complete chain containing every node before execution."""
        readers = [n for n in self.nodes.values() if n.kind == "Read Text"]
        writers = [n for n in self.nodes.values() if n.kind == "Save File"]
        if len(readers) != 1 or len(writers) != 1:
            raise ValueError("Use exactly one Read Text and one Save File node.")
        following = dict(self.edges)
        result = []
        current = readers[0]
        visited = set()
        while current.id not in visited:
            visited.add(current.id)
            result.append(current)
            if current.id not in following:
                break
            current = self.nodes[following[current.id]]
        if len(visited) != len(self.nodes) or result[-1].kind != "Save File":
            raise ValueError("Connect every node into one Read → Replace → Save chain.")
        for node in result:
            required = "find" if node.kind == "Replace Text" else "path"
            if not node.settings[required]:
                raise ValueError(f"Node {node.id} ({node.kind}) needs {required}.")
        return result

    def to_dict(self) -> dict:
        """Return a portable JSON document, including incomplete workflows."""
        return {
            "version": 1,
            "nodes": [asdict(node) for node in self.nodes.values()],
            "edges": [list(edge) for edge in self.edges],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Workflow":
        """Validate a document before replacing the current editor graph."""
        if not isinstance(data, dict) or data.get("version") != 1:
            raise ValueError("Expected a version 1 workflow document.")
        nodes, edges = data.get("nodes"), data.get("edges")
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise ValueError("Nodes and edges must be lists.")
        graph = cls()
        for item in nodes:
            if not isinstance(item, dict):
                raise ValueError("Each node must be an object.")
            node_id, kind = item.get("id"), item.get("kind")
            if type(node_id) is not int or node_id <= 0 or node_id in graph.nodes:
                raise ValueError("Node IDs must be unique positive integers.")
            if not isinstance(kind, str) or kind not in KINDS:
                raise ValueError("Unknown node type.")
            x, y = item.get("x"), item.get("y")
            for coordinate in (x, y):
                if (
                    type(coordinate) not in (int, float)
                    or not 20 <= coordinate <= 10000
                    or not math.isfinite(coordinate)
                ):
                    raise ValueError("Node positions must be between 20 and 10000.")
            settings = item.get("settings")
            if not isinstance(settings, dict) or set(settings) != set(FIELDS[kind]):
                raise ValueError("Node parameters do not match its type.")
            if not all(isinstance(value, str) for value in settings.values()):
                raise ValueError("Node parameters must be strings.")
            graph.nodes[node_id] = Node(node_id, kind, x, y, settings.copy())
        for edge in edges:
            if (
                not isinstance(edge, list)
                or len(edge) != 2
                or any(type(value) is not int for value in edge)
            ):
                raise ValueError("Each wire must contain two node IDs.")
            graph.connect(*edge)
        return graph


def save_workflow(path: Path, graph: Workflow) -> None:
    """Atomically save graph data without truncating an existing workflow."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as target:
            temporary = Path(target.name)
            json.dump(graph.to_dict(), target, indent=2, ensure_ascii=False)
            target.write("\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def run_workflow(
    graph: Workflow,
    base_dir: Path,
    stop: threading.Event,
    report: Callable[[str], None],
) -> None:
    """Execute literal, case-sensitive replacements using UTF-8 file I/O.

    Outputs are exclusively created: existing files are never overwritten.
    Cancellation is checked between operations, before creating the output.
    """
    nodes = graph.ordered_nodes()
    text = ""
    for node in nodes:
        if stop.is_set():
            report("Cancelled before the next operation.")
            return
        report(f"Running #{node.id}: {node.kind}")
        if node.kind == "Replace Text":
            count = text.count(node.settings["find"])
            text = text.replace(node.settings["find"], node.settings["replace"])
            report(f"Replaced {count} occurrence(s).")
        else:
            path = Path(node.settings["path"]).expanduser()
            if not path.is_absolute():
                path = base_dir / path
            if node.kind == "Read Text":
                text = path.read_text(encoding="utf-8")
                report(f"Read {len(text)} characters from {path}.")
            else:
                with path.open("x", encoding="utf-8") as output:
                    output.write(text)
                report(f"Saved {len(text)} characters to {path}.")
    report("Workflow complete.")


class WorkflowEditor(tk.Tk):
    """A canvas graph editor with a parameter inspector and execution log."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Text Flow — Visual Workflow Editor")
        self.geometry("1120x740")
        self.minsize(900, 620)
        self.graph = Workflow()
        self.workflow_path = None
        self.selected = None
        self.connecting = None
        self.drag_start = None
        self.dirty = False
        self.running = False
        self.messages = queue.Queue()
        self.stop = threading.Event()
        self.poll_id = None
        self.variables = {}
        self.status = tk.StringVar(value="Ready")
        self._build_ui()
        self._new_graph()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.poll_id = self.after(75, self._poll_messages)

    def _build_ui(self) -> None:
        toolbar = ttk.Frame(self, padding=10)
        toolbar.pack(fill="x")
        for label, action in (
            ("New", self._new),
            ("Open…", self._open),
            ("Save…", self._save),
        ):
            ttk.Button(toolbar, text=label, command=action).pack(side="left", padx=3)
        for kind in KINDS:
            ttk.Button(
                toolbar, text=f"+ {kind}", command=lambda kind=kind: self._add(kind)
            ).pack(side="left", padx=3)
        self.run_button = ttk.Button(toolbar, text="▶ Run", command=self._run)
        self.run_button.pack(side="right", padx=3)
        self.cancel_button = ttk.Button(
            toolbar, text="Cancel", command=self.stop.set, state="disabled"
        )
        self.cancel_button.pack(side="right", padx=3)
        ttk.Label(
            self,
            text="Drag blocks to move • Click an output dot, then an input dot to "
            "connect • Select a block to edit",
            padding=(12, 0, 12, 8),
        ).pack(anchor="w")
        pane = ttk.Panedwindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True, padx=12)
        board = ttk.Frame(pane)
        board.rowconfigure(0, weight=1)
        board.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(board, bg="#18222f", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(board, command=self.canvas.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(
            board, orient="horizontal", command=self.canvas.xview
        )
        horizontal.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(
            yscrollcommand=vertical.set, xscrollcommand=horizontal.set
        )
        pane.add(board, weight=4)
        self.inspector = ttk.LabelFrame(pane, text="Node properties", padding=12)
        pane.add(self.inspector, weight=1)
        self.canvas.bind("<Button-1>", self._press)
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        self.canvas.bind("<Escape>", lambda event: self._cancel_connection())
        self.log = tk.Text(self, height=7, state="disabled", wrap="word")
        self.log.pack(fill="x", padx=12, pady=(10, 0))
        ttk.Label(self, textvariable=self.status, padding=10).pack(fill="x")

    def _new_graph(self) -> None:
        self.graph = Workflow()
        read = self.graph.add_node("Read Text", 50, 100)
        replace = self.graph.add_node("Replace Text", 310, 180)
        save = self.graph.add_node("Save File", 570, 100)
        self.graph.connect(read.id, replace.id)
        self.graph.connect(replace.id, save.id)
        self.workflow_path = None
        self.selected = None
        self.connecting = None
        self.dirty = False
        self._draw()
        self._inspect()
        self.status.set("Choose input and output paths, then enter text to replace.")

    def _draw(self) -> None:
        self.canvas.delete("all")
        for source, target in self.graph.edges:
            a, b = self.graph.nodes[source], self.graph.nodes[target]
            x1, y1 = a.x + NODE_WIDTH, a.y + NODE_HEIGHT / 2
            x2, y2 = b.x, b.y + NODE_HEIGHT / 2
            self.canvas.create_line(
                x1,
                y1,
                x1 + 70,
                y1,
                x2 - 70,
                y2,
                x2,
                y2,
                smooth=True,
                width=3,
                fill="#8faac4",
                arrow="last",
            )
        for node in self.graph.nodes.values():
            tag = f"node:{node.id}"
            outline = "#ffd166" if node.id == self.selected else "#576d82"
            self.canvas.create_rectangle(
                node.x,
                node.y,
                node.x + NODE_WIDTH,
                node.y + NODE_HEIGHT,
                fill="#253447",
                outline=outline,
                width=2,
                tags=(tag,),
            )
            self.canvas.create_rectangle(
                node.x + 2,
                node.y + 2,
                node.x + NODE_WIDTH - 2,
                node.y + 30,
                fill=COLORS[node.kind],
                outline="",
                tags=(tag,),
            )
            self.canvas.create_text(
                node.x + 12,
                node.y + 16,
                anchor="w",
                text=f"{node.id}  {node.kind}",
                fill="white",
                font=("Segoe UI", 10, "bold"),
                tags=(tag,),
            )
            summary = (
                node.settings["find"] or "Set replacement text"
                if node.kind == "Replace Text"
                else node.settings["path"] or "Choose a file"
            )
            self.canvas.create_text(
                node.x + 12,
                node.y + 57,
                anchor="w",
                text=summary.replace("\n", " ")[:24],
                fill="#c7d4e3",
                tags=(tag,),
            )
            for direction, x in (("in", node.x), ("out", node.x + NODE_WIDTH)):
                if (direction == "in" and node.kind == "Read Text") or (
                    direction == "out" and node.kind == "Save File"
                ):
                    continue
                y = node.y + NODE_HEIGHT / 2
                color = "#ffd166" if self.connecting == node.id else "#7de0ce"
                self.canvas.create_oval(
                    x - 7,
                    y - 7,
                    x + 7,
                    y + 7,
                    fill=color,
                    outline="#18222f",
                    tags=(tag, f"{direction}:{node.id}"),
                )
        bounds = self.canvas.bbox("all") or (0, 0, 900, 500)
        self.canvas.configure(
            scrollregion=(0, 0, max(1000, bounds[2] + 150), max(650, bounds[3] + 150))
        )

    def _press(self, event: tk.Event) -> None:
        self.canvas.focus_set()
        self.drag_start = None
        tags = self.canvas.gettags("current")
        for tag in tags:
            if tag.startswith("out:"):
                self.connecting = int(tag.split(":")[1])
                self.status.set("Click an input dot to finish; Escape cancels.")
                self._draw()
                return
            if tag.startswith("in:") and self.connecting is not None:
                try:
                    self.graph.connect(self.connecting, int(tag.split(":")[1]))
                except ValueError as error:
                    self.status.set(str(error))
                else:
                    self.dirty = True
                    self.status.set("Connected.")
                self.connecting = None
                self._draw()
                return
        self.connecting = None
        self.selected = next(
            (int(tag.split(":")[1]) for tag in tags if tag.startswith("node:")), None
        )
        if self.selected is not None:
            node = self.graph.nodes[self.selected]
            self.drag_start = (
                self.canvas.canvasx(event.x) - node.x,
                self.canvas.canvasy(event.y) - node.y,
            )
        self._draw()
        self._inspect()

    def _drag(self, event: tk.Event) -> None:
        if self.selected is not None and self.drag_start is not None:
            node = self.graph.nodes[self.selected]
            node.x = max(
                20, min(10000, self.canvas.canvasx(event.x) - self.drag_start[0])
            )
            node.y = max(
                20, min(10000, self.canvas.canvasy(event.y) - self.drag_start[1])
            )
            self.dirty = True
            self._draw()

    def _release(self, event: tk.Event) -> None:
        self.drag_start = None

    def _cancel_connection(self) -> None:
        self.connecting = None
        self.status.set("Connection cancelled.")
        self._draw()

    def _inspect(self) -> None:
        for widget in self.inspector.winfo_children():
            widget.destroy()
        self.variables = {}
        if self.selected is None:
            ttk.Label(self.inspector, text="Select a block to edit.").pack(anchor="w")
            return
        node = self.graph.nodes[self.selected]
        ttk.Label(self.inspector, text=f"#{node.id} {node.kind}").pack(
            anchor="w", pady=8
        )
        for key in FIELDS[node.kind]:
            ttk.Label(self.inspector, text=key.title()).pack(anchor="w", pady=(8, 2))
            variable = tk.StringVar(value=node.settings[key])
            self.variables[key] = variable
            ttk.Entry(self.inspector, textvariable=variable, width=26).pack(fill="x")
            variable.trace_add(
                "write", lambda *args, key=key, var=variable: self._edit(key, var.get())
            )
        if "path" in FIELDS[node.kind]:
            ttk.Button(self.inspector, text="Browse…", command=self._browse).pack(
                pady=8
            )
        ttk.Button(self.inspector, text="Disconnect", command=self._disconnect).pack(
            fill="x", pady=(20, 6)
        )
        ttk.Button(self.inspector, text="Delete Node", command=self._delete).pack(
            fill="x"
        )
        ttk.Label(
            self.inspector,
            text="UTF-8 text. Replacements are literal and case-sensitive. "
            "Choose a new output filename; existing files are preserved.",
            wraplength=210,
        ).pack(anchor="w", pady=16)

    def _edit(self, key: str, value: str) -> None:
        if self.selected in self.graph.nodes:
            self.graph.nodes[self.selected].settings[key] = value
            self.dirty = True
            self._draw()

    def _browse(self) -> None:
        node = self.graph.nodes[self.selected]
        base = (
            self.workflow_path.parent if self.workflow_path else Path(__file__).parent
        )
        options = {"parent": self, "initialdir": str(base)}
        if node.kind == "Read Text":
            path = filedialog.askopenfilename(**options)
        else:
            path = filedialog.asksaveasfilename(defaultextension=".txt", **options)
        if path:
            self.variables["path"].set(path)

    def _add(self, kind: str) -> None:
        offset = len(self.graph.nodes) * 25
        node = self.graph.add_node(kind, 80 + offset, 60 + offset)
        self.selected = node.id
        self.dirty = True
        self._draw()
        self._inspect()

    def _disconnect(self) -> None:
        self.graph.disconnect(self.selected)
        self.connecting = None
        self.dirty = True
        self._draw()

    def _delete(self) -> None:
        self._disconnect()
        del self.graph.nodes[self.selected]
        self.selected = None
        self._draw()
        self._inspect()

    def _can_discard(self) -> bool:
        return not self.dirty or messagebox.askyesno(
            "Unsaved workflow", "Discard unsaved workflow changes?", parent=self
        )

    def _new(self) -> None:
        if self._can_discard():
            self._new_graph()

    def _open(self) -> None:
        if not self._can_discard():
            return
        filename = filedialog.askopenfilename(
            parent=self, filetypes=[("Workflow JSON", "*.json")]
        )
        if not filename:
            return
        try:
            path = Path(filename)
            graph = Workflow.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError) as error:
            messagebox.showerror("Cannot open workflow", str(error), parent=self)
            return
        self.graph = graph
        self.workflow_path = path
        self.selected = None
        self.connecting = None
        self.dirty = False
        self._draw()
        self._inspect()
        self.status.set(f"Opened {path.name}. Relative paths use {path.parent}.")

    def _save(self) -> None:
        filename = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".json",
            initialfile=self.workflow_path.name
            if self.workflow_path
            else "workflow.json",
            filetypes=[("Workflow JSON", "*.json")],
        )
        if not filename:
            return
        path = Path(filename)
        # Preserve relative file references when saving beside a different folder.
        base = (
            self.workflow_path.parent if self.workflow_path else Path(__file__).parent
        )
        try:
            snapshot = Workflow.from_dict(self.graph.to_dict())
            for node in snapshot.nodes.values():
                raw = node.settings.get("path")
                if raw and not Path(raw).expanduser().is_absolute():
                    node.settings["path"] = str((base / raw).resolve())
            save_workflow(path, snapshot)
        except (OSError, ValueError, RuntimeError) as error:
            messagebox.showerror("Cannot save workflow", str(error), parent=self)
            return
        self.graph = snapshot
        self.workflow_path = path
        self.dirty = False
        self._draw()
        self._inspect()
        self.status.set(f"Saved {path.name}.")

    def _append_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _run(self) -> None:
        if self.running:
            return
        try:
            snapshot = Workflow.from_dict(self.graph.to_dict())
            snapshot.ordered_nodes()
        except ValueError as error:
            messagebox.showerror("Incomplete workflow", str(error), parent=self)
            return
        base = (
            self.workflow_path.parent if self.workflow_path else Path(__file__).parent
        )
        self.stop.clear()
        self.running = True
        self.run_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.status.set("Running a snapshot; edits apply to the next run.")
        self._append_log("--- Run started ---")

        def worker() -> None:
            try:
                run_workflow(
                    snapshot,
                    base,
                    self.stop,
                    lambda text: self.messages.put(("log", text)),
                )
            except (OSError, ValueError) as error:
                self.messages.put(("log", f"Failed: {error}"))
            finally:
                self.messages.put(("finished", "Run finished; see log for details."))

        threading.Thread(target=worker, daemon=True).start()

    def _poll_messages(self) -> None:
        for _ in range(100):
            try:
                kind, text = self.messages.get_nowait()
            except queue.Empty:
                break
            if kind == "log":
                self._append_log(text)
            else:
                self.running = False
                self.run_button.configure(state="normal")
                self.cancel_button.configure(state="disabled")
                self.status.set(text)
        self.poll_id = self.after(75, self._poll_messages)

    def _close(self) -> None:
        if not self._can_discard():
            return
        self.stop.set()
        if self.poll_id is not None:
            self.after_cancel(self.poll_id)
            self.poll_id = None
        self.destroy()


def main() -> None:
    """Launch the standalone visual editor."""
    WorkflowEditor().mainloop()


if __name__ == "__main__":
    main()

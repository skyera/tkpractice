"""Graph, history, and execution helpers for the visual workflow editor."""

import json
import math
import os
import tempfile
import threading
from collections import deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Optional

NODE_WIDTH = 200
NODE_HEIGHT = 100
FIELDS = {
    "Read Text": ("path",),
    "Replace Text": ("find", "replace"),
    "Uppercase": (),
    "Lowercase": (),
    "Trim Whitespace": (),
    "Filter Lines": ("contains",),
    "Preview Text": (),
    "Save File": ("path",),
}
KINDS = tuple(FIELDS)
COLORS = {
    "Read Text": "#256d85",
    "Replace Text": "#8056a5",
    "Uppercase": "#8056a5",
    "Lowercase": "#8056a5",
    "Trim Whitespace": "#8056a5",
    "Filter Lines": "#a46527",
    "Preview Text": "#326ea8",
    "Save File": "#387657",
}
PREVIEW_LIMIT = 8000


@dataclass
class Node:
    """A block's identity, world position, and text parameters."""

    id: int
    kind: str
    x: float
    y: float
    settings: dict = field(default_factory=dict)


class Workflow:
    """An acyclic graph with branching outputs and one input per node."""

    def __init__(self) -> None:
        self.nodes = {}
        self.edges = []

    def add_node(self, kind: str, x: float, y: float) -> Node:
        """Create a supported node with empty parameters."""
        if kind not in KINDS:
            raise ValueError("Unknown node type.")
        node_id = max(self.nodes, default=0) + 1
        node = Node(node_id, kind, x, y, dict.fromkeys(FIELDS[kind], ""))
        self.nodes[node_id] = node
        return node

    def check_connection(self, source: int, target: int) -> None:
        """Raise a useful error if a proposed wire is incompatible."""
        if source not in self.nodes or target not in self.nodes:
            raise ValueError("Both nodes must exist.")
        if source == target:
            raise ValueError("A node cannot connect to itself.")
        if self.nodes[source].kind == "Save File":
            raise ValueError("Save File has no output.")
        if self.nodes[target].kind == "Read Text":
            raise ValueError("Read Text has no input.")
        if any(b == target for _, b in self.edges):
            raise ValueError("This input is occupied. Remove its wire first.")
        following = {}
        for a, b in self.edges:
            following.setdefault(a, []).append(b)
        pending = [target]
        visited = set()
        while pending:
            current = pending.pop()
            if current == source:
                raise ValueError("Connections cannot form a cycle.")
            if current not in visited:
                visited.add(current)
                pending.extend(following.get(current, ()))

    def connect(self, source: int, target: int) -> None:
        """Add a wire; outputs may connect to multiple different inputs."""
        self.check_connection(source, target)
        self.edges.append((source, target))

    def disconnect(self, node_id: int) -> None:
        """Remove all wires touching a node."""
        self.edges = [(a, b) for a, b in self.edges if node_id not in (a, b)]

    def ordered_nodes(self, target: Optional[int] = None) -> list:
        """Validate a complete graph, or just the ancestors of a preview target."""
        parents = {b: a for a, b in self.edges}
        required = set(self.nodes)
        if target is not None:
            if target not in self.nodes:
                raise ValueError("Select a node to preview.")
            required = {target}
            current = target
            while current in parents:
                current = parents[current]
                if current in required:
                    raise ValueError("Connections cannot form a cycle.")
                required.add(current)
        readers = [self.nodes[n] for n in required if self.nodes[n].kind == "Read Text"]
        if len(readers) != 1:
            raise ValueError("Use exactly one Read Text node per connected workflow.")
        children = {node_id: [] for node_id in required}
        for a, b in self.edges:
            if a in required and b in required:
                children[a].append(b)
        pending = deque([readers[0].id])
        result = []
        visited = set()
        while pending:
            node_id = pending.popleft()
            if node_id in visited:
                raise ValueError("Connections cannot form a cycle.")
            visited.add(node_id)
            node = self.nodes[node_id]
            result.append(node)
            pending.extend(children[node_id])
        if visited != required:
            raise ValueError("Connect every node to the Read Text output.")
        for node in result:
            if target is None and not children[node.id]:
                if node.kind not in ("Save File", "Preview Text"):
                    raise ValueError(
                        f"End branch #{node.id} with Save File or Preview Text."
                    )
            error = parameter_error(node, preview=target is not None)
            if error:
                raise ValueError(f"Node {node.id} ({node.kind}) needs {error}.")
        return result

    def to_dict(self) -> dict:
        """Return version 1 JSON data, also supporting incomplete workflows."""
        return {
            "version": 1,
            "nodes": [asdict(node) for node in self.nodes.values()],
            "edges": [list(edge) for edge in self.edges],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Workflow":
        """Validate a JSON document without executing its contents."""
        if (
            not isinstance(data, dict)
            or type(data.get("version")) is not int
            or data["version"] != 1
        ):
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


def parameter_error(node: Node, preview: bool = False) -> str:
    """Return a short inline validation message, or an empty string."""
    if "path" in node.settings:
        if node.kind == "Save File" and preview:
            return ""
        if not node.settings["path"].strip():
            return "path"
        if "\x00" in node.settings["path"]:
            return "a path without null characters"
    if node.kind == "Replace Text" and not node.settings["find"]:
        return "find"
    if node.kind == "Filter Lines" and not node.settings["contains"]:
        return "contains"
    return ""


def write_json(path: Path, data: dict) -> None:
    """Atomically replace JSON so failed saves preserve the previous file."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as target:
            temporary = Path(target.name)
            json.dump(data, target, indent=2, ensure_ascii=False)
            target.write("\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def save_workflow(path: Path, graph: Workflow) -> None:
    """Save the graph atomically."""
    write_json(path, graph.to_dict())


def resolve_path(raw: str, base_dir: Path) -> Path:
    """Resolve user paths consistently for hints, previews, and execution."""
    path = Path(raw).expanduser()
    return (path if path.is_absolute() else base_dir / path).resolve()


def run_workflow(
    graph: Workflow,
    base_dir: Path,
    stop: threading.Event,
    report: Callable[[str], None],
    on_event: Optional[Callable[[str, dict], None]] = None,
    target: Optional[int] = None,
) -> dict:
    """Run branching text operations; preview ancestors without writing files.

    Each child receives its parent's output independently. Cancellation takes
    effect between operations. All output destinations are checked before work,
    and exclusive creation also prevents overwrites if a file appears later.
    """
    nodes = graph.ordered_nodes(target)
    parents = {b: a for a, b in graph.edges}
    outputs = {}

    def emit(kind: str, **payload) -> None:
        if on_event is not None:
            on_event(kind, payload)

    if stop.is_set():
        for node in nodes:
            emit("state", id=node.id, state="cancelled")
        report("Cancelled before the next operation.")
        return outputs

    if target is None:
        destinations = set()
        for node in nodes:
            if node.kind != "Save File":
                continue
            try:
                path = resolve_path(node.settings["path"], base_dir)
                key = os.path.normcase(str(path))
                if path.exists():
                    raise FileExistsError(f"Output already exists: {path}")
                if key in destinations:
                    raise ValueError(f"Two Save File nodes use the same output: {path}")
                if not path.parent.is_dir():
                    raise FileNotFoundError(
                        f"Output folder does not exist: {path.parent}"
                    )
                destinations.add(key)
            except (OSError, ValueError, RuntimeError):
                emit("state", id=node.id, state="failed")
                raise
    for index, node in enumerate(nodes):
        if stop.is_set():
            for remaining in nodes[index:]:
                emit("state", id=remaining.id, state="cancelled")
            report("Cancelled before the next operation.")
            return outputs
        emit("state", id=node.id, state="running")
        report(f"Running #{node.id}: {node.kind}")
        text = outputs.get(parents.get(node.id), "")
        try:
            if node.kind == "Read Text":
                path = resolve_path(node.settings["path"], base_dir)
                text = path.read_text(encoding="utf-8")
                report(f"Read {len(text)} characters from {path}.")
            elif node.kind == "Replace Text":
                count = text.count(node.settings["find"])
                text = text.replace(node.settings["find"], node.settings["replace"])
                report(f"Replaced {count} occurrence(s).")
            elif node.kind == "Uppercase":
                text = text.upper()
            elif node.kind == "Lowercase":
                text = text.lower()
            elif node.kind == "Trim Whitespace":
                text = "\n".join(line.strip() for line in text.split("\n"))
            elif node.kind == "Filter Lines":
                text = "".join(
                    line
                    for line in text.splitlines(keepends=True)
                    if node.settings["contains"] in line
                )
            elif node.kind == "Save File" and target is None:
                path = resolve_path(node.settings["path"], base_dir)
                with path.open("x", encoding="utf-8") as output:
                    output.write(text)
                report(f"Saved {len(text)} characters to {path}.")
        except (OSError, ValueError, RuntimeError):
            emit("state", id=node.id, state="failed")
            raise
        outputs[node.id] = text
        emit("preview", id=node.id, text=text[:PREVIEW_LIMIT], characters=len(text))
        emit("state", id=node.id, state="success")
    report("Preview complete; no files written." if target else "Workflow complete.")
    return outputs


class History:
    """Bounded graph snapshots; each edit or drag is one undoable action."""

    def __init__(self, limit: int = 100) -> None:
        self.undo_stack = []
        self.redo_stack = []
        self.limit = limit

    def record(self, before: dict, after: dict) -> bool:
        """Record a changed snapshot and discard the obsolete redo branch."""
        if before == after:
            return False
        self.undo_stack.append(before)
        self.undo_stack = self.undo_stack[-self.limit :]
        self.redo_stack.clear()
        return True

    def undo(self, current: dict) -> Optional[dict]:
        """Return the previous graph, remembering the current graph for redo."""
        if not self.undo_stack:
            return None
        self.redo_stack.append(current)
        return self.undo_stack.pop()

    def redo(self, current: dict) -> Optional[dict]:
        """Return the next graph and restore its undo entry."""
        if not self.redo_stack:
            return None
        self.undo_stack.append(current)
        return self.redo_stack.pop()

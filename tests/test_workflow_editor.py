"""Check workflow graph rules and file execution in isolated directories."""

import copy
import json
import tempfile
import threading
import unittest
from pathlib import Path

from workflow_editor import Workflow, run_workflow, save_workflow
from workflow_support import PREVIEW_LIMIT, History


class WorkflowTests(unittest.TestCase):
    """Exercise persistence and execution without starting a Tk mainloop."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.graph = Workflow()
        self.read = self.graph.add_node("Read Text", 50, 50)
        self.replace = self.graph.add_node("Replace Text", 300, 50)
        self.save = self.graph.add_node("Save File", 550, 50)
        self.read.settings["path"] = "input.txt"
        self.replace.settings.update(find="world", replace="Tkinter")
        self.save.settings["path"] = "output.txt"
        self.graph.connect(self.read.id, self.replace.id)
        self.graph.connect(self.replace.id, self.save.id)
        (self.directory / "input.txt").write_text("Hello world! 🌍", encoding="utf-8")
        self.messages = []

    def run_graph(self, stop: threading.Event = None) -> None:
        run_workflow(
            self.graph, self.directory, stop or threading.Event(), self.messages.append
        )

    def test_execution_uses_relative_paths_and_unicode(self) -> None:
        self.run_graph()
        output = (self.directory / "output.txt").read_text(encoding="utf-8")
        self.assertEqual(output, "Hello Tkinter! 🌍")
        self.assertIn("Replaced 1 occurrence(s).", self.messages)
        self.assertEqual(self.messages[-1], "Workflow complete.")

    def test_existing_output_and_input_are_preserved(self) -> None:
        output = self.directory / "output.txt"
        output.write_text("Keep me", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.run_graph()
        self.assertEqual(output.read_text(encoding="utf-8"), "Keep me")
        self.save.settings["path"] = "input.txt"
        with self.assertRaises(FileExistsError):
            self.run_graph()
        self.assertEqual(
            (self.directory / "input.txt").read_text(encoding="utf-8"),
            "Hello world! 🌍",
        )

    def test_empty_replacement_deletes_text_and_multiple_nodes_execute(self) -> None:
        self.graph.disconnect(self.save.id)
        other = self.graph.add_node("Replace Text", 400, 200)
        other.settings.update(find="!", replace="")
        self.graph.connect(self.replace.id, other.id)
        self.graph.connect(other.id, self.save.id)
        self.run_graph()
        self.assertEqual(
            (self.directory / "output.txt").read_text(encoding="utf-8"),
            "Hello Tkinter 🌍",
        )

    def test_cancellation_after_read_does_not_create_output(self) -> None:
        stop = threading.Event()

        def report(message: str) -> None:
            self.messages.append(message)
            if message.startswith("Read "):
                stop.set()

        run_workflow(self.graph, self.directory, stop, report)
        self.assertFalse((self.directory / "output.txt").exists())
        self.assertIn("Cancelled", self.messages[-1])

    def test_invalid_graph_is_rejected_before_reading(self) -> None:
        self.replace.settings["find"] = ""
        self.read.settings["path"] = "missing.txt"
        with self.assertRaisesRegex(ValueError, "needs find"):
            self.run_graph()
        self.assertFalse((self.directory / "output.txt").exists())
        self.replace.settings["find"] = "x"
        self.graph.disconnect(self.replace.id)
        with self.assertRaisesRegex(ValueError, "Connect every node"):
            self.run_graph()

    def test_connection_rules_and_cycle_detection(self) -> None:
        for source, target in (
            (self.read.id, self.save.id),
            (self.save.id, self.read.id),
            (self.replace.id, self.replace.id),
            (999, self.save.id),
        ):
            with self.subTest(source=source, target=target):
                with self.assertRaises(ValueError):
                    self.graph.connect(source, target)
        graph = Workflow()
        a = graph.add_node("Replace Text", 50, 50)
        b = graph.add_node("Replace Text", 300, 50)
        graph.connect(a.id, b.id)
        with self.assertRaisesRegex(ValueError, "cycle"):
            graph.connect(b.id, a.id)

    def test_json_round_trip_and_snapshot_independence(self) -> None:
        path = self.directory / "flow.json"
        save_workflow(path, self.graph)
        loaded = Workflow.from_dict(json.loads(path.read_text(encoding="utf-8")))
        self.assertEqual(loaded.to_dict(), self.graph.to_dict())
        loaded.nodes[self.replace.id].settings["replace"] = "Different"
        self.assertEqual(self.replace.settings["replace"], "Tkinter")

    def test_branch_outputs_do_not_modify_their_siblings(self) -> None:
        upper = self.graph.add_node("Uppercase", 300, 200)
        second_save = self.graph.add_node("Save File", 550, 200)
        second_save.settings["path"] = "upper.txt"
        self.graph.connect(self.read.id, upper.id)
        self.graph.connect(upper.id, second_save.id)
        self.run_graph()
        self.assertEqual(
            (self.directory / "upper.txt").read_text(encoding="utf-8"),
            "HELLO WORLD! 🌍",
        )
        self.assertEqual(
            (self.directory / "output.txt").read_text(encoding="utf-8"),
            "Hello Tkinter! 🌍",
        )

    def test_output_conflicts_are_checked_before_any_file_is_written(self) -> None:
        second = self.graph.add_node("Save File", 550, 200)
        self.graph.connect(self.read.id, second.id)
        for path in ("output.txt", "occupied.txt"):
            with self.subTest(path=path):
                second.settings["path"] = path
                (self.directory / "occupied.txt").write_text("Keep", encoding="utf-8")
                with self.assertRaises((ValueError, FileExistsError)):
                    self.run_graph()
                self.assertFalse((self.directory / "output.txt").exists())

    def test_preview_evaluates_only_ancestors_and_never_writes(self) -> None:
        self.save.settings["path"] = ""
        invalid = self.graph.add_node("Replace Text", 700, 400)
        self.assertFalse(invalid.settings["find"])
        outputs = run_workflow(
            self.graph,
            self.directory,
            threading.Event(),
            self.messages.append,
            target=self.save.id,
        )
        self.assertEqual(outputs[self.save.id], "Hello Tkinter! 🌍")
        self.assertNotIn(invalid.id, outputs)
        self.assertFalse((self.directory / "output.txt").exists())
        self.assertEqual(self.messages[-1], "Preview complete; no files written.")

    def test_new_text_nodes_and_preview_terminal(self) -> None:
        graph = Workflow()
        read = graph.add_node("Read Text", 50, 50)
        read.settings["path"] = "input.txt"
        (self.directory / "input.txt").write_text(
            "  keep Me  \n  discard  \n  KEEP too  \n", encoding="utf-8"
        )
        previous = read
        for kind in (
            "Trim Whitespace",
            "Uppercase",
            "Filter Lines",
            "Lowercase",
            "Preview Text",
        ):
            node = graph.add_node(kind, 300, 50)
            if kind == "Filter Lines":
                node.settings["contains"] = "KEEP"
            graph.connect(previous.id, node.id)
            previous = node
        events = []
        outputs = run_workflow(
            graph,
            self.directory,
            threading.Event(),
            self.messages.append,
            lambda kind, payload: events.append((kind, payload)),
        )
        self.assertEqual(outputs[previous.id], "keep me\nkeep too\n")
        self.assertEqual(events[-1], ("state", {"id": previous.id, "state": "success"}))

    def test_failure_and_cancel_events_identify_nodes(self) -> None:
        self.read.settings["path"] = "missing.txt"
        events = []
        with self.assertRaises(FileNotFoundError):
            run_workflow(
                self.graph,
                self.directory,
                threading.Event(),
                self.messages.append,
                lambda kind, payload: events.append((kind, payload)),
            )
        self.assertIn(("state", {"id": self.read.id, "state": "failed"}), events)
        self.read.settings["path"] = "input.txt"
        stop = threading.Event()
        events.clear()

        def receive(kind: str, payload: dict) -> None:
            events.append((kind, payload))
            if kind == "state" and payload["state"] == "success":
                stop.set()

        run_workflow(self.graph, self.directory, stop, self.messages.append, receive)
        self.assertIn(("state", {"id": self.save.id, "state": "cancelled"}), events)
        self.assertFalse((self.directory / "output.txt").exists())

    def test_preview_payloads_are_bounded_and_multiline_replacements_work(self) -> None:
        (self.directory / "input.txt").write_text("a\nb\n" * 5000, encoding="utf-8")
        self.replace.settings.update(find="a\nb", replace="multiline")
        events = []
        output = run_workflow(
            self.graph,
            self.directory,
            threading.Event(),
            self.messages.append,
            lambda kind, payload: events.append((kind, payload)),
            target=self.replace.id,
        )
        self.assertEqual(output[self.replace.id], "multiline\n" * 5000)
        previews = [payload for kind, payload in events if kind == "preview"]
        self.assertTrue(all(len(p["text"]) <= PREVIEW_LIMIT for p in previews))
        self.assertEqual(previews[-1]["characters"], 50000)

    def test_history_restores_snapshots_and_invalidates_redo_on_new_edit(self) -> None:
        history = History(limit=2)
        original = self.graph.to_dict()
        self.replace.settings["replace"] = "one"
        first = self.graph.to_dict()
        history.record(original, first)
        self.assertEqual(history.undo(first), original)
        self.assertEqual(history.redo(original), first)
        self.assertEqual(history.undo(first), original)
        history.record(original, {"different": True})
        self.assertIsNone(history.redo(original))
        history.record({"one": 1}, {"two": 2})
        history.record({"two": 2}, {"three": 3})
        self.assertEqual(len(history.undo_stack), 2)

    def test_malformed_documents_are_rejected(self) -> None:
        valid = self.graph.to_dict()
        documents = [None, [], {}, {"version": 1, "nodes": {}, "edges": []}]
        for field, value in (
            ("id", True),
            ("id", 0),
            ("kind", []),
            ("kind", "Unknown"),
            ("x", float("nan")),
            ("y", -20),
            ("settings", {"path": 4}),
        ):
            document = copy.deepcopy(valid)
            document["nodes"][0][field] = value
            documents.append(document)
        duplicate = copy.deepcopy(valid)
        duplicate["nodes"].append(duplicate["nodes"][0])
        documents.append(duplicate)
        for edge in ([1, 999], [1], [True, 2], [3, 1]):
            document = copy.deepcopy(valid)
            document["edges"] = [edge]
            documents.append(document)
        for document in documents:
            with self.subTest(document=document):
                with self.assertRaises(ValueError):
                    Workflow.from_dict(document)


if __name__ == "__main__":
    unittest.main()

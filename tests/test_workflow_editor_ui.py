"""Exercise real Tk widgets; skip these checks when no display is available."""

import json
import tempfile
import threading
import time
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

from workflow_editor import NODE_HEIGHT, NODE_WIDTH, WorkflowEditor
from workflow_support import run_workflow


class EditorTests(unittest.TestCase):
    """Check canvas gestures, document edits, and queued worker updates."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        try:
            self.app = WorkflowEditor(self.directory / "recent.json")
        except tk.TclError as error:
            self.skipTest(f"Tk display unavailable: {error}")
        self.errors = []
        self.app.report_callback_exception = lambda *error: self.errors.append(error)
        self.error_dialog = self.enterContext(
            patch("workflow_editor.messagebox.showerror")
        )
        self.enterContext(
            patch("workflow_editor.messagebox.askyesnocancel", return_value=False)
        )
        self.app.update()

    def tearDown(self) -> None:
        if hasattr(self, "app") and not self.app.closing:
            self.app.saved_graph = self.app.graph.to_dict()
            self.app._close()
        if hasattr(self, "app") and self.app.worker is not None:
            self.app.worker.join(timeout=3)
        self.assertEqual(getattr(self, "errors", []), [])

    def point(self, node_id: int, port: str = "body") -> tuple:
        node = self.app.graph.nodes[node_id]
        x = node.x + (NODE_WIDTH if port == "out" else 0 if port == "in" else 35)
        y = node.y + (15 if port == "body" else NODE_HEIGHT / 2)
        return tuple(round(value) for value in self.app._screen(x, y))

    def gesture(self, start: tuple, end: tuple, state: int = 0) -> None:
        self.app.canvas.event_generate(
            "<Button-1>", x=start[0], y=start[1], state=state
        )
        self.app.canvas.event_generate(
            "<B1-Motion>", x=end[0], y=end[1], state=state | 0x100
        )
        self.app.canvas.event_generate(
            "<ButtonRelease-1>", x=end[0], y=end[1], state=state
        )
        self.app.update()

    def prepare_files(self) -> None:
        self.app.base_dir = self.directory
        (self.directory / "input.txt").write_text("Hello world!", encoding="utf-8")
        self.app._edit(1, "path", "input.txt")
        self.app._edit(2, "find", "world")
        self.app._edit(2, "replace", "Tkinter")
        self.app._edit(3, "path", "output.txt")
        self.app._flush_edit()

    def finish_run(self) -> None:
        deadline = time.monotonic() + 5
        while self.app.running and time.monotonic() < deadline:
            self.app.update()
            time.sleep(0.01)
        self.assertFalse(self.app.running)
        self.app.update()

    def test_drag_snap_and_undo_redo(self) -> None:
        start = self.point(1)
        self.gesture(start, (start[0] + 47, start[1] + 39))
        node = self.app.graph.nodes[1]
        self.assertEqual(node.x % 20, 0)
        self.assertTrue(self.app.dirty)
        moved = self.app.graph.to_dict()
        self.app._undo()
        self.assertEqual(self.app.graph.nodes[1].x, 50)
        self.assertFalse(self.app.dirty)
        self.app._redo()
        self.assertEqual(self.app.graph.to_dict(), moved)

    def test_drag_connect_ghost_valid_targets_and_wire_removal(self) -> None:
        self.app.selected = {2}
        self.app._disconnect()
        start, end = self.point(1, "out"), self.point(2, "in")
        self.app.canvas.event_generate("<Button-1>", x=start[0], y=start[1])
        self.app.canvas.event_generate("<B1-Motion>", x=end[0], y=end[1])
        self.assertTrue(self.app.canvas.find_withtag("ghost"))
        self.assertEqual(self.app.connecting, 1)
        self.app.canvas.event_generate("<ButtonRelease-1>", x=end[0], y=end[1])
        self.app.update()
        self.assertIn((1, 2), self.app.graph.edges)
        self.assertIsNone(self.app.connecting)
        self.gesture(self.point(2, "out"), self.point(3, "in"))
        self.assertIn((2, 3), self.app.graph.edges)
        self.app.selected_edge = (1, 2)
        self.app._delete()
        self.assertNotIn((1, 2), self.app.graph.edges)
        self.assertIn((2, 3), self.app.graph.edges)
        self.app._undo()
        self.assertIn((1, 2), self.app.graph.edges)

    def test_multiselect_copy_paste_duplicate_and_delete(self) -> None:
        for node_id, state in ((1, 0), (2, 1)):
            point = self.point(node_id)
            self.gesture(point, point, state)
        self.assertEqual(self.app.selected, {1, 2})
        self.app._copy()
        self.app._paste()
        self.assertEqual(len(self.app.graph.nodes), 5)
        self.assertEqual(len(self.app.selected), 2)
        copied = self.app.selected.copy()
        self.assertTrue(
            any(a in copied and b in copied for a, b in self.app.graph.edges)
        )
        self.app._delete()
        self.assertEqual(len(self.app.graph.nodes), 3)
        self.app._undo()
        self.assertEqual(len(self.app.graph.nodes), 5)
        self.app.selected = {1}
        self.app._duplicate()
        self.assertEqual(len(self.app.graph.nodes), 6)

    def test_zoom_pan_fit_reset_and_collapsible_panel(self) -> None:
        anchor = self.app._world(200, 150)
        self.app._zoom_at(200, 150, 1.4)
        for actual, expected in zip(self.app._world(200, 150), anchor):
            self.assertAlmostEqual(actual, expected)
        old = self.app.offset.copy()
        self.app.canvas.event_generate("<Button-2>", x=50, y=50)
        self.app.canvas.event_generate("<B2-Motion>", x=80, y=90)
        self.app.canvas.event_generate("<ButtonRelease-2>", x=80, y=90)
        self.assertEqual(self.app.offset, [old[0] + 30, old[1] + 40])
        self.app._toggle_inspector()
        self.assertNotIn(str(self.app.inspector), self.app.main_pane.panes())
        self.app._toggle_inspector()
        self.assertIn(str(self.app.inspector), self.app.main_pane.panes())
        self.app.update()
        self.app._fit_all()
        for node in self.app.graph.nodes.values():
            x, y = self.app._screen(node.x, node.y)
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
        self.app._reset_view()
        self.assertEqual(self.app.zoom, 1.0)

    def test_multiline_properties_validation_and_grouped_history(self) -> None:
        self.app.selected = {2}
        self.app._inspect()
        self.assertIn("find", self.app.validation.get())
        text = self.app.text_fields["find"]
        text.insert("1.0", "two\nlines")
        self.app.update()
        self.assertEqual(self.app.graph.nodes[2].settings["find"], "two\nlines")
        self.assertFalse(self.app.validation.get())
        self.app._flush_edit()
        self.app._undo()
        self.assertEqual(self.app.graph.nodes[2].settings["find"], "")
        self.app._redo()
        self.assertEqual(self.app.graph.nodes[2].settings["find"], "two\nlines")

    def test_save_save_as_recent_files_and_undo_after_save(self) -> None:
        self.prepare_files()
        path = self.directory / "workflow.json"
        with patch(
            "workflow_editor.filedialog.asksaveasfilename", return_value=str(path)
        ):
            self.assertTrue(self.app._save())
        self.assertFalse(self.app.dirty)
        self.assertIn("workflow.json", self.app.title())
        self.app._edit(2, "replace", "Changed")
        self.app._flush_edit()
        self.assertIn("*", self.app.title())
        self.app._undo()
        self.assertFalse(self.app.dirty)
        with patch("workflow_editor.filedialog.asksaveasfilename") as dialog:
            self.assertTrue(self.app._save())
            dialog.assert_not_called()
        folder = self.directory / "elsewhere"
        folder.mkdir()
        other_path = folder / "copy.json"
        self.assertTrue(self.app._save_to(other_path))
        document = json.loads(other_path.read_text(encoding="utf-8"))
        self.assertEqual(
            Path(document["nodes"][0]["settings"]["path"]), self.directory / "input.txt"
        )
        self.app._open(other_path)
        self.assertEqual(self.app.base_dir, folder)
        self.assertEqual(self.app._read_recent()[0], str(other_path))

    def test_preview_then_run_and_failure_states(self) -> None:
        self.prepare_files()
        self.app.selected = {3}
        self.app._preview()
        self.finish_run()
        self.assertFalse((self.directory / "output.txt").exists())
        self.assertIn("Hello Tkinter!", self.app.preview_text.get("1.0", "end"))
        self.assertEqual(self.app.states[3], "success")
        self.app._run()
        self.finish_run()
        self.assertEqual(
            (self.directory / "output.txt").read_text(encoding="utf-8"),
            "Hello Tkinter!",
        )
        self.app._run()
        self.finish_run()
        self.assertEqual(self.app.states[3], "failed")
        self.assertTrue(self.app.status.get().startswith("Failed:"))

    def test_arrange_is_undoable_and_preserves_graph(self) -> None:
        before = self.app.graph.to_dict()
        self.app._arrange()
        self.assertEqual(self.app.graph.edges, [(1, 2), (2, 3)])
        self.assertLess(self.app.graph.nodes[1].x, self.app.graph.nodes[2].x)
        self.app._undo()
        self.assertEqual(self.app.graph.to_dict(), before)

    def test_marquee_selects_nodes_and_branching_runs_through_canvas_ports(
        self,
    ) -> None:
        self.prepare_files()
        self.app._add("Preview Text")
        preview_id = next(iter(self.app.selected))
        preview = self.app.graph.nodes[preview_id]
        preview.x, preview.y = 330, 350
        self.app._fit_all()
        self.app._draw()
        self.gesture(self.point(1, "out"), self.point(preview_id, "in"))
        self.assertIn((1, 2), self.app.graph.edges)
        self.assertIn((1, preview_id), self.app.graph.edges)
        # A marquee around both descendants selects them without touching the reader.
        left, top = self.app._screen(320, 170)
        right, bottom = self.app._screen(540, 460)
        self.gesture((round(left), round(top)), (round(right), round(bottom)))
        self.assertEqual(self.app.selected, {2, preview_id})
        self.app._run()
        self.finish_run()
        self.assertEqual(self.app.previews[preview_id]["text"], "Hello world!")
        self.assertEqual(self.app.previews[3]["text"], "Hello Tkinter!")

    def test_failed_open_keeps_document_and_save_cancel_keeps_dirty_state(self) -> None:
        self.prepare_files()
        before = self.app.graph.to_dict()
        bad = self.directory / "bad.json"
        bad.write_text("{}", encoding="utf-8")
        self.app._open(bad)
        self.error_dialog.assert_called_once()
        self.assertEqual(self.app.graph.to_dict(), before)
        with patch("workflow_editor.filedialog.asksaveasfilename", return_value=""):
            self.assertFalse(self.app._save())
        self.assertTrue(self.app.dirty)

    def test_close_signals_worker_and_cancels_timers(self) -> None:
        self.prepare_files()
        entered = threading.Event()
        release = threading.Event()

        def delayed(*args, **kwargs):
            entered.set()
            release.wait(timeout=2)
            return run_workflow(*args, **kwargs)

        with patch("workflow_editor.run_workflow", side_effect=delayed):
            self.app._run()
            self.assertTrue(entered.wait(timeout=2))
            self.app.saved_graph = self.app.graph.to_dict()
            self.app._close()
            release.set()
            self.app.worker.join(timeout=3)
        self.assertTrue(self.app.stop.is_set())
        self.assertIsNone(self.app.poll_id)
        self.assertIsNone(self.app.edit_id)
        self.assertFalse(self.app.worker.is_alive())
        self.assertFalse((self.directory / "output.txt").exists())


if __name__ == "__main__":
    unittest.main()

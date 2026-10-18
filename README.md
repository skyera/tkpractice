# tkpractice
Python tkinter

Run `python run_practice.py` to browse and launch the examples.

`python persistence_demo.py` demonstrates saving and reloading JSON preferences
and creating, reading, updating, and deleting SQLite tasks. It requires only the
Python standard library and stores data in `~/.tkpractice/persistence`. Settings
save when you click **Save Settings**; task changes save immediately.

`python workflow_editor.py` opens **Text Flow**, a visual text workflow editor
with a light canvas. The starting graph connects **Read Text → Replace Text →
Save File**. Select blocks to choose a UTF-8 input, enter search/replacement
text, and choose a new output filename, then click **Run Workflow**. No extra
packages are required.

- Drag an output dot to an input dot to connect nodes. Clicking the two ports
  also works. A temporary wire follows the pointer and valid inputs turn green.
  Outputs support multiple branches; each input accepts one wire. Cycles and
  merging inputs are rejected. Use one Read Text node and end each branch with
  Save File or Preview Text.
- Click a wire and press Delete, or right-click it and choose **Remove Wire**.
  **Disconnect** removes all wires touching the selected nodes.
- Zoom with the wheel, pan with a middle-button drag, and use **Fit All** or
  **Reset View**. **Snap** aligns moved nodes to the grid. **Arrange** lays out
  the graph from left to right.
- Shift-click nodes or drag a box over empty canvas space for multiple selection.
  Drag the selection to move it together. Delete removes selected nodes;
  Ctrl+C/Ctrl+V copy and paste nodes with their internal connections. Ctrl+D
  duplicates a selection. These node shortcuts apply while the canvas has focus.
- **Undo/Redo** (Ctrl+Z/Ctrl+Y) cover moves, connections, parameter edits, deletion,
  duplication, and arrangement. Typing is grouped into history entries after a
  short pause. Undoing to the saved state clears the unsaved-change marker.
- The properties panel supports multiline replacements, required-field feedback,
  and file-path hints. **Preview This Node** evaluates only its upstream nodes
  without writing files. The **Output Preview** tab shows up to 8,000 characters
  and the full character count. Editing the graph clears cached results.
- Add **Uppercase**, **Lowercase**, **Trim Whitespace** (each line), **Filter Lines**
  (case-sensitive contains), or **Preview Text** nodes from the toolbar menu.
  A Preview Text node can end a branch or pass its text to another node.
- Node labels and colors show queued, running, successful, failed, cancelled,
  and skipped operations. Execution runs in a worker thread. Cancel takes effect
  between operations; completed writes are kept. Graph editing pauses during
  execution, while selection and navigation remain available.
- **Save** (Ctrl+S) updates the current JSON workflow; **Save As** (Ctrl+Shift+S)
  writes a new file. The title shows the filename and an asterisk for changes.
  **File → Recent Files** remembers the last eight workflows in
  `~/.tkpractice/workflow_editor/recent.json`. Existing version 1 workflows open
  normally. Relative file references resolve beside loaded JSON files, or beside
  the script for a new workflow; saves export absolute references so Save As
  preserves their meaning. The properties panel shows the current base folder.
- **Properties** collapses or restores the inspector. Drag the horizontal divider
  to resize the log area, or the vertical divider to resize the inspector.

Existing output files are never overwritten. All destination paths are checked
before execution, including duplicate destinations across branches. Each child
receives its parent's text independently, so one branch cannot modify another.

Run regression checks with
`python -m unittest discover -s tests -v`.
GUI tests use temporary folders and skip when no Tk display is available.

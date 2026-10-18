# tkpractice
Python tkinter

Run `python run_practice.py` to browse and launch the examples.

`python persistence_demo.py` demonstrates saving and reloading JSON preferences
and creating, reading, updating, and deleting SQLite tasks. It requires only the
Python standard library and stores data in `~/.tkpractice/persistence`. Settings
save when you click **Save Settings**; task changes save immediately.

`python workflow_editor.py` opens a visual text workflow editor. Drag nodes to
move them and click an output dot followed by an input dot to connect them.
Select a node to set its parameters in the properties panel. The starting graph
already connects **Read Text → Replace Text → Save File**; choose a UTF-8 input
file, enter a search and replacement, and choose a new output filename, then
click **Run**. Existing output files are preserved. **Disconnect** removes a
node's wires so you can reconnect it; **New / Open / Save** manage JSON workflows.
Relative file paths resolve beside the workflow JSON file, or beside the script
for a new workflow. Execution runs in a background thread; cancellation takes
effect between operations. No additional packages are required.

Run regression checks with
`python -m unittest discover -s tests -v`.

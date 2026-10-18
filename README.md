# tkpractice
Python tkinter

Run `python run_practice.py` to browse and launch the examples.

`python persistence_demo.py` demonstrates saving and reloading JSON preferences
and creating, reading, updating, and deleting SQLite tasks. It requires only the
Python standard library and stores data in `~/.tkpractice/persistence`. Settings
save when you click **Save Settings**; task changes save immediately.

Run persistence regression checks with
`python -m unittest discover -s tests -v`.

"""
notebook_tabs.py - Demonstrates ttk.Notebook (tabbed interface).

Covers:
  - Creating tabs and adding content
  - Dynamic tab add / close / rename
  - <<NotebookTabChanged>> event
  - Tab state (normal, disabled, hidden)
  - Tab configuration (text, padding, sticky)
  - Practical tabbed text-editor example
"""

import tkinter as tk
from tkinter import ttk


class NotebookDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Notebook / Tabs Demo")
        self.geometry("750x520")
        self.minsize(650, 450)

        # ── Top-level notebook to organize demos ──
        self.main_nb = ttk.Notebook(self)
        self.main_nb.pack(fill="both", expand=True, padx=8, pady=8)

        self._build_basics_tab()
        self._build_state_tab()
        self._build_dynamic_tab()
        self._build_editor_tab()

    # ============================
    #  Tab 1 – Basics
    # ============================
    def _build_basics_tab(self):
        frame = ttk.Frame(self.main_nb, padding=12)
        self.main_nb.add(frame, text="Basics")

        ttk.Label(frame, text="ttk.Notebook Basics",
                  font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 8))

        info = (
            "• Create a Notebook:  nb = ttk.Notebook(parent)\n"
            "• Add a tab:  nb.add(child_frame, text='Tab Title')\n"
            "• Insert at position:  nb.insert(pos, child, text='...')\n"
            "• Select a tab:  nb.select(tab_id)\n"
            "• Get current tab:  nb.index('current')\n"
            "• Iterate tabs:  nb.tabs()  →  tuple of tab widget names\n"
            "• Remove a tab:  nb.forget(tab_id)\n"
            "• Hide a tab:  nb.hide(tab_id)\n"
            "• Configure tab:  nb.tab(tab_id, text='New', state='disabled')\n"
            "\n"
            "Events:\n"
            "  nb.bind('<<NotebookTabChanged>>', callback)\n"
            "  Fires whenever the selected tab changes."
        )
        text = tk.Text(frame, wrap="word", height=14, font=("Consolas", 10),
                       bg="#f4f4f4", relief="flat", padx=10, pady=10)
        text.insert("1.0", info)
        text.config(state="disabled")
        text.pack(fill="both", expand=True)

    # ============================
    #  Tab 2 – Tab States
    # ============================
    def _build_state_tab(self):
        frame = ttk.Frame(self.main_nb, padding=12)
        self.main_nb.add(frame, text="Tab States")

        ttk.Label(frame, text="Control tab states: normal / disabled / hidden",
                  font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 10))

        # Inner notebook with sample tabs
        self.state_nb = ttk.Notebook(frame)
        self.state_nb.pack(fill="both", expand=True, pady=(0, 10))

        colors = {"Red": "#e74c3c", "Green": "#27ae60", "Blue": "#2980b9",
                  "Purple": "#8e44ad"}
        self._state_tabs = {}
        for name, color in colors.items():
            tab = tk.Frame(self.state_nb, bg=color, height=120)
            tk.Label(tab, text=f"This is the {name} tab",
                     bg=color, fg="white",
                     font=("Arial", 14, "bold")).pack(expand=True)
            self.state_nb.add(tab, text=name)
            self._state_tabs[name] = tab

        # Controls
        ctrl = ttk.LabelFrame(frame, text="Set tab state", padding=8)
        ctrl.pack(fill="x")

        self._state_target = tk.StringVar(value="Red")
        self._state_action = tk.StringVar(value="normal")

        ttk.Label(ctrl, text="Tab:").grid(row=0, column=0, padx=(0, 4))
        ttk.Combobox(ctrl, textvariable=self._state_target,
                     values=list(colors.keys()), width=10,
                     state="readonly").grid(row=0, column=1, padx=4)

        ttk.Label(ctrl, text="State:").grid(row=0, column=2, padx=(12, 4))
        ttk.Combobox(ctrl, textvariable=self._state_action,
                     values=["normal", "disabled", "hidden"], width=10,
                     state="readonly").grid(row=0, column=3, padx=4)

        ttk.Button(ctrl, text="Apply",
                   command=self._apply_state).grid(row=0, column=4, padx=8)

        self._state_label = ttk.Label(ctrl, text="", foreground="gray")
        self._state_label.grid(row=0, column=5, padx=8)

    def _apply_state(self):
        tab_name = self._state_target.get()
        state = self._state_action.get()
        tab_widget = self._state_tabs[tab_name]

        if state == "hidden":
            self.state_nb.hide(tab_widget)
            self._state_label.config(text=f"{tab_name} hidden")
        else:
            # Re-add if it was hidden, then set state
            try:
                self.state_nb.index(tab_widget)
            except tk.TclError:
                # Tab was hidden/forgotten – re-add it
                self.state_nb.add(tab_widget, text=tab_name)
            self.state_nb.tab(tab_widget, state=state)
            self._state_label.config(text=f"{tab_name} → {state}")

    # ============================
    #  Tab 3 – Dynamic Tabs
    # ============================
    def _build_dynamic_tab(self):
        frame = ttk.Frame(self.main_nb, padding=12)
        self.main_nb.add(frame, text="Dynamic Tabs")

        ttk.Label(frame, text="Add, close, and rename tabs at runtime",
                  font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 10))

        # Toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=(0, 6))

        ttk.Button(toolbar, text="+ New Tab",
                   command=self._add_tab).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Close Current",
                   command=self._close_tab).pack(side="left", padx=2)

        ttk.Separator(toolbar, orient="vertical").pack(side="left",
                                                        fill="y", padx=8)

        ttk.Label(toolbar, text="Rename:").pack(side="left", padx=(0, 4))
        self._rename_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self._rename_var,
                  width=14).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Apply",
                   command=self._rename_tab).pack(side="left", padx=2)

        # Inner notebook
        self.dyn_nb = ttk.Notebook(frame)
        self.dyn_nb.pack(fill="both", expand=True)

        # Event label
        self._event_label = ttk.Label(frame, text="(tab events appear here)",
                                      foreground="gray")
        self._event_label.pack(anchor="w", pady=(6, 0))

        self.dyn_nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self._tab_counter = 0
        # Start with two tabs
        self._add_tab()
        self._add_tab()

    def _add_tab(self):
        self._tab_counter += 1
        tab = ttk.Frame(self.dyn_nb, padding=16)

        ttk.Label(tab, text=f"Tab #{self._tab_counter}",
                  font=("Arial", 16, "bold")).pack(expand=True)
        ttk.Label(tab, text="Try adding, closing, and renaming tabs "
                            "using the toolbar above.",
                  foreground="gray").pack()

        self.dyn_nb.add(tab, text=f"Tab {self._tab_counter}")
        self.dyn_nb.select(tab)

    def _close_tab(self):
        current = self.dyn_nb.select()
        if current:
            self.dyn_nb.forget(current)

    def _rename_tab(self):
        new_name = self._rename_var.get().strip()
        current = self.dyn_nb.select()
        if current and new_name:
            self.dyn_nb.tab(current, text=new_name)
            self._rename_var.set("")

    def _on_tab_changed(self, event):
        nb = event.widget
        try:
            idx = nb.index("current")
            name = nb.tab("current", "text")
            self._event_label.config(
                text=f"<<NotebookTabChanged>>  →  index={idx}, "
                     f"text=\"{name}\"")
        except tk.TclError:
            pass

    # ============================
    #  Tab 4 – Tabbed Editor
    # ============================
    def _build_editor_tab(self):
        frame = ttk.Frame(self.main_nb, padding=12)
        self.main_nb.add(frame, text="Mini Editor")

        ttk.Label(frame, text="Practical example: tabbed text editor",
                  font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 6))

        # Toolbar
        bar = ttk.Frame(frame)
        bar.pack(fill="x", pady=(0, 4))
        ttk.Button(bar, text="New File",
                   command=self._editor_new).pack(side="left", padx=2)
        ttk.Button(bar, text="Close File",
                   command=self._editor_close).pack(side="left", padx=2)
        ttk.Button(bar, text="Word Count",
                   command=self._editor_wc).pack(side="left", padx=2)

        self._wc_label = ttk.Label(bar, text="", foreground="gray")
        self._wc_label.pack(side="right", padx=8)

        # Editor notebook
        self.editor_nb = ttk.Notebook(frame)
        self.editor_nb.pack(fill="both", expand=True)

        self._file_counter = 0
        # Start with one file
        self._editor_new()

    def _editor_new(self):
        self._file_counter += 1
        tab = ttk.Frame(self.editor_nb)

        text = tk.Text(tab, wrap="word", font=("Consolas", 11),
                       undo=True, padx=8, pady=8,
                       insertbackground="#2980b9", selectbackground="#3498db")
        text.pack(fill="both", expand=True)
        text.insert("1.0", f"# Untitled-{self._file_counter}\n\n"
                           "Start typing here...\n")
        text.focus_set()

        # Store text widget reference on the frame
        tab.text_widget = text

        self.editor_nb.add(tab, text=f"Untitled-{self._file_counter}")
        self.editor_nb.select(tab)

    def _editor_close(self):
        current = self.editor_nb.select()
        if current:
            self.editor_nb.forget(current)

    def _editor_wc(self):
        current = self.editor_nb.select()
        if not current:
            return
        tab = self.nametowidget(current)
        content = tab.text_widget.get("1.0", "end-1c")
        words = len(content.split())
        chars = len(content)
        lines = content.count("\n") + 1
        self._wc_label.config(
            text=f"Lines: {lines}  |  Words: {words}  |  Chars: {chars}")


if __name__ == "__main__":
    NotebookDemo().mainloop()

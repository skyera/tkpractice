"""
run_practice.py - Interactive launcher, code viewer, and syntax highlighter for tkinter practice scripts.

Covers:
  - Dynamic discovery of .py scripts in the current directory (excluding itself)
  - Synced line-number sidebar matching code scroll position perfectly
  - Fast, regex-based Python syntax highlighter (keywords, definition names, strings, comments, numbers, builtins)
  - Asynchronous background script execution via subprocesses
  - Clean Dracula-inspired color theme for the code view
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import sys
import subprocess
import ast
import re
import bisect


class PracticeRunnerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Practice Launcher & Code Viewer")
        self.geometry("960x640")
        self.minsize(850, 500)

        # File exclusion list (exclude this script itself)
        self.self_filename = os.path.basename(__file__)

        # Compile syntax highlighter regex patterns (Dracula style)
        self.syntax_pattern = re.compile(
            r'(?P<comment>#[^\n]*)|'
            r'(?P<string>"{3}(?:.|\n)*?"{3}|\'{3}(?:.|\n)*?\'{3}|"[^"\n\\]*(?:\\.[^"\n\\]*)*"|\'[^\'\n\\]*(?:\\.[^\'\n\\]*)*\')|'
            r'\b(?P<keyword>def|class|import|from|return|if|else|elif|for|while|try|except|finally|with|as|lambda|global|nonlocal|pass|break|continue|in|is|not|and|or|True|False|None)\b|'
            r'\b(?P<builtin>print|len|int|str|float|list|dict|set|tuple|range|super|self|open)\b|'
            r'\b(?P<number>\d+)\b|'
            r'(?:def|class)\s+(?P<definition>\w+)'
        )

        self._build_ui()
        self._load_scripts()

    def _build_ui(self):
        # ── Top Panel: Search and Control ──
        top_frame = ttk.Frame(self, padding=12)
        top_frame.pack(fill="x")

        ttk.Label(top_frame, text="Practice Launcher & Viewer", font=("Arial", 13, "bold")).pack(side="left", padx=(0, 15))

        # Search Entry
        search_lbl = ttk.Label(top_frame, text="Filter:")
        search_lbl.pack(side="left", padx=5)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._filter_scripts())
        search_ent = ttk.Entry(top_frame, textvariable=self.search_var, width=24)
        search_ent.pack(side="left", padx=5)
        search_ent.focus_set()

        # Action Buttons
        self.run_btn = ttk.Button(top_frame, text="▶ Run Selected", command=self._run_selected_script, state="disabled")
        self.run_btn.pack(side="right", padx=5)

        ttk.Button(top_frame, text="🔄 Refresh List", command=self._load_scripts).pack(side="right", padx=5)

        # ── Middle Layout: Paned Window ──
        pane = ttk.PanedWindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Left Pane: Script list Treeview
        tree_frame = ttk.LabelFrame(pane, text="Available Scripts", padding=8)
        pane.add(tree_frame, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=("Filename", "Size"), show="headings", selectmode="browse")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("Filename", text="Script Name", anchor="w")
        self.tree.heading("Size", text="Size (KB)", anchor="e")

        self.tree.column("Filename", width=180, anchor="w")
        self.tree.column("Size", width=70, anchor="e")

        # Scrollbar for tree
        tree_scroll = ttk.Scrollbar(tree_frame, command=self.tree.yview)
        tree_scroll.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=tree_scroll.set)

        # Bind selection events
        self.tree.bind("<<TreeviewSelect>>", self._on_script_select)
        self.tree.bind("<Double-1>", lambda e: self._run_selected_script())

        # Right Pane: Notebook with Documentation and Source Code tabs
        details_frame = ttk.Frame(pane)
        pane.add(details_frame, weight=2)

        self.notebook = ttk.Notebook(details_frame)
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: Documentation (Docstring)
        doc_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(doc_tab, text="📋 Documentation")

        self.info_txt = tk.Text(doc_tab, wrap="word", bg="#fcfcfc", relief="flat", font=("Arial", 11))
        self.info_txt.pack(side="left", fill="both", expand=True)

        doc_scroll = ttk.Scrollbar(doc_tab, command=self.info_txt.yview)
        doc_scroll.pack(side="right", fill="y")
        self.info_txt.config(yscrollcommand=doc_scroll.set)

        # Tab 2: Source Code Viewer with Line Numbers
        code_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(code_tab, text="💻 Source Code")

        # Container to align scrollbars, line numbers, and text widget
        code_container = ttk.Frame(code_tab)
        code_container.pack(fill="both", expand=True)

        # Line numbers sidebar
        self.line_numbers = tk.Text(
            code_container, width=5, bg="#1e1e1e", fg="#6272a4",
            font=("Consolas", 10), relief="flat", wrap="none",
            state="disabled", borderwidth=0, highlightthickness=0
        )
        self.line_numbers.pack(side="left", fill="y")
        self.line_numbers.tag_configure("right", justify="right")

        # Main Code text area (Dracula colors)
        self.code_txt = tk.Text(
            code_container, wrap="none", bg="#1e1e1e", fg="#f8f8f2",
            insertbackground="#f8f8f2", font=("Consolas", 10), relief="flat",
            borderwidth=0, highlightthickness=0
        )
        self.code_txt.pack(side="left", fill="both", expand=True)

        # Set up Syntax highlighting tags
        self.code_txt.tag_configure("comment", foreground="#6272a4")
        self.code_txt.tag_configure("string", foreground="#f1fa8c")
        self.code_txt.tag_configure("keyword", foreground="#ff79c6", font=("Consolas", 10, "bold"))
        self.code_txt.tag_configure("builtin", foreground="#8be9fd")
        self.code_txt.tag_configure("number", foreground="#bd93f9")
        self.code_txt.tag_configure("definition", foreground="#50fa7b", font=("Consolas", 10, "bold"))

        # Scrollbar setup
        self.code_vscroll = ttk.Scrollbar(code_tab, orient="vertical", command=self._on_vscroll)
        self.code_vscroll.pack(side="right", fill="y")
        
        code_hscroll = ttk.Scrollbar(code_tab, orient="horizontal", command=self.code_txt.xview)
        code_hscroll.pack(side="bottom", fill="x")

        self.code_txt.config(yscrollcommand=self._on_code_yscroll, xscrollcommand=code_hscroll.set)

        # Bind mouse wheels on both to remain synced
        self.line_numbers.bind("<MouseWheel>", self._on_mousewheel)
        self.code_txt.bind("<MouseWheel>", self._on_mousewheel)

        # Status Bar
        self.status_lbl = ttk.Label(self, text="Ready. Double-click or select a script to run.", relief="sunken", padding=4, anchor="w")
        self.status_lbl.pack(fill="x")

    def _on_vscroll(self, *args):
        """Coordinates vertical scrollbar moves to scroll both sidebars simultaneously."""
        self.line_numbers.yview(*args)
        self.code_txt.yview(*args)

    def _on_code_yscroll(self, *args):
        """Syncs line number offset to match code scrollbar shifts."""
        self.code_vscroll.set(*args)
        self.line_numbers.yview("moveto", args[0])

    def _on_mousewheel(self, event):
        """Locks mousewheel scroll increments on both widgets simultaneously."""
        self.code_txt.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.line_numbers.yview("moveto", self.code_txt.yview()[0])
        return "break"  # Intercept native behavior to prevent desyncing

    def _load_scripts(self):
        """Loads and lists all python scripts in the directory."""
        self.all_scripts = []
        directory = os.path.dirname(os.path.abspath(__file__))

        try:
            for item in os.listdir(directory):
                if item.endswith(".py") and item != self.self_filename:
                    full_path = os.path.join(directory, item)
                    size_kb = os.path.getsize(full_path) / 1024.0
                    self.all_scripts.append({
                        "name": item,
                        "path": full_path,
                        "size": f"{size_kb:.1f} KB"
                    })

            # Sort alphabetically
            self.all_scripts.sort(key=lambda x: x["name"].lower())
            self._filter_scripts()

        except Exception as e:
            messagebox.showerror("Error Loading Scripts", f"An error occurred loading files:\n{e}")

    def _filter_scripts(self):
        """Filters the Treeview list based on the search query."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = self.search_var.get().strip().lower()

        for s in self.all_scripts:
            if not query or query in s["name"].lower():
                self.tree.insert("", "end", values=(s["name"], s["size"]))

        self.run_btn.config(state="disabled")
        
        # Clear Text fields
        for widget in (self.info_txt, self.code_txt, self.line_numbers):
            widget.config(state="normal")
            widget.delete("1.0", "end")
            widget.config(state="disabled")
            
        self.status_lbl.config(text=f"Loaded {len(self.all_scripts)} scripts.")

    def _get_docstring(self, filepath):
        """Safely parse and extract a script's top-level docstring without executing it."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filepath)
                doc = ast.get_docstring(tree)
                if doc:
                    return doc.strip()
        except Exception:
            pass
        return "No documentation docstring found in this script."

    def _get_source_code(self, filepath):
        """Safely reads the source code of the script."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error loading source code:\n{e}"

    def _highlight_source_code(self, code_text):
        """Runs the fast regex-based highlighting parser and tags segments."""
        # Compile cumulative offsets to convert character offsets to tk line/col
        line_offsets = [0]
        for line in code_text.splitlines(keepends=True):
            line_offsets.append(line_offsets[-1] + len(line))

        def offset_to_tk(offset):
            # Binary search to find the correct line index
            line_idx = bisect.bisect_right(line_offsets, offset) - 1
            col = offset - line_offsets[line_idx]
            return f"{line_idx + 1}.{col}"

        # Clean tags
        for tag in ["comment", "string", "keyword", "builtin", "number", "definition"]:
            self.code_txt.tag_remove(tag, "1.0", "end")

        # Map regex groups
        for match in self.syntax_pattern.finditer(code_text):
            for group_name in ["comment", "string", "keyword", "builtin", "number", "definition"]:
                start, end = match.span(group_name)
                if start != -1:
                    tk_start = offset_to_tk(start)
                    tk_end = offset_to_tk(end)
                    self.code_txt.tag_add(group_name, tk_start, tk_end)

    def _update_line_numbers_pane(self, line_count):
        """Updates and formats the line numbers sidebar."""
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        
        # Add line numbers formatted with right justification
        numbers_str = "\n".join(f"{i:>4} " for i in range(1, line_count + 1))
        self.line_numbers.insert("1.0", numbers_str, "right")
        self.line_numbers.config(state="disabled")

    def _on_script_select(self, event):
        sel = self.tree.selection()
        if not sel:
            self.run_btn.config(state="disabled")
            return

        filename = self.tree.item(sel[0], "values")[0]
        script_info = next((s for s in self.all_scripts if s["name"] == filename), None)
        
        if script_info:
            self.run_btn.config(state="normal")
            
            # Fetch content
            doc = self._get_docstring(script_info["path"])
            code = self._get_source_code(script_info["path"])

            # 1. Update Documentation Tab
            self.info_txt.config(state="normal")
            self.info_txt.delete("1.0", "end")
            self.info_txt.insert("1.0", f"File: {filename}\nSize: {script_info['size']}\n\nDocumentation:\n{'-'*30}\n\n{doc}")
            self.info_txt.config(state="disabled")

            # 2. Update Line Numbers Sidebar
            line_count = len(code.splitlines())
            self._update_line_numbers_pane(line_count)

            # 3. Update Source Code Tab & Highlight
            self.code_txt.config(state="normal")
            self.code_txt.delete("1.0", "end")
            self.code_txt.insert("1.0", code)
            
            self._highlight_source_code(code)
            self.code_txt.config(state="disabled")
            
            self.status_lbl.config(text=f"Selected {filename}. Ready to launch or view code.")

    def _run_selected_script(self):
        sel = self.tree.selection()
        if not sel:
            return

        filename = self.tree.item(sel[0], "values")[0]
        script_info = next((s for s in self.all_scripts if s["name"] == filename), None)

        if script_info:
            try:
                # Launch script in an independent background subprocess using sys.executable
                subprocess.Popen([sys.executable, script_info["path"]], cwd=os.path.dirname(script_info["path"]))
                self.status_lbl.config(text=f"Successfully launched {filename} in background.")
            except Exception as e:
                messagebox.showerror("Execution Error", f"Unable to run script '{filename}':\n{e}")


if __name__ == "__main__":
    PracticeRunnerApp().mainloop()

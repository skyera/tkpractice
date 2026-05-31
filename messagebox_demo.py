"""
Messagebox & Simpledialog Demo
===============================
Demonstrates every standard tkinter messagebox and simpledialog function.

Covered dialogs:
  Information dialogs:
    - messagebox.showinfo()
    - messagebox.showwarning()
    - messagebox.showerror()

  Question dialogs (return boolean or string):
    - messagebox.askyesno()       -> True / False
    - messagebox.askokcancel()    -> True / False
    - messagebox.askretrycancel() -> True / False
    - messagebox.askyesnocancel() -> True / False / None
    - messagebox.askquestion()    -> "yes" / "no"

  Input dialogs (return typed value or None on cancel):
    - simpledialog.askstring()    -> str or None
    - simpledialog.askinteger()   -> int or None
    - simpledialog.askfloat()     -> float or None

Each button triggers a dialog and logs the return value (with its Python
type) into a scrollable results area at the bottom of the window.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime


# ---------------------------------------------------------------------------
# Application class
# ---------------------------------------------------------------------------
class MessageboxDemoApp:
    """Main application demonstrating messagebox and simpledialog."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Messagebox & Simpledialog Demo")
        self.root.minsize(720, 620)

        # --- Style setup ---------------------------------------------------
        style = ttk.Style()
        style.configure("Group.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", padding=(8, 4))

        # --- Main container ------------------------------------------------
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top area: three LabelFrame groups side-by-side
        groups_frame = ttk.Frame(main_frame)
        groups_frame.pack(fill=tk.BOTH, expand=False)

        # Let the three columns share space equally
        groups_frame.columnconfigure(0, weight=1)
        groups_frame.columnconfigure(1, weight=1)
        groups_frame.columnconfigure(2, weight=1)

        # ---- Group 1: Information dialogs ---------------------------------
        info_group = ttk.LabelFrame(
            groups_frame, text="  Information Dialogs  ", style="Group.TLabelframe",
            padding=10,
        )
        info_group.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        ttk.Label(info_group, text="These dialogs display a message.\nReturn value: always 'ok'.").pack(
            anchor="w", pady=(0, 8)
        )

        ttk.Button(
            info_group, text="showinfo()",
            command=self._demo_showinfo,
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            info_group, text="showwarning()",
            command=self._demo_showwarning,
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            info_group, text="showerror()",
            command=self._demo_showerror,
        ).pack(fill=tk.X, pady=2)

        # ---- Group 2: Question dialogs ------------------------------------
        question_group = ttk.LabelFrame(
            groups_frame, text="  Question Dialogs  ", style="Group.TLabelframe",
            padding=10,
        )
        question_group.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        ttk.Label(question_group, text="These dialogs ask the user\na yes/no/ok/cancel question.").pack(
            anchor="w", pady=(0, 8)
        )

        ttk.Button(
            question_group, text="askyesno()",
            command=self._demo_askyesno,
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            question_group, text="askokcancel()",
            command=self._demo_askokcancel,
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            question_group, text="askretrycancel()",
            command=self._demo_askretrycancel,
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            question_group, text="askyesnocancel()",
            command=self._demo_askyesnocancel,
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            question_group, text="askquestion()",
            command=self._demo_askquestion,
        ).pack(fill=tk.X, pady=2)

        # ---- Group 3: Input dialogs (simpledialog) ------------------------
        input_group = ttk.LabelFrame(
            groups_frame, text="  Input Dialogs (simpledialog)  ", style="Group.TLabelframe",
            padding=10,
        )
        input_group.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        ttk.Label(input_group, text="These dialogs prompt for typed\ninput. Return None on cancel.").pack(
            anchor="w", pady=(0, 8)
        )

        ttk.Button(
            input_group, text="askstring()",
            command=self._demo_askstring,
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            input_group, text="askinteger()",
            command=self._demo_askinteger,
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            input_group, text="askfloat()",
            command=self._demo_askfloat,
        ).pack(fill=tk.X, pady=2)

        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # ---- Results area -------------------------------------------------
        results_label_frame = ttk.LabelFrame(
            main_frame, text="  Results Log  ", style="Group.TLabelframe", padding=8,
        )
        results_label_frame.pack(fill=tk.BOTH, expand=True)

        # Toolbar row: clear button + counter
        toolbar = ttk.Frame(results_label_frame)
        toolbar.pack(fill=tk.X, pady=(0, 4))

        self._counter_var = tk.StringVar(value="0 entries")
        ttk.Label(toolbar, textvariable=self._counter_var).pack(side=tk.LEFT)

        ttk.Button(toolbar, text="Clear Log", command=self._clear_log).pack(side=tk.RIGHT)

        # Scrollable text widget for results
        text_frame = ttk.Frame(results_label_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.results_text = tk.Text(
            text_frame, height=12, wrap=tk.WORD,
            font=("Consolas", 10), state=tk.DISABLED,
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            selectbackground="#264f78", selectforeground="#ffffff",
            relief=tk.FLAT, borderwidth=2,
        )
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure text tags for colour-coded output
        self.results_text.tag_configure("timestamp", foreground="#6a9955")   # green
        self.results_text.tag_configure("funcname", foreground="#569cd6")    # blue
        self.results_text.tag_configure("arrow", foreground="#808080")      # grey
        self.results_text.tag_configure("value_true", foreground="#4ec9b0") # teal
        self.results_text.tag_configure("value_false", foreground="#ce9178") # orange
        self.results_text.tag_configure("value_none", foreground="#d16969") # red
        self.results_text.tag_configure("value_str", foreground="#ce9178")  # orange
        self.results_text.tag_configure("value_num", foreground="#b5cea8")  # light green
        self.results_text.tag_configure("value_ok", foreground="#808080")   # grey

        self._entry_count = 0

    # -------------------------------------------------------------------
    # Logging helper
    # -------------------------------------------------------------------
    def _log_result(self, func_name: str, result) -> None:
        """Append a colour-coded result line to the log."""
        self._entry_count += 1
        self._counter_var.set(f"{self._entry_count} entr{'y' if self._entry_count == 1 else 'ies'}")

        timestamp = datetime.now().strftime("%H:%M:%S")
        type_name = type(result).__name__

        # Choose tag based on value
        if result is True:
            val_tag = "value_true"
        elif result is False:
            val_tag = "value_false"
        elif result is None:
            val_tag = "value_none"
        elif isinstance(result, str) and result == "ok":
            val_tag = "value_ok"
        elif isinstance(result, (int, float)):
            val_tag = "value_num"
        else:
            val_tag = "value_str"

        # Build the display string for the value
        display_value = repr(result)

        self.results_text.configure(state=tk.NORMAL)
        self.results_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.results_text.insert(tk.END, f"{func_name:<22s}", "funcname")
        self.results_text.insert(tk.END, " → ", "arrow")
        self.results_text.insert(tk.END, f"{display_value}  ", val_tag)
        self.results_text.insert(tk.END, f"({type_name})\n", "arrow")
        self.results_text.configure(state=tk.DISABLED)
        self.results_text.see(tk.END)

    def _clear_log(self) -> None:
        """Clear all entries from the results log."""
        self.results_text.configure(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.configure(state=tk.DISABLED)
        self._entry_count = 0
        self._counter_var.set("0 entries")

    # -------------------------------------------------------------------
    # Information dialog callbacks
    # -------------------------------------------------------------------
    def _demo_showinfo(self) -> None:
        """messagebox.showinfo — displays an informational message."""
        result = messagebox.showinfo(
            title="Information",
            message="This is an informational message.",
            detail="showinfo() always returns the string 'ok'.",
        )
        self._log_result("showinfo()", result)

    def _demo_showwarning(self) -> None:
        """messagebox.showwarning — displays a warning message."""
        result = messagebox.showwarning(
            title="Warning",
            message="This is a warning message.",
            detail="showwarning() always returns the string 'ok'.",
        )
        self._log_result("showwarning()", result)

    def _demo_showerror(self) -> None:
        """messagebox.showerror — displays an error message."""
        result = messagebox.showerror(
            title="Error",
            message="This is an error message.",
            detail="showerror() always returns the string 'ok'.",
        )
        self._log_result("showerror()", result)

    # -------------------------------------------------------------------
    # Question dialog callbacks
    # -------------------------------------------------------------------
    def _demo_askyesno(self) -> None:
        """messagebox.askyesno — Yes/No buttons, returns True or False."""
        result = messagebox.askyesno(
            title="Yes / No",
            message="Do you like tkinter?",
            detail="askyesno() returns True (Yes) or False (No).",
        )
        self._log_result("askyesno()", result)

    def _demo_askokcancel(self) -> None:
        """messagebox.askokcancel — OK/Cancel buttons, returns True or False."""
        result = messagebox.askokcancel(
            title="OK / Cancel",
            message="Proceed with the operation?",
            detail="askokcancel() returns True (OK) or False (Cancel).",
        )
        self._log_result("askokcancel()", result)

    def _demo_askretrycancel(self) -> None:
        """messagebox.askretrycancel — Retry/Cancel buttons, returns True or False."""
        result = messagebox.askretrycancel(
            title="Retry / Cancel",
            message="The operation failed. Retry?",
            detail="askretrycancel() returns True (Retry) or False (Cancel).",
        )
        self._log_result("askretrycancel()", result)

    def _demo_askyesnocancel(self) -> None:
        """messagebox.askyesnocancel — Yes/No/Cancel, returns True/False/None."""
        result = messagebox.askyesnocancel(
            title="Yes / No / Cancel",
            message="Save changes before closing?",
            detail="askyesnocancel() returns True (Yes), False (No), or None (Cancel).",
        )
        self._log_result("askyesnocancel()", result)

    def _demo_askquestion(self) -> None:
        """messagebox.askquestion — Yes/No buttons, returns 'yes' or 'no' strings."""
        result = messagebox.askquestion(
            title="Question",
            message="Is this a question?",
            detail="askquestion() returns the string 'yes' or 'no' (not bool!).",
        )
        self._log_result("askquestion()", result)

    # -------------------------------------------------------------------
    # Input dialog callbacks (simpledialog)
    # -------------------------------------------------------------------
    def _demo_askstring(self) -> None:
        """simpledialog.askstring — prompts for a string value."""
        result = simpledialog.askstring(
            title="Ask String",
            prompt="Enter your name:",
            initialvalue="World",
            parent=self.root,
        )
        self._log_result("askstring()", result)

    def _demo_askinteger(self) -> None:
        """simpledialog.askinteger — prompts for an integer with optional bounds."""
        result = simpledialog.askinteger(
            title="Ask Integer",
            prompt="Pick a number (1–100):",
            initialvalue=42,
            minvalue=1,
            maxvalue=100,
            parent=self.root,
        )
        self._log_result("askinteger()", result)

    def _demo_askfloat(self) -> None:
        """simpledialog.askfloat — prompts for a float with optional bounds."""
        result = simpledialog.askfloat(
            title="Ask Float",
            prompt="Enter a temperature (°C):",
            initialvalue=36.6,
            minvalue=-273.15,
            maxvalue=1000.0,
            parent=self.root,
        )
        self._log_result("askfloat()", result)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = MessageboxDemoApp(root)
    root.mainloop()

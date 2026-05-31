"""
grid_layout.py - Demonstrates the grid() layout manager.

Covers:
  - Basic row/column placement
  - columnspan and rowspan
  - sticky (N, S, E, W) for alignment
  - padx / pady / ipadx / ipady for spacing
  - columnconfigure / rowconfigure with weight for resizing
  - A practical form layout example
"""

import tkinter as tk
from tkinter import ttk


def main():
    root = tk.Tk()
    root.title("Grid Layout Demo")
    root.geometry("700x520")
    root.minsize(600, 480)

    # ── Notebook to organize demos into tabs ──
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=8, pady=8)

    # ============================
    #  Tab 1 – Basic Grid
    # ============================
    tab1 = ttk.Frame(notebook, padding=10)
    notebook.add(tab1, text="Basic Grid")

    tk.Label(tab1, text="Basic row / column placement",
             font=("Arial", 11, "bold")).grid(row=0, column=0,
                                               columnspan=3, pady=(0, 8))

    colors = [
        ("#e74c3c", "0,0"), ("#3498db", "0,1"), ("#2ecc71", "0,2"),
        ("#f39c12", "1,0"), ("#9b59b6", "1,1"), ("#1abc9c", "1,2"),
        ("#e67e22", "2,0"), ("#2c3e50", "2,1"), ("#d35400", "2,2"),
    ]
    for i, (color, pos) in enumerate(colors):
        r, c = divmod(i, 3)
        tk.Label(tab1, text=f"row={r} col={c}",
                 bg=color, fg="white", width=14, height=2,
                 font=("Arial", 10)).grid(row=r + 1, column=c,
                                          padx=4, pady=4)

    # ============================
    #  Tab 2 – Span & Sticky
    # ============================
    tab2 = ttk.Frame(notebook, padding=10)
    notebook.add(tab2, text="Span & Sticky")

    tk.Label(tab2, text="columnspan / rowspan / sticky",
             font=("Arial", 11, "bold")).grid(row=0, column=0,
                                               columnspan=3, pady=(0, 8))

    # columnspan example
    tk.Label(tab2, text="columnspan=2", bg="#2980b9", fg="white",
             height=2, font=("Arial", 10)).grid(row=1, column=0,
                                                  columnspan=2,
                                                  sticky="ew",
                                                  padx=4, pady=4)
    tk.Label(tab2, text="col=2", bg="#27ae60", fg="white",
             height=2, font=("Arial", 10)).grid(row=1, column=2,
                                                  sticky="ew",
                                                  padx=4, pady=4)

    # rowspan example
    tk.Label(tab2, text="rowspan=2", bg="#8e44ad", fg="white",
             width=12, font=("Arial", 10)).grid(row=2, column=0,
                                                  rowspan=2,
                                                  sticky="ns",
                                                  padx=4, pady=4)
    tk.Label(tab2, text="row=2, col=1", bg="#e74c3c", fg="white",
             width=12, height=2, font=("Arial", 10)).grid(row=2, column=1,
                                                           padx=4, pady=4)
    tk.Label(tab2, text="row=3, col=1", bg="#f39c12", fg="white",
             width=12, height=2, font=("Arial", 10)).grid(row=3, column=1,
                                                           padx=4, pady=4)

    # sticky demo
    tk.Label(tab2, text="sticky='w' (west/left)",
             bg="#16a085", fg="white",
             font=("Arial", 10)).grid(row=4, column=0, columnspan=3,
                                       sticky="w", padx=4, pady=4)
    tk.Label(tab2, text="sticky='e' (east/right)",
             bg="#c0392b", fg="white",
             font=("Arial", 10)).grid(row=5, column=0, columnspan=3,
                                       sticky="e", padx=4, pady=4)
    tk.Label(tab2, text="sticky='ew' (stretch horizontally)",
             bg="#2c3e50", fg="white",
             font=("Arial", 10)).grid(row=6, column=0, columnspan=3,
                                       sticky="ew", padx=4, pady=4)

    # Give columns equal weight so sticky stretching is visible
    for c in range(3):
        tab2.columnconfigure(c, weight=1)

    # ============================
    #  Tab 3 – Weight & Resize
    # ============================
    tab3 = ttk.Frame(notebook, padding=10)
    notebook.add(tab3, text="Weight & Resize")

    tk.Label(tab3, text="Resize the window to see weight in action",
             font=("Arial", 11, "bold")).grid(row=0, column=0,
                                               columnspan=3, pady=(0, 8))

    # Row of labels with different column weights
    info = [
        ("weight=0\n(fixed)", "#e74c3c", 0),
        ("weight=1", "#3498db", 1),
        ("weight=2\n(grows 2×)", "#2ecc71", 2),
    ]
    for col, (text, color, weight) in enumerate(info):
        tab3.columnconfigure(col, weight=weight)
        tk.Label(tab3, text=text, bg=color, fg="white",
                 font=("Arial", 10), height=3).grid(row=1, column=col,
                                                      sticky="ew",
                                                      padx=4, pady=4)

    # Row weights
    tab3.rowconfigure(2, weight=1)
    tk.Label(tab3, text="This row has weight=1 — it expands vertically",
             bg="#8e44ad", fg="white",
             font=("Arial", 10)).grid(row=2, column=0, columnspan=3,
                                       sticky="nsew", padx=4, pady=4)

    tab3.rowconfigure(3, weight=0)
    tk.Label(tab3, text="This row has weight=0 — fixed height",
             bg="#f39c12", fg="white",
             font=("Arial", 10)).grid(row=3, column=0, columnspan=3,
                                       sticky="ew", padx=4, pady=4)

    # ============================
    #  Tab 4 – Practical Form
    # ============================
    tab4 = ttk.Frame(notebook, padding=16)
    notebook.add(tab4, text="Form Example")

    tk.Label(tab4, text="Registration Form",
             font=("Arial", 13, "bold")).grid(row=0, column=0,
                                               columnspan=2, pady=(0, 12))

    fields = ["First Name", "Last Name", "Email", "Phone", "Address"]
    entries = {}
    for i, field in enumerate(fields):
        tk.Label(tab4, text=field + ":", anchor="e",
                 font=("Arial", 10)).grid(row=i + 1, column=0,
                                           sticky="e", padx=(0, 8), pady=4)
        ent = ttk.Entry(tab4, width=30)
        ent.grid(row=i + 1, column=1, sticky="ew", pady=4)
        entries[field] = ent

    # Gender with radio buttons spanning a row
    tk.Label(tab4, text="Gender:", anchor="e",
             font=("Arial", 10)).grid(row=len(fields) + 1, column=0,
                                       sticky="e", padx=(0, 8), pady=4)
    gender_frame = ttk.Frame(tab4)
    gender_frame.grid(row=len(fields) + 1, column=1, sticky="w", pady=4)
    gender_var = tk.StringVar(value="other")
    for g in ("Male", "Female", "Other"):
        ttk.Radiobutton(gender_frame, text=g, variable=gender_var,
                        value=g.lower()).pack(side="left", padx=(0, 12))

    # Agree checkbox
    agree_var = tk.BooleanVar()
    ttk.Checkbutton(tab4, text="I agree to the terms",
                    variable=agree_var).grid(row=len(fields) + 2,
                                             column=1, sticky="w", pady=8)

    # Buttons
    btn_frame = ttk.Frame(tab4)
    btn_frame.grid(row=len(fields) + 3, column=0, columnspan=2, pady=(8, 0))

    def on_submit():
        data = {k: v.get() for k, v in entries.items()}
        data["Gender"] = gender_var.get()
        data["Agreed"] = agree_var.get()
        print("Submitted:", data)

    ttk.Button(btn_frame, text="Submit", command=on_submit).pack(side="left",
                                                                  padx=4)
    ttk.Button(btn_frame, text="Clear",
               command=lambda: [e.delete(0, "end")
                                for e in entries.values()]).pack(side="left",
                                                                 padx=4)

    # Let the entry column stretch
    tab4.columnconfigure(1, weight=1)

    # ── Run ──
    root.mainloop()


if __name__ == "__main__":
    main()

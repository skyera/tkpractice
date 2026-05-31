"""
class_based_app.py - Demonstrates the standard Class-Based (OOP) Architecture Patterns for tkinter apps.

Covers:
  - Pattern 1: Subclassing tk.Tk directly (best for main single-window applications)
  - Pattern 2: Subclassing tk.Frame (best for reusable components, modular sub-panels, or multi-instance views)
  - Pattern 3: Controller/Model-View-Controller (MVC) Pattern (best for separating logical model from visual layouts)
  - Interactive widgets showcasing all three structural designs.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


# =========================================================================
# PATTERN 2 COMPONENT: Reusable Temperature Converter Frame (Subclass Frame)
# =========================================================================
class TempConverterFrame(ttk.Frame):
    """
    A reusable widget subclassing Frame. It converts Celsius to Fahrenheit and vice versa.
    Since it is a Frame subclass, we can easily instantiate multiple instances of this.
    """
    def __init__(self, parent, default_val=0.0, bg_color=None):
        # We call super() and accept standard frame arguments
        super().__init__(parent)

        self.padding_lbl = ttk.Label(self, text="Temp Converter Component", font=("Arial", 10, "bold"))
        self.padding_lbl.pack(anchor="w", pady=(0, 10))

        # Main variables
        self.val_var = tk.StringVar(value=str(default_val))
        self.result_var = tk.StringVar(value="Select direction & convert")

        # Input elements
        self.inp_frame = ttk.Frame(self)
        self.inp_frame.pack(fill="x", pady=2)
        ttk.Label(self.inp_frame, text="Temperature:").pack(side="left")
        self.ent = ttk.Entry(self.inp_frame, textvariable=self.val_var, width=10)
        self.ent.pack(side="left", padx=5)

        # Conversions combobox
        self.conv_var = tk.StringVar(value="C to F")
        self.conv_cb = ttk.Combobox(self, textvariable=self.conv_var, values=["C to F", "F to C"], state="readonly", width=8)
        self.conv_cb.pack(anchor="w", pady=5)

        # Output Button & Labels
        self.btn = ttk.Button(self, text="Convert", command=self.convert)
        self.btn.pack(anchor="w", pady=2)

        self.res_lbl = ttk.Label(self, textvariable=self.result_var, font=("Arial", 9, "bold"), foreground="#2980b9")
        self.res_lbl.pack(anchor="w", pady=(5, 0))

    def convert(self):
        try:
            val = float(self.val_var.get())
            direction = self.conv_var.get()

            if direction == "C to F":
                res = (val * 9/5) + 32
                self.result_var.set(f"{val:.1f}°C  =  {res:.1f}°F")
            else:
                res = (val - 32) * 5/9
                self.result_var.set(f"{val:.1f}°F  =  {res:.1f}°C")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid numeric value.")


# =========================================================================
# PATTERN 3 STRUCTS: Model-View-Controller (MVC) To-Do List
# =========================================================================

# 1. Model (Independent Data Layer)
class TodoModel:
    def __init__(self):
        self.tasks = ["Learn grid layout", "Learn notebooks", "Learn class patterns"]

    def add_task(self, text):
        if text:
            self.tasks.append(text)
            return True
        return False

    def remove_task_at(self, idx):
        if 0 <= idx < len(self.tasks):
            self.tasks.pop(idx)
            return True
        return False


# 2. View (Visual Representation subclassing Frame)
class TodoView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="MVC To-Do List View", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 10))

        # Input Row
        self.entry_frame = ttk.Frame(self)
        self.entry_frame.pack(fill="x", pady=(0, 10))

        self.task_entry = ttk.Entry(self.entry_frame)
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.task_entry.bind("<Return>", lambda e: self.controller.add_task())

        ttk.Button(self.entry_frame, text="Add Task", command=self.controller.add_task).pack(side="right")

        # List of items
        self.list_frame = ttk.Frame(self)
        self.list_frame.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(self.list_frame, font=("Arial", 10), selectbackground="#3498db")
        self.listbox.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(self.list_frame, command=self.listbox.yview)
        scroll.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scroll.set)

        # Action row
        ttk.Button(self, text="Remove Selected Task", command=self.controller.remove_task).pack(anchor="e", pady=(8, 0))

    def get_task_input(self):
        val = self.task_entry.get().strip()
        self.task_entry.delete(0, "end")
        return val

    def refresh_list(self, tasks):
        self.listbox.delete(0, "end")
        for t in tasks:
            self.listbox.insert("end", t)


# 3. Controller (Binds Model and View)
class TodoController:
    def __init__(self, parent_tab):
        self.model = TodoModel()
        self.view = TodoView(parent_tab, self)
        self.view.pack(fill="both", expand=True)

        # Initial view display
        self.view.refresh_list(self.model.tasks)

    def add_task(self):
        text = self.view.get_task_input()
        if text:
            self.model.add_task(text)
            self.view.refresh_list(self.model.tasks)
        else:
            messagebox.showwarning("Empty Task", "Please enter a task description.", parent=self.view)

    def remove_task(self):
        sel = self.view.listbox.curselection()
        if sel:
            idx = sel[0]
            self.model.remove_task_at(idx)
            self.view.refresh_list(self.model.tasks)
        else:
            messagebox.showwarning("No Selection", "Please select a task to remove.", parent=self.view)


# =========================================================================
# APPLICATION MASTER (Subclassing tk.Tk Directly)
# =========================================================================
class MainApplication(tk.Tk):
    def __init__(self):
        # 1. Initialize master Tk class
        super().__init__()
        self.title("Class-Based (OOP) Architectures Demo")
        self.geometry("700x500")
        self.minsize(620, 420)

        # 2. Main Notebook for Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self._build_subclass_tk_tab()
        self._build_subclass_frame_tab()
        self._build_mvc_tab()

    # =========================================================================
    # TAB 1: Subclass Tk Demo (Counter App)
    # =========================================================================
    def _build_subclass_tk_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="Pattern 1: Subclass Tk")

        # Layout
        ttk.Label(tab, text="Pattern 1: Subclassing tk.Tk directly", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        explanation = (
            "Pros: Extremely clean for single-window apps. All frames, menus, widgets, and callbacks are bound "
            "directly as self.properties. No separate window instance variable (root) is required.\n\n"
            "Cons: Hard to reuse. If the app grows and you want this master logic to become a sub-panel, "
            "refactoring is very tedious."
        )
        ttk.Label(tab, text=explanation, font=("Arial", 9, "italic"), foreground="gray", justify="left", wrap=550).pack(anchor="w", pady=(0, 15))

        # Counter panel
        counter_frame = ttk.LabelFrame(tab, text="Interactive Simple Counter App", padding=15)
        counter_frame.pack(fill="x", pady=10)

        self.counter_var = tk.IntVar(value=0)

        self.num_lbl = ttk.Label(counter_frame, textvariable=self.counter_var, font=("Arial", 28, "bold"), foreground="#2c3e50")
        self.num_lbl.pack(pady=10)

        btn_row = ttk.Frame(counter_frame)
        btn_row.pack()

        ttk.Button(btn_row, text="Decrement", command=self.decrement_counter).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Reset", command=self.reset_counter).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Increment", command=self.increment_counter).pack(side="left", padx=5)

    def increment_counter(self):
        self.counter_var.set(self.counter_var.get() + 1)

    def decrement_counter(self):
        self.counter_var.set(self.counter_var.get() - 1)

    def reset_counter(self):
        self.counter_var.set(0)

    # =========================================================================
    # TAB 2: Subclass Frame Demo (Reusable Components)
    # =========================================================================
    def _build_subclass_frame_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="Pattern 2: Subclass Frame")

        ttk.Label(tab, text="Pattern 2: Subclassing tk.Frame / ttk.Frame", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        explanation = (
            "Pros: Highly reusable and modular! You construct composite widget components with custom layouts and logic. "
            "These frames can then be instantiated multiple times and packed into different sections of a larger window "
            "seamlessly.\n\n"
            "Cons: Needs a parent window or master frame passed in during initialization."
        )
        ttk.Label(tab, text=explanation, font=("Arial", 9, "italic"), foreground="gray", justify="left", wrap=550).pack(anchor="w", pady=(0, 15))

        # Show two side-by-side instances of the TempConverterFrame subclass!
        panes_container = ttk.Frame(tab)
        panes_container.pack(fill="both", expand=True)

        # Instance 1
        comp1 = TempConverterFrame(panes_container, default_val=0.0)
        comp1.pack(side="left", fill="both", expand=True, padx=8, pady=5)

        # Visual Separator
        ttk.Separator(panes_container, orient="vertical").pack(side="left", fill="y", padx=5)

        # Instance 2 (starts with different default value)
        comp2 = TempConverterFrame(panes_container, default_val=100.0)
        comp2.pack(side="right", fill="both", expand=True, padx=8, pady=5)

    # =========================================================================
    # TAB 3: MVC Orchestration Demo
    # =========================================================================
    def _build_mvc_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="Pattern 3: Model-View-Controller")

        ttk.Label(tab, text="Pattern 3: MVC Orchestration Pattern", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        explanation = (
            "Pros: Superb separation of concerns! Model stores pure data structure. View handles UI layouts/draws. "
            "Controller acts as bridge to receive View interactions and update Model. Essential for larger production apps "
            "making debugging, testing, and scaling easy.\n\n"
            "Cons: More boilerplate code to organize."
        )
        ttk.Label(tab, text=explanation, font=("Arial", 9, "italic"), foreground="gray", justify="left", wrap=550).pack(anchor="w", pady=(0, 15))

        # Create MVC Todo Controller on this tab
        TodoController(tab)


if __name__ == "__main__":
    MainApplication().mainloop()

"""
ttk_styles.py - Comprehensive demonstration of ttk Styling and Themes.

Covers:
  - ttk.Style() structure: configure, map, layout, element lookup
  - Live Theme switcher: listing theme_names() and applying theme_use()
  - Creating and extending custom styles (e.g. 'Custom.TButton', 'Custom.TLabel')
  - State mapping (hover, active, disabled, focus)
  - Styling individual widgets (background, foreground, font, padding, relief)
  - Real-time showcase of styled widgets that respond to live theme switches
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class TTKStylesDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TTK Styles & Themes Demo")
        self.geometry("760x560")
        self.minsize(700, 480)

        # Initialize ttk Style object
        self.style = ttk.Style()

        # Build custom styles (to show styling overrides in action)
        self._setup_custom_styles()

        # Main Layout
        self._build_ui()

    def _setup_custom_styles(self):
        # Configure a Custom Label style
        self.style.configure("Custom.TLabel",
                             font=("Courier New", 12, "bold"),
                             foreground="#1abc9c",
                             background="#2c3e50",
                             padding=10)

        # Configure a Custom Button style
        self.style.configure("Custom.TButton",
                             font=("Arial", 10, "bold"),
                             foreground="#ffffff",
                             background="#2980b9",
                             padding=6,
                             relief="flat")

        # Map state changes (like hovering, active, pressed)
        self.style.map("Custom.TButton",
                       foreground=[("pressed", "#f1c40f"), ("active", "#ffffff")],
                       background=[("pressed", "#1abc9c"), ("active", "#3498db")],
                       relief=[("pressed", "sunken")])

        # Custom LabelFrame style
        self.style.configure("Custom.TLabelframe",
                             bd=3,
                             relief="groove",
                             background="#ecf0f1")
        self.style.configure("Custom.TLabelframe.Label",
                             font=("Arial", 11, "bold"),
                             foreground="#2c3e50",
                             background="#ecf0f1")

    def _build_ui(self):
        # Left Panel: Controls (Theme selector, Style inspector)
        left_panel = ttk.Frame(self, padding=12)
        left_panel.pack(side="left", fill="y", padx=5)

        # Right Panel: Widget Showcase (updates interactively when theme changes)
        right_panel = ttk.LabelFrame(self, text="Widget Showcase", padding=15)
        right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # ── Left Panel Components ──
        ttk.Label(left_panel, text="Theme & Styles", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))

        # Theme Switcher
        theme_frame = ttk.LabelFrame(left_panel, text="Select Theme", padding=10)
        theme_frame.pack(fill="x", pady=5)

        available_themes = self.style.theme_names()

        self.theme_var = tk.StringVar(value=self.style.theme_use())
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=available_themes, state="readonly")
        theme_combo.pack(fill="x", pady=5)
        theme_combo.bind("<<ComboboxSelected>>", self._change_theme)

        # Theme Info Labels
        self.theme_info_lbl = ttk.Label(theme_frame, text=f"Active Theme: {self.theme_var.get()}", font=("Arial", 9, "italic"))
        self.theme_info_lbl.pack(anchor="w", pady=(5, 0))

        # Instructions / Explanation
        info_frame = ttk.LabelFrame(left_panel, text="How Styles Work", padding=10)
        info_frame.pack(fill="both", expand=True, pady=10)

        explanation = (
            "TTK separation of structure and styling:\n\n"
            "1. Themes:\n"
            "A collection of styles defining default look/feel for all widgets.\n\n"
            "2. Styles:\n"
            "Instantiate Style() then call:\n"
            "style.configure(style_name, **opts)\n"
            "To assign styles to widgets, pass:\n"
            "style='StyleName'\n\n"
            "3. State Mapping:\n"
            "style.map() changes visual properties automatically based on widget state flags (active, hover, pressed, focus, disabled).\n\n"
            "4. Dynamic Layouts:\n"
            "A tree structure of elements determines how widgets draw parts of themselves."
        )
        tk_text = tk.Text(info_frame, wrap="word", width=25, font=("Arial", 8), bg="#f4f4f4", relief="flat")
        tk_text.insert("1.0", explanation)
        tk_text.config(state="disabled")
        tk_text.pack(fill="both", expand=True)

        # ── Right Panel Components (Showcase) ──

        # 1. Custom Styled Widgets (Created above)
        custom_grp = ttk.LabelFrame(right_panel, text="Custom Styled widgets (Independent styles)", style="Custom.TLabelframe", padding=12)
        custom_grp.pack(fill="x", pady=(0, 15))

        ttk.Label(custom_grp, text="This uses Custom.TLabel style", style="Custom.TLabel").pack(side="left", padx=10, pady=5)
        ttk.Button(custom_grp, text="Custom.TButton", style="Custom.TButton", command=self._on_custom_btn_click).pack(side="left", padx=10, pady=5)

        # 2. Standard TTK Widgets (These adapt completely to theme switches)
        std_grp = ttk.LabelFrame(right_panel, text="Standard Theme-Responsive widgets", padding=12)
        std_grp.pack(fill="both", expand=True)

        # Row 1: Label and Entry
        row1 = ttk.Frame(std_grp)
        row1.pack(fill="x", pady=6)
        ttk.Label(row1, text="Standard Label:").pack(side="left", padx=5)
        ttk.Entry(row1, width=20).pack(side="left", padx=5)

        # Row 2: Radio and Check buttons
        row2 = ttk.Frame(std_grp)
        row2.pack(fill="x", pady=6)
        chk_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row2, text="Checkbox", variable=chk_var).pack(side="left", padx=15)

        rad_var = tk.StringVar(value="A")
        ttk.Radiobutton(row2, text="Option A", variable=rad_var, value="A").pack(side="left", padx=5)
        ttk.Radiobutton(row2, text="Option B", variable=rad_var, value="B").pack(side="left", padx=5)

        # Row 3: Interactive Scale & Progressbar
        row3 = ttk.Frame(std_grp)
        row3.pack(fill="x", pady=10)
        ttk.Label(row3, text="Progressbar:").pack(side="left", padx=5)

        pb_var = tk.DoubleVar(value=60.0)
        pb = ttk.Progressbar(row3, variable=pb_var, maximum=100, length=120)
        pb.pack(side="left", padx=5)

        scale = ttk.Scale(row3, from_=0, to=100, variable=pb_var, length=100)
        scale.pack(side="left", padx=10)

        # Row 4: Combobox
        row4 = ttk.Frame(std_grp)
        row4.pack(fill="x", pady=6)
        ttk.Label(row4, text="Combobox:").pack(side="left", padx=5)
        ttk.Combobox(row4, values=["Selection 1", "Selection 2", "Selection 3"], state="readonly", width=15).pack(side="left", padx=5)

        # Row 5: Treeview (Very styles-reliant widget)
        row5 = ttk.Frame(std_grp)
        row5.pack(fill="both", expand=True, pady=10)

        tree = ttk.Treeview(row5, columns=("Name", "Role"), show="headings", height=3)
        tree.pack(side="left", fill="both", expand=True)

        tree.heading("Name", text="Name")
        tree.heading("Role", text="Role")

        tree.column("Name", width=100)
        tree.column("Role", width=150)

        tree.insert("", "end", values=("Alan Turing", "Mathematician"))
        tree.insert("", "end", values=("Ada Lovelace", "First Programmer"))

    def _change_theme(self, event):
        new_theme = self.theme_var.get()
        try:
            self.style.theme_use(new_theme)
            self.theme_info_lbl.config(text=f"Active Theme: {new_theme}")
            # Reset Custom overrides since theme switches can clear current configs
            self._setup_custom_styles()
        except tk.TclError as e:
            messagebox.showerror("Theme Error", f"Unable to switch to theme '{new_theme}':\n{e}")

    def _on_custom_btn_click(self):
        messagebox.showinfo("Style Click", "Custom styled button was clicked!")


if __name__ == "__main__":
    TTKStylesDemo().mainloop()

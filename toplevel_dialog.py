"""
toplevel_dialog.py - Comprehensive demonstration of tk.Toplevel windows and custom modal/non-modal dialogs.

Covers:
  - Creating a basic Toplevel window
  - Modal dialogs with grab_set() and wait_window()
  - transient() to associate with parent
  - Close protocol handling ('WM_DELETE_WINDOW')
  - Custom attributes: overrideredirect, -alpha, -topmost
  - State management: withdraw(), deiconify(), iconify()
  - Passing data back from dialogs to parent (via custom classes or dictionary callbacks)
  - Practical example: a fully operational Settings/Preferences dialog that alters parent's state
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


# =========================================================================
# CUSTOM INPUT DIALOG (Returns a value)
# =========================================================================
class CustomInputDialog(tk.Toplevel):
    def __init__(self, parent, title="Input Dialog"):
        super().__init__(parent)
        self.transient(parent)  # Keeps on top of parent window
        self.title(title)
        self.geometry("320x150")
        self.resizable(False, False)

        # Center dialog relative to parent
        self.geometry(f"+{parent.winfo_x() + 50}+{parent.winfo_y() + 50}")

        self.result = None

        ttk.Label(self, text="Please enter your nickname:", font=("Arial", 10)).pack(pady=(15, 5))

        self.entry = ttk.Entry(self, width=28)
        self.entry.pack(pady=5)
        self.entry.focus_set()

        # Keyboard confirmation
        self.entry.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.on_cancel())

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="OK", command=self.on_ok, width=10).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.on_cancel, width=10).pack(side="left", padx=5)

        self.grab_set()  # Make dialog modal: intercept all events
        self.wait_window()  # Block main loop execution until this window is destroyed

    def on_ok(self):
        val = self.entry.get().strip()
        if val:
            self.result = val
            self.destroy()
        else:
            messagebox.showwarning("Empty Value", "Please input a nickname!", parent=self)

    def on_cancel(self):
        self.destroy()


# =========================================================================
# PREFERENCES DIALOG (Alters parent settings)
# =========================================================================
class PreferencesDialog(tk.Toplevel):
    def __init__(self, parent, current_settings, save_callback):
        super().__init__(parent)
        self.transient(parent)
        self.title("Settings / Preferences")
        self.geometry("350x260")
        self.resizable(False, False)
        self.geometry(f"+{parent.winfo_x() + 50}+{parent.winfo_y() + 50}")

        self.current_settings = current_settings
        self.save_callback = save_callback

        # Prevent closing dialog directly using window 'X' without checking
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        frame = ttk.Frame(self, padding=15)
        frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(frame, text="User Preferences", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))

        # Font size settings
        font_frame = ttk.Frame(frame)
        font_frame.pack(fill="x", pady=5)
        ttk.Label(font_frame, text="Log Font Size:").pack(side="left", padx=(0, 10))

        self.font_size_var = tk.IntVar(value=current_settings.get("font_size", 10))
        font_spin = ttk.Spinbox(font_frame, from_=8, to=24, textvariable=self.font_size_var, width=6)
        font_spin.pack(side="left")

        # Background color settings
        bg_frame = ttk.Frame(frame)
        bg_frame.pack(fill="x", pady=5)
        ttk.Label(bg_frame, text="Log Theme:").pack(side="left", padx=(0, 10))

        self.theme_var = tk.StringVar(value=current_settings.get("theme", "Dark"))
        theme_combo = ttk.Combobox(bg_frame, textvariable=self.theme_var, values=["Dark", "Light", "Solarized"],
                                   state="readonly", width=12)
        theme_combo.pack(side="left")

        # Topmost settings
        self.topmost_var = tk.BooleanVar(value=current_settings.get("topmost", False))
        ttk.Checkbutton(frame, text="Keep main window always on top", variable=self.topmost_var).pack(anchor="w", pady=10)

        # Action Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side="bottom", fill="x", pady=(10, 0))

        ttk.Button(btn_frame, text="Save Settings", command=self.on_save).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.on_close).pack(side="right", padx=5)

        self.grab_set()
        self.wait_window()

    def on_save(self):
        new_settings = {
            "font_size": self.font_size_var.get(),
            "theme": self.theme_var.get(),
            "topmost": self.topmost_var.get()
        }
        self.save_callback(new_settings)
        self.destroy()

    def on_close(self):
        self.destroy()


# =========================================================================
# MAIN APP WINDOW
# =========================================================================
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Toplevel Windows & Dialogs Demo")
        self.geometry("600x480")
        self.minsize(550, 400)

        # Default Settings
        self.settings = {
            "font_size": 10,
            "theme": "Dark",
            "topmost": False
        }

        # Create control panel
        ctrl_frame = ttk.LabelFrame(self, text="Window Operations", padding=15)
        ctrl_frame.pack(fill="x", padx=15, pady=(15, 10))

        # Basic Operations Row
        btn_basic = ttk.Button(ctrl_frame, text="New Basic Toplevel", command=self.open_basic_toplevel)
        btn_basic.grid(row=0, column=0, padx=5, pady=5)

        btn_attr = ttk.Button(ctrl_frame, text="Special Attribute Window", command=self.open_attribute_toplevel)
        btn_attr.grid(row=0, column=1, padx=5, pady=5)

        # Modal/Data Flow Row
        btn_modal = ttk.Button(ctrl_frame, text="Get Nickname (Modal Dialog)", command=self.get_nickname)
        btn_modal.grid(row=1, column=0, padx=5, pady=5)

        btn_pref = ttk.Button(ctrl_frame, text="Preferences Dialog", command=self.open_preferences)
        btn_pref.grid(row=1, column=1, padx=5, pady=5)

        # Results area
        results_frame = ttk.LabelFrame(self, text="Interactive Event Log", padding=10)
        results_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.log_txt = tk.Text(results_frame, font=("Consolas", self.settings["font_size"]), wrap="word")
        self.log_txt.pack(fill="both", expand=True)
        self.update_log_theme()

        self.log("App loaded. Select a Toplevel operation above.")

    def log(self, message):
        self.log_txt.insert("end", f"[*] {message}\n")
        self.log_txt.see("end")

    def open_basic_toplevel(self):
        top = tk.Toplevel(self)
        top.title("Basic Secondary Window")
        top.geometry("300x200")
        # Center basic window on screen
        top.geometry(f"+{self.winfo_x() + 80}+{self.winfo_y() + 80}")

        lbl = ttk.Label(top, text="This is a simple non-modal window.\nYou can click the main window behind it.",
                        justify="center", font=("Arial", 10))
        lbl.pack(pady=30)

        self.log("Created non-modal basic Toplevel window.")

    def open_attribute_toplevel(self):
        top = tk.Toplevel(self)
        top.title("Special Attributes")
        top.geometry("320x220")
        top.geometry(f"+{self.winfo_x() + 100}+{self.winfo_y() + 100}")

        # Set specific attributes
        top.attributes("-topmost", True)  # Always on top
        top.attributes("-alpha", 0.9)  # Subtle transparency

        frm = ttk.Frame(top, padding=15)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Window Attributes Demo", font=("Arial", 11, "bold")).pack(pady=(0, 5))
        ttk.Label(frm, text="• Always On Top (topmost = True)\n• Transparency (alpha = 0.90)",
                  foreground="gray").pack(anchor="w", pady=(0, 15))

        # Alpha adjustment slider
        slider_frame = ttk.Frame(frm)
        slider_frame.pack(fill="x", pady=5)
        ttk.Label(slider_frame, text="Alpha:").pack(side="left", padx=5)

        def set_alpha(val):
            top.attributes("-alpha", float(val))

        alpha_scale = ttk.Scale(slider_frame, from_=0.2, to=1.0, value=0.9, orient="horizontal", command=set_alpha)
        alpha_scale.pack(side="left", fill="x", expand=True, padx=5)

        ttk.Button(frm, text="Close Window", command=top.destroy).pack(pady=10)
        self.log("Created Toplevel with attributes topmost=True, alpha=0.9.")

    def get_nickname(self):
        self.log("Opening modal Input dialog...")
        dialog = CustomInputDialog(self, "Specify User Nickname")
        if dialog.result is not None:
            self.log(f"Dialog Returned Value: '{dialog.result}'")
        else:
            self.log("Dialog cancelled/closed without value.")

    def open_preferences(self):
        self.log("Opening Preferences modal dialog...")
        PreferencesDialog(self, self.settings, self.apply_preferences)

    def apply_preferences(self, new_settings):
        self.settings.update(new_settings)
        self.log(f"New settings saved: {self.settings}")

        # Apply settings
        self.attributes("-topmost", self.settings["topmost"])
        self.log_txt.config(font=("Consolas", self.settings["font_size"]))
        self.update_log_theme()

    def update_log_theme(self):
        themes = {
            "Dark": {"bg": "#1e1e1e", "fg": "#5af78e"},
            "Light": {"bg": "#ffffff", "fg": "#000000"},
            "Solarized": {"bg": "#fdf6e3", "fg": "#586e75"}
        }
        theme_cfg = themes.get(self.settings["theme"], themes["Dark"])
        self.log_txt.config(bg=theme_cfg["bg"], fg=theme_cfg["fg"], insertbackground=theme_cfg["fg"])


if __name__ == "__main__":
    MainApp().mainloop()

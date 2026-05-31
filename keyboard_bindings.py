"""
keyboard_bindings.py - Comprehensive demonstration of Keyboard Event Bindings and Focus Traversal in tkinter.

Covers:
  - Event binding scopes: widget.bind(), root.bind_all(), widget.bind_class()
  - Handling diverse key events (<Key>, <KeyPress>, <KeyRelease>)
  - Catching specific keys (<Return>, <Escape>, <Tab>, <BackSpace>, <Delete>, <space>)
  - Processing modifiers (<Control-s>, <Shift-Up>, <Control-Shift-Z>)
  - Inspecting event attributes: keysym, keycode, char, state
  - Managing focus and traversal (focus_set, focus_get, tk_focusNext, unbind)
  - Practical Demo: Arrow-key controlled canvas square with live event log overlay
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class KeyboardBindingsDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Keyboard Bindings & Focus Demo")
        self.geometry("780x560")
        self.minsize(700, 480)

        self._build_ui()
        self._setup_bindings()

    def _build_ui(self):
        # Top Header explanation
        top_frame = ttk.Frame(self, padding=12)
        top_frame.pack(fill="x")
        ttk.Label(top_frame, text="Keyboard Bindings & Focus Traversal", font=("Arial", 12, "bold")).pack(anchor="w")
        ttk.Label(top_frame, text="Click inside components to focus them, press keys to trigger actions, and watch event logs.",
                  foreground="gray").pack(anchor="w", pady=2)

        # Paned Window (Left: Event Log, Right: Interactive Panels)
        pane = ttk.PanedWindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True, padx=8, pady=8)

        # Left Column - Event Log
        log_frame = ttk.LabelFrame(pane, text="Live Keyboard Event Log", padding=10)
        pane.add(log_frame, weight=1)

        # Scrollbar + Text box for event logs
        self.log_txt = tk.Text(log_frame, bg="#1e1e1e", fg="#39ff14", font=("Consolas", 10), wrap="none", height=10, width=42)
        self.log_txt.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(log_frame, command=self.log_txt.yview)
        scroll.pack(side="right", fill="y")
        self.log_txt.config(yscrollcommand=scroll.set)

        # Clear logs button
        ttk.Button(log_frame, text="Clear Log", command=self._clear_log).pack(side="bottom", anchor="e", pady=(5, 0))

        # Right Column - Actions
        right_panel = ttk.Frame(pane)
        pane.add(right_panel, weight=2)

        # Top Right: Interactive Canvas (Control shape with arrow keys)
        self.canvas_frame = ttk.LabelFrame(right_panel, text="Arrow Keys Interactive Canvas (Click to Focus)", padding=10)
        self.canvas_frame.pack(fill="both", expand=True, pady=(0, 10), padx=(10, 0))

        self.canvas = tk.Canvas(self.canvas_frame, bg="#2c3e50", height=160, highlightthickness=2, highlightbackground="#34495e")
        self.canvas.pack(fill="both", expand=True)

        # Draw a shape inside the canvas
        self.sq_size = 30
        self.sq_x = 100
        self.sq_y = 60
        self.square = self.canvas.create_rectangle(
            self.sq_x, self.sq_y, self.sq_x + self.sq_size, self.sq_y + self.sq_size,
            fill="#e74c3c", outline="#ffffff", width=2
        )

        # Instruction text inside canvas
        self.canvas.create_text(
            15, 15, text="Click to focus. Use arrows to move. Hold Shift for speed boost.",
            fill="#bdc3c7", anchor="nw", font=("Arial", 9)
        )

        # Bottom Right: Focus Traversal & Inputs
        self.input_frame = ttk.LabelFrame(right_panel, text="Focus Traversal & Widget Bindings", padding=10)
        self.input_frame.pack(fill="x", padx=(10, 0))

        # Row 1: Focusable Fields
        ttk.Label(self.input_frame, text="Field 1 (Press Tab/Shift+Tab to traverse):").grid(row=0, column=0, sticky="w", pady=4)
        self.ent1 = ttk.Entry(self.input_frame, width=25)
        self.ent1.grid(row=0, column=1, pady=4, padx=5, sticky="ew")

        ttk.Label(self.input_frame, text="Field 2 (Press Return to print text):").grid(row=1, column=0, sticky="w", pady=4)
        self.ent2 = ttk.Entry(self.input_frame, width=25)
        self.ent2.grid(row=1, column=1, pady=4, padx=5, sticky="ew")

        # Row 2: Special Key Test Buttons
        btn_frame = ttk.Frame(self.input_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")

        self.btn_bind = ttk.Button(btn_frame, text="Bind Local <space>", command=self._bind_local_space)
        self.btn_bind.pack(side="left", padx=5)

        self.btn_unbind = ttk.Button(btn_frame, text="Unbind Local <space>", command=self._unbind_local_space, state="disabled")
        self.btn_unbind.pack(side="left", padx=5)

        # Configure responsive grid
        self.input_frame.columnconfigure(1, weight=1)

    def _clear_log(self):
        self.log_txt.config(state="normal")
        self.log_txt.delete("1.0", "end")

    def _log_event(self, event, desc=""):
        # Format the event variables into readable structures
        log_str = (
            f"[{desc:^10}] "
            f"keysym={event.keysym:<10} "
            f"char={repr(event.char):<6} "
            f"keycode={event.keycode:<5} "
            f"state={event.state:<5}\n"
        )
        self.log_txt.insert("end", log_str)
        self.log_txt.see("end")

    def _setup_bindings(self):
        # 1. Bind keys to the Interactive Canvas
        self.canvas.bind("<FocusIn>", lambda e: self.canvas.config(highlightcolor="#1abc9c", highlightbackground="#1abc9c"))
        self.canvas.bind("<FocusOut>", lambda e: self.canvas.config(highlightcolor="#34495e", highlightbackground="#34495e"))

        # Bind mouse click on canvas to focus it
        self.canvas.bind("<Button-1>", lambda e: self.canvas.focus_set())

        # Arrow key bindings
        self.canvas.bind("<Left>", lambda e: self._move_square(-10, 0, e))
        self.canvas.bind("<Right>", lambda e: self._move_square(10, 0, e))
        self.canvas.bind("<Up>", lambda e: self._move_square(0, -10, e))
        self.canvas.bind("<Down>", lambda e: self._move_square(0, 10, e))

        # 2. General application wide keyboard shortcuts (bind_all)
        self.bind_all("<Control-s>", self._app_shortcut_save)
        self.bind_all("<Control-Shift-Z>", self._app_shortcut_undo)
        self.bind_all("<F1>", self._app_help)

        # 3. Widget Specific bindings
        # Detect any keypress inside Entry 1
        self.ent1.bind("<Key>", lambda e: self._log_event(e, "Entry 1 Key"))

        # Detect specific Key (Return/Enter) on Entry 2
        self.ent2.bind("<Return>", self._on_entry2_return)
        self.ent2.bind("<Escape>", lambda e: [self.ent2.delete(0, "end"), self._log_event(e, "Entry 2 Esc")])

    def _move_square(self, dx, dy, event):
        # Highlight focus and show key event log
        self._log_event(event, "Canvas Move")

        # Shift modifier: event.state contains bitmasks representing pressed modifiers
        # Shift key is typically bitmask 1 (0x0001) or 0x0003
        if event.state & 0x0001:
            dx *= 2.5
            dy *= 2.5
            self._log_event(event, "SHIFT Speed")

        c_w = self.canvas.winfo_width()
        c_h = self.canvas.winfo_height()

        # Update and boundary check
        self.sq_x = max(0, min(c_w - self.sq_size, self.sq_x + dx))
        self.sq_y = max(0, min(c_h - self.sq_size, self.sq_y + dy))

        self.canvas.coords(
            self.square,
            self.sq_x, self.sq_y, self.sq_x + self.sq_size, self.sq_y + self.sq_size
        )

    def _app_shortcut_save(self, event):
        self._log_event(event, "SAVE SHORTCUT")
        messagebox.showinfo("Application Shortcut", "Control-S (Save Shortcut) recognized globally!")

    def _app_shortcut_undo(self, event):
        self._log_event(event, "UNDO SHORTCUT")
        messagebox.showinfo("Application Shortcut", "Control-Shift-Z (Redo/Undo Shortcut) recognized globally!")

    def _app_help(self, event):
        self._log_event(event, "HELP SHORTCUT")
        messagebox.showinfo("Help Shortcut", "F1 pressed. Application help is not yet implemented.")

    def _on_entry2_return(self, event):
        self._log_event(event, "Entry 2 Ret")
        val = self.ent2.get().strip()
        if val:
            messagebox.showinfo("Input Submitted", f"Submitted text: '{val}'")
            self.ent2.delete(0, "end")

    # Local Space binding toggling
    def _bind_local_space(self):
        # Bind the global <space> key locally to our App window
        self.bind("<space>", self._space_pressed)
        self.btn_bind.config(state="disabled")
        self.btn_unbind.config(state="normal")
        self.log_txt.insert("end", "[*] Bound global <space> key locally to the root window.\n")

    def _unbind_local_space(self):
        # Remove the <space> binding
        self.unbind("<space>")
        self.btn_bind.config(state="normal")
        self.btn_unbind.config(state="disabled")
        self.log_txt.insert("end", "[*] Unbound <space> key.\n")

    def _space_pressed(self, event):
        self._log_event(event, "Space Root")


if __name__ == "__main__":
    KeyboardBindingsDemo().mainloop()

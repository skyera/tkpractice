"""
progressbar_demo.py - Comprehensive demonstration of ttk.Progressbar.

Covers:
  - Determinate mode (manual value setting)
  - Determinate mode (automatic stepping using progressbar.step() / progressbar.start() / progressbar.stop())
  - Indeterminate mode (bouncing bar animation)
  - Horizontal vs Vertical orientation
  - Linking progress to widget variables (DoubleVar)
  - A realistic multi-step simulated file downloader / background task with:
    - Custom speed, pause/resume, cancel support
    - Clean status messages and dynamic percentage label updates
"""

import tkinter as tk
from tkinter import ttk
import random


class ProgressbarDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Progressbar Demo")
        self.geometry("700x520")
        self.minsize(600, 450)

        # Main notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_basic_tab()
        self._build_modes_tab()
        self._build_downloader_tab()

    # =========================================================================
    # TAB 1: Basics & Manual Control
    # =========================================================================
    def _build_basic_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="Basic & Orientations")

        # Top explanation
        ttk.Label(tab, text="ttk.Progressbar Basics", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(tab, text="Progress bars show status of long-running operations. They can be horizontal or vertical.",
                  foreground="gray").pack(anchor="w", pady=(0, 15))

        # Paned view for Horizontal vs Vertical
        pane = ttk.Frame(tab)
        pane.pack(fill="both", expand=True)

        # Horizontal side
        left_frame = ttk.LabelFrame(pane, text="Horizontal Progressbar", padding=15)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.horiz_val = tk.DoubleVar(value=25.0)
        self.horiz_pb = ttk.Progressbar(left_frame, orient="horizontal", length=200,
                                        mode="determinate", variable=self.horiz_val, maximum=100)
        self.horiz_pb.pack(pady=15, fill="x")

        # Label to show percentage
        self.horiz_lbl = ttk.Label(left_frame, text="Value: 25.0%")
        self.horiz_lbl.pack(pady=5)

        # Manual control buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="-10", command=lambda: self._adjust_pb(-10)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="+10", command=lambda: self._adjust_pb(10)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Reset", command=lambda: self._adjust_pb(None)).pack(side="left", padx=5)

        # Vertical side
        right_frame = ttk.LabelFrame(pane, text="Vertical Progressbar", padding=15)
        right_frame.pack(side="right", fill="both", expand=True)

        self.vert_val = tk.DoubleVar(value=50.0)
        self.vert_pb = ttk.Progressbar(right_frame, orient="vertical", length=150,
                                       mode="determinate", variable=self.vert_val, maximum=100)
        self.vert_pb.pack(pady=10)

        self.vert_lbl = ttk.Label(right_frame, text="Value: 50.0%")
        self.vert_lbl.pack(pady=5)

        # Vertical control scale
        scale = ttk.Scale(right_frame, from_=0, to=100, orient="horizontal",
                          variable=self.vert_val, command=self._on_vert_scale_move)
        scale.pack(pady=10, fill="x")
        ttk.Label(right_frame, text="Drag scale to manually adjust vertical bar", foreground="gray", font=("Arial", 9)).pack()

    def _adjust_pb(self, amount):
        if amount is None:
            self.horiz_val.set(0.0)
        else:
            curr = self.horiz_val.get()
            new_val = max(0.0, min(100.0, curr + amount))
            self.horiz_val.set(new_val)
        self.horiz_lbl.config(text=f"Value: {self.horiz_val.get():.1f}%")

    def _on_vert_scale_move(self, val):
        self.vert_lbl.config(text=f"Value: {float(val):.1f}%")

    # =========================================================================
    # TAB 2: Determinate vs Indeterminate Modes
    # =========================================================================
    def _build_modes_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="Modes & Animation")

        # Mode explanation
        ttk.Label(tab, text="Progressbar Animation Modes", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 15))

        # Container
        grid_frame = ttk.Frame(tab)
        grid_frame.pack(fill="both", expand=True)

        # Determinate auto-step panel
        det_panel = ttk.LabelFrame(grid_frame, text="Determinate (Auto-stepping)", padding=15)
        det_panel.pack(fill="x", pady=(0, 15))

        self.det_pb = ttk.Progressbar(det_panel, orient="horizontal", mode="determinate", maximum=100)
        self.det_pb.pack(fill="x", pady=10)

        det_btn_frame = ttk.Frame(det_panel)
        det_btn_frame.pack()

        self.det_running = False
        self.det_btn = ttk.Button(det_btn_frame, text="Start Autostep", command=self._toggle_det_autostep)
        self.det_btn.pack(side="left", padx=5)
        ttk.Button(det_btn_frame, text="Step (+5)", command=lambda: self.det_pb.step(5)).pack(side="left", padx=5)

        # Indeterminate panel
        indet_panel = ttk.LabelFrame(grid_frame, text="Indeterminate (Activity Indicator)", padding=15)
        indet_panel.pack(fill="x")

        ttk.Label(indet_panel, text="Used when the duration of the task is unknown.",
                  foreground="gray").pack(anchor="w", pady=(0, 8))

        self.indet_pb = ttk.Progressbar(indet_panel, orient="horizontal", mode="indeterminate")
        self.indet_pb.pack(fill="x", pady=10)

        indet_btn_frame = ttk.Frame(indet_panel)
        indet_btn_frame.pack()

        self.indet_running = False
        self.indet_btn = ttk.Button(indet_btn_frame, text="Start Animation", command=self._toggle_indet_animation)
        self.indet_btn.pack(side="left", padx=5)

    def _toggle_det_autostep(self):
        if self.det_running:
            self.det_running = False
            self.det_btn.config(text="Start Autostep")
        else:
            self.det_running = True
            self.det_btn.config(text="Stop Autostep")
            self._det_loop()

    def _det_loop(self):
        if not self.det_running:
            return
        # step() advances the bar by the given increment. It loops back when reaching maximum.
        self.det_pb.step(1)
        self.after(50, self._det_loop)

    def _toggle_indet_animation(self):
        if self.indet_running:
            self.indet_running = False
            # stop() halts the animation
            self.indet_pb.stop()
            self.indet_btn.config(text="Start Animation")
        else:
            self.indet_running = True
            # start(interval) runs animation on a timer. Smaller interval = faster bounce
            self.indet_pb.start(10)
            self.indet_btn.config(text="Stop Animation")

    # =========================================================================
    # TAB 3: Simulated Downloader (Real-world Scenario)
    # =========================================================================
    def _build_downloader_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="Practical Downloader")

        ttk.Label(tab, text="Simulated Downloader", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(tab, text="Combines a determinate progress bar, variable updates, and user action states.",
                  foreground="gray").pack(anchor="w", pady=(0, 15))

        # Settings
        settings_frame = ttk.Frame(tab)
        settings_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(settings_frame, text="Download Speed:").pack(side="left", padx=(0, 5))
        self.speed_var = tk.StringVar(value="Normal")
        speed_cb = ttk.Combobox(settings_frame, textvariable=self.speed_var,
                                 values=["Slow", "Normal", "Fast", "Super Fast"], state="readonly", width=12)
        speed_cb.pack(side="left", padx=5)

        # Progress bar
        self.dl_pb = ttk.Progressbar(tab, orient="horizontal", mode="determinate", maximum=100)
        self.dl_pb.pack(fill="x", pady=(10, 5))

        # Status text & percentage frame
        status_frame = ttk.Frame(tab)
        status_frame.pack(fill="x", pady=(0, 15))
        self.dl_status = ttk.Label(status_frame, text="Status: Ready to download", font=("Arial", 10))
        self.dl_status.pack(side="left")
        self.dl_percent = ttk.Label(status_frame, text="0%", font=("Arial", 10, "bold"))
        self.dl_percent.pack(side="right")

        # Controls
        ctrl_frame = ttk.Frame(tab)
        ctrl_frame.pack()

        self.btn_dl_start = ttk.Button(ctrl_frame, text="Start Download", command=self._start_download)
        self.btn_dl_start.pack(side="left", padx=5)

        self.btn_dl_pause = ttk.Button(ctrl_frame, text="Pause", command=self._pause_download, state="disabled")
        self.btn_dl_pause.pack(side="left", padx=5)

        self.btn_dl_cancel = ttk.Button(ctrl_frame, text="Cancel", command=self._cancel_download, state="disabled")
        self.btn_dl_cancel.pack(side="left", padx=5)

        # Download states
        self.dl_active = False
        self.dl_paused = False
        self.dl_progress = 0.0

    def _start_download(self):
        if self.dl_paused:
            self.dl_paused = False
            self.dl_active = True
            self.dl_status.config(text="Status: Downloading...")
            self.btn_dl_start.config(state="disabled")
            self.btn_dl_pause.config(state="normal")
            self._download_tick()
            return

        self.dl_active = True
        self.dl_paused = False
        self.dl_progress = 0.0
        self.dl_pb["value"] = 0
        self.dl_status.config(text="Status: Initializing connection...")
        self.btn_dl_start.config(state="disabled")
        self.btn_dl_pause.config(state="normal")
        self.btn_dl_cancel.config(state="normal")
        self.after(800, self._download_tick)

    def _pause_download(self):
        if self.dl_active and not self.dl_paused:
            self.dl_paused = True
            self.dl_active = False
            self.dl_status.config(text="Status: Paused")
            self.btn_dl_start.config(state="normal", text="Resume")
            self.btn_dl_pause.config(state="disabled")

    def _cancel_download(self):
        self.dl_active = False
        self.dl_paused = False
        self.dl_progress = 0.0
        self.dl_pb["value"] = 0
        self.dl_status.config(text="Status: Download cancelled.")
        self.dl_percent.config(text="0%")
        self.btn_dl_start.config(state="normal", text="Start Download")
        self.btn_dl_pause.config(state="disabled")
        self.btn_dl_cancel.config(state="disabled")

    def _download_tick(self):
        if not self.dl_active or self.dl_paused:
            return

        # Determine step speed
        speed_map = {"Slow": 0.5, "Normal": 1.5, "Fast": 4.0, "Super Fast": 8.0}
        base_step = speed_map.get(self.speed_var.get(), 1.5)
        # Add slight randomness
        step = base_step * random.uniform(0.7, 1.3)

        self.dl_progress += step
        if self.dl_progress >= 100.0:
            self.dl_progress = 100.0
            self.dl_pb["value"] = 100.0
            self.dl_percent.config(text="100%")
            self.dl_status.config(text="Status: Complete! File saved successfully.")
            self.btn_dl_start.config(state="normal", text="Start Download")
            self.btn_dl_pause.config(state="disabled")
            self.btn_dl_cancel.config(state="disabled")
            self.dl_active = False
        else:
            self.dl_pb["value"] = self.dl_progress
            self.dl_percent.config(text=f"{int(self.dl_progress)}%")
            # Dynamically update status label based on progress
            if self.dl_progress < 30:
                self.dl_status.config(text="Status: Downloading assets...")
            elif self.dl_progress < 60:
                self.dl_status.config(text="Status: Extracting packages...")
            elif self.dl_progress < 90:
                self.dl_status.config(text="Status: Verifying installation checksums...")
            else:
                self.dl_status.config(text="Status: Finalizing setup...")

            # Run again in 100ms
            self.after(100, self._download_tick)


if __name__ == "__main__":
    ProgressbarDemo().mainloop()

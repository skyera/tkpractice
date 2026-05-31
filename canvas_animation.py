"""
canvas_animation.py - Comprehensive demonstration of interactive Canvas Animation and after() loops.

Covers:
  - Designing a robust, framerate-independent (or fixed interval) after() animation loop
  - Single bouncing ball edge collision physics
  - Multi-ball physics with dynamic speeds, directions, and random colors
  - Gravitational particle system fountain
  - Speed customization, Start/Stop/Reset controls
  - Cleaning up animations properly using after_cancel()
"""

import tkinter as tk
from tkinter import ttk
import random
import colorsys


class CanvasAnimationDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Canvas Animation & Physics Demo")
        self.geometry("780x560")
        self.minsize(700, 480)

        # Handle window closure cleanly (stop all running loops)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Tabbed notebook structure
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        # Tab 1: Single Bouncing Ball
        self._build_single_ball_tab()
        # Tab 2: Multiple Balls
        self._build_multi_ball_tab()
        # Tab 3: Gravitational Particle Fountain
        self._build_fountain_tab()

    def _on_close(self):
        # Stop all running timers before exit
        self._stop_single_ball()
        self._stop_multi_ball()
        self._stop_fountain()
        self.destroy()

    # =========================================================================
    # TAB 1: Single Bouncing Ball
    # =========================================================================
    def _build_single_ball_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Single Bouncing Ball")

        # Controls Left Side
        ctrl_frame = ttk.Frame(tab, padding=5)
        ctrl_frame.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(ctrl_frame, text="Controls", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 10))

        self.btn_sb_start = ttk.Button(ctrl_frame, text="Start Animation", command=self._start_single_ball)
        self.btn_sb_start.pack(fill="x", pady=4)

        self.btn_sb_stop = ttk.Button(ctrl_frame, text="Stop Animation", command=self._stop_single_ball, state="disabled")
        self.btn_sb_stop.pack(fill="x", pady=4)

        ttk.Button(ctrl_frame, text="Reset Ball", command=self._reset_single_ball).pack(fill="x", pady=4)

        # Speed scaling
        ttk.Label(ctrl_frame, text="Speed Factor:").pack(anchor="w", pady=(15, 2))
        self.sb_speed_scale = ttk.Scale(ctrl_frame, from_=1.0, to=15.0, value=5.0, orient="horizontal")
        self.sb_speed_scale.pack(fill="x", pady=2)

        # Canvas Right Side
        self.sb_canvas = tk.Canvas(tab, bg="#1e1e1e", highlightthickness=0)
        self.sb_canvas.pack(side="right", fill="both", expand=True)

        # Ball variables
        self.sb_ball = None
        self.sb_timer_id = None
        self.sb_x, self.sb_y = 150.0, 150.0
        self.sb_dx, self.sb_dy = 1.0, 1.2
        self.sb_radius = 18

        # Draw first instance
        self._reset_single_ball()

    def _reset_single_ball(self):
        self._stop_single_ball()
        self.sb_canvas.delete("all")

        # Start coordinates at center
        width = max(100, self.sb_canvas.winfo_width())
        height = max(100, self.sb_canvas.winfo_height())
        if width == 1:
            width, height = 500, 400

        self.sb_x, self.sb_y = width / 2.0, height / 2.0

        # Choose random angle
        angle = random.uniform(0.2, 1.5)
        self.sb_dx = random.choice([-1, 1]) * angle
        self.sb_dy = random.choice([-1, 1]) * (2.0 - angle)

        self.sb_ball = self.sb_canvas.create_oval(
            self.sb_x - self.sb_radius, self.sb_y - self.sb_radius,
            self.sb_x + self.sb_radius, self.sb_y + self.sb_radius,
            fill="#e74c3c", outline="#ffffff", width=2
        )

    def _start_single_ball(self):
        if self.sb_timer_id is None:
            self.btn_sb_start.config(state="disabled")
            self.btn_sb_stop.config(state="normal")
            self._single_ball_tick()

    def _stop_single_ball(self):
        if self.sb_timer_id is not None:
            self.after_cancel(self.sb_timer_id)
            self.sb_timer_id = None
            self.btn_sb_start.config(state="normal")
            self.btn_sb_stop.config(state="disabled")

    def _single_ball_tick(self):
        # Calculate speed
        speed = self.sb_speed_scale.get()

        # Update position
        self.sb_x += self.sb_dx * speed
        self.sb_y += self.sb_dy * speed

        # Handle wall collisions
        c_width = self.sb_canvas.winfo_width()
        c_height = self.sb_canvas.winfo_height()

        if self.sb_x - self.sb_radius <= 0:
            self.sb_x = self.sb_radius
            self.sb_dx = -self.sb_dx
            self.sb_canvas.itemconfig(self.sb_ball, fill="#e67e22")  # Color flash on hit
        elif self.sb_x + self.sb_radius >= c_width:
            self.sb_x = c_width - self.sb_radius
            self.sb_dx = -self.sb_dx
            self.sb_canvas.itemconfig(self.sb_ball, fill="#f1c40f")

        if self.sb_y - self.sb_radius <= 0:
            self.sb_y = self.sb_radius
            self.sb_dy = -self.sb_dy
            self.sb_canvas.itemconfig(self.sb_ball, fill="#2ecc71")
        elif self.sb_y + self.sb_radius >= c_height:
            self.sb_y = c_height - self.sb_radius
            self.sb_dy = -self.sb_dy
            self.sb_canvas.itemconfig(self.sb_ball, fill="#3498db")

        # Reposition drawing
        self.sb_canvas.coords(
            self.sb_ball,
            self.sb_x - self.sb_radius, self.sb_y - self.sb_radius,
            self.sb_x + self.sb_radius, self.sb_y + self.sb_radius
        )

        # Loop next tick in 16ms (~60 FPS)
        self.sb_timer_id = self.after(16, self._single_ball_tick)

    # =========================================================================
    # TAB 2: Multiple Balls
    # =========================================================================
    def _build_multi_ball_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Multi-Ball Physics")

        ctrl_frame = ttk.Frame(tab, padding=5)
        ctrl_frame.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(ctrl_frame, text="Controls", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 10))

        self.btn_mb_start = ttk.Button(ctrl_frame, text="Start Animation", command=self._start_multi_ball)
        self.btn_mb_start.pack(fill="x", pady=4)

        self.btn_mb_stop = ttk.Button(ctrl_frame, text="Stop Animation", command=self._stop_multi_ball, state="disabled")
        self.btn_mb_stop.pack(fill="x", pady=4)

        ttk.Button(ctrl_frame, text="Clear Canvas", command=self._clear_multi_ball).pack(fill="x", pady=4)
        ttk.Button(ctrl_frame, text="Add 10 Balls", command=self._add_random_balls).pack(fill="x", pady=4)

        # Speed scaling
        ttk.Label(ctrl_frame, text="Speed Factor:").pack(anchor="w", pady=(15, 2))
        self.mb_speed_scale = ttk.Scale(ctrl_frame, from_=0.5, to=8.0, value=3.0, orient="horizontal")
        self.mb_speed_scale.pack(fill="x", pady=2)

        # Info
        self.mb_info_lbl = ttk.Label(ctrl_frame, text="Balls Active: 0", font=("Arial", 9, "italic"))
        self.mb_info_lbl.pack(anchor="w", pady=(15, 0))

        # Canvas
        self.mb_canvas = tk.Canvas(tab, bg="#1e1e1e", highlightthickness=0)
        self.mb_canvas.pack(side="right", fill="both", expand=True)

        self.balls_list = []
        self.mb_timer_id = None

    def _add_random_balls(self, count=10):
        w = max(200, self.mb_canvas.winfo_width())
        h = max(200, self.mb_canvas.winfo_height())
        if w == 1:
            w, h = 500, 400

        for _ in range(count):
            r = random.randint(10, 24)
            x = random.uniform(r + 5, w - r - 5)
            y = random.uniform(r + 5, h - r - 5)
            dx = random.uniform(-2, 2)
            dy = random.uniform(-2, 2)
            if dx == 0: dx = 0.5
            if dy == 0: dy = 0.5

            # Random attractive color
            h_hue = random.random()
            rgb = colorsys.hsv_to_rgb(h_hue, 0.85, 0.95)
            hex_color = "#{:02x}{:02x}{:02x}".format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

            item = self.mb_canvas.create_oval(x - r, y - r, x + r, y + r, fill=hex_color, outline="")
            self.balls_list.append({
                "item": item, "x": x, "y": y, "dx": dx, "dy": dy, "r": r
            })

        self.mb_info_lbl.config(text=f"Balls Active: {len(self.balls_list)}")

    def _clear_multi_ball(self):
        self._stop_multi_ball()
        self.mb_canvas.delete("all")
        self.balls_list.clear()
        self.mb_info_lbl.config(text="Balls Active: 0")

    def _start_multi_ball(self):
        if self.mb_timer_id is None:
            if not self.balls_list:
                self._add_random_balls(15)
            self.btn_mb_start.config(state="disabled")
            self.btn_mb_stop.config(state="normal")
            self._multi_ball_tick()

    def _stop_multi_ball(self):
        if self.mb_timer_id is not None:
            self.after_cancel(self.mb_timer_id)
            self.mb_timer_id = None
            self.btn_mb_start.config(state="normal")
            self.btn_mb_stop.config(state="disabled")

    def _multi_ball_tick(self):
        c_w = self.mb_canvas.winfo_width()
        c_h = self.mb_canvas.winfo_height()
        speed = self.mb_speed_scale.get()

        for b in self.balls_list:
            b["x"] += b["dx"] * speed
            b["y"] += b["dy"] * speed

            # Border collisions
            if b["x"] - b["r"] <= 0:
                b["x"] = b["r"]
                b["dx"] = -b["dx"]
            elif b["x"] + b["r"] >= c_w:
                b["x"] = c_w - b["r"]
                b["dx"] = -b["dx"]

            if b["y"] - b["r"] <= 0:
                b["y"] = b["r"]
                b["dy"] = -b["dy"]
            elif b["y"] + b["r"] >= c_h:
                b["y"] = c_h - b["r"]
                b["dy"] = -b["dy"]

            self.mb_canvas.coords(
                b["item"],
                b["x"] - b["r"], b["y"] - b["r"],
                b["x"] + b["r"], b["y"] + b["r"]
            )

        self.mb_timer_id = self.after(16, self._multi_ball_tick)

    # =========================================================================
    # TAB 3: Gravitational Particle Fountain
    # =========================================================================
    def _build_fountain_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Particle Fountain")

        ctrl_frame = ttk.Frame(tab, padding=5)
        ctrl_frame.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(ctrl_frame, text="Controls", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 10))

        self.btn_f_start = ttk.Button(ctrl_frame, text="Start Fountain", command=self._start_fountain)
        self.btn_f_start.pack(fill="x", pady=4)

        self.btn_f_stop = ttk.Button(ctrl_frame, text="Stop Fountain", command=self._stop_fountain, state="disabled")
        self.btn_f_stop.pack(fill="x", pady=4)

        ttk.Button(ctrl_frame, text="Clear", command=self._clear_fountain).pack(fill="x", pady=4)

        # Gravity slider
        ttk.Label(ctrl_frame, text="Gravity Acceleration:").pack(anchor="w", pady=(15, 2))
        self.f_gravity_scale = ttk.Scale(ctrl_frame, from_=0.05, to=0.8, value=0.25, orient="horizontal")
        self.f_gravity_scale.pack(fill="x", pady=2)

        # Info
        self.f_info_lbl = ttk.Label(ctrl_frame, text="Particles Active: 0", font=("Arial", 9, "italic"))
        self.f_info_lbl.pack(anchor="w", pady=(15, 0))

        # Canvas
        self.f_canvas = tk.Canvas(tab, bg="#111111", highlightthickness=0)
        self.f_canvas.pack(side="right", fill="both", expand=True)

        self.particles = []
        self.f_timer_id = None

    def _clear_fountain(self):
        self._stop_fountain()
        self.f_canvas.delete("all")
        self.particles.clear()
        self.f_info_lbl.config(text="Particles Active: 0")

    def _start_fountain(self):
        if self.f_timer_id is None:
            self.btn_f_start.config(state="disabled")
            self.btn_f_stop.config(state="normal")
            self._fountain_tick()

    def _stop_fountain(self):
        if self.f_timer_id is not None:
            self.after_cancel(self.f_timer_id)
            self.f_timer_id = None
            self.btn_f_start.config(state="normal")
            self.btn_f_stop.config(state="disabled")

    def _fountain_tick(self):
        w = max(100, self.f_canvas.winfo_width())
        h = max(100, self.f_canvas.winfo_height())
        if w == 1:
            w, h = 500, 400

        # Launching new particles from the bottom center
        emitter_x = w / 2.0
        emitter_y = h - 20.0

        gravity = self.f_gravity_scale.get()

        # Spawn a few particles per frame if active
        if self.btn_f_stop["state"] == "normal":
            for _ in range(4):
                dx = random.uniform(-2.5, 2.5)
                dy = random.uniform(-8.0, -14.0)  # Move upwards (negative y)
                size = random.uniform(2.0, 5.0)
                life = random.randint(50, 100)  # Number of frames of life

                # Nice color spectrum
                hue = random.uniform(0.5, 0.7)  # Nice blues & cyans
                rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                color = "#{:02x}{:02x}{:02x}".format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

                item = self.f_canvas.create_oval(
                    emitter_x - size, emitter_y - size,
                    emitter_x + size, emitter_y + size,
                    fill=color, outline=""
                )
                self.particles.append({
                    "item": item, "x": emitter_x, "y": emitter_y,
                    "dx": dx, "dy": dy, "size": size, "life": life, "max_life": life
                })

        # Update existing particles
        dead_list = []
        for p in self.particles:
            p["x"] += p["dx"]
            p["dy"] += gravity  # Gravity accelerates downwards (positive y)
            p["y"] += p["dy"]
            p["life"] -= 1

            # Render
            self.f_canvas.coords(
                p["item"],
                p["x"] - p["size"], p["y"] - p["size"],
                p["x"] + p["size"], p["y"] + p["size"]
            )

            # Check fade / death conditions
            if p["life"] <= 0 or p["y"] > h:
                self.f_canvas.delete(p["item"])
                dead_list.append(p)
            else:
                # Fade color relative to remaining life
                ratio = p["life"] / p["max_life"]
                if ratio < 0.4:
                    self.f_canvas.itemconfig(p["item"], fill="#444444")  # Turn grey before disappearing

        # Remove dead particles
        for p in dead_list:
            self.particles.remove(p)

        self.f_info_lbl.config(text=f"Particles Active: {len(self.particles)}")

        self.f_timer_id = self.after(16, self._fountain_tick)


if __name__ == "__main__":
    CanvasAnimationDemo().mainloop()

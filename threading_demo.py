"""
threading_demo.py - Comprehensive demonstration of Threading with tkinter.

Covers:
  - The "Frozen GUI" problem: running synchronous blocking tasks (time.sleep) on main loop
  - Resolving freezes with background threads (threading.Thread)
  - Thread-Safe GUI updates using queue.Queue and regular polling with root.after()
  - Thread cancellation using threading.Event flags
  - A real-world Task Manager simulating multiple background processes executing concurrently,
    each updating its own progress bar, status text, and supporting individual cancellations.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import queue
import time
import random


class ThreadingDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Multi-Threading Demo")
        self.geometry("780x560")
        self.minsize(700, 480)

        # Queue for thread communication
        self.queue = queue.Queue()

        # Window closing handler
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Tabbed notebook structure
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self._build_frozen_tab()
        self._build_queue_tab()
        self._build_manager_tab()

        # Start the periodic queue checking loop (crucial for receiving thread messages safely)
        self._check_queue_loop()

    def _on_close(self):
        # Set cancel flags on any active thread tasks
        for task in self.active_tasks.values():
            task["stop_event"].set()
        self.destroy()

    # =========================================================================
    # TAB 1: Frozen vs Responsive (The "Why")
    # =========================================================================
    def _build_frozen_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="Frozen vs Responsive")

        ttk.Label(tab, text="The Frozen GUI Problem", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        explanation = (
            "Because tkinter runs on a single main thread, performing heavy blocking calculations or "
            "network requests (like time.sleep) directly inside a button click callback will FREEZE the entire window. "
            "The OS thinks the app is dead, clicks are ignored, and it won't redraw.\n\n"
            "By spawning a background thread, the GUI mainloop remains active, leaving the window responsive, "
            "animations moving, and allowing buttons to still be clicked."
        )
        ttk.Label(tab, text=explanation, font=("Arial", 9, "italic"), foreground="gray", justify="left", wrap=600).pack(anchor="w", pady=(0, 15))

        # Spinner to prove if GUI is frozen
        spin_frame = ttk.LabelFrame(tab, text="Responsiveness Indicator (Continuous Animation)", padding=10)
        spin_frame.pack(fill="x", pady=(0, 15))

        self.spin_pb = ttk.Progressbar(spin_frame, orient="horizontal", mode="indeterminate")
        self.spin_pb.pack(fill="x", pady=5)
        self.spin_pb.start(15)  # Start animation

        # Interaction buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Run Blocking Task (FREEZES GUI 3s)", command=self._run_blocking_task).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Run Threaded Task (RESPONSIVE 3s)", command=self._run_threaded_task).pack(side="left", padx=10)

        # Status text
        self.resp_lbl = ttk.Label(tab, text="Status: Ready", font=("Arial", 10, "bold"), foreground="#2c3e50")
        self.resp_lbl.pack(pady=10)

    def _run_blocking_task(self):
        self.resp_lbl.config(text="Status: Executing blocking time.sleep(3)... watch spinner freeze!")
        self.update_idletasks()  # Force update GUI before sleep

        # Blocks main thread completely
        time.sleep(3.0)

        self.resp_lbl.config(text="Status: Task Completed. (UI is unfrozen)")

    def _run_threaded_task(self):
        self.resp_lbl.config(text="Status: Spawning background thread... watch spinner keep moving!")

        def bg_work():
            time.sleep(3.0)
            # Schedule label update thread-safely back on main thread using 'after'
            self.after(0, lambda: self.resp_lbl.config(text="Status: Threaded Task Completed!"))

        # Spawn non-blocking thread
        t = threading.Thread(target=bg_work)
        t.daemon = True
        t.start()

    # =========================================================================
    # TAB 2: Thread-Safe Queue Pattern
    # =========================================================================
    def _build_queue_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="Queue-based Updates")

        ttk.Label(tab, text="Thread-Safe Queue Polling", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        explanation = (
            "Calling widget methods (like widget.config or text.insert) directly from secondary threads is a "
            "Tcl/Tk concurrency violation and causes random memory crashes. The safe approach is to have background "
            "threads place messages into a thread-safe queue.Queue. The main thread polls the queue periodically "
            "using root.after() and performs all actual GUI operations."
        )
        ttk.Label(tab, text=explanation, font=("Arial", 9, "italic"), foreground="gray", justify="left", wrap=600).pack(anchor="w", pady=(0, 15))

        # Panel
        action_frame = ttk.LabelFrame(tab, text="Calculations Queue Logger", padding=12)
        action_frame.pack(fill="both", expand=True)

        self.queue_btn = ttk.Button(action_frame, text="Generate Numbers (Parallel Thread)", command=self._start_queue_generator)
        self.queue_btn.pack(anchor="w", pady=(0, 10))

        # Text area to dump queue logs
        self.queue_txt = tk.Text(action_frame, font=("Consolas", 10), bg="#222222", fg="#00ff00", height=8)
        self.queue_txt.pack(fill="both", expand=True)

    def _start_queue_generator(self):
        self.queue_btn.config(state="disabled")
        self.queue_txt.delete("1.0", "end")
        self.queue_txt.insert("end", "[*] Starting worker thread...\n")

        def number_worker():
            for i in range(1, 6):
                time.sleep(0.6)  # Simulate workload
                num = random.randint(100, 999)
                # Thread-safe write to queue
                self.queue.put(("log", f"Step {i}/5: Computed random number {num}\n"))

            self.queue.put(("finish_queue", None))

        t = threading.Thread(target=number_worker)
        t.daemon = True
        t.start()

    def _check_queue_loop(self):
        """
        Periodically checks the queue for messages from secondary threads.
        Runs on the main GUI thread.
        """
        try:
            while True:
                msg_type, payload = self.queue.get_nowait()

                if msg_type == "log":
                    self.queue_txt.insert("end", payload)
                    self.queue_txt.see("end")
                elif msg_type == "finish_queue":
                    self.queue_txt.insert("end", "[*] Worker thread finished processing!\n")
                    self.queue_btn.config(state="normal")

                # Multi-Task Manager queue requests
                elif msg_type == "task_progress":
                    task_id, progress = payload
                    self._update_task_progress(task_id, progress)
                elif msg_type == "task_complete":
                    task_id, result = payload
                    self._complete_task(task_id, result)

                self.queue.task_done()
        except queue.Empty:
            pass
        finally:
            # Poll again in 50ms
            self.after(50, self._check_queue_loop)

    # =========================================================================
    # TAB 3: Dynamic Multi-Task Manager (With Cancellation)
    # =========================================================================
    def _build_manager_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="Threaded Task Manager")

        ttk.Label(tab, text="Multi-Task Manager with Cancellation", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(tab, text="Spawns multiple threads. Each task uses a threading.Event flag for graceful stop cancellation.",
                  foreground="gray").pack(anchor="w", pady=(0, 15))

        # Start button
        self.btn_spawn_task = ttk.Button(tab, text="Launch New Background Task", command=self._spawn_manager_task)
        self.btn_spawn_task.pack(anchor="w", pady=(0, 10))

        # Container for task rows
        self.tasks_container = ttk.LabelFrame(tab, text="Running Background Processes", padding=10)
        self.tasks_container.pack(fill="both", expand=True)

        self.active_tasks = {}
        self.task_counter = 0

    def _spawn_manager_task(self):
        self.task_counter += 1
        tid = f"Task #{self.task_counter}"

        # Create UI Row components dynamically
        row = ttk.Frame(self.tasks_container)
        row.pack(fill="x", pady=6)

        lbl = ttk.Label(row, text=f"{tid}: Processing...", font=("Arial", 9, "bold"), width=18)
        lbl.pack(side="left", padx=5)

        pb = ttk.Progressbar(row, orient="horizontal", maximum=100, length=200)
        pb.pack(side="left", padx=10, fill="x", expand=True)

        percent_lbl = ttk.Label(row, text="0%", width=6)
        percent_lbl.pack(side="left", padx=5)

        # Thread cancellation flag
        stop_event = threading.Event()

        cancel_btn = ttk.Button(row, text="Cancel", command=lambda: self._cancel_manager_task(tid))
        cancel_btn.pack(side="right", padx=5)

        # Store task information
        self.active_tasks[tid] = {
            "row": row, "label": lbl, "pb": pb, "percent": percent_lbl,
            "cancel_btn": cancel_btn, "stop_event": stop_event
        }

        # Define Thread Worker Loop
        def task_worker(task_id, st_event):
            steps = 20
            for i in range(1, steps + 1):
                # Check for cancellation
                if st_event.is_set():
                    return  # Terminate early safely

                time.sleep(random.uniform(0.15, 0.35))  # Simulate calculations

                progress_val = int((i / steps) * 100)
                # Thread safe update message to queue
                self.queue.put(("task_progress", (task_id, progress_val)))

            # Complete task
            self.queue.put(("task_complete", (task_id, "Completed successfully")))

        # Start thread
        t = threading.Thread(target=task_worker, args=(tid, stop_event))
        t.daemon = True
        t.start()

    def _cancel_manager_task(self, task_id):
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task["stop_event"].set()  # Signal cancellation to the worker thread

            task["label"].config(text=f"{task_id}: Cancelled", foreground="#c0392b")
            task["cancel_btn"].config(state="disabled")
            task["pb"]["value"] = 0
            task["percent"].config(text="")

            # Remove row after a short delay
            self.after(1500, lambda: self._remove_task_row(task_id))

    def _update_task_progress(self, task_id, progress):
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            # Don't update if thread cancellation occurred
            if not task["stop_event"].is_set():
                task["pb"]["value"] = progress
                task["percent"].config(text=f"{progress}%")

    def _complete_task(self, task_id, result):
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if not task["stop_event"].is_set():
                task["label"].config(text=f"{task_id}: Complete!", foreground="#27ae60")
                task["pb"]["value"] = 100
                task["percent"].config(text="100%")
                task["cancel_btn"].config(text="Clear", command=lambda: self._remove_task_row(task_id))

    def _remove_task_row(self, task_id):
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task["row"].destroy()
            del self.active_tasks[task_id]


if __name__ == "__main__":
    ThreadingDemo().mainloop()

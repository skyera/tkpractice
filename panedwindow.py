import tkinter as tk
import tkinter.ttk as ttk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        self.make_panedwindow()
        self.make_left_pane()
        self.make_right_pane()

    def make_panedwindow(self):
        self.pw = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.pw.pack(fill=tk.BOTH, expand=True)

    def make_left_pane(self):
        left = ttk.Frame(self.pw)
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)
        self.pw.add(left, weight=1)

        label_left = ttk.Label(left, text="Left size", background="red")
        label_left.grid(row=0, column=0, sticky="nswe")

    def make_right_pane(self):
        right = ttk.Frame(self.pw, width=200, height=200)
        right.grid_propagate(0)
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)
        self.pw.add(right, weight=0)

        label_right = ttk.Label(right, text="Right side", background="blue")
        label_right.grid(row=0, column=0, sticky="nswe")


if __name__ == "__main__":
    app = App()
    app.mainloop()

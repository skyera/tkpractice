import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()
        self.geometry("500x400")

    def make_widgets(self):
        self.frame = tk.Frame(self, bd=2, relief=tk.RIDGE)
        self.frame.pack(fill=tk.X, padx=5, pady=10)
        tk.Label(self.frame, text="Label:").pack(side=tk.LEFT, padx=5)
        self.var = tk.StringVar()
        tk.Entry(self.frame, textvariable=self.var, bg="white").pack(
            side=tk.RIGHT, padx=5
        )
        self.var.set("Entry widget")


if __name__ == "__main__":
    app = App()
    app.mainloop()

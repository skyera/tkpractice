import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Canvas text")
        self.geometry("300x100")
        self.make_widgets()
        self.make_text()

    def make_widgets(self):
        self.var = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self.var)
        self.canvas = tk.Canvas(self, bg="white")
        self.entry.pack(pady=5)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def make_text(self):
        self.update()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        options = {"font": "courier", "fill": "blue", "activefill": "red"}
        self.text_id = self.canvas.create_text((w / 2, h / 2), **options)
        self.var.trace("w", self.write_text)

    def write_text(self, *args):
        self.canvas.itemconfig(self.text_id, text=self.var.get())


if __name__ == "__main__":
    app = App()
    app.mainloop()

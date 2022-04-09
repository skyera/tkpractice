import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Colors')
        self.make_widgets()

    def make_widgets(self):
        self.canvas = tk.Canvas(self)
        self.canvas.create_rectangle(30, 10, 120, 80, outline='#fb0', fill='#fb0')
        self.canvas.create_rectangle(150, 10, 240, 80, outline='#f50', fill='#f50')
        self.canvas.create_rectangle(270, 10, 370, 80, outline='#05f', fill='#05f')
        self.canvas.pack(fill=tk.BOTH, expand=True)


if __name__ == '__main__':
    app = App()
    app.mainloop()


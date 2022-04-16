import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Basic canvas")
        self.make_widgets()

    def make_widgets(self):
        self.canvas = tk.Canvas(self, bg='white')
        self.label = tk.Label(self)
        self.canvas.bind('<Motion>', self.mouse_motion)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.label.pack(fill=tk.X)

    def mouse_motion(self, event):
        x, y = event.x, event.y
        text = 'Mouse position: ({}, {})'.format(x, y)
        self.label.config(text=text)


if __name__ == '__main__':
    app = App()
    app.mainloop()

import tkinter as tk
import tkinter.ttk as ttk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        self.frame = tk.Frame(self, borderwidth=10, name='demo')
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.make_canvas()
        self.make_scale()

    def make_canvas(self):
        self.canvas = tk.Canvas(self.frame, width=50, height=50,
                bd=0, highlightthickness=0, name='arrow')
        self.canvas.create_polygon('0 0 1 1 2 2', fill='SeaGreen3',
                tags=('poly',), outline='black')
        self.canvas.pack(side=tk.LEFT, fill=tk.Y, anchor='nw')

    def make_scale(self):
        self.scale = ttk.Scale(self.frame, orient=tk.VERTICAL, length=284, from_=0, to=250,
                command=self.set_height)
        self.scale.set(75)
        self.scale.pack(side=tk.LEFT, anchor='ne')

    def set_height(self, height):
        canvas = self.nametowidget('demo.arrow')
        height = float(height)
        y2 = height - 30
        y2 = str(y2)
        height = str(height)

        shape = (15, 0, 35, 0, 35, y2, 45, y2, 25, height,
                 5, y2, 15, y2, 15, 0)
        canvas.coords('poly', shape)


if __name__ == '__main__':
    app = App()
    app.mainloop()

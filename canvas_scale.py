import tkinter as tk
import random


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()
        self.layout_widgets()
        self.plot_rectangles()
        self.bind_events()
        
    def make_widgets(self):
        self.canvas = tk.Canvas(self, width=400, height=400, bg='bisque')
        self.x_scroll = tk.Scrollbar(self, orient=tk.HORIZONTAL,
                command=self.canvas.xview)
        self.y_scroll = tk.Scrollbar(self, orient=tk.VERTICAL,
                command=self.canvas.yview)
        self.canvas.config(xscrollcommand=self.x_scroll.set,
                           yscrollcommand=self.y_scroll.set)

    def layout_widgets(self):
        self.x_scroll.grid(row=1, column=0, sticky='ew')
        self.y_scroll.grid(row=0, column=1, sticky='ns')
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def plot_rectangles(self):
        for n in range(50):
            x0 = random.randint(0, 900)
            y0 = random.randint(50, 900)
            x1 = x0 + random.randint(50, 100)
            y1 = y0 + random.randint(50, 100)
            color = ('red', 'orange', 'yellow', 'green', 'blue')[random.randint(0,4)]
            self.canvas.create_rectangle(x0, y0, x1, y1, outline='black',
                    fill=color, activefill='black', tags=n)
        self.canvas.create_text(50, 10, anchor='nw', text='Click and drag')

    def bind_events(self):
        self.canvas.bind('<ButtonPress-1>', self.move_start)
        self.canvas.bind('<B1-Motion>', self.move_move)

    def move_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def move_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)


if __name__ == '__main__':
    app = App()
    app.mainloop()

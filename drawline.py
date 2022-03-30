import tkinter as tk


class LineOptionFrame(tk.LabelFrame):
    arrows = (tk.NONE, tk.FIRST, tk.LAST, tk.BOTH)
    colors = ('black', 'red', 'blue', 'green')
    def __init__(self, master, **kw):
        super().__init__(master, text='Line Options', **kw)
        self.make_widgets()
        self.layout_widgets()

    def make_widgets(self):
        self.make_arrow_style_widgets()
        self.make_color_widgets()
        self.make_line_width_widgets()

    def make_arrow_style_widgets(self):
        self.arrow_var = tk.StringVar()
        self.arrow_label = tk.Label(self, text='Array style')
        self.arrow_option = tk.OptionMenu(self, self.arrow_var, *self.arrows)

    def make_color_widgets(self):
        self.color_var = tk.StringVar()
        self.color_var.set(self.colors[0])
        self.color_label = tk.Label(self, text='Color')
        self.color_option = tk.OptionMenu(self, self.color_var, *self.colors)

    def make_line_width_widgets(self):
        self.line_width_label = tk.Label(self, text='Line width')
        self.line_width_spinbox = tk.Spinbox(self, values=(1,2,3,4), width=5)

    def layout_widgets(self):
        self.arrow_label.grid(row=0, column=0, sticky=tk.W)
        self.arrow_option.grid(row=0, column=1, pady=10)
        self.color_label.grid(row=1, column=0, sticky=tk.W)
        self.color_option.grid(row=1, column=1, pady=10)
        self.line_width_label.grid(row=2, column=0, sticky=tk.W)
        self.line_width_spinbox.grid(row=2, column=1, pady=10)

    def get_arrow(self):
        return self.arrow_var.get()

    def get_color(self):
        return self.color_var.get()

    def get_width(self):
        return int(self.line_width_spinbox.get())


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Draw lines')
        self.line_start = None
        self.make_widgets()

    def make_widgets(self):
        self.option_frame = LineOptionFrame(self)
        self.canvas = tk.Canvas(self, bg='white')
        self.option_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y, pady=10)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Button-1>', self.draw)

    def draw(self, event):
        if not self.line_start:
            self.line_start = event.x, event.y
            return
        x, y = event.x, event.y
        self._do_draw(x, y)

    def _do_draw(self, x, y):
        x_origin, y_origin = self.line_start
        self.line_start = None
        line = (x_origin, y_origin, x, y)
        arrow = self.option_frame.get_arrow()
        color = self.option_frame.get_color()
        width = self.option_frame.get_width()
        self.canvas.create_line(*line, arrow=arrow, fill=color, width=width)


if __name__ == '__main__':
    app = App()
    app.mainloop()


import tkinter as tk


class LineForm(tk.LabelFrame):
    arrows = (tk.NONE, tk.FIRST, tk.LAST, tk.BOTH)
    colors = ('black', 'red', 'blue', 'green')

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.make_widgets()

    def make_widgets(self):
        self.make_arrow_style_widgets()
        self.make_color_widgets()
        self.make_line_width_widgets()
        self.layout_widgets()

    def make_arrow_style_widgets(self):
        self.arrow_var = tk.StringVar()
        self.arrow_var.set(self.arrows[0])
        self.arrow_label = tk.Label(self, text='Arrow style')
        self.arrow_option = tk.OptionMenu(self, self.arrow_var, *self.arrows)

    def make_color_widgets(self):
        self.color_var = tk.StringVar()
        self.color_var.set(self.colors[0])
        self.color_label = tk.Label(self, text='Fill color')
        self.color_option = tk.OptionMenu(self, self.color_var, *self.colors)

    def make_line_width_widgets(self):
        self.line_width_label = tk.Label(self, text='Line width')
        self.line_width = tk.Spinbox(self, values=(1,2,3,4), width=5)

    def layout_widgets(self):
        self.arrow_label.grid(row=0, column=0, sticky=tk.W)
        self.arrow_option.grid(row=0, column=1, pady=10)
        self.color_label.grid(row=1, column=0, sticky=tk.W)
        self.color_option.grid(row=1, column=1, pady=10)
        self.line_width_label.grid(row=2, column=0, sticky=tk.W)
        self.line_width.grid(row=2, column=1, pady=10)

    def get_arrow(self):
        return self.arrow_var.get()

    def get_color(self):
        return self.color_var.get()

    def get_width(self):
        return int(self.line_width.get())


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()
        self.start_point = None
    
    def make_widgets(self):
        self.option_form = LineForm(self, text='Line options', bg='gray90')
        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.bind('<Button-1>', self.mouse_move)
        self.option_form.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def mouse_move(self, event):
        x, y = event.x, event.y
        if not self.start_point:
            self.start_point = (x, y)
            return

        self.draw_line(event.x, event.y)
    
    def draw_line(self, x, y):
        start_x, start_y = self.start_point
        line = (start_x, start_y, x, y)
        self.canvas.create_line(*line, arrow=self.option_form.get_arrow(),
                fill=self.option_form.get_color(),
                width=self.option_form.get_width())
        self.start_point = None


if __name__ == '__main__':
    app = App()
    app.mainloop()

import tkinter as tk
import tkinter.ttk as ttk


class PlotFrame(ttk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.make_widgets()
        self.bind_events()
        self.oldx = 0
        self.oldy = 0

    def bind_events(self):
        self.canvas.tag_bind("point", "<Any-Enter>", self.on_enter)
        self.canvas.tag_bind("point", "<Any-Leave>", self.on_leave)
        self.canvas.tag_bind("point", "<B1-Motion>", self.on_motion)

    def on_enter(self, event):
        self.canvas.itemconfigure(tk.CURRENT, fill="red")
        self.oldx = event.x
        self.oldy = event.y

    def on_leave(self, event):
        self.canvas.itemconfigure(tk.CURRENT, fill="SkyBlue2")

    def on_motion(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.canvas.move(tk.CURRENT, x - self.oldx, y - self.oldy)
        self.oldx = x
        self.oldy = y

    def make_widgets(self):
        self.make_frame()
        self.make_plot()

    def make_frame(self):
        self.frame = tk.Frame(self)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.Y)

    def make_plot(self):
        self.make_canvas()
        self.make_axes()
        self.make_x_axis_labels()
        self.make_y_axis_labels()
        self.make_data_points()

    def make_canvas(self):
        self.canvas = tk.Canvas(self.frame, relief=tk.RAISED, width=450, height=300)
        self.canvas.pack(side=tk.TOP, fill=tk.X)
        self.plot_font = ("Helv", 18)

    def make_axes(self):
        self.canvas.create_line(100, 250, 400, 250, width=2)
        self.canvas.create_line(100, 250, 100, 50, width=2)
        self.canvas.create_text(
            225, 20, text="A plot", font=self.plot_font, fill="brown"
        )

    def make_x_axis_labels(self):
        for i in range(11):
            x = 100 + i * 30
            self.canvas.create_line(x, 250, x, 245, width=2)
            self.canvas.create_text(
                x, 254, text="{}".format((10 * i)), anchor=tk.N, font=self.plot_font
            )

    def make_y_axis_labels(self):
        for i in range(1, 6):
            y = 250 - (i * 40)
            self.canvas.create_line(100, y, 105, y, width=2)
            self.canvas.create_text(
                96, y, text="{}".format((i * 50.0)), anchor=tk.E, font=self.plot_font
            )

    def make_data_points(self):
        data = [
            (12, 56),
            (20, 94),
            (33, 98),
            (32, 120),
            (61, 180),
            (75, 160),
            (98, 223),
        ]

        for p0, p1 in data:
            x = 100 + 3 * p0
            y = 250 - (4 * p1) / 5
            item = self.canvas.create_oval(
                x - 6, y - 6, x + 6, y + 6, width=1, outline="black", fill="SkyBlue2"
            )
            self.canvas.addtag_withtag("point", item)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        frame = PlotFrame(self)
        frame.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()

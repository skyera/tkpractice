import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scale")
        self.make_widgets()

    def make_widgets(self):
        self.make_canvas()
        self.make_scale()
        self.scale.grid(row=0, column=0, sticky="NE")
        self.canvas.grid(row=0, column=1, sticky="NSWE")
        self.scale.set(100)

    def make_canvas(self):
        self.canvas = tk.Canvas(self, width=50, height=50, bd=0, highlightthickness=0)
        self.canvas.create_polygon(0, 0, 1, 1, 2, 2, fill="cadetblue", tags="poly")
        self.canvas.create_line(0, 0, 1, 1, 2, 2, 0, 0, fill="black", tags="line")

    def make_scale(self):
        self.scale = tk.Scale(
            self,
            orient=tk.VERTICAL,
            length=284,
            from_=0,
            to=250,
            tickinterval=50,
            command=self.set_height,
        )

    def set_height(self, h):
        height = int(h)
        height += 21
        y2 = height - 30
        if y2 < 21:
            y2 = 21

        self.canvas.coords(
            "poly", 15, 20, 35, 20, 35, y2, 45, y2, 25, height, 5, y2, 15, y2, 15, 20
        )
        self.canvas.coords(
            "line", 15, 20, 35, 20, 35, y2, 45, y2, 25, height, 5, y2, 15, y2, 15, 20
        )


if __name__ == "__main__":
    app = App()
    app.mainloop()

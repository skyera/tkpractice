import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()
        self.kinds = [self.canvas.create_oval, self.canvas.create_rectangle]
        self.start = None
        self.item_id = None

    def make_widgets(self):
        self.canvas = tk.Canvas(self, width=300, height=300, bg="beige")
        self.canvas.bind("<ButtonPress-1>", self.onstart)
        self.canvas.bind("<B1-Motion>", self.ongrow)
        self.canvas.bind("<Double-1>", self.onclear)
        self.canvas.bind("<ButtonPress-3>", self.onmove)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def onstart(self, event):
        self.shape = self.kinds[0]
        self.kinds = self.kinds[1:] + self.kinds[:1]
        self.start = event
        self.item_id = None

    def ongrow(self, event):
        if not self.start:
            return

        canvas = event.widget
        if self.item_id:
            canvas.delete(self.item_id)

        self.item_id = self.shape(
            self.start.x, self.start.y, event.x, event.y, fill="red"
        )

    def onclear(self, event):
        event.widget.delete(tk.ALL)

    def onmove(self, event):
        if self.item_id:
            canvas = event.widget
            dx, dy = (event.x - self.start.x), (event.y - self.start.y)
            canvas.move(self.item_id, dx, dy)
            self.start = event


if __name__ == "__main__":
    app = App()
    app.mainloop()

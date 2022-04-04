import tkinter as tk
import random


class App(tk.Tk):
    colors = ('red', 'yellow', 'green', 'blue', 'orange')
    def __init__(self):
        super().__init__()
        self.title("Drag and drop")
        self.make_widgets()
        self.calc_size()
        self.make_shapes()
        self.bind_events()

    def make_widgets(self):
        self.canvas = tk.Canvas(self, bg='white', bd=4, relief=tk.RAISED)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def calc_size(self):
        self.update()
        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()

    def make_shapes(self):
        for _ in range(10):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            color = random.choice(self.colors)
            self.canvas.create_oval(x, y, x + 20, y + 20, fill=color,
                    tags='draggable')

    def bind_events(self):
        self.canvas.tag_bind('draggable', '<ButtonPress-1>',
                self.button_press)
        self.canvas.tag_bind('draggable', '<Button1-Motion>',
                self.button_motion)

    def button_press(self, event):
        item = self.canvas.find_withtag(tk.CURRENT)
        self.dnd_item = (item, event.x, event.y)

    def button_motion(self, event):
        x, y = event.x, event.y
        item, x0, y0 = self.dnd_item
        self.canvas.move(item, x-x0, y-y0)
        self.dnd_item = (item, x, y)


if __name__ == '__main__':
    app = App()
    app.mainloop()

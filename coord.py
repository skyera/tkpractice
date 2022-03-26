import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Basic canvas")
        self.init_ui()

    def init_ui(self):
        self.make_widgets()
        self.layout()
        self.bind_events()

    def make_widgets(self):
        self.canvas = tk.Canvas(self, bg='white')
        self.label = tk.Label(self)
        self.create_oval()

    def create_oval(self):
        self.oval_item = self.canvas.create_oval(0, 0, 20, 20, fill='red')

    def layout(self):
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.label.pack(fill=tk.X)

    def bind_events(self):
        self.canvas.bind('<Motion>', self.mouse_motion)

    def mouse_motion(self, event):
        self.show_pos(event)
        self.move_oval(event)
   
    def show_pos(self, event):
        x, y = event.x, event.y
        text = 'Mouse pos: ({}, {})'.format(x, y)
        self.label.config(text=text)

    def move_oval(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.oval_item, x, y, x + 20, y + 20)


if __name__ == '__main__':
    app = App()
    app.mainloop()

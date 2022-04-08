import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Find canvas item')
        self.current = None
        self.make_widgets()

    def make_widgets(self):
        self.make_canvas()
        self.make_shapes()
        self.make_label()

    def make_canvas(self):
        self.canvas = tk.Canvas(self, bg='white', bd=4, relief=tk.RAISED)
        self.canvas.bind('<Motion>', self.mouse_motion)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def make_shapes(self):
        self.update()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        positions = [(60, 60), (w-60,60), (60, h-60), (w-60,h-60)]
        for x, y in positions:
            self.canvas.create_rectangle(x-10,y-10,x+10,y+10, fill='red')

    def make_label(self):
        self.label = tk.Label(self, text='position', bg='gray90', fg='blue')
        self.label.pack(fill=tk.X) 

    def mouse_motion(self, event):
        self.canvas.itemconfig(self.current, fill='red')
        self.current = self.canvas.find_closest(event.x, event.y)
        self.canvas.itemconfig(self.current, fill='yellow')
        text = 'Mouse position {}, {}'.format(event.x, event.y)
        self.label.config(text=text)


if __name__ == '__main__':
    app = App()
    app.mainloop()


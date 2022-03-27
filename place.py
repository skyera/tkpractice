import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()
        self.bind_events()

    def make_widgets(self):
        self.place_a()
        self.place_b()
        self.place_c()
        self.place_d()
        self.place_e()
    
    def bind_events(self):
        self.bind('<Motion>', self.mouse_move)

    def mouse_move(self, event):
        x, y = event.x, event.y
        text = 'Mouse pos: ({}, {})'.format(x, y)
        print(text)

    def place_a(self):
        self.label_a = tk.Label(self, text='A', bg='yellow')
        self.label_a.place(relwidth=0.25, relheight=0.25)

    def place_b(self):
        self.label_b = tk.Label(self, text='B', bg='orange')
        self.label_b.place(x=100, anchor=tk.N, width=100, height=50)

    def place_c(self):
        self.label_c = tk.Label(self, text='C', bg='red')
        self.label_c.place(relx=0.5, rely=0.5, anchor=tk.CENTER,
                           relwidth=0.5, relheight=0.5)

    def place_d(self):
        self.label_d = tk.Label(self, text='D', bg='green')
        self.label_d.place(in_=self.label_c, anchor=tk.N + tk.W,
                           x=2, y=2,
                           relx=0.5, rely=0.5,
                           relwidth=0.5, relheight=0.5)

    def place_e(self):
        self.label_e = tk.Label(self, text='E', bg='blue')
        self.label_e.place(x=200, y=200, anchor=tk.S + tk.E,
                           relwidth=0.25, relheight=0.25)


if __name__ == '__main__':
    app = App()
    app.mainloop()


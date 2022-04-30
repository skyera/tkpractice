import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        tk.Button(self, text='Left').pack(side=tk.LEFT, fill=tk.X, expand=tk.NO)
        tk.Button(self, text='Center').pack(side=tk.LEFT, fill=tk.X, expand=tk.NO)
        tk.Button(self, text='Right').pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)


if __name__ == '__main__':
    app = App()
    app.mainloop()

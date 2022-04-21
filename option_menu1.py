import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        self.var = tk.StringVar()
        self.menu = tk.OptionMenu(self, self.var, 'A', 'B', 'C')
        self.menu.pack(fill=tk.X, padx=0, pady=10)
        self.var.set('A')
        self.btn = tk.Button(self, text='State', command=self.on_click)
        self.btn.pack(padx=5, pady=5)

    def on_click(self):
        print(self.var.get())


if __name__ == '__main__':
    app = App()
    app.mainloop()

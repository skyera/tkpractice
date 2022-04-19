import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        self.spinbox = tk.Spinbox(self, fg='red', from_=0, to=5, bg='gray90')
        self.scale = tk.Scale(self, from_=0, to=5, orient=tk.HORIZONTAL, fg='blue', bg='gray75')
        self.btn = tk.Button(self, text='Print', command=self.print_values)
        self.spinbox.pack(fill=tk.X, padx=10, pady=10)
        self.scale.pack(fill=tk.X, padx=10, pady=10)
        self.btn.pack()

    def print_values(self):
        print('spinbox: {}'.format(self.spinbox.get()))
        print('scale; {}'.format(self.scale.get()))


if __name__ == '__main__':
    app = App()
    app.mainloop()

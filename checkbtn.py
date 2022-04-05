import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        self.var = tk.IntVar()
        self.check_btn = tk.Checkbutton(self, text='Active?',
                bd=2, relief=tk.RIDGE, fg='blue', bg='gray90',
                activeforeground='red',
                activebackground='orange',
            variable=self.var, command=self.print_value)
        self.check_btn.pack()

    def print_value(self):
        print(self.var.get())


if __name__ == '__main__':
    app = App()
    app.mainloop()

import tkinter as tk


COLORS = [('red', 'red'), ('green', 'green'), ('blue', 'blue')]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        self.var = tk.StringVar()
        self.var.set("red")
        self.buttons = [self.create_radio(c) for c in COLORS]
        for button in self.buttons:
            button.pack(anchor=tk.W, padx=10, pady=10)

    def create_radio(self, option):
        text, value = option
        return tk.Radiobutton(self, text=text, value=value, foreground=value,
                command=self.print_option, variable=self.var)

    def print_option(self):
        print(self.var.get())


if __name__ == '__main__':
    app = App()
    app.mainloop()

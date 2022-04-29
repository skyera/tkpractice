import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.option_add('*font', ('verdana', 12, 'bold'))
        self.title('Pack1')
        self.make_widgets()

    def make_widgets(self):
        tk.Button(self, text='Left').pack(side=tk.LEFT)
        tk.Button(self, text='Center').pack(side=tk.LEFT)
        tk.Button(self, text='Right').pack(side=tk.LEFT)


if __name__ == '__main__':
    app = App()
    app.mainloop()



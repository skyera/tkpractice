import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()
        self.geometry('+300+150')

    def make_widgets(self):
        label1 = tk.Label(self, width=20, height=5, bg='SlateGray2')
        label1.pack(side=tk.TOP, pady=15, padx=10, fill=tk.BOTH, expand=True)

        label2 = tk.Label(self, width=20, height=5, bg='SlateGray3')
        label2.pack(side=tk.TOP, padx=10, fill=tk.BOTH, expand=True)

        label3 = tk.Label(self, width=20, height=5, bg='SlateGray4')
        label3.pack(side=tk.TOP, pady=15, padx=10, fill=tk.BOTH, expand=True)


if __name__ == '__main__':
    app = App()
    app.mainloop()

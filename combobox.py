import tkinter as tk
from tkinter import ttk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('500x250')
        self.make_widgets()

    def make_widgets(self):
        label = ttk.Label(self, text='Combobox', background='green',
                foreground='white', font=('Times New Roman', 15))
        label.grid(row=0, column=1)
        label2 = ttk.Label(self, text='Select Month:',
                font=('Times New ROman', 10))
        label2.grid(column=0, row=5, padx=10, pady=25)

        var = tk.StringVar()
        box = ttk.Combobox(self, width=27, textvariable=var)
        box['values'] = (' January', 
                          ' February',
                          ' March',
                          ' April',
                          ' May',
                          ' June',
                          ' July',
                          ' August',
                          ' September',
                          ' October',
                          ' November',
                          ' December')
        box.grid(column=1, row=5)
        box.current()


if __name__ == '__main__':
    app = App()
    app.mainloop()




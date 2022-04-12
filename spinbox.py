import tkinter as tk
import tkinter.ttk as ttk


class App(tk.Tk):
    cities = ('Toronto', 'Ottawa', 'Mantreal', 'Vancouver', 'St. John')
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        self.sb1 = tk.Spinbox(self, from_=1, to=10, width=10, state='readonly',
                readonlybackground='yellow')
        self.sb2 = tk.Spinbox(self, from_=0, to=3, increment=.5, format='%05.2f',
                width=10)
        self.sb3 = tk.Spinbox(self, values=sorted(self.cities), width=len(max(self.cities)) + 2)
        self.sb1.pack(padx=10)
        self.sb2.pack(padx=10)
        self.sb3.pack(padx=10)


if __name__ == '__main__':
    app = App()
    app.mainloop()

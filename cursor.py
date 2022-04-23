import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        btn = tk.Button(self, text='Spam', padx=10, pady=10)
        btn.pack(padx=20, pady=20)
        btn.config(cursor='gumby')
        btn.config(font=('helvetica', 20, 'underline italic'))


if __name__ == '__main__':
    app = App()
    app.mainloop()

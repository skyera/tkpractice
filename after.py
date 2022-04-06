import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        self.button = tk.Button(self, command=self.start_action,
                text='Wait 5 seconds',
                fg='red', bg='gray80',
                activeforeground='blue')
        self.button.pack(padx=50, pady=20)

    def start_action(self):
        self.button.config(state=tk.DISABLED)
        self.after(5000, lambda: self.button.config(state=tk.NORMAL))


if __name__ == '__main__':
    app = App()
    app.mainloop()

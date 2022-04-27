import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        frame = tk.Frame(self, width=500, height=400, bd=1)
        frame.pack(fill=tk.BOTH, expand=True)
        iframe = tk.Frame(frame, bd=2, relief=tk.RAISED)
        iframe.pack(fill=tk.X, expand=1, padx=5, pady=5)
        canvas = tk.Canvas(iframe, bg='white', width=340, height=100)
        canvas.pack(fill=tk.BOTH, expand=1)

        for i in range(25):
            canvas.create_oval(5+(4*i),5+(3*i),(5*i)+60, i+60, fill='gray70')
        canvas.create_text(260, 80, text='Canvas', font=('verdana', 10, 'bold'))


if __name__ == '__main__':
    app = App()
    app.mainloop()

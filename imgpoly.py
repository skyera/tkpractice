import tkinter as tk
from PIL import Image, ImageTk


class MainFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.make_widgets()

    def make_widgets(self):
        pass


class View(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('600x400')


class Model(object):
    def __init__(self):
        pass


class Controller(object):
    def __init__(self, model, view):
        self.model = model
        self.view = view


class App:
    def __init__(self):
        self.model = Model()
        self.view = View()
        self.controller = Controller(self.model, self.view)

    def run(self):
        self.view.mainloop()


if __name__ == '__main__':
    app = App()
    app.run()


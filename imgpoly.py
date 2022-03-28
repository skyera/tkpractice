from PIL import Image, ImageTk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import tkinter.ttk as ttk


class ImageGalleryFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__()
        self.make_widgets()
    
    def make_widgets(self):
        self.make_info_label()
        self.make_scrolledtext()

    def make_info_label(self):
        self.info_label = tk.Label(self, text='Image Gallery', bg='gray80')
        self.info_label.pack(fill=tk.X, padx=5, pady=5)

    def make_scrolledtext(self):
        self.stext = ScrolledText(self)
        self.stext.pack(fill=tk.BOTH, expand=True)


class MainFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.make_widgets()

    def make_widgets(self):
        self.pw = ttk.PanedWindow(orient=tk.HORIZONTAL)
        self.pw.pack(fill=tk.BOTH, expand=True)
        self.make_left_pane()
        self.make_right_pane()
    
    def make_left_pane(self):
        self.left_pane = ImageGalleryFrame(self.pw)
        self.pw.add(self.left_pane)

    def make_right_pane(self):
        pass


class View(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('600x400')
        self.make_menu()
        self.make_frame()

    def make_menu(self):
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        self.make_file_menu()

    def make_file_menu(self):
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label='Open')
        file_menu.add_separator()
        file_menu.add_command(label='Quit', command=self.destroy)
        self.menu.add_cascade(label='File', menu=file_menu)
        self.file_menu = file_menu

    def make_frame(self):
        self.main_frame = MainFrame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)


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


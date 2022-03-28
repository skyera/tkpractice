from PIL import Image, ImageTk
import os
import tkinter as tk
import tkinter.filedialog as fd
from tkinter.scrolledtext import ScrolledText
import tkinter.ttk as ttk


class ImageGalleryFrame(tk.Frame):
    def __init__(self, parent, **options):
        super().__init__(**options)
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

    def display_images(self, images):
        self.stext.delete("1.0", tk.END)
        for img in images:
            self.stext.image_create(tk.END, image=img)
        self.stext.config(state=tk.DISABLED)


class ImagePolyFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.make_widgets()

    def make_widgets(self):
        self.make_info_label()
        self.make_canvas()
    
    def make_info_label(self):
        self.info_label = tk.Label(self, text='Canvas playground', bg='gray90', bd=2)
        self.info_label.pack(fill=tk.X, padx=5, pady=5)
    
    def make_canvas(self):
        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)


class MainFrame(tk.Frame):
    def __init__(self, parent, **options):
        super().__init__(parent, **options)
        self.make_widgets()
    
    def make_panedwindow(self):
        self.pw = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.pw.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def make_widgets(self):
        self.make_info_panel()
        self.make_panedwindow()
        self.make_left_pane()
        self.make_right_pane()

    def make_info_panel(self):
        group = tk.LabelFrame(self, padx=5, pady=5, text='Info')
        group.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)
        tk.Label(group, text='Path').grid(row=0, column=0)
    
    def make_left_pane(self):
        self.left_pane = ImageGalleryFrame(self.pw, width=100)
        self.left_pane.pack(fill=tk.BOTH, expand=True)
        self.pw.add(self.left_pane, width=150)

    def make_right_pane(self):
        self.right_pane = ImagePolyFrame(self.pw)
        self.right_pane.pack(fill=tk.BOTH, expand=True)
        self.pw.add(self.right_pane, width=300)

    def display_images(self, images):
        self.left_pane.display_images(images)


class View(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('800x600')
        self.make_menu()
        self.make_frame()

    def make_menu(self):
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        self.make_file_menu()

    def make_file_menu(self):
        file_menu = tk.Menu(self.menu, tearoff=0)
        self.open_menu_item = file_menu.add_command(label='Open', command=self.on_open)
        file_menu.add_separator()
        file_menu.add_command(label='Quit', command=self.destroy)
        self.menu.add_cascade(label='File', menu=file_menu)
        self.file_menu = file_menu

    def make_frame(self):
        self.main_frame = MainFrame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
    def set_controller(self, controller):
        self.controller = controller

    def on_open(self):
        self.controller.on_open_directory()

    def display_images(self, images):
        self.main_frame.display_images(images)


class Model(object):
    def __init__(self):
        self.image_fnames = []

    def set_image_fnames(self, image_fnames):
        self.image_fnames = image_fnames
        self.read_images()
    
    def read_images(self):
        self.images = []
        for fname in self.image_fnames:
            self.read_image(fname)

    def read_image(self, fname):
        image = Image.open(fname)
        image.thumbnail((128, 128))
        self.images.append(ImageTk.PhotoImage(image))


def choose_directory():
    directory = fd.askdirectory(title='Open directory')
    if directory:
        print(directory)
    return directory


def collect_images(directory):
    fnames = os.listdir(directory)
    fnames = [os.path.join(directory, name) for name in fnames]
    return fnames


class Controller(object):
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.bind_events()
    
    def bind_events(self):
        pass

    def on_open_directory(self):
        fnames = self.get_image_names()
        self.model.set_image_fnames(fnames)
        self.view.display_images(self.model.images)

    def get_image_names(self):
        directory = choose_directory()
        fnames = []
        if directory:
            fnames = collect_images(directory)
        return fnames


class App:
    def __init__(self):
        self.model = Model()
        self.view = View()
        self.controller = Controller(self.model, self.view)
        self.view.set_controller(self.controller)

    def run(self):
        self.view.mainloop()


if __name__ == '__main__':
    app = App()
    app.run()


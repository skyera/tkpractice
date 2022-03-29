from functools import partial
from PIL import Image, ImageTk
import os
import tkinter as tk
import tkinter.filedialog as fd
from tkinter.scrolledtext import ScrolledText
import tkinter.ttk as ttk


class ImageFrame(tk.Frame):
    def __init__(self, parent, image, img_index, controller, **options):
        super().__init__(parent, **options)
        self.image = image
        self.img_index = img_index
        self.controller = controller
        self.make_widgets()
        self.bind_events()

    def make_widgets(self):
        self.label = tk.Label(self, image=self.image)
        self.label.pack(fill=tk.BOTH, expand=True)

    def bind_events(self):
        self.label.bind('<Double-Button-1>', self.on_double_click)

    def on_double_click(self, event):
        print('d click')
        self.controller.show_one_image(self.img_index)


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
        for img_index, img in enumerate(images):
            img_label = ImageFrame(self.stext, img, img_index, self.controller, bd=4, relief=tk.RAISED)
            self.stext.window_create(tk.END, window=img_label)
        self.stext.config(state=tk.DISABLED)

    def set_controller(self, controller):
        self.controller = controller



class ScrolledCanvas(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)
        self.make_widgets()
        self.layout_widegts()
        self.bind_events()
        self.poly_item = None
        self.process_movements()

    def make_widgets(self):
        self.scroll_x = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.scroll_y = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.canvas = tk.Canvas(self, width=300, height=100,
                                xscrollcommand=self.scroll_x.set,
                                yscrollcommand=self.scroll_y.set)
        self.scroll_x.config(command=self.canvas.xview)
        self.scroll_y.config(command=self.canvas.yview)

    def layout_widegts(self):
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.scroll_x.grid(row=1, column=0, sticky='we')
        self.scroll_y.grid(row=0, column=1, sticky='ns')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
    
    def bind_events(self):
        self.bind('<Configure>', self.resize)
        self.canvas.tag_bind("draggable", '<ButtonPress-1>', self.button_press)
        self.canvas.tag_bind("draggable", '<Button1-Motion>', self.button_motion)
        self.pressed_keys = {}
        self.canvas.bind("<KeyPress>", self.key_press)
        self.canvas.bind("<KeyRelease>", self.key_release)
    
    def key_press(self, event):
        print('key press')
        self.pressed_keys[event.keysym] = True

    def key_release(self, event):
        print('key release')
        self.pressed_keys.pop(event.keysym, None)
    
    def button_press(self, event):
        item = self.canvas.find_withtag(tk.CURRENT)
        self.dnd_item = (item, event.x, event.y)
    
    def process_movements(self):
        if self.poly_item != None:
            self.calc_move_offsets()
            if self.off_x != 0 or self.off_y != 0:
                self.canvas.move(self.poly_item, self.off_x, self.off_y)
        self.after(10, self.process_movements)

    def button_motion(self, event):
        x, y = event.x, event.y
        item, x0, y0 = self.dnd_item
        self.canvas.move(item, x-x0, y-y0)
        self.dnd_item = (item, x, y)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def resize(self, event):
        self.update_canvas_region()

    def update_canvas_region(self):
        region = self.canvas.bbox(tk.ALL)
        self.canvas.configure(scrollregion=region)
    
    def create_polygon(self, zoom_level):
        self.points = [150, 100, 200, 120, 240, 180, 210,
            200, 150, 150, 100, 200]
        points = [p * zoom_level for p in self.points]

        self.canvas.delete(self.poly_item)
        self.poly_item = self.canvas.create_polygon(points,
                                outline='red', fill='yellow', width=1,
                                tags='draggable')

    def show_image(self, image, zoom_level):
        self.image = image
        self.canvas.delete(tk.ALL)
        self.canvas.create_image(0, 0, image=self.image, anchor=tk.NW)
        self.create_polygon(zoom_level)
        self.update_canvas_region()
    
    def calc_move_offsets(self):
        self.off_x, self.off_y = 0, 0
        self.speed = 3

        self.calc_right_move()
        self.calc_left_move()
        self.calc_down_move()
        self.calc_up_move()
    
    def calc_right_move(self):
        if 'Right' in self.pressed_keys:
            self.off_x += self.speed
    
    def calc_left_move(self):
        if 'Left' in self.pressed_keys:
            self.off_x -= self.speed

    def calc_down_move(self):
        if 'Down' in self.pressed_keys:
            self.off_y += self.speed

    def calc_up_move(self):
        if 'Up' in self.pressed_keys:
            self.off_y -= self.speed


class ImagePolyFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.make_widgets()

    def make_widgets(self):
        self.make_info_label()
        self.make_canvas()
        self.make_scale()
    
    def make_info_label(self):
        self.info_label = tk.Label(self, text='Canvas playground', bg='gray90', bd=2)
        self.info_label.pack(fill=tk.X, padx=5, pady=5)
    
    def make_canvas(self):
        self.canvas_frame = ScrolledCanvas(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

    def make_scale(self):
        self.scale = tk.Scale(self, from_=1, to=10, orient=tk.HORIZONTAL, command=self.on_scale)
        self.scale.pack(fill=tk.X)

    def on_scale(self, level):
        print(level)
        level = int(level)
        self.controller.scale_image(level)

    def show_image(self, image, zoom_level):
        self.canvas_frame.show_image(image, zoom_level)

    def set_controller(self, controller):
        self.controller = controller


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

    def set_controller(self, controller):
        self.controller = controller
        self.left_pane.set_controller(controller)
        self.right_pane.set_controller(controller)

    def show_one_image(self, image, zoom_level):
        self.right_pane.show_image(image, zoom_level)


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
        self.main_frame.set_controller(controller)

    def on_open(self):
        self.controller.on_open_directory()

    def display_images(self, images):
        self.main_frame.display_images(images)
    
    def show_one_image(self, image, zoom_level):
        self.main_frame.show_one_image(image, zoom_level)


class Model(object):
    def __init__(self):
        self.image_fnames = []
        self.curr_image_index = -1
        self.small_images = []
        self.images = []
        self.orig_images = []

    def set_image_fnames(self, image_fnames):
        self.image_fnames = image_fnames
        self.read_images()
    
    def read_images(self):
        self.small_images = []
        self.images = []
        self.orig_images = []
        for fname in self.image_fnames:
            self.read_image(fname)

    def read_image(self, fname):
        image = Image.open(fname)
        self.orig_images.append(image)
        self.images.append(ImageTk.PhotoImage(image))
        small_image = image.copy()
        small_image.thumbnail((128, 128))
        self.small_images.append(ImageTk.PhotoImage(small_image))

    def get_image(self, index):
        return self.images[index]

    def set_curr_image(self, img_index):
        self.curr_image_index = img_index

    def get_scaled_image(self, level):
        orig_img = self.orig_images[self.curr_image_index]
        size = orig_img.width * level, orig_img.height * level
        new_image = orig_img.resize(size)
        return ImageTk.PhotoImage(new_image)


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
        self.view.display_images(self.model.small_images)

    def get_image_names(self):
        directory = choose_directory()
        fnames = []
        if directory:
            fnames = collect_images(directory)
        return fnames

    def show_one_image(self, img_index):
        print('image index', img_index)
        self.model.set_curr_image(img_index)
        image = self.model.get_image(img_index)
        self.view.show_one_image(image, zoom_level=1)

    def scale_image(self, zoom_level):
        if self.model.curr_image_index == -1:
            return
        
        scaled_image = self.model.get_scaled_image(zoom_level)
        self.view.show_one_image(scaled_image, zoom_level)


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

from PIL import Image, ImageTk
import tkinter as tk
import tkinter.filedialog as fd


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()
        self.layout_widgets()
        self.bind_events()
        self.update_idletasks()
        self.minsize(self.winfo_width(), self.winfo_height())

    def make_widgets(self):
        self.make_scrollbars()
        self.make_canvas()
        self.make_image_frame()
        self.make_load_image_button()

    def make_scrollbars(self):
        self.scroll_x = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.scroll_y = tk.Scrollbar(self, orient=tk.VERTICAL)

    def make_canvas(self):
        self.canvas = tk.Canvas(self, width=300, height=100,
                                xscrollcommand=self.scroll_x.set,
                                yscrollcommand=self.scroll_y.set)
        self.scroll_x.config(command=self.canvas.xview)
        self.scroll_y.config(command=self.canvas.yview)
        
    def make_image_frame(self):
        self.image_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.image_frame, anchor=tk.NW)
        self.image_label = tk.Label(self.image_frame, text='Image')
        self.image_label.pack(fill=tk.BOTH, expand=True)

    def make_load_image_button(self):
        self.load_image_button = tk.Button(self, text='Load image', command=self.load_image)

    def layout_widgets(self):
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.scroll_x.grid(row=1, column=0, sticky='we')
        self.scroll_y.grid(row=0, column=1, sticky='ns')
        self.load_image_button.grid(row=2, column=0, padx=10, pady=10)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def load_image(self):
        filetypes = (('Images', '*.jpg *.gif *.png'), ('All files', '*'))
        filename = fd.askopenfilename(title='Open Image', filetypes=filetypes)
        if filename:
            print(filename)
            image = Image.open(filename)
            self.image = ImageTk.PhotoImage(image)
            self.image_label.config(image=self.image)

    def bind_events(self):
        self.bind('<Configure>', self.resize)

    def resize(self, event):
        region = self.canvas.bbox(tk.ALL)
        self.canvas.configure(scrollregion=region)


if __name__ == '__main__':
    app = App()
    app.mainloop()


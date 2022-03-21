import os
from PIL import Image, ImageTk
import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()
        self.info_displayed = False
        self.display_image(0)

    def make_widgets(self):
        self.frame = tk.Frame(self, width=400, height=620,
                              bg='gray50', relief=tk.RAISED,
                              bd=4)
        self.make_image_label()
        self.make_image_buttons()
        self.make_done_button()
        self.make_info_button()
        self.frame.pack(expand=True, fill=tk.BOTH)
    
    def make_image_label(self):
        self.image_label = tk.Label(self.frame)
        self.image_label.place(relx=0.5, rely=0.48, anchor=tk.CENTER)

    def make_image_buttons(self):
        self.image_fnames = os.listdir('images')
        self.xpos = 0.05
        
        for i in range(len(self.image_fnames)):
            self.make_one_image_button(i)

    def make_one_image_button(self, i):
        btn = tk.Button(self.frame, text='%d'% (i+1),
                        bg='gray10', fg='white',
                        command=lambda : self.display_image(i))
        btn.place(relx=self.xpos, rely=0.99, anchor=tk.S)
        self.xpos += 0.08

    def make_done_button(self):
        done_btn = tk.Button(self.frame, text='Done', command=self.destroy,
                             bg='red', fg='yellow')
        done_btn.place(relx=0.99, rely=0.99, anchor=tk.SE)

    def make_info_button(self):
        btn_info = tk.Button(self.frame, text="info", command=self.show_image_info,
                             bg='blue', fg='yellow')
        btn_info.place(relx=0.99, rely=0.90, anchor=tk.SE)
    
    def display_image(self, index):
        self.image = Image.open(os.path.join('images', self.image_fnames[index]))
        self.image.thumbnail((400, 400))
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.image_label.config(image=self.tk_image)
        self.show_image_info()

    def show_image_info(self):
        if hasattr(self, 'info_frame'):
            self.info_frame.destroy()

        self.make_image_info_frame()
        self.make_image_info_labels()
    
    def make_image_info_frame(self):
        self.info_frame = tk.Frame(self, bg='gray10')
        self.info_frame.place(in_=self.image_label,
                              relx=0.5,
                              relwidth=1.0,
                              height=50,
                              anchor=tk.S,
                              rely=0.0,
                              y=-4,
                              bordermode='outside')

    def make_image_info_labels(self):
        self.ypos = 0.15
        for attr_name in ['Format', 'Size', 'Mode']:
            self.make_image_info_label(attr_name)

    def make_image_info_label(self, attr_name):
        attr_label = tk.Label(self.info_frame,
                              text=self.get_image_attr(attr_name),
                              bg='gray10', fg='white',
                              font=('verdana', 8))
        attr_label.place(relx=0.3, rely=self.ypos, anchor=tk.W)
        self.ypos += 0.35
     
    def get_image_attr(self, attr_name):                             
        attr_value = getattr(self.image, attr_name.lower())
        text = '%s:\t%s' % (attr_name, attr_value)
        return text


if __name__ == '__main__':
    app = App()
    app.mainloop()

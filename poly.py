from PIL import Image, ImageTk
import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shape")
        self.make_widgets()
        self.bind_events()
        self.process_movements()

    def make_widgets(self):
        self.make_canvas_frame()
        self.make_canvas()
        self.load_image()
        self.create_polygon()
        self.create_rect()
        self.make_scale()

    def make_canvas_frame(self):
        self.frame = tk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=1)
        
    def make_canvas(self):
        self.scroll_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.scroll_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.canvas = tk.Canvas(self.frame, bg='white', bd=2,
                                xscrollcommand=self.scroll_x.set,
                                yscrollcommand=self.scroll_y.set)
        self.scroll_x.config(command=self.canvas.xview)
        self.scroll_y.config(command=self.canvas.yview)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.scroll_x.grid(row=1, column=0, sticky='we')
        self.scroll_y.grid(row=0, column=1, sticky='ns')
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
    
    def create_polygon(self):
        self.points = [150, 100, 200, 120, 240, 180, 210,
            200, 150, 150, 100, 200]

        self.poly_item = self.canvas.create_polygon(self.points,
                                outline='red', fill='yellow', width=1,
                                tags='draggable')

    def create_rect(self):
        self.rect = self.canvas.create_rectangle(230, 10, 290, 60,
                                            outline="red", fill="gray90", 
                                            width=2, tags='draggable')

    def make_scale(self):
        self.zoom = tk.Scale(self, from_=1, to=10, 
                             orient=tk.HORIZONTAL,
                             command=self.change_zoom)
        self.zoom.pack(fill=tk.X)

    def load_image(self):
        img = Image.open('images/boat.jpg')
        self.img = ImageTk.PhotoImage(img)
        self.canvas.create_image(100, 100, anchor=tk.NW, image=self.img, tags='draggable')

    def mouse_motion(self, event):
        x, y = event.x, event.y
        print('mouse pos', x, y)
        cx = self.canvas.canvasx(x)
        cy = self.canvas.canvasy(y)
        print('canvas pos', cx, cy)
    
    def change_zoom(self, level):
        level = int(level)
        ps = [ x * level for x in self.points]
        self.canvas.coords(self.poly_item, ps)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def bind_events(self):
        self.frame.bind('<Configure>', self.resize)
        self.canvas.bind('<Motion>', self.mouse_motion)
        self.pressed_keys = {}
        self.bind("<KeyPress>", self.key_press)
        self.bind("<KeyRelease>", self.key_release)
        self.canvas.tag_bind("draggable", '<ButtonPress-1>', self.button_press)
        self.canvas.tag_bind("draggable", '<Button1-Motion>', self.button_motion)

    def key_press(self, event):
        self.pressed_keys[event.keysym] = True

    def key_release(self, event):
        self.pressed_keys.pop(event.keysym, None)

    def process_movements(self):
        self.calc_move_offsets()
        self.canvas.move(self.poly_item, self.off_x, self.off_y)
        self.after(10, self.process_movements)
        
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

    def button_press(self, event):
        item = self.canvas.find_withtag(tk.CURRENT)
        self.dnd_item = (item, event.x, event.y)

    def button_motion(self, event):
        x, y = event.x, event.y
        item, x0, y0 = self.dnd_item
        self.canvas.move(item, x-x0, y-y0)
        self.dnd_item = (item, x, y)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def resize(self, event):
        region = self.canvas.bbox(tk.ALL)
        self.canvas.configure(scrollregion=region)


if __name__ == '__main__':
    app = App()
    app.mainloop()


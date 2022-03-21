import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shape")
        self.make_widgets()
        self.bind_events()
        self.process_movements()

    def make_widgets(self):
        self.frame = tk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=1)

        self.canvas = tk.Canvas(self.frame, bg='white', bd=2)
        self.points = [150, 100, 200, 120, 240, 180, 210,
            200, 150, 150, 100, 200]

        self.poly_item = self.canvas.create_polygon(self.points,
                                outline='#f11', fill='#1f1', width=2,
                                tags='draggable')
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.zoom = tk.Scale(self.frame, from_=1, to=4, 
                             orient=tk.HORIZONTAL,
                             command=self.change_zoom)
        self.zoom.pack()
    
    def change_zoom(self, level):
        level = int(level)
        ps = [ x * level for x in self.points]
        self.canvas.coords(self.poly_item, ps)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def bind_events(self):
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


if __name__ == '__main__':
    app = App()
    app.mainloop()


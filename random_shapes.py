import tkinter as tk
import random

selected_shape = None
offset_x = 0
offset_y = 0

def random_color():
    return "#{:02x}{:02x}{:02x}".format(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

def draw_random_shapes():
    canvas.delete("all")
    for _ in range(random.randint(5, 15)):
        shape_type = random.choice(["rectangle", "oval", "polygon"])
        color = random_color()
        x1 = random.randint(0, 550)
        y1 = random.randint(0, 350)
        x2 = x1 + random.randint(20, 100)
        y2 = y1 + random.randint(20, 100)
        
        if shape_type == "rectangle":
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", tags=("shape",))
        elif shape_type == "oval":
            canvas.create_oval(x1, y1, x2, y2, fill=color, outline="black", tags=("shape",))
        else:
            points = [
                x1, y1,
                x1 + random.randint(-50, 50), y2,
                x2, y2,
                x1, y1 + random.randint(-50, 50)
            ]
            canvas.create_polygon(points, fill=color, outline="black", tags=("shape",))

def on_mouse_down(event):
    global selected_shape, offset_x, offset_y
    selected_shape = canvas.find_closest(event.x, event.y)
    if selected_shape:
        canvas.itemconfig(selected_shape, outline="blue", width=2)
        bbox = canvas.bbox(selected_shape)
        offset_x = event.x - bbox[0]
        offset_y = event.y - bbox[1]

def on_mouse_drag(event):
    global selected_shape, offset_x, offset_y
    if selected_shape:
        canvas.move(selected_shape, event.x - offset_x - canvas.coords(selected_shape)[0], event.y - offset_y - canvas.coords(selected_shape)[1])
        offset_x = event.x - canvas.coords(selected_shape)[0]
        offset_y = event.y - canvas.coords(selected_shape)[1]

def on_mouse_up(event):
    global selected_shape, offset_x, offset_y
    if selected_shape:
        canvas.itemconfig(selected_shape, outline="black", width=1)
        selected_shape = None

root = tk.Tk()
root.title("Random Shapes")

canvas = tk.Canvas(root, width=600, height=400, bg="white")
canvas.pack()

canvas.tag_bind("shape", "<Button-1>", on_mouse_down)
canvas.tag_bind("shape", "<B1-Motion>", on_mouse_drag)
canvas.tag_bind("shape", "<ButtonRelease-1>", on_mouse_up)

btn = tk.Button(root, text="Generate", command=draw_random_shapes)
btn.pack(pady=10)

draw_random_shapes()
root.mainloop()